# FASE 2: Base de Datos - Resumen de Implementación

## ✅ Completado

### 1. Dependencias Instaladas ✓
Se actualizó `pyproject.toml` con las siguientes dependencias:
- `sqlalchemy>=2.0.0` - ORM para manejo de base de datos
- `alembic>=1.14.0` - Sistema de migraciones
- `python-dotenv>=1.0.1` - Manejo de variables de entorno
- `pytest>=8.0.0` - Framework de testing
- `pytest-asyncio>=0.23.0` - Soporte async para tests

Todas instaladas con `uv sync` ✓

### 2. Modelos SQLAlchemy Creados ✓

#### Modelo Usuario (`app/models/usuario.py`)
```python
Campos:
- id: Integer (Primary Key)
- nombre: String(255) - Requerido
- email: String(255) - Único, Requerido
- fecha_registro: DateTime - Timestamp automático
```

#### Modelo Document (`app/models/document.py`)
```python
Campos:
- id: Integer (Primary Key)
- usuario_id: Integer (Foreign Key → usuarios.id)
- nombre_archivo: String(255)
- ruta_archivo: String(500)
- texto_extraido: Text (Nullable)
- fecha_creacion: DateTime - Timestamp automático

Relación:
- Usuario (backref: "documentos")
```

### 3. Configuración de Alembic ✓
- `alembic.ini` - Configuración de Alembic
- `alembic/env.py` - Entorno de ejecución
- `alembic/script.py.mako` - Plantilla de migraciones

### 4. Migración Inicial Creada ✓
- `alembic/versions/001_initial.py` - Migración para crear tablas usuario y documentos

## 📋 Base de Datos (config.py)
- URL PostgreSQL: `postgresql://postgres:postgres@localhost:5432/notebookum`
- Driver: `psycopg` (psycopg3)

## 🚀 Próximos Pasos - Cuando PostgreSQL esté disponible

### 1. Crear la base de datos
```bash
psql -U postgres
CREATE DATABASE notebookum;
\q
```

### 2. Aplicar las migraciones
```bash
uv run alembic upgrade head
```

### 3. Verificar las tablas creadas
```bash
psql -U postgres -d notebookum -c "\dt"
```

### 4. Restaurar imports en documents.py
Cuando tengas celery instalado, descomenta las líneas en:
- `app/controllers/documents.py`
- `app/controllers/__init__.py`

## 📁 Estructura de Carpetas Actualizada
```
app/
  models/
    ├── __init__.py         (Actualizado con exports)
    ├── base.py             (Nueva - Base de SQLAlchemy)
    ├── usuario.py          (Nueva - Modelo Usuario)
    ├── document.py         (Nueva - Modelo Document)
    └── example_model.py
  
alembic/
  versions/
    └── 001_initial.py      (Nueva - Migración inicial)
  env.py                     (Nueva - Configuración)
  script.py.mako            (Nueva - Plantilla)
```

## ⚙️ Configuración de Entorno
Para cambiar credenciales de BD, actualiza en `config.py`:
```python
DATABASE_URL: str = Field(default="postgresql://usuario:password@host:puerto/basedatos")
```

O usa variable de entorno:
```bash
export DATABASE_URL="postgresql://usuario:password@localhost:5432/notebookum"
```

---

**Estado**: Listo para aplicar migraciones cuando PostgreSQL esté disponible
