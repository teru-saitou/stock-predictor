"""株価データ取得のポート（抽象）。

内側（application）がこのインターフェースを所有し、外側（infrastructure）が実装する。
これにより依存の向きが「infrastructure → application」になる（依存性逆転）。
"""
from typing import Protocol

from app.domain.entities import PriceHistory


class PriceRepository(Protocol):
    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        """日足の株価履歴を返す。

        見つからなければ DataNotFoundError、通信失敗なら DataSourceError を投げる。
        """
        ...

    def get_company_name(self, ticker: str) -> str | None:
        """会社名（指数なら指数名）を返す。取得できなければ None。"""
        ...
