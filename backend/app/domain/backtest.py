"""売買シミュレーション。

日付 t で「上がる」(position=1) と予測したら t の終値で買い、t+1 の終値まで保有する。
ポジションが変わるたびに片道 cost のコストを差し引く。
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


def run_backtest(position: pd.Series, next_ret: pd.Series, cost: float) -> BacktestResult:
    """position: 各日の保有(1)/非保有(0)、next_ret: 各日→翌日のリターン。"""
    trades = position.diff().abs().fillna(position.iloc[0])
    strat_ret = position * next_ret - trades * cost
    return BacktestResult(
        strategy_equity=(1 + strat_ret).cumprod(),
        buy_hold_equity=(1 + next_ret).cumprod(),
        trades=int(trades.sum()),
    )
