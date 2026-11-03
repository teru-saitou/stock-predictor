"""銘柄コードによって使うリポジトリを切り替える。

"DEMO" は疑似データ、それ以外は本番用のリポジトリへ回す。
"""
from app.application.ports.price_repository import PriceRepository
from app.domain.entities import PriceHistory


class RoutingPriceRepository:
    def __init__(self, default: PriceRepository, demo: PriceRepository):
        self.default = default
        self.demo = demo

    def _pick(self, ticker: str) -> PriceRepository:
        return self.demo if ticker.upper() == "DEMO" else self.default

    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        return self._pick(ticker).get_price_history(ticker, period)

    def get_company_name(self, ticker: str) -> str | None:
        return self._pick(ticker).get_company_name(ticker)
