"""エントリポイント：FastAPI アプリを作り、組み立て済みのユースケースを渡す。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.application.use_cases.predict_stock import PredictStockUseCase
from app.config import Settings, settings as default_settings
from app.container import build_predict_stock_use_case
from app.presentation.api.errors import register_error_handlers
from app.presentation.api.routes import health, predict


def create_app(
    settings: Settings = default_settings,
    predict_stock_use_case: PredictStockUseCase | None = None,
) -> FastAPI:
    app = FastAPI(title="Stock Predictor API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(predict.router)
    app.state.predict_stock_use_case = (
        predict_stock_use_case or build_predict_stock_use_case(settings)
    )
    return app


app = create_app()
