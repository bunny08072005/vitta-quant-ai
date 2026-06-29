from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import market_data
from app.api.v1.router import api_router
from app.core.config import settings
from app.market_data.scheduler import start_market_data_scheduler, stop_market_data_scheduler


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(market_data.router, prefix="/market", tags=["market-data"])

    @app.on_event("startup")
    def start_schedulers() -> None:
        if settings.market_data_scheduler_enabled:
            start_market_data_scheduler(settings.market_data_scheduler_interval_minutes)

    @app.on_event("shutdown")
    def stop_schedulers() -> None:
        stop_market_data_scheduler()

    return app


app = create_app()
