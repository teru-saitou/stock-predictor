"""ネット接続なしで動作確認するための疑似データ。

"DEMO" は疑似の個別銘柄、"DEMO_INDEX" は疑似の市場指数。
DEMO_INDEX は DEMO と同じ日の値動きを一部含むので、両者には相関がある
（市場指数の特徴量を試すため）。DEMO 自体のデータは従来と同じ。
"""
import numpy as np
import pandas as pd

from app.domain.entities import PriceHistory

_NAMES = {"DEMO": "デモ銘柄（疑似データ）", "DEMO_INDEX": "デモ指数（疑似データ）"}


class DemoPriceRepository:
    def __init__(self, days: int = 1500, seed: int = 42):
        self.days = days
        self.seed = seed

    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        n = self.days
        dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)

        # DEMO の値動き（乱数の並びを変えないよう、最初に生成する）
        rng = np.random.default_rng(self.seed)
        rets = rng.normal(0.0003, 0.015, n)

        if ticker.upper() == "DEMO_INDEX":
            rng = np.random.default_rng(self.seed + 1000)
            rets = 0.5 * rets + rng.normal(0.0001, 0.008, n)

        close = 1000 * np.exp(np.cumsum(rets))
        open_ = close * (1 + rng.normal(0, 0.003, n))
        high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.005, n)))
        low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.005, n)))
        volume = rng.integers(1_000_000, 5_000_000, n)
        bars = pd.DataFrame(
            {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )
        return PriceHistory(ticker=ticker.upper(), bars=bars)

    def get_company_name(self, ticker: str) -> str | None:
        return _NAMES.get(ticker.upper(), "デモ（疑似データ）")
