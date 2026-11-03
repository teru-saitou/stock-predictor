"""application 層のテスト。ポートを偽実装に差し替え、ユースケースの流れだけを検証する。"""
import pandas as pd
import pytest

from app.application.benchmark import benchmark_ticker_for
from app.application.dto import PredictStockInput
from app.application.use_cases.predict_stock import PredictStockConfig, PredictStockUseCase
from app.domain.errors import InsufficientDataError
from app.infrastructure.ml.features import ExtendedFeatureBuilder, TechnicalFeatureBuilder
from tests.fakes import ConstantPredictor, InMemoryPriceRepository, RecordingPredictor, demo_history

BUILDERS = {"basic": TechnicalFeatureBuilder(), "extended": ExtendedFeatureBuilder()}


def _use_case(repo=None, days: int = 400, predictor=lambda: ConstantPredictor(0.7)) -> PredictStockUseCase:
    return PredictStockUseCase(
        repo=repo or InMemoryPriceRepository(demo_history(days)),
        feature_builders=BUILDERS,
        predictor_factory=predictor,
        config=PredictStockConfig(test_ratio=0.3, min_rows=200, retrain_every=20),
    )


def _input(**kw) -> PredictStockInput:
    return PredictStockInput(ticker="demo", **{"feature_set": "basic", "validation": "holdout", **kw})


def test_always_up_model_matches_buy_and_hold():
    out = _use_case().execute(_input(cost=0.0))
    m = out.metrics
    assert out.ticker == "DEMO"
    assert out.next_up_probability == pytest.approx(0.7)
    assert m.trades == 1  # 最初に買って持ち続けるだけ
    assert m.strategy_return == pytest.approx(m.buy_hold_return)


def test_trades_at_next_open_and_buy_and_hold_uses_same_timing():
    """t の予測で t+1 の始値に買う。買い持ちも同じ始値で買い、最後の始値で評価する。"""
    history = demo_history(400)
    out = _use_case(repo=InMemoryPriceRepository(history)).execute(_input(cost=0.0))
    opens = history.open
    first_signal = opens.index.get_loc(pd.Timestamp(out.metrics.test_period[0]))
    bought, sold = opens.iloc[first_signal + 1], opens.iloc[-1]
    assert out.metrics.buy_hold_return == pytest.approx(sold / bought - 1, rel=1e-9)
    # 資産額は結果が確定した日（t+2）の日付で並ぶ
    assert out.equity[0].date == opens.index[first_signal + 2].date()
    assert out.equity[-1].date == opens.index[-1].date()


def test_prices_include_open():
    out = _use_case().execute(_input())
    assert all(p.open > 0 for p in out.prices)


def test_never_up_model_stays_in_cash():
    out = _use_case(predictor=lambda: ConstantPredictor(0.3)).execute(_input(cost=0.001))
    assert out.metrics.trades == 0
    assert out.metrics.strategy_return == pytest.approx(0.0)


def test_insufficient_data_raises():
    with pytest.raises(InsufficientDataError):
        _use_case(days=150).execute(_input())


@pytest.mark.parametrize("validation", ["walk_forward", "holdout"])
def test_never_trains_on_future_data(validation):
    """どの区間でも、学習データの最終日 < 予測する最初の日 になっている。"""
    RecordingPredictor.log = []
    _use_case(predictor=lambda: RecordingPredictor()).execute(_input(validation=validation))
    *folds, _final = RecordingPredictor.log  # 最後は最新日の予測
    assert folds
    for last_train, first_pred in folds:
        assert last_train < first_pred


def test_walk_forward_retrains_periodically():
    out = _use_case().execute(_input(validation="walk_forward"))
    m = out.metrics
    assert m.validation == "walk_forward"
    assert m.retrain_every == 20
    assert m.folds == -(-m.test_days // 20)  # テスト日数 ÷ 20 の切り上げ
    assert len(out.equity) == m.test_days - 1  # 最後の日は売る日の始値がまだ無い


def test_holdout_trains_once():
    m = _use_case().execute(_input(validation="holdout")).metrics
    assert m.folds == 1
    assert m.retrain_every is None


def test_extended_features_use_benchmark_when_available():
    repo = InMemoryPriceRepository(
        demo_history(400), others={"DEMO_INDEX": demo_history(400, "DEMO_INDEX")}
    )
    m = _use_case(repo=repo).execute(_input(feature_set="extended")).metrics
    assert m.benchmark == "DEMO_INDEX"
    assert m.feature_count == 24


def test_extended_features_continue_without_benchmark():
    """市場指数が取れなくても、指数なしの特徴量で予測を続ける。"""
    repo = InMemoryPriceRepository(demo_history(400))  # DEMO_INDEX は未登録 → 取得失敗
    m = _use_case(repo=repo).execute(_input(feature_set="extended")).metrics
    assert m.benchmark is None
    assert m.feature_count == 20


def test_basic_features_do_not_fetch_benchmark():
    repo = InMemoryPriceRepository(demo_history(400))
    _use_case(repo=repo).execute(_input(feature_set="basic"))
    assert repo.requested == ["demo"]


@pytest.mark.parametrize(
    ("ticker", "expected"),
    [("7203.T", "^N225"), ("aapl", "^GSPC"), ("^N225", None), ("DEMO", "DEMO_INDEX"), ("DEMO_INDEX", None)],
)
def test_benchmark_ticker_for(ticker, expected):
    assert benchmark_ticker_for(ticker) == expected
