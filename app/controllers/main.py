import os
from urllib.parse import urlparse

import psycopg
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Optional

main_router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]


@main_router.get("/")
async def index():
    return {"message": "NotebookUm API is running 🚀"}


@main_router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for process and backing services."""
    status_info = {"status": "ok", "services": {}}

    database_url = os.getenv("DATABASE_URL", "")

    # Check PostgreSQL connectivity when DATABASE_URL is configured.
    try:
        dsn = _as_psycopg_dsn(database_url)
        if not dsn:
            status_info["services"]["database"] = "not-configured"
        else:
            with psycopg.connect(dsn, connect_timeout=3) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            status_info["services"]["database"] = "ok"
    except Exception as exc:  # pragma: no cover - defensive health endpoint
        status_info["services"]["database"] = f"error: {exc}"
        status_info["status"] = "degraded"

    return status_info


def _as_psycopg_dsn(database_url: str) -> str | None:
    if not database_url:
        return None

    if database_url.startswith("postgresql+psycopg://"):
        return "postgresql://" + database_url.split("://", 1)[1]

    if database_url.startswith("postgres://"):
        return "postgresql://" + database_url.split("://", 1)[1]

    parsed = urlparse(database_url)
    if parsed.scheme == "postgresql":
        return database_url

    return None
