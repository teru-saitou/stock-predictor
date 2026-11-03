"""ユースケースの入出力（DTO）。presentation との受け渡しに使う。"""
from dataclasses import dataclass
from datetime import date
from typing import Literal

FeatureSet = Literal["basic", "extended"]
Validation = Literal["walk_forward", "holdout"]

DEFAULT_PERIOD = "5y"
DEFAULT_COST = 0.001  # 片道の取引コスト（0.1%）
DEFAULT_FEATURE_SET: FeatureSet = "extended"
DEFAULT_VALIDATION: Validation = "walk_forward"


@dataclass(frozen=True)
class PredictStockInput:
    ticker: str
    period: str = DEFAULT_PERIOD
    cost: float = DEFAULT_COST
    feature_set: FeatureSet = DEFAULT_FEATURE_SET
    validation: Validation = DEFAULT_VALIDATION


@dataclass(frozen=True)
class PricePoint:
    date: date
    close: float


@dataclass(frozen=True)
class EquityPoint:
    date: date
    strategy: float
    buy_hold: float


@dataclass(frozen=True)
class Metrics:
    train_period: tuple[date, date]  # 最初の学習期間（ウォークフォワードではここから広がっていく）
    test_period: tuple[date, date]
    test_days: int
    accuracy: float
    baseline_accuracy: float
    strategy_return: float
    buy_hold_return: float
    strategy_max_drawdown: float
    buy_hold_max_drawdown: float
    trades: int
    cost_per_trade: float
    validation: Validation
    retrain_every: int | None  # ウォークフォワードの再学習間隔（営業日）
    folds: int  # 学習し直した回数
    feature_set: FeatureSet
    feature_count: int
    benchmark: str | None  # 使った市場指数（使っていなければ None）


@dataclass(frozen=True)
class PredictStockOutput:
    ticker: str
    name: str | None
    latest_date: date
    latest_close: float
    next_up_probability: float
    metrics: Metrics
    prices: list[PricePoint]
    equity: list[EquityPoint]
