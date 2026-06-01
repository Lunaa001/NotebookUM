# 📚 NotebookUM - Document Processing & AI Summarization API

**Status:** ✅ **FASE 1-5 COMPLETAS** | Production Ready

NotebookUM es una API FastAPI para procesar documentos PDF, extraer texto y generar resúmenes automáticos usando IA (OpenAI-compatible API de UM).

---

## 🎯 Características

| FASE | Componente | Estado |
|------|-----------|--------|
| **1** | FastAPI + Router Registration | ✅ |
| **2** | PostgreSQL + SQLAlchemy + Alembic | ✅ |
| **3** | Repository Pattern + CRUD | ✅ |
| **4** | PDF Extraction (Docling) + Storage Service | ✅ |
| **5** | AI Summarization (OpenAI-compatible) + Summary Endpoint | ✅ |

### Flujo Completo:
```
PDF Upload → Docling Extract (OCR, Tables, Layout)
    ↓
Texto Extraído → Almacenado en BD
    ↓
Solicitar Resumen → OpenAI-compatible API (UM AI Cloud)
    ↓
Resumen Generado → Almacenado en BD
```

---

## 🛠️ Tech Stack

- **Backend:** FastAPI 0.135.3
- **Database:** PostgreSQL 15 + SQLAlchemy 2.0 + Alembic
- **PDF Processing:** Docling 2.91.0 (OCR, Tables, Layouts)
- **AI/Summarization:** OpenAI-compatible API (UM AI Cloud)
- **Package Manager:** uv
- **Testing:** pytest 9.0.3
- **Containerization:** Docker + Docker Compose
- **Server:** Granian (async ASGI)

---

## 📦 Instalación Local

### Requisitos
- Python 3.14+
- PostgreSQL 15+
- `uv` package manager
- API Key de OpenAI-compatible (UM AI Cloud)

### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/NotebookUM.git
cd NotebookUM
```

### 2. Instalar dependencias
```bash
uv sync
```

### 3. Configurar variables de environment
```bash
cp .env.example .env
# Editar .env con:
# - DATABASE_URL=postgresql+psycopg://notebookum:notebookum123@localhost:5432/notebookum
# - OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 4. Iniciar PostgreSQL (Docker)
```bash
cd dockers/PostgreSQL
docker-compose up -d
# Esperar ~10s para que inicie
```

### 5. Aplicar migraciones
```bash
cd /path/to/NotebookUM
uv run alembic upgrade head
# Output: "Done" significa migraciones aplicadas
```

### 6. Ejecutar tests
```bash
uv run pytest tests/ -v
# Esperado: 78 passed, 7 skipped
```

### 7. Iniciar servidor
```bash
uv run granian --interface asgi --host 0.0.0.0 --port 8000 main:app
# Server corriendo en http://localhost:8000
```

### 8. Acceder a documentación
- **OpenAPI (Swagger):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🚀 Ejemplos de Uso

### A) Subir Documento PDF

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@documento.pdf" \
  -H "X-User-ID: 1"
```

**Respuesta:**
```json
{
  "document_id": 1,
  "nombre_archivo": "documento.pdf",
  "status": "almacenado",
  "mensaje": "Documento almacenado y procesado exitosamente"
}
```

### B) Generar Resumen Automático

```bash
curl -X POST http://localhost:8000/api/v1/documents/1/summary \
  -H "Content-Type: application/json" \
  -d '{"max_tokens": 300}'
```

**Respuesta:**
```json
{
  "document_id": 1,
  "status": "generado",
  "resumen": "La inteligencia artificial es una rama de la informática...",
  "resumen_longitud": 287,
  "mensaje": "Resumen generado exitosamente"
}
```

### C) Recuperar Documento con Resumen

```bash
curl -X GET http://localhost:8000/api/v1/documents/1
```

**Respuesta:**
```json
{
  "id": 1,
  "usuario_id": 1,
  "nombre_archivo": "documento.pdf",
  "texto_extraido": "...",
  "fecha_creacion": "2026-04-27T10:00:00"
}
```

### D) Eliminar Documento

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/1
```

---

## 🐳 Deploy con Docker

### Opción 1: Docker Individual

```bash
# Construir imagen
docker build -t notebookum:1.2.0 .

# Ejecutar
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg://user:pass@db:5432/notebookum" \
  -e OPENAI_API_KEY="sk-..." \
  notebookum:1.2.0
```

### Opción 2: Docker Compose (Recomendado)

Crear `docker-compose.yml` en raíz:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15.4-bullseye
    environment:
      POSTGRES_USER: notebookum
      POSTGRES_PASSWORD: notebookum123
      POSTGRES_DB: notebookum
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U notebookum"]
      interval: 10s
      timeout: 5s
      retries: 5

  notebookum:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+psycopg://notebookum:notebookum123@postgres:5432/notebookum
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DEBUG: "false"
    depends_on:
      postgres:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head &&
             granian --interface asgi --host 0.0.0.0 --port 8000 main:app"

volumes:
  postgres_data:
```

**Ejecutar:**
```bash
OPENAI_API_KEY="sk-..." docker-compose up -d
```

**Logs:**
```bash
docker-compose logs -f notebookum
```

---

## 📊 Estructura del Proyecto

```
NotebookUM/
├── app/
│   ├── controllers/          # Routers FastAPI
│   │   ├── documents.py      # POST /upload, /summary, GET, DELETE
│   │   ├── ai_controller.py  # AI endpoints
│   │   └── ...
│   ├── services/             # Business logic
│   │   ├── ai_service.py          # OpenAI-compatible API integration
│   │   ├── summary_service.py     # FASE 5: Summarization
│   │   ├── pdf_extraction_service.py # Docling integration
│   │   ├── document_service.py
│   │   ├── storage_service.py     # File persistence
│   │   └── ...
│   ├── models/               # ORM + Pydantic
│   │   ├── document.py       # Documento + resumen field
│   │   ├── usuario.py
│   │   └── base.py
│   └── database.py           # SQLAlchemy setup
├── tests/                    # Unit + integration tests
│   ├── test_summary_service_fase5.py  # FASE 5 tests (8 passed)
│   └── ...
├── alembic/
│   ├── versions/
│   │   ├── 001_initial.py               # Create usuarios, documentos
│   │   └── 002_add_resumen_to_documento.py  # Add resumen field (FASE 5)
│   └── env.py
├── config.py                 # Pydantic Settings
├── main.py                   # FastAPI app entry point
├── pyproject.toml            # Dependencies
└── Dockerfile                # Container image

Storage:
/tmp/notebookum_uploads/     # Uploaded PDF files
```

---

## 🧪 Testing

### Ejecutar todos los tests
```bash
uv run pytest tests/ -v
# Expected: 78 passed, 7 skipped
```

### Tests específicos por FASE

```bash
# FASE 4: PDF Extraction
uv run pytest tests/test_pdf_extraction_service.py -v

# FASE 5: AI Summarization
uv run pytest tests/test_summary_service_fase5.py -v
uv run pytest tests/test_summary.py -v

# AI Service (OpenAI-compatible API)

```

### Coverage
```bash
uv run pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🔑 Configuración de Environment

### `.env` requerido:

```env
# Database
DATABASE_URL=postgresql+psycopg://notebookum:notebookum123@localhost:5432/notebookum

# AI API (OpenAI)
OPENAI_API_KEY=sk-your-openai-api-key-here

# App Config
DEBUG=true
VERSION=1.2.0
APP_NAME=NotebookUM
MAX_UPLOAD_SIZE=10485760  # 10MB en bytes
```

### Variables disponibles en `config.py`:
- `SECRET_KEY` - Para JWT (futuro)
- `DATABASE_URL` - PostgreSQL connection
- `OPENAI_API_KEY` - OpenAI API key
- `DEBUG` - Debug mode
- `MAX_UPLOAD_SIZE` - Max file upload size
- `ALLOWED_ORIGINS` - CORS origins

---

## 🐛 Troubleshooting

### Error: "Connection refused" en Alembic

**Causa:** PostgreSQL no está corriendo

**Solución:**
```bash
# Iniciar PostgreSQL
docker-compose -f dockers/PostgreSQL/docker-compose.yml up -d
sleep 10
uv run alembic upgrade head
```

### Error: "OPENAI_API_KEY extra inputs not permitted"

**Causa:** `config.py` sin field `OPENAI_API_KEY`

**Solución:** Ya está incluido en la actualización. Reiniciar servidor:
```bash
pkill -f granian
uv run granian --interface asgi --host 0.0.0.0 --port 8000 main:app
```

### PDF no se extrae correctamente

**Causa:** PDF con imágenes/tablas complejas

**Solución:** Docling maneja OCR automáticamente. Verificar:
```bash
# Test extraction
uv run python -c "
from app.services.pdf_extraction_service import PDFExtractionService
text = PDFExtractionService.extract_text('path/to/file.pdf')
print(f'Extracted: {len(text)} chars')
"
```

### Resumen vacío en respuesta

**Causa:** OpenAI-compatible API respondiendo con `content: ""` y `reasoning: ""`

**Status:** ✅ Ya manejado en `AIService.generate_summary()` - usa `reasoning` como fallback

---

## 📚 API Reference

### Endpoints

| Método | Ruta | Descripción | Status |
|--------|------|-------------|--------|
| **POST** | `/api/v1/documents/upload` | Subir PDF | ✅ |
| **GET** | `/api/v1/documents/{id}` | Obtener documento | ✅ |
| **DELETE** | `/api/v1/documents/{id}` | Eliminar documento | ✅ |
| **POST** | `/api/v1/documents/{id}/summary` | Generar resumen (FASE 5) | ✅ |
| **GET** | `/api/v1/health` | Health check | ✅ |

---

## 🤝 Contribuciones

1. Las FASE 1-5 están completas
2. Para nuevas funcionalidades, crear branch: `feature/nueva-funcionalidad`
3. Mantener cobertura de tests >80%
4. Seguir PEP 8 + SOLID principles

---

## 📄 Licencia

MIT License - 2026

---

**Última actualización:** 27 de abril de 2026 | **Versión:** 1.2.0

- **Método y Ejecución:** POST, con procesamiento asincrónico vía `BackgroundTasks` de FastAPI.
- **Respuesta Inmediata:** Retornar **Status 202 Accepted** con el ID del documento tras validar el archivo.
- **El flujo interno debe:** Extraer texto (Docling) -> Generar resumen (OpenAI-compatible API) -> Guardar DB.
- **Restricción:** Prohibido guardar el archivo físico en el servidor (procesar en memoria/stream).
- **Validaciones:**
    - `contentType: application/pdf` (Error 400 si falla).
    - Tamaño máximo: **25MB** (Error 400 siguiendo **RFC 9457**).

## 3. Rutas Principales de API
- `POST /api/v1/users`: Registro de usuario (Hashear contraseñas obligatoriamente).
- `GET /api/v1/users/{id}`: Consulta de perfil.
- `POST /api/v1/documento/upload`: Subida y procesamiento asíncrono.
- `GET /api/v1/summaries/document/{document_id}`: Recuperar resumen. Debe manejar estados (`pending`, `processing`, `completed`, `failed`).

## 4. Gestión de Errores
- Implementar el estándar **RFC 9457** (Problem Details for HTTP APIs) en TODAS las respuestas de error.
- Los errores deben incluir estructuralmente: `type`, `title`, `status`, `detail` e `instance`.
- Implementar un manejador de excepciones global en FastAPI (Global Exception Handler) para evitar código repetido (DRY).

## 5. Seguridad y Configuración
- **Autenticación:** Implementar JWT (JSON Web Tokens). Las rutas de subida de documentos y consulta de resúmenes deben estar protegidas.
- **Autorización:** Un usuario solo puede acceder a los resúmenes de los documentos que él mismo subió.
- **Variables de Entorno:** Utilizar `pydantic-settings` para gestionar credenciales (DB, API Keys) cumpliendo el principio Config de 12-Factor App.
**Logging:** Implementar un sistema de logging estructurado (ej. módulo `logging` de Python) para monitorear el inicio, éxito o fallo de las `BackgroundTasks` y los servicios externos.

## 6. Testing y Calidad (TDD)
- Escribir pruebas unitarias y de integración utilizando `pytest`.
- **Mocks:** Burlar (mockear) la capa de infraestructura (Docling y OpenAI-compatible API) durante los tests para asegurar que las pruebas sean rápidas y no dependan de servicios externos.