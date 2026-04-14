# Tasks: API de Procesamiento de Documentos

**Input**: Design documents from `/specs/001-document-processing-api/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: TDD es obligatorio por constitución. Todas las historias incluyen tests.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Task parallelizable
- **[Story]**: User story label (US1/US2/US3)
- Cada tarea incluye ruta exacta de archivo

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Inicializar proyecto y estructura base.

- [ ] T001 [#256] Inicializar proyecto Python con uv en `pyproject.toml`
- [ ] T002 [#257] Crear estructura de carpetas base en `app/` y `tests/`
- [ ] T003 [#258] [P] Configurar entorno base en `.env.example`
- [ ] T004 [#259] [P] Configurar pytest y pytest-asyncio en `pyproject.toml`
- [ ] T005 [#260] [P] Crear fixtures base en `tests/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura común que bloquea todas las historias.

### Tests for Foundational Phase

- [ ] T006 [#262] [P] Crear test de configuración en `tests/unit/test_config.py`
- [ ] T007 [#263] [P] Crear test de conexión PostgreSQL en `tests/unit/test_db_connection.py`
- [ ] T008 [#264] [P] Crear test de esquema RFC9457 en `tests/unit/test_problem_details.py`
- [ ] T009 [#265] [P] Crear test de JWT utilities en `tests/unit/test_security.py`
- [ ] T010 [#266] [P] Crear test de error handler global en `tests/unit/test_error_handler.py`

### Implementation for Foundational Phase

- [ ] T011 [#267] Implementar settings con pydantic-settings en `app/config.py`
- [ ] T012 [#268] Implementar pool asyncpg en `app/db/connection.py`
- [ ] T013 [#269] [P] Implementar esquema Problem Details en `app/schemas/error.py`
- [ ] T014 [#270] [P] Implementar excepciones de dominio en `app/core/exceptions.py`
- [ ] T015 [#271] Implementar exception handler global en `app/core/error_handlers.py`
- [ ] T016 [#272] Implementar utilidades JWT en `app/core/security.py`
- [ ] T017 [#273] [P] Implementar logger estructurado en `app/core/logging.py`
- [ ] T018 [#274] Implementar app factory FastAPI en `app/main.py`
- [ ] T019 [#275] [P] Crear DDL de usuarios en `docs/usuarios.sql`
- [ ] T020 [#276] [P] Crear DDL de documentos en `docs/documentos.sql`
- [ ] T021 [#277] [P] Crear DDL de resumenes en `docs/resumenes.sql`
- [ ] T022 [#278] Validar contrato OpenAPI base en `specs/001-document-processing-api/contracts/openapi.yaml`

**Checkpoint**: Base técnica lista; historias pueden empezar.

---

## Phase 3: User Story 1 - Registro de Usuario (Priority: P1)

**Goal**:  completo de usuarios con autenticación segura.

**Independent Test**: Crear, consultar, actualizar y eliminar usuario; login válido devuelve JWT.

### Tests for User Story 1

- [ ] T023 [#280] [P] [US1] Crear tests de modelo usuario en `tests/unit/test_models/test_usuario.py`
- [ ] T024 [#281] [P] [US1] Crear tests de repositorio usuario en `tests/unit/test_repositories/test_usuario_repository.py`
- [ ] T025 [#282] [P] [US1] Crear tests de servicio auth en `tests/unit/test_services/test_auth_service.py`
- [ ] T026 [#283] [P] [US1] Crear contract test POST users en `tests/contract/test_users_post.py`
- [ ] T027 [#284] [P] [US1] Crear contract test GET users/{id} en `tests/contract/test_users_get.py`
- [ ] T028 [#285] [P] [US1] Crear contract test PUT users/{id} en `tests/contract/test_users_put.py`
- [ ] T029 [#286] [P] [US1] Crear contract test DELETE users/{id} en `tests/contract/test_users_delete.py`
- [ ] T030 [#287] [P] [US1] Crear integration test flujo CRUD usuario en `tests/integration/test_api/test_users_crud_flow.py`

### Implementation for User Story 1

- [ ] T031 [#288] [P] [US1] Implementar modelo usuario en `app/models/usuario.py`
- [ ] T032 [#289] [P] [US1] Implementar schemas usuario en `app/schemas/usuario.py`
- [ ] T033 [#290] [US1] Implementar repositorio usuario en `app/repositories/usuario_repository.py`
- [ ] T034 [#291] [US1] Implementar servicio auth/hash/login en `app/services/auth_service.py`
- [ ] T035 [#292] [US1] Implementar endpoints POST/GET/PUT/DELETE users en `app/api/v1/users.py`
- [ ] T036 [#293] [US1] Implementar endpoint POST auth/login en `app/api/v1/auth.py`
- [ ] T037 [#294] [US1] Registrar rutas de usuario/auth en `app/api/v1/router.py`

**Checkpoint**: US1 funcional e independiente.

---

## Phase 4: User Story 2 - Subida y Procesamiento de Documentos (Priority: P1)

**Goal**: CRUD de documentos + upload asíncrono + validaciones PDF/25MB + estados.

**Independent Test**: Subir PDF válido recibe 202; documento cambia de estado y permite CRUD de metadatos.

### Tests for User Story 2

- [ ] T038 [#296] [P] [US2] Crear tests de modelo documento en `tests/unit/test_models/test_documento.py`
- [ ] T039 [#297] [P] [US2] Crear tests de repositorio documento en `tests/unit/test_repositories/test_documento_repository.py`
- [ ] T040 [#298] [P] [US2] Crear tests de extracción Docling mock en `tests/unit/test_services/test_extraction_service.py`
- [ ] T041 [#299] [P] [US2] Crear tests de resumen OpenAI mock en `tests/unit/test_services/test_summary_service.py`
- [ ] T042 [#300] [P] [US2] Crear tests de orquestación documento en `tests/unit/test_services/test_document_service.py`
- [ ] T043 [#301] [P] [US2] Crear contract test POST documento/upload en `tests/contract/test_documents_upload_post.py`
- [ ] T044 [#302] [P] [US2] Crear contract test validación PDF/25MB en `tests/contract/test_documents_upload_validation.py`
- [ ] T045 [#303] [P] [US2] Crear contract test GET documentos/{id} en `tests/contract/test_documents_get.py`
- [ ] T046 [#304] [P] [US2] Crear contract test GET documentos por usuario en `tests/contract/test_documents_list_by_user.py`
- [ ] T047 [#305] [P] [US2] Crear contract test PUT documentos/{id} en `tests/contract/test_documents_put.py`
- [ ] T048 [#306] [P] [US2] Crear contract test DELETE documentos/{id} en `tests/contract/test_documents_delete.py`
- [ ] T049 [#307] [P] [US2] Crear integration test flujo upload async en `tests/integration/test_api/test_documents_upload_async_flow.py`

### Implementation for User Story 2

- [ ] T050 [#308] [P] [US2] Implementar modelo documento en `app/models/documento.py`
- [ ] T051 [#309] [P] [US2] Implementar schemas documento en `app/schemas/documento.py`
- [ ] T052 [#310] [US2] Implementar repositorio documento en `app/repositories/documento_repository.py`
- [ ] T053 [#311] [US2] Implementar servicio extracción con Docling en `app/services/extraction_service.py`
- [ ] T054 [#312] [US2] Implementar servicio resumen con OpenAI/Nemotron en `app/services/summary_service.py`
- [ ] T055 [#313] [US2] Implementar servicio documento y BackgroundTasks en `app/services/document_service.py`
- [ ] T056 [#314] [US2] Implementar endpoints POST upload y CRUD documentos en `app/api/v1/documents.py`
- [ ] T057 [#315] [US2] Implementar validaciones `application/pdf` y 25MB en `app/api/v1/documents.py`
- [ ] T058 [#316] [US2] Registrar rutas de documentos en `app/api/v1/router.py`

**Checkpoint**: US2 funcional e independiente.

---

## Phase 5: User Story 3 - Consulta y CRUD de Resúmenes (Priority: P2)

**Goal**: CRUD de resúmenes y consulta por `document_id` con control de ownership.

**Independent Test**: Consultar resumen por documento retorna contenido/estado correcto y bloquea accesos cruzados.

### Tests for User Story 3

- [ ] T059 [#318] [P] [US3] Crear tests de modelo resumen en `tests/unit/test_models/test_resumen.py`
- [ ] T060 [#319] [P] [US3] Crear tests de repositorio resumen en `tests/unit/test_repositories/test_resumen_repository.py`
- [ ] T061 [#320] [P] [US3] Crear contract test GET summaries/document/{document_id} en `tests/contract/test_summaries_get_by_document.py`
- [ ] T062 [#321] [P] [US3] Crear contract test PUT summaries/{id} en `tests/contract/test_summaries_put.py`
- [ ] T063 [#322] [P] [US3] Crear contract test DELETE summaries/{id} en `tests/contract/test_summaries_delete.py`
- [ ] T064 [#323] [P] [US3] Crear contract test autorización ownership en `tests/contract/test_summaries_authorization.py`
- [ ] T065 [#324] [P] [US3] Crear integration test flujo consulta resumen en `tests/integration/test_api/test_summaries_flow.py`

### Implementation for User Story 3

- [ ] T066 [#325] [P] [US3] Implementar modelo resumen en `app/models/resumen.py`
- [ ] T067 [#326] [P] [US3] Implementar schemas resumen en `app/schemas/resumen.py`
- [ ] T068 [#327] [US3] Implementar repositorio resumen en `app/repositories/resumen_repository.py`
- [ ] T069 [#328] [US3] Implementar endpoint GET summaries/document/{document_id} en `app/api/v1/summaries.py`
- [ ] T070 [#329] [US3] Implementar endpoints PUT/DELETE summaries/{id} en `app/api/v1/summaries.py`
- [ ] T071 [#330] [US3] Implementar control ownership en `app/api/v1/summaries.py`
- [ ] T072 [#331] [US3] Registrar rutas de resúmenes en `app/api/v1/router.py`

**Checkpoint**: US3 funcional e independiente.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cierre técnico, calidad y operación.

- [ ] T073 [#333] [P] Completar documentación operativa en `specs/001-document-processing-api/quickstart.md`
- [ ] T074 [#334] [P] Añadir endpoint healthcheck en `app/api/v1/health.py`
- [ ] T075 [#335] [P] Añadir test de contrato OpenAPI en `tests/contract/test_openapi.py`
- [ ] T076 [#336] Ejecutar suite completa y cobertura en `tests/`
- [ ] T077 [#337] Validar formato RFC9457 en errores clave en `tests/integration/test_api/test_error_format.py`
- [ ] T078 [#338] [P] Preparar comando de ejecución Granian en `README.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 → Phase 2 → (Phase 3 y Phase 4 en paralelo) → Phase 5 → Phase 6

### User Story Dependencies

- **US1**: depende de Foundational
- **US2**: depende de Foundational
- **US3**: depende de US2 (resúmenes dependen de documentos procesados)

### Parallel Opportunities

- Setup: T003, T004, T005 en paralelo
- Foundational: T006–T010 y T013, T014, T017, T019–T021 en paralelo
- Historias: pruebas por historia en paralelo; modelos/schemas por historia en paralelo
- Equipo de 4:  
  - Dev A: US1  
  - Dev B: US2  
  - Dev C: US3 (arranca al estabilizar US2)  
  - Dev D: contratos, observabilidad, CI/calidad transversal

---

## Parallel Example: User Story 2

```bash
Task: "T043 [US2] Contract test POST upload en tests/contract/test_documents_upload_post.py"
Task: "T044 [US2] Contract test validación PDF/25MB en tests/contract/test_documents_upload_validation.py"
Task: "T050 [US2] Modelo documento en app/models/documento.py"
Task: "T051 [US2] Schemas documento en app/schemas/documento.py"
```

---

## Implementation Strategy

### MVP First

1. Completar Phase 1 + Phase 2
2. Completar US1 (registro/login + CRUD usuarios)
3. Completar US2 (upload async + CRUD documentos)
4. Validar demo MVP

### Incremental Delivery

1. US1 release interno
2. US2 release funcional de negocio
3. US3 release de consulta/gestión de resúmenes
4. Polish para estabilización final

