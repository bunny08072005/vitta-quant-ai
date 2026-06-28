from pydantic import BaseModel


class TradeHistoryStatusResponse(BaseModel):
    ready: bool
    message: str
