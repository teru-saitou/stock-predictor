"""テスト用の偽実装。ポートを満たすので、本物の代わりに差し込める。"""
import numpy as np
import pandas as pd

from app.application.errors import DataNotFoundError
from app.domain.entities import PriceHistory
from app.infrastructure.repositories.demo_repository import DemoPriceRepository


def demo_history(days: int = 300) -> PriceHistory:
    return DemoPriceRepository(days=days).get_price_history("DEMO", "5y")


class InMemoryPriceRepository:
    def __init__(self, history: PriceHistory, name: str | None = "テスト銘柄"):
        self.history = history
        self.name = name

    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        return self.history

    def get_company_name(self, ticker: str) -> str | None:
        return self.name


class NotFoundPriceRepository:
    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        raise DataNotFoundError(f"データが取得できませんでした: {ticker}")

    def get_company_name(self, ticker: str) -> str | None:
        return None


class ConstantPredictor:
    """常に同じ確率を返すモデル。学習ライブラリなしでユースケースを検証できる。"""

    def __init__(self, prob: float = 0.7):
        self.prob = prob
        self.fitted_rows = 0

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        self.fitted_rows = len(features)

    def predict_proba_up(self, features: pd.DataFrame) -> np.ndarray:
        return np.full(len(features), self.prob)
