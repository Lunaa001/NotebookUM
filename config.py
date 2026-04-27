import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    SECRET_KEY: str = Field(default="clave-secreta-por-defecto")
    DATABASE_URL: str = Field(default="sqlite:///app.db")
    DEBUG: bool = Field(default=True)
    VERSION: str = "1.0.0"
    APP_NAME: str = "NotebookUM"
    ALLOWED_ORIGINS: list = Field(default=["*"])
    
    class Config:
        # Usar variables de entorno pero no leer .env file
        # Cambiar a json=[\"*\"] en variables de entorno si es necesario
        case_sensitive = False

settings = Settings()