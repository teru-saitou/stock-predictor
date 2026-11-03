"""PriceRepository の yfinance（Yahoo Finance の非公式ライブラリ）実装。"""
import pandas as pd

from app.application.errors import DataNotFoundError, DataSourceError
from app.domain.entities import OHLCV_COLUMNS, PriceHistory


class YFinancePriceRepository:
    def get_price_history(self, ticker: str, period: str) -> PriceHistory:
        import yfinance as yf

        try:
            df = yf.download(ticker, period=period, auto_adjust=True, progress=False)
        except Exception as e:  # ネットワークエラーなど
            raise DataSourceError(f"株価データの取得に失敗しました: {e}") from e

        if df is None or df.empty:
            raise DataNotFoundError(f"データが取得できませんでした: {ticker}")
        # yfinance は列が MultiIndex になることがあるので平坦化
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        bars = df[list(OHLCV_COLUMNS)].dropna().sort_index()
        return PriceHistory(ticker=ticker.upper(), bars=bars)

    def get_company_name(self, ticker: str) -> str | None:
        import yfinance as yf

        # 会社名は「あれば嬉しい」情報なので、失敗しても予測自体は止めない
        try:
            info = yf.Ticker(ticker).info or {}
        except Exception:
            return None
        return info.get("longName") or info.get("shortName")
