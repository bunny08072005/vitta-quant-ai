from fastapi import APIRouter

from app.schemas.market_data import MarketDataStatusResponse

router = APIRouter()


@router.get("/status", response_model=MarketDataStatusResponse)
def market_data_status() -> MarketDataStatusResponse:
    return MarketDataStatusResponse(provider=None, ready=False)
