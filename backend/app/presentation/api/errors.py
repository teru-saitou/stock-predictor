"""内側の層の例外を HTTP レスポンスに変換する。"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.errors import ApplicationError, DataNotFoundError, DataSourceError
from app.domain.errors import DomainError, InsufficientDataError, InvalidPriceDataError

_STATUS: dict[type[Exception], int] = {
    DataNotFoundError: 404,
    InsufficientDataError: 400,
    DataSourceError: 502,
    InvalidPriceDataError: 502,
}


def register_error_handlers(app: FastAPI) -> None:
    async def handle(_: Request, exc: Exception) -> JSONResponse:
        status = next((s for t, s in _STATUS.items() if isinstance(exc, t)), 500)
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    app.add_exception_handler(DomainError, handle)
    app.add_exception_handler(ApplicationError, handle)
