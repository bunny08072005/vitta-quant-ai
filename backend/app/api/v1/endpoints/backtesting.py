from fastapi import APIRouter

from app.schemas.backtesting import BacktestStatusResponse

router = APIRouter()


@router.get("/status", response_model=BacktestStatusResponse)
def backtesting_status() -> BacktestStatusResponse:
    return BacktestStatusResponse(ready=False, message="Backtesting engine scaffolded.")
