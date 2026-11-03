"""ドメインのエンティティ・値オブジェクト。

方針: pandas は時系列を扱うための「この領域の標準語」として domain での利用を許容する。
scikit-learn / yfinance / FastAPI などのフレームワークは domain に持ち込まない
（import-linter で検査している）。
"""
from dataclasses import dataclass
from datetime import date

import pandas as pd

from .errors import InvalidPriceDataError

OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


@dataclass(frozen=True)
class PriceHistory:
    """ある銘柄の日足の株価履歴（index=日付・昇順、列=OHLCV）。"""

    ticker: str
    bars: pd.DataFrame

    def __post_init__(self) -> None:
        missing = [c for c in OHLCV_COLUMNS if c not in self.bars.columns]
        if missing:
            raise InvalidPriceDataError(f"株価データに列がありません: {missing}")
        if self.bars.empty:
            raise InvalidPriceDataError("株価データが空です")
        if not self.bars.index.is_monotonic_increasing:
            raise InvalidPriceDataError("株価データが日付の昇順になっていません")

    @property
    def open(self) -> pd.Series:
        return self.bars["Open"]

    @property
    def close(self) -> pd.Series:
        return self.bars["Close"]

    @property
    def latest_date(self) -> date:
        return self.bars.index[-1].date()

    @property
    def latest_close(self) -> float:
        return float(self.close.iloc[-1])

    def __len__(self) -> int:
        return len(self.bars)
