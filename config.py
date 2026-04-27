import os
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=False)
    
    SECRET_KEY: str = Field(default="clave-secreta-por-defecto")
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/notebookum")
    DEBUG: bool = Field(default=True)
    VERSION: str = "1.0.0"
    APP_NAME: str = "NotebookUM"
    ALLOWED_ORIGINS: list = Field(default=["*"])
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)

settings = Settings()