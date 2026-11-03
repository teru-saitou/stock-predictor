"""API のレスポンス型（Pydantic）。/docs にもこの型が表示される。"""
from datetime import date

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PricePointOut(_Base):
    date: date
    close: float


class EquityPointOut(_Base):
    date: date
    strategy: float
    buy_hold: float


class MetricsOut(_Base):
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


class PredictResponse(_Base):
    ticker: str
    name: str | None = None
    latest_date: date
    latest_close: float
    next_up_probability: float
    metrics: MetricsOut
    prices: list[PricePointOut]
    equity: list[EquityPointOut]


class ErrorResponse(BaseModel):
    detail: str
