"""infrastructure 層（特徴量）のテスト。"""
import pandas as pd

from app.domain.entities import PriceHistory
from app.infrastructure.ml.features import FEATURE_COLS, TechnicalFeatureBuilder
from tests.fakes import demo_history


def test_features_do_not_use_future_data():
    """最終日の価格を変えても、それより前の日の特徴量は変わらない（リークなし）。"""
    history = demo_history()
    base = TechnicalFeatureBuilder().build(history)

    changed_bars = history.bars.copy()
    changed_bars.iloc[-1, changed_bars.columns.get_loc("Close")] *= 2
    after = TechnicalFeatureBuilder().build(PriceHistory(history.ticker, changed_bars))

    pd.testing.assert_frame_equal(base.iloc[:-1], after.iloc[:-1])


def test_feature_columns():
    f = TechnicalFeatureBuilder().build(demo_history())
    assert list(f.columns) == FEATURE_COLS
    assert f.index.equals(demo_history().bars.index)
