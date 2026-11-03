"""domain 層のテスト。フレームワークなしの純粋なロジックだけを検証する。"""
import pandas as pd
import pytest

from app.domain.backtest import holding_return, max_drawdown, run_backtest, settlement_dates
from app.domain.entities import PriceHistory
from app.domain.errors import InvalidPriceDataError
from app.domain.labels import next_day_return, up_label
from app.domain.timeseries import chronological_split_point, holdout_folds, walk_forward_folds


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


def test_walk_forward_folds_cover_test_period_without_gaps():
    folds = walk_forward_folds(100, 0.3, retrain_every=8)
    assert folds[0].test_start == 70
    assert folds[-1].test_end == 100
    assert [f.test_end - f.test_start for f in folds] == [8, 8, 8, 6]
    for prev, cur in zip(folds, folds[1:]):
        assert cur.test_start == prev.test_end  # 隙間も重なりもない
    for f in folds:
        assert f.train_end == f.test_start  # 学習は常に予測区間より前まで


def test_holdout_is_single_fold():
    assert len(holdout_folds(100, 0.3)) == 1
    assert holdout_folds(100, 0.3)[0].test_end == 100


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


def test_holding_return_buys_next_open_and_sells_following_open():
    """t の予測では、t+1 の始値で買って t+2 の始値で売る。"""
    open_ = pd.Series([100.0, 110.0, 121.0, 100.0])
    r = holding_return(open_)
    assert r.iloc[0] == pytest.approx(121 / 110 - 1)
    assert r.iloc[1] == pytest.approx(100 / 121 - 1)
    assert r.iloc[2:].isna().all()  # 売る日の始値がまだ無い


def test_holding_return_does_not_use_same_day_prices():
    """予測した日 t 自体の始値は使わない（t の終値を見てから t の値段では買えない）。"""
    a = holding_return(pd.Series([100.0, 110.0, 121.0]))
    b = holding_return(pd.Series([999.0, 110.0, 121.0]))
    assert a.iloc[0] == b.iloc[0]


def test_settlement_dates_are_two_business_days_later():
    idx = pd.bdate_range("2024-01-01", periods=4)
    s = settlement_dates(idx)
    assert s.iloc[0] == idx[2]
    assert s.iloc[1] == idx[3]
    assert s.iloc[2:].isna().all()


def test_max_drawdown():
    eq = pd.Series([1.0, 1.2, 0.9, 1.3, 1.04])
    assert max_drawdown(eq) == pytest.approx(0.9 / 1.2 - 1)
