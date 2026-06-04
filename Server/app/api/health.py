from fastapi import APIRouter

from app.dependencies import SettingsDep
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get("/ready", response_model=ReadinessResponse)
async def ready() -> ReadinessResponse:
    return ReadinessResponse(status="ready", checks={"app": "ok"})

