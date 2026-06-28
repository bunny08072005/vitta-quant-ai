from pydantic import BaseModel


class MarketDataStatusResponse(BaseModel):
    provider: str | None
    ready: bool
