"""
NotebookUM — Route Registration

DEPRECATED: El monolito ha sido reemplazado por microservicios.
Las funcionalidades ahora viven en:
  - Controller (Go :5000) — API Gateway + Orquestación
  - Extract Service (:8002) — Extracción de texto de PDFs
  - Summary Service (:8003) — Generación de resúmenes con Groq
  - Persistence Service (:8004) — CRUD en PostgreSQL
  - User Service (:8001) — Autenticación y gestión de usuarios

Solo se mantienen las rutas de:
  - health: Health check del monolito
  - main: Landing page y dashboard
"""

from .health_controller import health_router
from .main import main_router


def register_routers(app):
    """Register only essential routers. Microservice routes are DEPRECATED."""
    
    # ── Rutas activas ───────────────────────────────────────────────────
    app.include_router(main_router, tags=["main"])
    app.include_router(health_router, prefix="/api/v1/health", tags=["health"])
    
    # ── DEPRECATED — Ahora viven en microservicios ──────────────────────
    # Los siguientes routers han sido migrados a microservicios:
    #
    # app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
    #   → Migrado a Controller (Go :5000) POST /api/v1/documents/upload
    #
    # app.include_router(summaries_router, prefix="/api/v1/summaries", tags=["summaries"])
    #   → Migrado a Summary Service (:8003) POST /summaries/generate
    #
    # app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
    #   → Migrado a User Service (:8001) /api/v1/auth/* y /api/v1/users/*
    #
    # app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
    #   → ELIMINADO — UM AI Cloud ya no se usa, ahora se usa Groq en Summary Service
    #
    # app.include_router(intelligence_router, prefix="/api/v1", tags=["intelligence"])
    #   → ELIMINADO — UM AI Cloud ya no se usa
    #
    # app.include_router(example_router, prefix="/api/v1/example", tags=["example"])
    #   → ELIMINADO — Era solo un ejemplo
    #
    # app.include_router(test_router, tags=["test"])
    #   → ELIMINADO — Era solo para testing
