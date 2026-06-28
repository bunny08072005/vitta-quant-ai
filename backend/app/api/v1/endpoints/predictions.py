from fastapi import APIRouter

from app.schemas.prediction import PredictionStatusResponse

router = APIRouter()


@router.get("/status", response_model=PredictionStatusResponse)
def prediction_status() -> PredictionStatusResponse:
    return PredictionStatusResponse(model_loaded=False, message="AI inference module scaffolded.")
