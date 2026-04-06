# Data Model: API de Procesamiento de Documentos

**Feature**: 001-document-processing-api  
**Date**: 2026-04-06

## Entity Relationship Diagram

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│  usuarios   │       │  documentos  │       │  resumenes  │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id (PK)     │──────<│ id (PK)      │──────<│ id (PK)     │
│ email       │       │ usuario_id   │       │ documento_id│
│ password    │       │ nombre       │       │ contenido   │
│ nombre      │       │ tamano       │       │ created_at  │
│ created_at  │       │ estado       │       │ updated_at  │
│ updated_at  │       │ texto        │       └─────────────┘
└─────────────┘       │ created_at   │
                      │ updated_at   │
                      └──────────────┘
```

## Entity: usuarios

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Identificador único |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email de login |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hash |
| nombre | VARCHAR(100) | NOT NULL | Nombre completo |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha creación |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última modificación |

**Validation Rules**:
- Email debe ser válido (RFC 5322)
- Password mínimo 8 caracteres antes de hash
- Nombre no vacío

## Entity: documentos

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Identificador único |
| usuario_id | UUID | FK → usuarios(id), NOT NULL | Propietario |
| nombre | VARCHAR(255) | NOT NULL | Nombre archivo original |
| tamano | INTEGER | NOT NULL, CHECK > 0 | Tamaño en bytes |
| estado | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Estado procesamiento |
| texto_extraido | TEXT | NULL | Texto extraído (NULL si no procesado) |
| error_mensaje | TEXT | NULL | Mensaje de error si failed |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha subida |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última modificación |

**State Machine**:
```
pending ──────► processing ──────► completed
    │               │
    │               ▼
    └──────────► failed
```

**Valid States**: `pending`, `processing`, `completed`, `failed`

**Validation Rules**:
- tamano ≤ 26,214,400 bytes (25MB)
- nombre debe terminar en .pdf
- estado solo valores válidos del enum

## Entity: resumenes

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Identificador único |
| documento_id | UUID | FK → documentos(id), UNIQUE, NOT NULL | Documento origen |
| contenido | TEXT | NOT NULL | Texto del resumen |
| modelo_version | VARCHAR(50) | NOT NULL | Versión modelo usado |
| tokens_entrada | INTEGER | NULL | Tokens de entrada |
| tokens_salida | INTEGER | NULL | Tokens generados |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha generación |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Última modificación |

**Validation Rules**:
- documento_id debe existir y tener estado 'completed'
- contenido no vacío
- Un documento solo puede tener un resumen (UNIQUE constraint)

## Relationships

| From | To | Type | Description |
|------|-----|------|-------------|
| documentos.usuario_id | usuarios.id | Many-to-One | Usuario puede tener múltiples documentos |
| resumenes.documento_id | documentos.id | One-to-One | Un documento tiene máximo un resumen |

## Indexes

```sql
-- usuarios
CREATE UNIQUE INDEX idx_usuarios_email ON usuarios(email);

-- documentos
CREATE INDEX idx_documentos_usuario_id ON documentos(usuario_id);
CREATE INDEX idx_documentos_estado ON documentos(estado);
CREATE INDEX idx_documentos_created_at ON documentos(created_at DESC);

-- resumenes
CREATE UNIQUE INDEX idx_resumenes_documento_id ON resumenes(documento_id);
```

## Cascade Rules

| Parent | Child | On Delete |
|--------|-------|-----------|
| usuarios | documentos | CASCADE (borrar documentos del usuario) |
| documentos | resumenes | CASCADE (borrar resumen del documento) |
