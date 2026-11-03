"""テスト用の偽実装。ポートを満たすので、本物の代わりに差し込める。"""
import numpy as np
import pandas as pd

from app.application.errors import DataNotFoundError
from app.domain.entities import PriceHistory
from app.infrastructure.repositories.demo_repository import DemoPriceRepository


def demo_history(days: int = 300, ticker: str = "DEMO") -> PriceHistory:
    return DemoPriceRepository(days=days).get_price_history(ticker, "5y")


class InMemoryPriceRepository:
    """銘柄コードごとに決まった株価を返す。登録のない銘柄は DataNotFoundError。"""

    def __init__(
        self,
        history: PriceHistory,
        name: str | None = "テスト銘柄",
        others: dict[str, PriceHistory] | None = None,
    ):
        self.history = history
        self.name = name
        self.others = {k.upper(): v for k, v in (others or {}).items()}
        self.requested: list[str] = []

    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        self.requested.append(ticker)
        if ticker.upper() in self.others:
            return self.others[ticker.upper()]
        if ticker.startswith("^") or ticker.upper() == "DEMO_INDEX":
            raise DataNotFoundError(f"データが取得できませんでした: {ticker}")
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

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        pass

    def predict_proba_up(self, features: pd.DataFrame) -> np.ndarray:
        return np.full(len(features), self.prob)


class RecordingPredictor(ConstantPredictor):
    """学習に使われたデータの最終日を記録する（未来のデータで学習していないか確認する用）。"""

    log: list[tuple[pd.Timestamp, pd.Timestamp]] = []

    def fit(self, features: pd.DataFrame, labels: pd.Series) -> None:
        self._last_train = features.index[-1]

    def predict_proba_up(self, features: pd.DataFrame) -> np.ndarray:
        RecordingPredictor.log.append((self._last_train, features.index[0]))
        return super().predict_proba_up(features)
