from fastapi import APIRouter
from app.services.health_service import HealthService
from app.models.health_model import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint para verificar el estado de la API
    """
    service = HealthService()
    return service.get_health_status()
