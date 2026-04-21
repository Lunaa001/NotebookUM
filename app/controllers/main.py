import os
from urllib.parse import urlparse

import psycopg
from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return jsonify({"message": "NotebookUm API is running 🚀"})


@main_bp.get("/health")
def health():
    """Health check endpoint for process and backing services."""
    status = {"status": "ok", "services": {}}

    database_url = os.getenv("DATABASE_URL", "")

    # Check PostgreSQL connectivity when DATABASE_URL is configured.
    try:
        dsn = _as_psycopg_dsn(database_url)
        if not dsn:
            status["services"]["database"] = "not-configured"
        else:
            with psycopg.connect(dsn, connect_timeout=3) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
            status["services"]["database"] = "ok"
    except Exception as exc:  # pragma: no cover - defensive health endpoint
        status["services"]["database"] = f"error: {exc}"
        status["status"] = "degraded"

    return jsonify(status), 200


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
