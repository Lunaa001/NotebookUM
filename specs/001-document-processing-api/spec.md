# Feature Specification: API de Procesamiento de Documentos

**Feature Branch**: `001-document-processing-api`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: Sistema de procesamiento de documentos PDF con extracción de texto y generación de resúmenes

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro de Usuario (Priority: P1)

Como nuevo usuario, quiero crear una cuenta en el sistema para poder subir documentos
y acceder a los resúmenes generados.

**Why this priority**: Sin usuarios registrados, ninguna otra funcionalidad del sistema
tiene sentido. Es el punto de entrada obligatorio para cualquier interacción.

**Independent Test**: Se puede probar creando un usuario y verificando que sus datos
se persisten correctamente y son recuperables.

**Acceptance Scenarios**:

1. **Given** un usuario sin cuenta, **When** envía sus datos de registro al sistema,
   **Then** se crea su cuenta y recibe confirmación con su identificador único.
2. **Given** un usuario registrado, **When** solicita sus datos por identificador,
   **Then** recibe la información de su perfil.
3. **Given** datos de registro incompletos, **When** intenta registrarse,
   **Then** recibe un mensaje de error indicando los campos faltantes.

---

### User Story 2 - Subida y Procesamiento de Documentos (Priority: P1)

Como usuario registrado, quiero subir un documento PDF para que el sistema extraiga
su texto y genere un resumen automáticamente.

**Why this priority**: Esta es la funcionalidad core del sistema. Sin procesamiento
de documentos, el producto no entrega valor.

**Independent Test**: Se puede probar subiendo un PDF válido y verificando que se
extrae el texto y se genera el resumen asociado al documento.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con un PDF válido (≤25MB), **When** sube el documento,
   **Then** el sistema procesa asincrónicamente: extrae texto, genera resumen y guarda
   la información sin almacenar el archivo original.
2. **Given** un archivo que no es PDF, **When** intenta subirlo,
   **Then** recibe error indicando que solo se aceptan archivos PDF.
3. **Given** un PDF mayor a 25MB, **When** intenta subirlo,
   **Then** recibe error indicando que el archivo excede el tamaño máximo permitido.
4. **Given** un documento procesado exitosamente, **When** el proceso finaliza,
   **Then** el usuario puede consultar el estado y resultado del procesamiento.

---

### User Story 3 - Consulta de Resúmenes (Priority: P2)

Como usuario registrado, quiero consultar el resumen generado de un documento
previamente procesado.

**Why this priority**: Complementa la funcionalidad core. Los usuarios necesitan
acceder a los resúmenes después del procesamiento.

**Independent Test**: Se puede probar consultando el resumen de un documento
previamente procesado y verificando que contiene el texto resumido.

**Acceptance Scenarios**:

1. **Given** un documento procesado exitosamente, **When** el usuario solicita su resumen,
   **Then** recibe el texto resumido del documento.
2. **Given** un identificador de documento inexistente, **When** solicita el resumen,
   **Then** recibe error indicando que el documento no existe.
3. **Given** un documento en procesamiento, **When** solicita el resumen,
   **Then** recibe indicación de que el procesamiento está en curso.

---

### Edge Cases

- ¿Qué sucede si el PDF está protegido con contraseña? El sistema rechaza el archivo
  indicando que no se pueden procesar PDFs protegidos.
- ¿Qué sucede si el PDF no contiene texto extraíble (solo imágenes)? El sistema
  genera un resumen vacío o indica que no se encontró texto.
- ¿Qué sucede si el servicio de resumen está temporalmente no disponible?
  El documento queda en estado "pendiente" y se reintenta automáticamente.
- ¿Qué sucede si se sube el mismo documento dos veces? Se crea un nuevo registro
  de documento y se procesa independientemente.

## Requirements *(mandatory)*

### Functional Requirements

#### Gestión de Usuarios

- **FR-001**: El sistema DEBE permitir crear cuentas de usuario mediante registro.
- **FR-002**: El sistema DEBE permitir consultar información de un usuario por su identificador.
- **FR-003**: El sistema DEBE permitir actualizar datos de un usuario existente.
- **FR-004**: El sistema DEBE permitir eliminar cuentas de usuario.
- **FR-005**: El sistema DEBE validar que los datos de registro estén completos.
- **FR-006**: El sistema DEBE hashear contraseñas antes de persistir cuentas de usuario.

#### Gestión de Documentos

- **FR-007**: El sistema DEBE permitir subir archivos PDF de hasta 25MB.
- **FR-008**: El sistema DEBE validar que el tipo de contenido sea `application/pdf`.
- **FR-009**: El sistema DEBE rechazar archivos que no sean PDF con error estructurado
  siguiendo el formato RFC 9457 (Problem Details).
- **FR-010**: El sistema DEBE rechazar archivos que excedan 25MB con error estructurado
  siguiendo el formato RFC 9457.
- **FR-011**: El sistema DEBE procesar documentos de forma asíncrona.
- **FR-012**: El sistema DEBE responder `202 Accepted` con el identificador del documento
  cuando el archivo pase validaciones iniciales.
- **FR-013**: El sistema DEBE extraer el texto del documento PDF.
- **FR-014**: El sistema DEBE generar un resumen del texto extraído usando el modelo
  Nemotron-3 nano 30B.
- **FR-015**: El sistema NO DEBE almacenar el archivo PDF original.
- **FR-016**: El sistema DEBE permitir consultar documentos por identificador.
- **FR-017**: El sistema DEBE permitir listar documentos de un usuario.
- **FR-018**: El sistema DEBE permitir actualizar metadatos de documentos.
- **FR-019**: El sistema DEBE permitir eliminar registros de documentos.
- **FR-020**: El sistema DEBE manejar estados de documento: `pending`, `processing`,
  `completed`, `failed`.

#### Gestión de Resúmenes

- **FR-021**: El sistema DEBE almacenar los resúmenes generados en base de datos.
- **FR-022**: El sistema DEBE permitir consultar el resumen de un documento específico.
- **FR-023**: El sistema DEBE permitir actualizar resúmenes existentes.
- **FR-024**: El sistema DEBE permitir eliminar resúmenes.
- **FR-025**: El sistema DEBE asociar cada resumen con su documento origen.
- **FR-026**: El sistema DEBE restringir el acceso a resúmenes para que cada usuario solo
  consulte documentos que él mismo subió.

#### Estructura de Datos

- **FR-027**: El sistema DEBE mantener tres entidades principales: usuarios,
  documentos y resumenes (nombres en plural y minúsculas).
- **FR-028**: Los scripts DDL DEBEN almacenarse en la carpeta `docs/` con extensión `.sql`.
- **FR-029**: Todos los endpoints DEBEN usar el prefijo `/api/v1/`.

#### Contratos de API y Errores

- **FR-030**: El sistema DEBE exponer `POST /api/v1/users` para crear usuarios.
- **FR-031**: El sistema DEBE exponer `GET /api/v1/users/{id}` para consultar usuarios.
- **FR-032**: El sistema DEBE exponer `POST /api/v1/documento/upload` para crear documentos
  mediante carga de archivo.
- **FR-033**: El sistema DEBE exponer `GET /api/v1/summaries/document/{document_id}` para
  consultar el resumen y el estado de procesamiento.
- **FR-034**: El sistema DEBE aplicar RFC 9457 en TODAS las respuestas de error con
  campos `type`, `title`, `status`, `detail`, `instance`.
- **FR-035**: El sistema DEBE centralizar el manejo de excepciones en un manejador global.

#### Seguridad, Configuración y Calidad

- **FR-036**: El sistema DEBE proteger con autenticación las rutas de subida de documentos
  y consulta de resúmenes.
- **FR-037**: El sistema DEBE gestionar credenciales y configuración sensible mediante
  variables de entorno.
- **FR-038**: El sistema DEBE registrar logs estructurados para inicio, éxito y fallo de
  procesamiento asíncrono y llamadas a servicios externos.
- **FR-039**: El sistema DEBE incluir pruebas unitarias e integración para los flujos
  principales.
- **FR-040**: El sistema DEBE permitir mockear Docling y Nemotron en pruebas para evitar
  dependencia de servicios externos.

#### Matriz CRUD Explícita

- **FR-041**: El sistema DEBE implementar CRUD completo de `usuarios`:
  - Create: registro de usuario
  - Read: consulta por identificador
  - Update: actualización de perfil
  - Delete: eliminación de cuenta
- **FR-042**: El sistema DEBE implementar CRUD completo de `documentos`:
  - Create: subida de documento (upload)
  - Read: consulta por identificador y listado por usuario
  - Update: actualización de metadatos y estado del documento
  - Delete: eliminación de documento
- **FR-043**: El sistema DEBE implementar CRUD completo de `resumenes`:
  - Create: generación y almacenamiento automático tras procesamiento
  - Read: consulta por `document_id`
  - Update: actualización del contenido de resumen
  - Delete: eliminación de resumen

### Key Entities

- **Usuario**: Representa una persona registrada en el sistema. Contiene información
  de identificación y datos de contacto. Puede tener múltiples documentos asociados.

- **Documento**: Representa un archivo PDF procesado. Contiene metadatos del archivo
  (nombre, tamaño, fecha de subida), el texto extraído y su estado de procesamiento.
  Pertenece a un usuario y tiene un resumen asociado.

- **Resumen**: Representa el texto resumido de un documento. Contiene el contenido
  del resumen, fecha de generación y referencia al documento origen.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los usuarios pueden completar el registro de cuenta en menos de 1 minuto.
- **SC-002**: El sistema acepta documentos PDF de hasta 25MB sin rechazos falsos.
- **SC-003**: Los archivos no-PDF son rechazados el 100% de las veces con mensaje claro.
- **SC-004**: Los archivos mayores a 25MB son rechazados el 100% de las veces con mensaje claro.
- **SC-005**: El procesamiento de un documento de 10 páginas completa en menos de 2 minutos.
- **SC-006**: Los usuarios pueden acceder a sus resúmenes inmediatamente después
  de que el procesamiento finaliza.
- **SC-007**: El sistema soporta al menos 100 usuarios concurrentes sin degradación
  perceptible.
- **SC-008**: Los errores se presentan en formato estructurado RFC 9457, permitiendo
  a los clientes manejarlos programáticamente.
- **SC-009**: El 95% de los documentos procesados generan resúmenes coherentes y útiles.

## Assumptions

- Los usuarios tienen conectividad a internet estable para subir archivos de hasta 25MB.
- Los documentos PDF subidos contienen texto extraíble (no solo imágenes escaneadas).
- El modelo Nemotron-3 nano 30B está disponible y accesible para el sistema.
- PostgreSQL está disponible como backing service.
- La autenticación de usuarios se implementará usando tokens (JWT) como práctica estándar.
- Los usuarios suben documentos propios y tienen derecho legal sobre su contenido.
- El sistema no requiere soporte móvil nativo en esta versión.
- La extracción de texto se realiza usando la librería Docling según la documentación del proyecto.
- Los DDL de las tablas se versionan junto con el código en el repositorio.
