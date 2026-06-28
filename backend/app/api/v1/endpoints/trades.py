from fastapi import APIRouter

from app.schemas.trade import TradeHistoryStatusResponse

router = APIRouter()


@router.get("/status", response_model=TradeHistoryStatusResponse)
def trades_status() -> TradeHistoryStatusResponse:
    return TradeHistoryStatusResponse(ready=False, message="Trade history module scaffolded.")
