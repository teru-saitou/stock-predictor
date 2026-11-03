"""夜間の一括更新。決めた銘柄の予測・バックテストをまとめて計算し、JSON にして返す。

画面はこの JSON をそのまま読むので、1件ずつの中身は API の PredictResponse と同じ形にする。
"""
from collections.abc import Iterable
from datetime import datetime, timezone

from app.application.dto import PredictStockInput
from app.application.errors import ApplicationError
from app.application.use_cases.predict_stock import PredictStockUseCase
from app.domain.errors import DomainError
from app.presentation.api.schemas import PredictResponse


def read_tickers(lines: Iterable[str]) -> list[str]:
    """1行に1銘柄。空行と「#」から後ろは無視する。"""
    tickers = [line.split("#", 1)[0].strip() for line in lines]
    return [t for t in tickers if t]


def run_nightly(use_case: PredictStockUseCase, tickers: list[str]) -> dict:
    results = []
    for ticker in tickers:
        try:
            output = use_case.execute(PredictStockInput(ticker=ticker))
        except (ApplicationError, DomainError) as e:
            # 1銘柄の失敗で全体を止めない（取得元の一時的な不調はよくある）
            results.append({"ticker": ticker.upper(), "error": str(e)})
            continue
        data = PredictResponse.model_validate(output).model_dump(mode="json")
        results.append({"ticker": data["ticker"], "data": data})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": results,
    }


def succeeded_count(report: dict) -> int:
    return sum(1 for r in report["results"] if "data" in r)
