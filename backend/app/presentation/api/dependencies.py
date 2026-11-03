"""ルーターがユースケースを受け取るための依存関数。

presentation は「どの実装で組み立てられたか」を知らない。
組み立て済みのユースケースは main.py が app.state に置く。
"""
from fastapi import Request

from app.application.use_cases.predict_stock import PredictStockUseCase


def get_predict_stock_use_case(request: Request) -> PredictStockUseCase:
    return request.app.state.predict_stock_use_case
