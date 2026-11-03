"""ユースケース「銘柄の翌日騰落を予測し、過去データで検証する」。

このクラスはポート（抽象）とドメインだけに依存する。
株価の取得元・特徴量の作り方・学習ライブラリは、外から注入される。
"""
from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.application.benchmark import benchmark_ticker_for
from app.application.dto import (
    EquityPoint, FeatureSet, Metrics, PredictStockInput, PredictStockOutput, PricePoint,
)
from app.application.errors import ApplicationError
from app.application.ports.predictor import FeatureBuilder, PredictorFactory
from app.application.ports.price_repository import PriceRepository
from app.domain.backtest import run_backtest
from app.domain.entities import PriceHistory
from app.domain.errors import DomainError, InsufficientDataError
from app.domain.evaluation import evaluate_accuracy
from app.domain.labels import next_day_return, up_label
from app.domain.timeseries import holdout_folds, walk_forward_folds


@dataclass(frozen=True)
class PredictStockConfig:
    test_ratio: float = 0.3  # テスト期間の割合
    min_rows: int = 200  # 学習に必要な最小営業日数
    chart_days: int = 500  # 画面に返す株価の日数
    threshold: float = 0.5  # この確率を超えたら「上がる」と判断
    retrain_every: int = 20  # ウォークフォワードで再学習する間隔（約1か月）


class PredictStockUseCase:
    def __init__(
        self,
        repo: PriceRepository,
        feature_builders: Mapping[FeatureSet, FeatureBuilder],
        predictor_factory: PredictorFactory,
        config: PredictStockConfig = PredictStockConfig(),
    ):
        self.repo = repo
        self.feature_builders = feature_builders
        self.predictor_factory = predictor_factory
        self.config = config

    def execute(self, inp: PredictStockInput) -> PredictStockOutput:
        cfg = self.config
        builder = self.feature_builders[inp.feature_set]
        history = self.repo.get_price_history(inp.ticker, inp.period)
        benchmark = self._load_benchmark(inp) if builder.uses_benchmark else None

        # 1. 特徴量とラベルを揃える
        x_all = builder.build(history, benchmark)
        next_ret = next_day_return(history.close)
        labeled = x_all.notna().all(axis=1) & next_ret.notna()
        x, r = x_all[labeled], next_ret[labeled]
        y = up_label(r)

        if len(x) < cfg.min_rows:
            raise InsufficientDataError(
                f"データが少なすぎます（{cfg.min_rows}営業日以上必要、現在 {len(x)}）"
            )
        latest_x = x_all.dropna().iloc[[-1]]  # 答えがまだ無い最新日

        # 2. 検証：区間ごとに「その直前までのデータ」で学習して予測する
        if inp.validation == "walk_forward":
            folds = walk_forward_folds(len(x), cfg.test_ratio, cfg.retrain_every)
        else:
            folds = holdout_folds(len(x), cfg.test_ratio)

        proba = np.concatenate([
            self._fit_predict(x.iloc[: f.train_end], y.iloc[: f.train_end], x.iloc[f.test_start : f.test_end])
            for f in folds
        ])
        split = folds[0].test_start
        x_test, y_test, y_train = x.iloc[split:], y.iloc[split:], y.iloc[:split]
        pred = (proba > cfg.threshold).astype(int)
        acc = evaluate_accuracy(pred, y_test, y_train)

        # 3. バックテスト
        bt = run_backtest(pd.Series(pred, index=x_test.index), r.iloc[split:], inp.cost)

        # 4. 全データで学習し直して最新日の予測
        next_up_prob = float(self._fit_predict(x, y, latest_x)[0])

        chart = history.close.iloc[-cfg.chart_days:]
        return PredictStockOutput(
            ticker=inp.ticker.upper(),
            name=self.repo.get_company_name(inp.ticker),
            latest_date=latest_x.index[-1].date(),
            latest_close=history.latest_close,
            next_up_probability=next_up_prob,
            metrics=Metrics(
                train_period=(x.index[0].date(), x.index[split - 1].date()),
                test_period=(x_test.index[0].date(), x_test.index[-1].date()),
                test_days=len(x_test),
                accuracy=acc.accuracy,
                baseline_accuracy=acc.baseline_accuracy,
                strategy_return=bt.strategy_return,
                buy_hold_return=bt.buy_hold_return,
                strategy_max_drawdown=bt.strategy_max_drawdown,
                buy_hold_max_drawdown=bt.buy_hold_max_drawdown,
                trades=bt.trades,
                cost_per_trade=inp.cost,
                validation=inp.validation,
                retrain_every=cfg.retrain_every if inp.validation == "walk_forward" else None,
                folds=len(folds),
                feature_set=inp.feature_set,
                feature_count=x.shape[1],
                benchmark=benchmark.ticker if benchmark is not None else None,
            ),
            prices=[PricePoint(d.date(), round(float(c), 4)) for d, c in chart.items()],
            equity=[
                EquityPoint(d.date(), round(float(s), 4), round(float(b), 4))
                for d, s, b in zip(
                    bt.strategy_equity.index,
                    bt.strategy_equity.to_numpy(),
                    bt.buy_hold_equity.to_numpy(),
                )
            ],
        )

    def _fit_predict(self, x_train: pd.DataFrame, y_train: pd.Series, x_pred: pd.DataFrame) -> np.ndarray:
        model = self.predictor_factory()
        model.fit(x_train, y_train)
        return model.predict_proba_up(x_pred)

    def _load_benchmark(self, inp: PredictStockInput) -> PriceHistory | None:
        """市場指数の株価。取れなくても予測は続ける（指数なしの特徴量で学習する）。"""
        ticker = benchmark_ticker_for(inp.ticker)
        if ticker is None:
            return None
        try:
            return self.repo.get_price_history(ticker, inp.period)
        except (ApplicationError, DomainError):
            return None
