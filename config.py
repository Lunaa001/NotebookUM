import os
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict, field_validator

class Settings(BaseSettings):
    model_config = ConfigDict(case_sensitive=False, env_file=".env")
    
    SECRET_KEY: str = Field(default="clave-secreta-por-defecto")
    DATABASE_URL: str = Field(default="postgresql+psycopg://notebookum:notebookum123@localhost:5432/notebookum")
    DEBUG: bool = Field(default=True)
    VERSION: str = "1.0.0"
    APP_NAME: str = "NotebookUM"
    ALLOWED_ORIGINS: list = Field(default=["*"])
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)
    OPENAI_API_KEY: str = Field(default="sk-default")
    OPENAI_MODEL: str = Field(default="gpt-4")
    GEMMA4_API_KEY: str = Field(default="sk-default")
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def validate_debug(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


# Testing configuration for backwards compatibility
class TestingConfig:
    """Testing configuration for old Flask-style tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


settings = Settings()
