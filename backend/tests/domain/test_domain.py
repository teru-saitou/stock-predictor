"""domain 層のテスト。フレームワークなしの純粋なロジックだけを検証する。"""
import pandas as pd
import pytest

from app.domain.backtest import max_drawdown, run_backtest
from app.domain.entities import PriceHistory
from app.domain.errors import InvalidPriceDataError
from app.domain.labels import next_day_return, up_label
from app.domain.timeseries import chronological_split_point


def _bars(closes, dates=None):
    idx = dates if dates is not None else pd.bdate_range("2024-01-01", periods=len(closes))
    return pd.DataFrame(
        {"Open": closes, "High": closes, "Low": closes, "Close": closes, "Volume": [1] * len(closes)},
        index=idx,
    )


def test_price_history_rejects_missing_columns():
    with pytest.raises(InvalidPriceDataError):
        PriceHistory("X", _bars([1.0, 2.0]).drop(columns=["Volume"]))


def test_price_history_rejects_unsorted_dates():
    idx = pd.to_datetime(["2024-01-02", "2024-01-01"])
    with pytest.raises(InvalidPriceDataError):
        PriceHistory("X", _bars([1.0, 2.0], idx))


def test_labels_are_next_day_direction():
    close = pd.Series([100.0, 101.0, 100.0, 100.0])
    r = next_day_return(close)
    assert r.iloc[0] == pytest.approx(0.01)
    assert pd.isna(r.iloc[-1])  # 最終日の答えはまだ無い
    assert up_label(r).tolist() == [1, 0, 0, 0]


def test_chronological_split_point():
    assert chronological_split_point(100, 0.3) == 70
    with pytest.raises(ValueError):
        chronological_split_point(100, 1.0)


def test_backtest_always_hold_equals_buy_and_hold_without_cost():
    idx = pd.bdate_range("2024-01-01", periods=5)
    ret = pd.Series([0.01, -0.02, 0.03, 0.0, 0.01], index=idx)
    bt = run_backtest(pd.Series(1, index=idx), ret, cost=0.0)
    pd.testing.assert_series_equal(bt.strategy_equity, bt.buy_hold_equity, check_names=False)
    assert bt.trades == 1


def test_backtest_charges_cost_on_each_trade():
    idx = pd.bdate_range("2024-01-01", periods=4)
    ret = pd.Series([0.0, 0.0, 0.0, 0.0], index=idx)
    bt = run_backtest(pd.Series([1, 0, 1, 0], index=idx), ret, cost=0.01)
    assert bt.trades == 4
    assert bt.strategy_return == pytest.approx(0.99**4 - 1)


def test_max_drawdown():
    eq = pd.Series([1.0, 1.2, 0.9, 1.3, 1.04])
    assert max_drawdown(eq) == pytest.approx(0.9 / 1.2 - 1)
