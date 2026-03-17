from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    """
    Modelo de respuesta para el health check
    """

    status: str
    timestamp: str
    version: str
    app_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-03-17T19:00:00",
                "version": "0.1.0",
                "app_name": "NotebookUM",
            }
        }
