from datetime import datetime
from config import settings


class HealthService:
    """
    Servicio para verificar el estado de la aplicación
    """

    def get_health_status(self) -> dict:
        """
        Retorna el estado actual del sistema
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.VERSION,
            "app_name": settings.APP_NAME,
        }
