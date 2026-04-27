# FASE 2: Testing de Modelos ✅

## Resumen de Tests

Se han creado **22 tests** para validar completamente los modelos `Usuario` y `Document`:

- ✅ **14 tests de estructura** - Validan que los modelos estén correctamente definidos
- ✅ **8 tests de integración** - Prueban operaciones CRUD y relaciones en BD

**Resultado**: 22/22 PASSED ✓

---

## Cómo Ejecutar los Tests

### 1. Tests de Estructura del Modelo
Valida que los campos, tipos y relaciones estén bien definidos:

```bash
uv run pytest tests/test_models.py -v
```

**Qué prueba:**
- ✓ Tablas Usuario y Document existen
- ✓ Columnas requeridas y tipos correctos
- ✓ Constraints (NOT NULL, PRIMARY KEY)
- ✓ Foreign key y relaciones
- ✓ Creación de instancias
- ✓ Representación de strings (`__repr__`)
- ✓ Valores por defecto

### 2. Tests de Integración (BD)
Valida CRUD completo usando SQLite en memoria:

```bash
uv run pytest tests/test_models_integration.py -v
```

**Qué prueba:**
- ✓ CREATE Usuario
- ✓ CREATE Document
- ✓ READ (queries)
- ✓ UPDATE (editar documentos)
- ✓ DELETE (eliminar documentos)
- ✓ Uniqueness de email
- ✓ Relaciones Usuario ↔ Document
- ✓ Foreign key constraints

### 3. Ejecutar Todos los Tests
```bash
uv run pytest tests/test_models.py tests/test_models_integration.py -v
```

O simplemente:
```bash
uv run pytest tests/ -k "test_models"
```

---

## Detalles de Tests

### Test Suite 1: `test_models.py` (14 tests)

#### TestModelStructure (7 tests)
```
✓ test_usuario_model_exists           - Tabla usuarios existe
✓ test_usuario_columns                - Columnas definidas correctamente
✓ test_usuario_email_unique           - Email es requerido
✓ test_document_model_exists          - Tabla documentos existe
✓ test_document_columns               - Columnas definidas
✓ test_document_foreign_key           - FK a usuario_id existe
✓ test_relationship_usuario_to_document - Relación backref definida
```

#### TestModelInstantiation (4 tests)
```
✓ test_usuario_instantiation          - Crear instancia Usuario
✓ test_document_instantiation         - Crear instancia Document
✓ test_usuario_repr                   - String representation Usuario
✓ test_document_repr                  - String representation Document
```

#### TestModelDefaults (2 tests)
```
✓ test_usuario_fecha_registro_default - fecha_registro tiene default
✓ test_document_fecha_creacion_default - fecha_creacion tiene default
```

#### TestBaseMetadata (1 test)
```
✓ test_base_contains_models           - Tablas en Base.metadata
```

---

### Test Suite 2: `test_models_integration.py` (8 tests)

Todos usan **SQLite en memoria** (`:memory:`)

```
✓ test_create_usuario                    - Crear usuario y recuperarlo
✓ test_usuario_email_unique              - Email único (IntegrityError)
✓ test_create_document                   - Crear documento con FK
✓ test_document_foreign_key              - FK constraint
✓ test_usuario_has_documents_relationship - Relación one-to-many
✓ test_query_documents_by_usuario        - Filtrar docs por usuario
✓ test_delete_usuario_documents          - Eliminar documents
✓ test_update_document                   - Actualizar texto_extraido
```

---

## Ejemplos de Uso en Tests

### Crear Usuario
```python
usuario = Usuario(
    nombre="Juan Pérez",
    email="juan@example.com",
    fecha_registro=datetime.utcnow()
)
session.add(usuario)
session.commit()
```

### Crear Documento
```python
documento = Document(
    usuario_id=usuario.id,
    nombre_archivo="documento.pdf",
    ruta_archivo="/uploads/documento.pdf",
    texto_extraido="Contenido extraído",
    fecha_creacion=datetime.utcnow()
)
session.add(documento)
session.commit()
```

### Acceder por Relación
```python
usuario = session.query(Usuario).first()
print(usuario.documentos)  # Acceder documentos del usuario
# [<Document(id=1, nombre_archivo=documento.pdf, usuario_id=1)>, ...]
```

### Consultar Documentos de Usuario
```python
docs = session.query(Document).filter_by(usuario_id=user_id).all()
```

---

## Comandos Útiles

### Ejecutar un test específico
```bash
uv run pytest tests/test_models.py::TestModelStructure::test_usuario_model_exists -v
```

### Ejecutar con cobertura
```bash
uv run pytest tests/test_models.py tests/test_models_integration.py --cov=app.models
```

### Ejecutar en modo quiet (solo resumen)
```bash
uv run pytest tests/test_models.py tests/test_models_integration.py -q
```

### Ver output con print statements
```bash
uv run pytest tests/test_models.py -v -s
```

---

## Archivos de Test

| Archivo | Descripción |
|---------|-------------|
| `tests/test_models.py` | Tests de estructura y validación de esquema |
| `tests/test_models_integration.py` | Tests CRUD con BD SQLite en memoria |
| `tests/test_models.py::TestModelStructure` | 7 tests de estructura |
| `tests/test_models.py::TestModelInstantiation` | 4 tests de instanciación |
| `tests/test_models.py::TestModelDefaults` | 2 tests de valores default |
| `tests/test_models.py::TestBaseMetadata` | 1 test de metadata |
| `tests/test_models_integration.py::TestModelsWithDatabase` | 8 tests con BD |

---

## Notas Importantes

1. **SQLite en Memoria**: Los tests de integración usan SQLite en memoria (`sqlite:///:memory:`) para no contaminar la BD real
2. **Transacciones**: Cada test hace rollback después para aislar cambios
3. **Deprecation Warnings**: Los warnings de `datetime.utcnow()` son por Python 3.13, no afectan tests
4. **Foreign Keys**: SQLite no enforza FK por defecto, pero los tests validan la estructura

---

## Próximos Pasos

Cuando PostgreSQL esté disponible:

```bash
# Aplicar migraciones
uv run alembic upgrade head

# Ejecutar tests contra PostgreSQL (si lo deseas)
# Actualizar test_models_integration.py para usar PostgreSQL
```

---

**Estado**: ✅ Todos los tests pasando correctamente
