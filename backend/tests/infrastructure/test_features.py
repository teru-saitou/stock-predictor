"""infrastructure 層（特徴量）のテスト。"""
import pandas as pd
import pytest

from app.domain.entities import PriceHistory
from app.infrastructure.ml.features import (
    BASIC_FEATURE_COLS, BENCHMARK_COLS, EXTENDED_EXTRA_COLS,
    ExtendedFeatureBuilder, TechnicalFeatureBuilder,
)
from tests.fakes import demo_history


def _double_last_day(history: PriceHistory) -> PriceHistory:
    bars = history.bars.copy()
    for col in ("Open", "High", "Low", "Close"):
        bars.iloc[-1, bars.columns.get_loc(col)] *= 2
    bars.iloc[-1, bars.columns.get_loc("Volume")] *= 3
    return PriceHistory(history.ticker, bars)


@pytest.mark.parametrize("builder", [TechnicalFeatureBuilder(), ExtendedFeatureBuilder()])
def test_features_do_not_use_future_data(builder):
    """最終日の値（株価・指数とも）を変えても、それより前の日の特徴量は変わらない（リークなし）。"""
    stock, index = demo_history(400), demo_history(400, "DEMO_INDEX")
    base = builder.build(stock, index)
    after = builder.build(_double_last_day(stock), _double_last_day(index))
    pd.testing.assert_frame_equal(base.iloc[:-1], after.iloc[:-1])


def test_basic_feature_columns():
    f = TechnicalFeatureBuilder().build(demo_history())
    assert list(f.columns) == BASIC_FEATURE_COLS
    assert f.index.equals(demo_history().bars.index)


def test_extended_feature_columns_with_and_without_benchmark():
    stock = demo_history(400)
    with_bench = ExtendedFeatureBuilder().build(stock, demo_history(400, "DEMO_INDEX"))
    without = ExtendedFeatureBuilder().build(stock, None)
    assert list(with_bench.columns) == BASIC_FEATURE_COLS + EXTENDED_EXTRA_COLS + BENCHMARK_COLS
    assert list(without.columns) == BASIC_FEATURE_COLS + EXTENDED_EXTRA_COLS


def test_benchmark_with_missing_days_is_forward_filled():
    """指数側だけ休場の日があっても、前日の値で埋めて特徴量が欠けない。"""
    stock = demo_history(400)
    index = demo_history(400, "DEMO_INDEX")
    holed = PriceHistory(index.ticker, index.bars.drop(index.bars.index[200]))
    f = ExtendedFeatureBuilder().build(stock, holed)
    assert f.iloc[200][BENCHMARK_COLS].notna().all()


def test_demo_index_is_correlated_with_demo():
    stock, index = demo_history(400), demo_history(400, "DEMO_INDEX")
    corr = stock.close.pct_change().corr(index.close.pct_change())
    assert corr > 0.4
