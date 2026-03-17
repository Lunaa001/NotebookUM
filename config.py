from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Información de la aplicación
    APP_NAME: str = "NotebookUM"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"

    # Base de datos (ejemplo si la usas)
    DATABASE_URL: str = "sqlite:///./notebookum.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
