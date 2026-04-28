# 🏗️ ARCHITECTURE - NotebookUM

**Project Structure:** Clean Architecture + Repository Pattern + Service Layer

---

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT / BROWSER                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP/REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FASTAPI APP (main.py)                    │
│         ┌─────────────────────────────────┐                │
│         │   ROUTING LAYER (Controllers)    │                │
│         │  - /api/v1/documents/upload     │                │
│         │  - /api/v1/documents/{id}       │                │
│         │  - /api/v1/documents/{id}/summary │  (FASE 5)   │
│         └─────────────────────────────────┘                │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌─────▼─────┐ ┌──────▼──────┐
│ Service Layer  │ │   Model   │ │  Repository │
│                │ │   Layer   │ │   Pattern   │
│ AIService      │ │  (ORM)    │ │             │
│ PDFExtService  │ │ Document  │ │ DocumentRep │
│ StorageService │ │ Usuario   │ │ UserRep     │
│ SummaryService │ │           │ │             │
└────────┬───────┘ └─────┬─────┘ └──────┬──────┘
         │                │              │
         └────────────────┼──────────────┘
                          │
                  DATABASE LAYER
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
   ┌────▼────┐    ┌──────▼───────┐   ┌─────▼────┐
   │PostgreSQL│    │  File Storage │   │  Gemma4  │
   │          │    │  (/tmp/uploads)   │   API    │
   │ usuarios │    │                   │  (UM)    │
   │documentos│    └─────────────────┘ └──────────┘
   │(+resumen)│
   └──────────┘
```

---

## 🔄 FASE 1-5: Detailed Breakdown

### FASE 1: FastAPI Framework + Router Registration

**Files:** `main.py`, `app/controllers/__init__.py`

```
main.py
  ├─ FastAPI() instantiation
  ├─ CORS middleware setup
  ├─ register_routers(app) call
  └─ Server start: granian

app/controllers/__init__.py
  ├─ import all routers
  └─ register each router
      ├─ example_router
      ├─ ai_router
      ├─ documents_router
      ├─ users_router
      ├─ summaries_router
      ├─ intelligence_router
      ├─ main_router
      └─ test_router
```

**Key Patterns:**
- APIRouter prefix for versioning: `/api/v1`
- Dependency injection via `Depends(get_session)`
- Exception handling with HTTPException

---

### FASE 2: Database + SQLAlchemy + Alembic

**Files:** `app/models/*.py`, `alembic/versions/`

```
Database Schema:
┌──────────────────────────────────────┐
│ usuarios                             │
├──────────────────────────────────────┤
│ id (PK)                              │
│ nombre (String)                      │
│ email (String, UNIQUE)               │
│ fecha_registro (DateTime)            │
└──────────────────────────────────────┘
         │
         │ (1:N)
         │
┌──────────────────────────────────────┐
│ documentos                           │
├──────────────────────────────────────┤
│ id (PK)                              │
│ usuario_id (FK → usuarios.id)        │
│ nombre_archivo (String)              │
│ ruta_archivo (String)                │
│ texto_extraido (Text)                │  FASE 4
│ resumen (Text)                       │  FASE 5
│ fecha_creacion (DateTime)            │
└──────────────────────────────────────┘
```

**ORM Stack:**
- SQLAlchemy 2.0 Core + ORM
- psycopg 3.3.3 (PostgreSQL driver)
- Alembic for migrations

**Migrations:**
- `001_initial.py` - Create users + documents tables
- `002_add_resumen_to_documento.py` - Add resumen field (FASE 5)

---

### FASE 3: Repository Pattern + CRUD

**Files:** `app/services/*_service.py`

```python
class DocumentService:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, data: dict) -> Document:
        # INSERT + commit
        
    def get_by_id(self, id: int) -> Document:
        # SELECT WHERE id
        
    def update(self, id: int, data: dict) -> Document:
        # UPDATE + commit
        
    def delete(self, id: int) -> bool:
        # DELETE + commit

class UserService:
    # Similar CRUD operations
```

**Design Patterns:**
- **Dependency Injection:** Services receive session via `__init__`
- **SRP (Single Responsibility):** Each service = one entity
- **Exception Handling:** ValueError for not found, etc

---

### FASE 4: PDF Extraction (Docling) + Storage

**Files:** `app/services/pdf_extraction_service.py`, `app/services/storage_service.py`

#### PDF Extraction Flow:

```
PDF File
    ↓
StorageService.save_file()
    ├─ Validate PDF header (%PDF)
    ├─ Generate UUID filename
    └─ Save to /tmp/notebookum_uploads/
        ↓
PDFExtractionService.extract_text()
    ├─ DocumentConverter(pdf_path)
    ├─ Convert to markdown
    ├─ Extract OCR text (if images)
    ├─ Preserve table structure
    └─ Return combined text
        ↓
Document.texto_extraido = extracted_text
    └─ Save to DB
```

**Key Features:**
- Docling 2.91.0 - Robust for any PDF type
- Automatic OCR via RapidOCR
- Table detection and preservation
- Layout awareness

**Storage Strategy:**
- File system: `/tmp/notebookum_uploads/`
- UUID naming: `{uuid}.{ext}`
- Metadata in DB: Document.ruta_archivo

---

### FASE 5: AI Summarization (Gemma4) ⭐

**Files:** `app/services/ai_service.py`, `app/services/summary_service.py`, `app/controllers/documents.py`

#### Summarization Flow:

```
POST /api/v1/documents/{id}/summary
    ↓
DocumentService.get_by_id(id)
    └─ Validate document exists
    └─ Get document.texto_extraido
        ↓
SummaryService.should_generate_summary()
    └─ Validate text length >= 100 chars
        ↓
SummaryService.generate_summary(texto_extraido)
    │
    └─ AIService.generate_summary()
        │
        ├─ Build prompt: "Genera resumen conciso..."
        ├─ Send to Gemma4 API (UM Faculty)
        │   POST https://ai.cloud.um.edu.ar/api/v1/chat/completions
        │   {
        │     "model": "gemma4-26b-16g",
        │     "messages": [{"role": "user", "content": prompt}],
        │     "max_tokens": 300
        │   }
        │
        └─ Parse response:
            ├─ Try choice.message.content
            ├─ Fallback to choice.message.reasoning
            └─ Return summary text
                ↓
Document.resumen = summary
    └─ Commit to DB
        ↓
Response: {
  "document_id": 1,
  "status": "generado",
  "resumen": "La IA es...",
  "resumen_longitud": 287
}
```

**Architecture Decisions:**

| Decision | Rationale |
|----------|-----------|
| Gemma4-26B | 26B params enough for summaries, UM Faculty API |
| max_tokens=300 | Balance: detailed but concise summaries |
| Fallback to "reasoning" | Gemma4 sometimes puts output there |
| Min 100 char check | Ensure meaningful summaries |
| Store in DB | Avoid re-summarizing same doc |
| Async endpoints | Handle long-running summarization |

---

## 🗂️ Directory Structure

```
NotebookUM/
├── app/
│   ├── __init__.py
│   ├── controllers/              # API Endpoints (Routers)
│   │   ├── __init__.py           # Router registration hub
│   │   ├── documents.py          # POST /upload, /summary, GET, DELETE
│   │   ├── ai_controller.py      # AI endpoints
│   │   ├── users.py              # User management
│   │   ├── summaries.py          # Summary endpoints
│   │   ├── intelligence.py       # Intelligence endpoints
│   │   ├── health_controller.py  # Health checks
│   │   ├── main.py               # Main endpoints
│   │   ├── example_controller.py # Example endpoints
│   │   └── test_controller.py    # Dev test endpoints
│   │
│   ├── services/                 # Business Logic Layer
│   │   ├── ai_service.py              # Gemma4 API integration
│   │   ├── summary_service.py         # Summarization logic (FASE 5)
│   │   ├── pdf_extraction_service.py  # Docling integration (FASE 4)
│   │   ├── storage_service.py         # File storage abstraction
│   │   ├── document_service.py        # Document CRUD
│   │   ├── user_service.py            # User CRUD
│   │   └── example_service.py         # Example service
│   │
│   ├── models/                   # ORM Models + Pydantic Schemas
│   │   ├── base.py               # SQLAlchemy Base class
│   │   ├── document.py           # Document ORM (+ resumen field)
│   │   ├── usuario.py            # Usuario ORM
│   │   ├── example_model.py      # Example models
│   │   └── health_model.py       # Health check schema
│   │
│   ├── database.py               # SQLAlchemy engine + session factory
│   └── CMD/                      # CLI commands
│       └── *.py                  # Task runners
│
├── tests/                        # Test Suite
│   ├── test_*.py                 # Unit tests per component
│   ├── test_summary_service_fase5.py    # FASE 5 tests
│   ├── test_gemma4_ai_service.py        # AI integration tests
│   └── ...
│
├── alembic/                      # Database Migrations
│   ├── env.py                    # Migration environment config
│   ├── script.py.mako            # Migration template
│   └── versions/
│       ├── 001_initial.py        # Initial schema
│       └── 002_add_resumen_to_documento.py  # FASE 5 migration
│
├── dockers/                      # Docker Compose files
│   ├── PostgreSQL/
│   │   ├── docker-compose.yml
│   │   └── data/                 # DB data volume
│   ├── redis/
│   ├── traefik/
│   └── notebookum/
│
├── main.py                       # FastAPI app entry point
├── config.py                     # Pydantic Settings
├── pyproject.toml                # Dependencies (uv)
├── pytest.ini                    # Test configuration
├── Dockerfile                    # Container image
├── dockerfile.compose.yml        # Full stack compose
├── readme.md                     # Documentation
├── DEPLOYMENT.md                 # Deployment guide
├── ARCHITECTURE.md               # This file
└── .env.example                  # Environment variables template
```

---

## 🔗 Data Flow Diagrams

### Upload → Extract → Store

```
CLIENT                      API                    SERVICES               DATABASE
  │                          │                        │                      │
  ├─POST /upload (PDF)──────→│                        │                      │
  │                          │                        │                      │
  │                          ├─ PDFExtractionService  │                      │
  │                          │   extract_text()       │                      │
  │                          │───────────────────────→│                      │
  │                          │                        │  Docling OCR         │
  │                          │   (text extracted)     │                      │
  │                          │←───────────────────────│                      │
  │                          │                        │                      │
  │                          ├─ DocumentService       │                      │
  │                          │   create()             │                      │
  │                          │────────────────────────────────────────────→  │
  │                          │                        │                    (INSERT)
  │◄─201 Created──────────────│                        │                      │
```

### Document → Summarize → Store

```
CLIENT                      API                    SERVICES               EXTERNAL API
  │                          │                        │                      │
  ├─POST /summary ────────→│                        │                      │
  │                          │                        │                      │
  │                          ├─ SummaryService        │                      │
  │                          │   generate_summary()   │                      │
  │                          │───────────────────────→│                      │
  │                          │                        ├─ AIService           │
  │                          │                        │  (Gemma4 API)        │
  │                          │                        │────────────────────→│
  │                          │                        │                      │
  │                          │                        │ (LLM Processing)     │
  │                          │                        │                      │
  │                          │                        │←────────────────────│
  │                          │   (summary text)       │                      │
  │                          │←───────────────────────│                      │
  │                          │                        │                      │
  │                          ├─ DocumentService       │                      │
  │                          │   update()             │                      │
  │                          │────────────────────────────────────────────→  │
  │                          │                        │                    (UPDATE)
  │◄─200 OK──────────────────│                        │                      │
  │{"resumen": "..."}        │                        │                      │
```

---

## 🏛️ Design Patterns Used

### 1. **Dependency Injection**
```python
# Controllers inject services via __init__
async def upload_document(
    session: Session = Depends(get_session)
):
    doc_service = DocumentService(session)
    storage = StorageService()
    pdf_service = PDFExtractionService()
```

### 2. **Repository Pattern**
```python
# Service abstracts database operations
class DocumentService:
    def create(self, data): pass
    def get_by_id(self, id): pass
    def update(self, id, data): pass
    def delete(self, id): pass
```

### 3. **Service Layer**
```python
# Business logic separated from controllers
class SummaryService:
    def generate_summary(self, text): pass
    def should_generate_summary(self, text): pass
```

### 4. **Factory Pattern**
```python
# Factories for complex object creation
get_session = sessionmaker(bind=engine)  # Session factory
```

### 5. **Strategy Pattern**
```python
# Different implementations of text extraction
PDFExtractionService  # Docling implementation
# Could have: PyPDFService, pdfplumber_service, etc
```

---

## 🔐 Security Considerations

| Layer | Implementation |
|-------|-----------------|
| **API** | HTTPException with status codes |
| **Database** | Parameterized queries (SQLAlchemy) |
| **Secrets** | Environment variables only (no hardcoding) |
| **Auth** | X-User-ID header (extensible to JWT) |
| **CORS** | Configurable origins from env |
| **File Upload** | Size limits, type validation, UUID naming |

---

## 📊 Performance Considerations

| Component | Optimization |
|-----------|--------------|
| **PDF Extraction** | Docling is parallel-friendly, cache on hash |
| **AI Summarization** | Async endpoint, store result in DB |
| **Database** | Connection pooling, indexes on FK+date |
| **File Storage** | Local FS (can scale to S3/GCS) |
| **API** | Granian ASGI (parallelized workers) |

---

## 🧪 Testing Strategy

```
Unit Tests (Fast, Isolated)
├─ test_ai_service.py (Mocked API responses)
├─ test_summary_service_fase5.py (FASE 5 logic)
├─ test_pdf_extraction_service.py (Mock PDFs)
└─ test_storage_service.py (File operations)

Integration Tests (Need DB)
├─ test_models_integration.py (ORM + relationships)
└─ test_document.py (Full CRUD + API)

E2E Tests (Need DB + API)
├─ test_summary_service_fase5.py (skipped - need live env)
└─ Manual testing with curl/Postman
```

**Coverage:** 78 passed tests, >80% code coverage

---

## 🚀 Future Enhancements

### Short Term (Next Sprint)
- [ ] JWT authentication (replace X-User-ID header)
- [ ] Rate limiting per user
- [ ] Webhook notifications on summary completion

### Medium Term
- [ ] Redis caching for extracted text
- [ ] Support for multiple file formats (DOCX, TXT, EPUB)
- [ ] Batch summarization endpoint
- [ ] Summary quality scoring

### Long Term
- [ ] Switch AI model (local vs cloud)
- [ ] Multi-language summarization
- [ ] Custom summarization templates
- [ ] Advanced analytics dashboard

---

**Version:** 1.2.0 | **Last Updated:** 2026-04-27
