from pydantic import BaseModel


class BacktestStatusResponse(BaseModel):
    ready: bool
    message: str
