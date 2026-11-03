"""予測 API。リクエストを入力 DTO に変換してユースケースを呼び、結果をレスポンス型に変換するだけ。"""
from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.application.dto import (
    DEFAULT_COST, DEFAULT_FEATURE_SET, DEFAULT_PERIOD, DEFAULT_VALIDATION, PredictStockInput,
)
from app.application.use_cases.predict_stock import PredictStockUseCase
from app.presentation.api.dependencies import get_predict_stock_use_case
from app.presentation.api.schemas import ErrorResponse, PredictResponse

router = APIRouter(prefix="/api", tags=["predict"])


@router.get(
    "/predict",
    response_model=PredictResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def predict(
    ticker: str = Query(..., min_length=1, description="例: 7203.T, AAPL, DEMO"),
    period: str = Query(DEFAULT_PERIOD, pattern="^(1y|2y|5y|10y|max)$"),
    cost: float = Query(DEFAULT_COST, ge=0, le=0.05, description="片道の取引コスト（0.001=0.1%）"),
    feature_set: Literal["basic", "extended"] = Query(
        DEFAULT_FEATURE_SET, description="basic=基本11特徴量 / extended=拡張（市場指数・カレンダー等を追加）"
    ),
    validation: Literal["walk_forward", "holdout"] = Query(
        DEFAULT_VALIDATION, description="walk_forward=定期的に再学習 / holdout=1回だけ学習"
    ),
    use_case: PredictStockUseCase = Depends(get_predict_stock_use_case),
):
    output = use_case.execute(
        PredictStockInput(
            ticker=ticker, period=period, cost=cost, feature_set=feature_set, validation=validation
        )
    )
    return PredictResponse.model_validate(output)
