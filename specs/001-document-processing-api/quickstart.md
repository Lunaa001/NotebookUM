# Quickstart: API de Procesamiento de Documentos

## Prerequisitos

- Python 3.11+
- PostgreSQL 15+
- uv (gestor de dependencias)

## Setup

### 1. Clonar e instalar dependencias

```bash
git clone <repo-url>
cd NotebookUM
git checkout 001-document-processing-api

# Instalar dependencias con uv
uv sync
```

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/notebookum

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# OpenAI/Nemotron
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.nemotron.example.com/v1
OPENAI_MODEL=nemotron-3-nano-30b

# App
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Crear base de datos

```bash
# Crear database
createdb notebookum

# Ejecutar DDLs
psql notebookum < docs/usuarios.sql
psql notebookum < docs/documentos.sql
psql notebookum < docs/resumenes.sql
```

### 4. Ejecutar servidor

```bash
# Desarrollo (con reload)
uv run granian --interface asgi --reload app.main:app

# Producción
uv run granian --interface asgi --workers 4 app.main:app
```

El servidor estará disponible en `http://localhost:8000`

## Verificar instalación

```bash
# Health check
curl http://localhost:8000/health

# Documentación OpenAPI
open http://localhost:8000/docs
```

## Flujo de uso básico

### 1. Registrar usuario

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123", "nombre": "Test User"}'
```

### 2. Obtener token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

### 3. Subir documento

```bash
curl -X POST http://localhost:8000/api/v1/documento/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@documento.pdf"
```

Respuesta (202 Accepted):
```json
{
  "id": "uuid-del-documento",
  "estado": "pending",
  "mensaje": "Documento aceptado para procesamiento"
}
```

### 4. Consultar resumen

```bash
curl http://localhost:8000/api/v1/summaries/document/<document_id> \
  -H "Authorization: Bearer <token>"
```

## Ejecutar tests

```bash
# Todos los tests
uv run pytest

# Con coverage
uv run pytest --cov=app --cov-report=html

# Solo unit tests
uv run pytest tests/unit/

# Solo integration tests
uv run pytest tests/integration/
```

## Troubleshooting

### Error: "Database connection failed"
- Verificar que PostgreSQL está corriendo
- Verificar DATABASE_URL en .env

### Error: "Invalid PDF"
- Verificar que el archivo es realmente un PDF
- Verificar que no está protegido con contraseña

### Error: "File too large"
- El límite es 25MB, verificar tamaño del archivo
