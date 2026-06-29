from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data_service import MarketDataService

_scheduler: BackgroundScheduler | None = None


def update_all_symbols() -> None:
    db: Session = SessionLocal()
    try:
        repository = MarketDataRepository(db)
        service = MarketDataService(repository)
        for symbol in repository.list_symbols():
            service.update_missing_history(symbol.ticker)
    finally:
        db.close()


def start_market_data_scheduler(interval_minutes: int = 240) -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    _scheduler.add_job(
        update_all_symbols,
        trigger="interval",
        minutes=interval_minutes,
        id="market-data-update",
        replace_existing=True,
        max_instances=1,
    )
    _scheduler.start()
    return _scheduler


def stop_market_data_scheduler() -> None:
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
