"""ユースケース「銘柄の翌日騰落を予測し、過去データで検証する」。

このクラスはポート（抽象）とドメインだけに依存する。
株価の取得元・特徴量の作り方・学習ライブラリは、外から注入される。
"""
from dataclasses import dataclass

import pandas as pd

from app.application.dto import (
    EquityPoint, Metrics, PredictStockInput, PredictStockOutput, PricePoint,
)
from app.application.ports.predictor import FeatureBuilder, PredictorFactory
from app.application.ports.price_repository import PriceRepository
from app.domain.backtest import run_backtest
from app.domain.errors import InsufficientDataError
from app.domain.evaluation import evaluate_accuracy
from app.domain.labels import next_day_return, up_label
from app.domain.timeseries import chronological_split_point


@dataclass(frozen=True)
class PredictStockConfig:
    test_ratio: float = 0.3  # テスト期間の割合
    min_rows: int = 200  # 学習に必要な最小営業日数
    chart_days: int = 500  # 画面に返す株価の日数
    threshold: float = 0.5  # この確率を超えたら「上がる」と判断


class PredictStockUseCase:
    def __init__(
        self,
        repo: PriceRepository,
        features: FeatureBuilder,
        predictor_factory: PredictorFactory,
        config: PredictStockConfig = PredictStockConfig(),
    ):
        self.repo = repo
        self.features = features
        self.predictor_factory = predictor_factory
        self.config = config

    def execute(self, inp: PredictStockInput) -> PredictStockOutput:
        cfg = self.config
        history = self.repo.get_price_history(inp.ticker, inp.period)

        # 1. 特徴量とラベルを揃える
        x_all = self.features.build(history)
        next_ret = next_day_return(history.close)
        labeled = x_all.notna().all(axis=1) & next_ret.notna()
        x, r = x_all[labeled], next_ret[labeled]
        y = up_label(r)
        latest_x = x_all.dropna().iloc[[-1]]  # 答えがまだ無い最新日

        if len(x) < cfg.min_rows:
            raise InsufficientDataError(
                f"データが少なすぎます（{cfg.min_rows}営業日以上必要、現在 {len(x)}）"
            )

        # 2. 時系列順に分割して学習・評価
        split = chronological_split_point(len(x), cfg.test_ratio)
        x_train, x_test = x.iloc[:split], x.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        model = self.predictor_factory()
        model.fit(x_train, y_train)
        pred = (model.predict_proba_up(x_test) > cfg.threshold).astype(int)
        acc = evaluate_accuracy(pred, y_test, y_train)

        # 3. バックテスト
        bt = run_backtest(pd.Series(pred, index=x_test.index), r.iloc[split:], inp.cost)

        # 4. 全データで学習し直して最新日の予測
        final_model = self.predictor_factory()
        final_model.fit(x, y)
        next_up_prob = float(final_model.predict_proba_up(latest_x)[0])

        chart = history.close.iloc[-cfg.chart_days:]
        return PredictStockOutput(
            ticker=inp.ticker.upper(),
            name=self.repo.get_company_name(inp.ticker),
            latest_date=latest_x.index[-1].date(),
            latest_close=history.latest_close,
            next_up_probability=next_up_prob,
            metrics=Metrics(
                train_period=(x_train.index[0].date(), x_train.index[-1].date()),
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
