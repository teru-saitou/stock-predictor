"""「何を予測するか」の定義（ビジネスルール）。

予測対象は「翌営業日の終値が当日の終値より上がるか」。
どんな特徴量・モデルを使うかに関係なく、この定義は変わらないので domain に置く。
"""
import pandas as pd


def next_day_return(close: pd.Series) -> pd.Series:
    """日付 t の値 = t の終値 → t+1 の終値のリターン。最終日は NaN。"""
    return close.pct_change().shift(-1)


def up_label(next_ret: pd.Series) -> pd.Series:
    """翌日に上がったら 1、それ以外は 0。"""
    return (next_ret > 0).astype(int)
