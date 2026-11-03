"""売買シミュレーション。

約定のルール: 日付 t の終値までのデータで予測し、「上がる」(position=1) なら
翌営業日 t+1 の始値で買い、t+2 の始値で売る。翌日も「上がる」なら売らずに持ち続ける。
（t の終値を見てから t の終値で買うことはできないため、最短で約定できる t+1 の始値を使う）
ポジションが変わるたびに片道 cost のコストを差し引く。
比較の基準（買い持ち）も同じく、最初の t+1 の始値で買って持ち続けた場合とする。
"""
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    strategy_equity: pd.Series
    buy_hold_equity: pd.Series
    trades: int

    @property
    def strategy_return(self) -> float:
        return float(self.strategy_equity.iloc[-1] - 1)

    @property
    def buy_hold_return(self) -> float:
        return float(self.buy_hold_equity.iloc[-1] - 1)

    @property
    def strategy_max_drawdown(self) -> float:
        return max_drawdown(self.strategy_equity)

    @property
    def buy_hold_max_drawdown(self) -> float:
        return max_drawdown(self.buy_hold_equity)


def max_drawdown(equity: pd.Series) -> float:
    """資産曲線のピークからの最大下落率（負の値）。"""
    return float((equity / equity.cummax() - 1).min())


def holding_return(open_: pd.Series) -> pd.Series:
    """日付 t の値 = t の予測で持つ期間（t+1 の始値 → t+2 の始値）のリターン。最後の2日は NaN。"""
    return open_.shift(-2) / open_.shift(-1) - 1


def settlement_dates(index: pd.DatetimeIndex) -> pd.Series:
    """日付 t の予測による売買の結果が確定する日（t+2 の始値の日）。最後の2日は NaT。"""
    return pd.Series(index, index=index).shift(-2)


def run_backtest(position: pd.Series, hold_ret: pd.Series, cost: float) -> BacktestResult:
    """position: 各日の予測に基づく保有(1)/非保有(0)、hold_ret: holding_return() の値。"""
    trades = position.diff().abs().fillna(position.iloc[0])
    strat_ret = position * hold_ret - trades * cost
    return BacktestResult(
        strategy_equity=(1 + strat_ret).cumprod(),
        buy_hold_equity=(1 + hold_ret).cumprod(),
        trades=int(trades.sum()),
    )
