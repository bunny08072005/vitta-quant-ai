from pydantic import BaseModel


class PredictionStatusResponse(BaseModel):
    model_loaded: bool
    message: str
