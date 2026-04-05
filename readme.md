# Constitucion 

# Proyecto NotebookUM
Es un proyecto que tiene como funcionalidades: 
- extraer texto de archivos, utilizando la libreria Docling, 
- El texto extraido debe ser pasado al modelo Nemotron-3 nano 30B para ser resumido.
- El texto resumido va a ser guardado en base de datos.
## Tecnologias utilizadas en el proyecto
Se utilizaran las siguientes tecnologias:
- Metodologia de gestion de proyecto: SCRUM
- Lenguaje: Python (usar PEP8)
- Freamework: FastAPI
- Herramienta de dependencia: uv
- Base de datos: PostgreSQL
- Usar la estructura limpia del proyecto
## Principios
Se aplicaran los siguientes principios:
- KISS
- DRY
- YAGNI
- SOLID
## Metodologias
- TDD
- SDD
# Principios de diseño aplicados:
- Responsabilidad Simple (SRP)
- Inyección de Dependencias (Dependency Injection)
## Factor App
Se aplicara los seis primeros factores:
- Codebase
- Dependencias
- Config
- Backing services
- Build, release, run
- Processes
## Diagramas 

## Configuracion de las tablas en base de datos
- 
## Funcionalidad de la base de datos
- 

# Especificacion

## 1. Arquitectura y Persistencia
- **Rutas:** Todos los endpoints deben comenzar con `/api/v1/`.
- **Base de Datos:** Crear tablas `usuarios`, `documentos` y `resumenes` (plural, minúsculas). 
- **ORM y DDL:** Implementar CRUD completo con el patrón Repository. Los archivos SQL en `/docs` son la fuente de verdad.

## 2. Endpoint y Flujo de Procesamiento (`/documento/upload`)
- **Método y Ejecución:** POST, con procesamiento asincrónico vía `BackgroundTasks` de FastAPI.
- **Respuesta Inmediata:** Retornar **Status 202 Accepted** con el ID del documento tras validar el archivo.
- **El flujo interno debe:** Extraer texto (Docling) -> Generar resumen (Nemotron) -> Guardar DB.
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
- **Mocks:** Burlar (mockear) la capa de infraestructura (Docling y Nemotron) durante los tests para asegurar que las pruebas sean rápidas y no dependan de servicios externos.