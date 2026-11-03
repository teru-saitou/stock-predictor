"""FeatureBuilder の実装：テクニカル指標による特徴量。

日付 t の特徴量は「t の終値時点までに分かる情報」だけで作る（未来の情報を使わない）。
特徴量を増やしたいときはこのファイルを変えるか、別の FeatureBuilder を作って差し替える。
"""
import pandas as pd

from app.domain.entities import PriceHistory

FEATURE_COLS = [
    "ret_1", "ret_5", "ret_10", "ret_20",
    "ma_ratio_5", "ma_ratio_20", "ma_ratio_60",
    "vol_20", "rsi_14", "volume_chg_5", "hl_range",
]


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    diff = close.diff()
    up = diff.clip(lower=0).rolling(n).mean()
    down = (-diff.clip(upper=0)).rolling(n).mean()
    rs = up / down.replace(0, 1e-9)
    return 100 - 100 / (1 + rs)


class TechnicalFeatureBuilder:
    def build(self, history: PriceHistory) -> pd.DataFrame:
        bars = history.bars
        close, volume = bars["Close"], bars["Volume"]
        f = pd.DataFrame(index=bars.index)

        for n in (1, 5, 10, 20):
            f[f"ret_{n}"] = close.pct_change(n)
        for n in (5, 20, 60):
            f[f"ma_ratio_{n}"] = close / close.rolling(n).mean() - 1
        f["vol_20"] = close.pct_change().rolling(20).std()
        f["rsi_14"] = rsi(close)
        f["volume_chg_5"] = volume / volume.rolling(5).mean() - 1
        f["hl_range"] = (bars["High"] - bars["Low"]) / close
        return f[FEATURE_COLS]
