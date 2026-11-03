"""組み立て（Composition Root）。

「どのポートにどの実装を差し込むか」を決めるのはこのファイルだけ。
データ源やモデルを差し替えるときは、ここを変える。
"""
from app.application.ports.price_repository import PriceRepository
from app.application.use_cases.predict_stock import PredictStockConfig, PredictStockUseCase
from app.config import Settings
from app.infrastructure.ml.features import TechnicalFeatureBuilder
from app.infrastructure.ml.sklearn_predictor import SklearnUpDownPredictor
from app.infrastructure.repositories.demo_repository import DemoPriceRepository
from app.infrastructure.repositories.routing_repository import RoutingPriceRepository
from app.infrastructure.repositories.yfinance_repository import YFinancePriceRepository


def build_price_repository() -> PriceRepository:
    return RoutingPriceRepository(
        default=YFinancePriceRepository(),
        demo=DemoPriceRepository(),
    )


def build_predict_stock_use_case(
    settings: Settings, repo: PriceRepository | None = None
) -> PredictStockUseCase:
    return PredictStockUseCase(
        repo=repo or build_price_repository(),
        features=TechnicalFeatureBuilder(),
        predictor_factory=SklearnUpDownPredictor,
        config=PredictStockConfig(
            test_ratio=settings.test_ratio,
            min_rows=settings.min_rows,
            chart_days=settings.chart_days,
        ),
    )
