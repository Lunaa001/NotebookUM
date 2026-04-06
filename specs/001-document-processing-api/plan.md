# Implementation Plan: API de Procesamiento de Documentos

**Branch**: `001-document-processing-api` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-document-processing-api/spec.md`

## Summary

Sistema de procesamiento de documentos PDF que permite a usuarios registrados subir
archivos, extraer texto mediante Docling, generar resúmenes con Nemotron-3 vía OpenAI API,
y almacenar resultados en PostgreSQL. Procesamiento asíncrono con BackgroundTasks,
autenticación JWT, y errores estructurados RFC 9457.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, OpenAI SDK, Docling, pydantic-settings, python-jose (JWT)  
**Storage**: PostgreSQL (asyncpg driver)  
**Testing**: pytest, pytest-asyncio, httpx (TestClient)  
**Target Platform**: Linux server (Granian ASGI server)  
**Project Type**: web-service (REST API)  
**Performance Goals**: 100 usuarios concurrentes, <2min procesamiento por documento 10 páginas  
**Constraints**: Archivos ≤25MB, no almacenar PDFs en servidor, RFC 9457 errores  
**Scale/Scope**: MVP con 3 entidades (usuarios, documentos, resumenes)  
**Dependency Manager**: uv (pyproject.toml)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| I. KISS | ✅ PASS | Arquitectura simple: 3 capas (API, Service, Repository) |
| II. DRY | ✅ PASS | Global Exception Handler, Repository pattern centralizado |
| III. YAGNI | ✅ PASS | Solo funcionalidad especificada, sin features especulativos |
| IV. SOLID | ✅ PASS | Repository abstrae DB, Services separados por dominio |
| V. TDD | ✅ PASS | pytest con mocks para Docling/Nemotron |
| VI. SDD | ✅ PASS | spec.md completo antes de implementación |
| VII. Codebase | ✅ PASS | Un repositorio Git |
| VIII. Dependencias | ✅ PASS | uv + pyproject.toml |
| IX. Config | ✅ PASS | pydantic-settings + .env |
| X. Backing Services | ✅ PASS | PostgreSQL configurable via DATABASE_URL |
| XI. Build/Release/Run | ✅ PASS | uv build, Granian run |
| XII. Processes | ✅ PASS | Stateless, estado en PostgreSQL |

## Project Structure

### Documentation (this feature)

```text
specs/001-document-processing-api/
├── plan.md              # This file
├── research.md          # Phase 0: Technology decisions
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Developer setup guide
├── contracts/           # Phase 1: API contracts (OpenAPI)
│   └── openapi.yaml
└── tasks.md             # Phase 2: Implementation tasks (/speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── main.py                    # FastAPI app factory
├── config.py                  # pydantic-settings
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py          # Main router /api/v1/
│   │   ├── users.py           # POST/GET /users
│   │   ├── documents.py       # POST /documento/upload
│   │   └── summaries.py       # GET /summaries/document/{id}
│   └── deps.py                # Dependency injection
├── models/
│   ├── __init__.py
│   ├── usuario.py
│   ├── documento.py
│   └── resumen.py
├── repositories/
│   ├── __init__.py
│   ├── base.py                # Abstract repository
│   ├── usuario_repository.py
│   ├── documento_repository.py
│   └── resumen_repository.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py        # JWT handling
│   ├── document_service.py    # Upload + async processing
│   ├── extraction_service.py  # Docling wrapper
│   └── summary_service.py     # OpenAI/Nemotron wrapper
├── schemas/
│   ├── __init__.py
│   ├── usuario.py             # Pydantic request/response
│   ├── documento.py
│   ├── resumen.py
│   └── error.py               # RFC 9457 Problem Details
├── core/
│   ├── __init__.py
│   ├── exceptions.py          # Custom exceptions
│   ├── error_handlers.py      # Global exception handler
│   └── security.py            # JWT utilities
└── db/
    ├── __init__.py
    ├── connection.py          # asyncpg pool
    └── migrations/            # SQL scripts

tests/
├── conftest.py                # Fixtures, mocks
├── unit/
│   ├── test_services/
│   └── test_repositories/
├── integration/
│   └── test_api/
└── contract/
    └── test_openapi.py

docs/
├── usuarios.sql               # DDL for usuarios table
├── documentos.sql             # DDL for documentos table
└── resumenes.sql              # DDL for resumenes table
```

**Structure Decision**: Clean Architecture con separación clara entre API layer (routers),
business logic (services), y data access (repositories). Los DDL en `/docs` como fuente
de verdad según constitución.

## Complexity Tracking

> No hay violaciones a la constitución. Todas las decisiones siguen los principios establecidos.

| Decisión | Justificación |
|----------|---------------|
| Repository Pattern | Requerido por constitución (SOLID - Dependency Inversion) |
| Global Exception Handler | Requerido por constitución (DRY) |
| BackgroundTasks | Necesario para procesamiento async sin complejidad de queue |
