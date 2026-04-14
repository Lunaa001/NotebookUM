# Implementation Plan: API de Procesamiento de Documentos

**Branch**: `001-document-processing-api` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-document-processing-api/spec.md`

## Summary

Construir una API REST con FastAPI para CRUD explícito de `usuarios`, `documentos` y
`resumenes`, más procesamiento asíncrono de PDFs en `/api/v1/documento/upload`:
validar PDF/25MB, extraer texto con Docling, resumir con Nemotron vía OpenAI SDK,
persistir en PostgreSQL, aplicar RFC 9457 y seguridad JWT con control de ownership.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI, OpenAI SDK, Docling, pydantic-settings, python-jose, passlib[bcrypt]  
**Storage**: PostgreSQL (asyncpg)  
**Testing**: pytest, pytest-asyncio, httpx, pytest-cov  
**Target Platform**: Linux server (Granian ASGI)  
**Project Type**: web-service (REST API)  
**Performance Goals**: 100 usuarios concurrentes; procesamiento de PDF de 10 páginas en <2 min  
**Constraints**: `application/pdf` obligatorio, tamaño máximo 25MB, no guardar archivo físico, RFC 9457  
**Scale/Scope**: MVP backend con 3 entidades y CRUD completo + flujo de resumen asíncrono

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| KISS | ✅ PASS | Arquitectura por capas (API, service, repository) |
| DRY | ✅ PASS | Exception handler global y esquemas compartidos |
| YAGNI | ✅ PASS | Alcance limitado a CRUD + procesamiento requerido |
| SOLID | ✅ PASS | Repositorios y servicios por responsabilidad |
| TDD | ✅ PASS | Tests unitarios/integración/contrato antes de implementar |
| SDD | ✅ PASS | Plan deriva de spec actualizado con CRUD explícito |
| 12-Factor Config | ✅ PASS | Variables de entorno con pydantic-settings |
| Backing Services | ✅ PASS | PostgreSQL y proveedor LLM desacoplados por config |

## Project Structure

### Documentation (this feature)

```text
specs/001-document-processing-api/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── main.py
├── config.py
├── api/v1/
│   ├── router.py
│   ├── users.py
│   ├── documents.py
│   ├── summaries.py
│   └── auth.py
├── schemas/
├── models/
├── repositories/
├── services/
├── core/
└── db/

tests/
├── unit/
├── integration/
└── contract/

docs/
├── usuarios.sql
├── documentos.sql
└── resumenes.sql
```

**Structure Decision**: Proyecto único backend, organizado para que 4 integrantes
trabajen en paralelo por verticales (Auth/Users, Upload/Documents, Summaries, Quality).

## Complexity Tracking

| Decisión | Justificación |
|----------|---------------|
| Repository Pattern | Requerido por README y facilita pruebas/mocks |
| BackgroundTasks vs queue externa | MVP simple sin infraestructura adicional |
| asyncpg en vez de ORM completo | Menos complejidad, mejor control SQL para DDL fuente en `/docs` |
