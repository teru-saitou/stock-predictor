"""ネット接続なしで動作確認するための疑似データ。"""
import numpy as np
import pandas as pd

from app.domain.entities import PriceHistory


class DemoPriceRepository:
    def __init__(self, days: int = 1500, seed: int = 42):
        self.days = days
        self.seed = seed

    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        rng = np.random.default_rng(self.seed)
        n = self.days
        dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
        rets = rng.normal(0.0003, 0.015, n)
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
        return "デモ銘柄（疑似データ）"
