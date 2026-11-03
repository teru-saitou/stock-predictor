"""application 層のテスト。ポートを偽実装に差し替え、ユースケースの流れだけを検証する。"""
import pytest

from app.application.dto import PredictStockInput
from app.application.use_cases.predict_stock import PredictStockConfig, PredictStockUseCase
from app.domain.errors import InsufficientDataError
from app.infrastructure.ml.features import TechnicalFeatureBuilder
from tests.fakes import ConstantPredictor, InMemoryPriceRepository, demo_history


def _use_case(days: int = 400, prob: float = 0.7) -> PredictStockUseCase:
    return PredictStockUseCase(
        repo=InMemoryPriceRepository(demo_history(days)),
        features=TechnicalFeatureBuilder(),
        predictor_factory=lambda: ConstantPredictor(prob),
        config=PredictStockConfig(test_ratio=0.3, min_rows=200),
    )


def test_always_up_model_matches_buy_and_hold_minus_one_trade():
    out = _use_case(prob=0.7).execute(PredictStockInput("demo", cost=0.0))
    m = out.metrics
    assert out.ticker == "DEMO"
    assert out.name == "テスト銘柄"
    assert out.next_up_probability == pytest.approx(0.7)
    assert m.trades == 1  # 最初に買って持ち続けるだけ
    assert m.strategy_return == pytest.approx(m.buy_hold_return)


def test_never_up_model_stays_in_cash():
    out = _use_case(prob=0.3).execute(PredictStockInput("demo", cost=0.001))
    assert out.metrics.trades == 0
    assert out.metrics.strategy_return == pytest.approx(0.0)


def test_train_period_is_before_test_period():
    m = _use_case().execute(PredictStockInput("demo")).metrics
    assert m.train_period[1] < m.test_period[0]
    assert m.test_days == len(_use_case().execute(PredictStockInput("demo")).equity)


def test_insufficient_data_raises():
    with pytest.raises(InsufficientDataError):
        _use_case(days=150).execute(PredictStockInput("demo"))
