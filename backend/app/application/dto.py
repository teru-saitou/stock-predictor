"""ユースケースの入出力（DTO）。presentation との受け渡しに使う。"""
from dataclasses import dataclass
from datetime import date

DEFAULT_PERIOD = "5y"
DEFAULT_COST = 0.001  # 片道の取引コスト（0.1%）


@dataclass(frozen=True)
class PredictStockInput:
    ticker: str
    period: str = DEFAULT_PERIOD
    cost: float = DEFAULT_COST


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
    train_period: tuple[date, date]
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
