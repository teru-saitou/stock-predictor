"""FeatureBuilder の実装。

日付 t の特徴量は「t の終値時点までに分かる情報」だけで作る（未来の情報を使わない）。
rolling / ewm / shift(正の数) は過去方向しか見ないので安全。shift(-1) などは使わないこと。

- TechnicalFeatureBuilder ：基本の11特徴量（価格・出来高のテクニカル指標）
- ExtendedFeatureBuilder  ：基本 + トレンド/過熱感/カレンダー/市場指数との関係
"""
import numpy as np
import pandas as pd

from app.domain.entities import PriceHistory

BASIC_FEATURE_COLS = [
    "ret_1", "ret_5", "ret_10", "ret_20",
    "ma_ratio_5", "ma_ratio_20", "ma_ratio_60",
    "vol_20", "rsi_14", "volume_chg_5", "hl_range",
]
# 互換のための別名
FEATURE_COLS = BASIC_FEATURE_COLS

EXTENDED_EXTRA_COLS = [
    "ret_60",            # 中期のモメンタム
    "macd_hist",         # MACD ヒストグラム（終値で正規化）
    "bb_pctb_20",        # ボリンジャーバンド %B（バンド内の位置）
    "vol_ratio_5_20",    # 直近の値動きの荒さ（短期/中期ボラティリティ比）
    "dist_high_250",     # 1年高値からの距離
    "gap",               # 寄り付きのギャップ（始値 / 前日終値）
    "volume_z_20",       # 出来高の異常度（Zスコア）
    "day_of_week",       # 曜日（0=月曜）
    "month",             # 月
]
BENCHMARK_COLS = [
    "bench_ret_1",       # 市場指数の当日リターン
    "bench_ret_5",       # 市場指数の5日リターン
    "rel_strength_20",   # 指数に対する20日の相対的な強さ
    "corr_60",           # 指数との60日相関
]


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    diff = close.diff()
    up = diff.clip(lower=0).rolling(n).mean()
    down = (-diff.clip(upper=0)).rolling(n).mean()
    rs = up / down.replace(0, 1e-9)
    return 100 - 100 / (1 + rs)


class TechnicalFeatureBuilder:
    uses_benchmark = False

    def build(self, history: PriceHistory, benchmark: PriceHistory | None = None) -> pd.DataFrame:
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
        return f[BASIC_FEATURE_COLS]


class ExtendedFeatureBuilder:
    uses_benchmark = True

    def build(self, history: PriceHistory, benchmark: PriceHistory | None = None) -> pd.DataFrame:
        bars = history.bars
        close, volume = bars["Close"], bars["Volume"]
        daily_ret = close.pct_change()

        f = TechnicalFeatureBuilder().build(history)

        # トレンド・過熱感
        f["ret_60"] = close.pct_change(60)
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        f["macd_hist"] = (macd - macd.ewm(span=9, adjust=False).mean()) / close
        ma20, sd20 = close.rolling(20).mean(), close.rolling(20).std()
        f["bb_pctb_20"] = (close - (ma20 - 2 * sd20)) / (4 * sd20).replace(0, np.nan)
        f["vol_ratio_5_20"] = daily_ret.rolling(5).std() / daily_ret.rolling(20).std().replace(0, np.nan)
        f["dist_high_250"] = close / close.rolling(250, min_periods=60).max() - 1

        # 当日の値動き・出来高
        f["gap"] = bars["Open"] / close.shift(1) - 1
        vol_mean, vol_sd = volume.rolling(20).mean(), volume.rolling(20).std()
        f["volume_z_20"] = (volume - vol_mean) / vol_sd.replace(0, np.nan)

        # カレンダー
        f["day_of_week"] = bars.index.dayofweek
        f["month"] = bars.index.month

        # 市場指数との関係（指数が取れたときだけ）
        if benchmark is not None:
            # 指数側だけ休場の日は直前の値で埋める（過去方向のみなのでリークしない）
            b_close = benchmark.close.reindex(bars.index).ffill()
            b_ret = b_close.pct_change()
            f["bench_ret_1"] = b_ret
            f["bench_ret_5"] = b_close.pct_change(5)
            f["rel_strength_20"] = close.pct_change(20) - b_close.pct_change(20)
            f["corr_60"] = daily_ret.rolling(60).corr(b_ret)

        return f
