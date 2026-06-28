from fastapi import APIRouter

from app.api.v1.endpoints import auth, backtesting, health, market_data, predictions, trades

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["backtesting"])
api_router.include_router(trades.router, prefix="/trades", tags=["trades"])
