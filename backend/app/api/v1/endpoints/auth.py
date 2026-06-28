from fastapi import APIRouter, status

from app.schemas.auth import AuthStatusResponse

router = APIRouter()


@router.get("/status", response_model=AuthStatusResponse, status_code=status.HTTP_200_OK)
def auth_status() -> AuthStatusResponse:
    return AuthStatusResponse(enabled=False, message="Authentication module scaffolded.")
