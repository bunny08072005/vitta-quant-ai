from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.market_data_repository import MarketDataRepository
from app.schemas.market_data import HistoryResponse, LatestPriceResponse, MarketDataStatusResponse, SymbolResponse
from app.services.market_data_service import MarketDataService

router = APIRouter()


def get_market_data_service(db: Session = Depends(get_db)) -> MarketDataService:
    return MarketDataService(MarketDataRepository(db))


@router.get("/status", response_model=MarketDataStatusResponse)
def market_data_status(service: MarketDataService = Depends(get_market_data_service)) -> MarketDataStatusResponse:
    return MarketDataStatusResponse(provider=service.provider.name, ready=service.is_ready())


@router.get("/symbols", response_model=list[SymbolResponse])
def list_symbols(service: MarketDataService = Depends(get_market_data_service)) -> list[SymbolResponse]:
    return list(service.list_symbols())


@router.get("/history/{symbol}", response_model=HistoryResponse)
def get_history(
    symbol: str,
    interval: str = Query(default="1d"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    auto_update: bool = Query(default=True),
    service: MarketDataService = Depends(get_market_data_service),
) -> HistoryResponse:
    prices = service.get_history(
        symbol,
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        auto_update=auto_update,
    )
    return HistoryResponse(
        symbol=symbol.upper(),
        interval=interval,
        start_date=start_date,
        end_date=end_date,
        count=len(prices),
        data=list(prices),
    )


@router.get("/latest/{symbol}", response_model=LatestPriceResponse)
def get_latest(
    symbol: str,
    interval: str = Query(default="1d"),
    auto_update: bool = Query(default=True),
    service: MarketDataService = Depends(get_market_data_service),
):
    latest = service.get_latest(symbol, interval=interval, auto_update=auto_update)
    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No market data found for symbol {symbol}.",
        )
    return latest
