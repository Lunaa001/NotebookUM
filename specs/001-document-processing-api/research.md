# Research: API de Procesamiento de Documentos

**Feature**: 001-document-processing-api  
**Date**: 2026-04-06

## Technology Decisions

### 1. Extracción de Texto PDF

**Decision**: Docling  
**Rationale**: Especificado en README del proyecto. Librería especializada para
extracción de texto de PDFs con soporte para estructuras complejas.  
**Alternatives Considered**:
- PyMuPDF: Más bajo nivel, requiere más código custom
- pdfplumber: Bueno para tablas pero menos robusto para texto general

### 2. Generación de Resúmenes

**Decision**: OpenAI SDK con modelo Nemotron-3 nano 30B  
**Rationale**: Especificado en spec. OpenAI SDK proporciona interfaz estándar
compatible con endpoints OpenAI-like.  
**Configuration**:
```python
# Via pydantic-settings
OPENAI_API_KEY=xxx
OPENAI_BASE_URL=https://api.nemotron.example.com/v1
OPENAI_MODEL=nemotron-3-nano-30b
```

### 3. Driver PostgreSQL

**Decision**: asyncpg (async) con connection pooling  
**Rationale**: FastAPI es async-first; asyncpg es el driver async más performante
para PostgreSQL. Sin ORM para mantener simplicidad (KISS).  
**Alternatives Considered**:
- psycopg2: Sync, bloquearía event loop
- SQLAlchemy async: Añade complejidad innecesaria para 3 tablas simples

### 4. Autenticación

**Decision**: python-jose para JWT, passlib[bcrypt] para hashing  
**Rationale**: Estándar de industria para FastAPI. JWT stateless cumple
12-Factor (processes stateless).  
**Token Structure**:
```json
{
  "sub": "user_id",
  "exp": "timestamp",
  "iat": "timestamp"
}
```

### 5. Servidor ASGI

**Decision**: Granian  
**Rationale**: Especificado por usuario. Server HTTP/2 async escrito en Rust,
excelente performance para APIs async.  
**Command**: `granian --interface asgi app.main:app`

### 6. Procesamiento Asíncrono

**Decision**: FastAPI BackgroundTasks  
**Rationale**: Para MVP, BackgroundTasks es suficiente. Evita complejidad de
Celery/Redis mientras el volumen sea manejable.  
**Flow**:
1. Request recibido → validación → respuesta 202 Accepted
2. BackgroundTask: Docling extract → Nemotron summarize → DB save
3. Usuario consulta estado vía GET /summaries/document/{id}

### 7. Manejo de Errores

**Decision**: RFC 9457 Problem Details  
**Rationale**: Requerido por spec. Formato estándar machine-readable.  
**Implementation**:
```python
class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str
```

### 8. Estados de Documento

**Decision**: Enum con 4 estados: `pending`, `processing`, `completed`, `failed`  
**Rationale**: Cubre flujo completo de procesamiento async:
- `pending`: Subido, esperando procesamiento
- `processing`: BackgroundTask en ejecución
- `completed`: Resumen generado exitosamente
- `failed`: Error durante procesamiento

## Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "granian>=1.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "openai>=1.0.0",
    "docling>=0.1.0",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "httpx>=0.27.0",
    "pytest-cov>=4.0.0",
]
```

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| ¿Cómo manejar PDFs protegidos? | Docling lanza excepción → catch → estado failed |
| ¿Retry automático? | No en MVP. Estado failed, retry manual |
| ¿Límite de texto por documento? | Sin límite, Nemotron maneja contexto largo |
