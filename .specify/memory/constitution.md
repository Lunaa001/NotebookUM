<!--
=============================================================================
SYNC IMPACT REPORT
=============================================================================
Version change: 0.0.0 → 1.0.0 (Initial ratification)

Modified principles: N/A (Initial version)

Added sections:
- Core Principles: KISS, DRY, YAGNI, SOLID
- Test-Driven Development (TDD)
- Specification-Driven Development (SDD)
- 12-Factor App (primeros 6 factores)
- Technology Stack
- Governance

Removed sections: N/A (Initial version)

Templates requiring updates:
- ✅ plan-template.md (Constitution Check section compatible)
- ✅ spec-template.md (Requirements section compatible)
- ✅ tasks-template.md (TDD workflow compatible)

Follow-up TODOs: None
=============================================================================
-->

# NotebookUM Constitution

## Core Principles

### I. KISS (Keep It Simple, Stupid)

El código DEBE ser lo más simple posible. La complejidad innecesaria está prohibida.

- Cada función DEBE tener una única responsabilidad clara
- Las soluciones DEBEN preferir claridad sobre ingenio
- Si una implementación requiere explicación extensa, DEBE ser simplificada
- La complejidad adicional DEBE ser justificada explícitamente en código o documentación

**Rationale**: La simplicidad reduce errores, facilita mantenimiento y acelera onboarding.

### II. DRY (Don't Repeat Yourself)

La duplicación de lógica está prohibida. Cada pieza de conocimiento DEBE tener una única
representación autoritativa en el sistema.

- El código duplicado DEBE ser extraído a funciones/módulos reutilizables
- La configuración DEBE estar centralizada, no dispersa
- Los patrones repetitivos DEBEN ser abstraídos

**Rationale**: La duplicación causa inconsistencias y aumenta el costo de cambios.

### III. YAGNI (You Aren't Gonna Need It)

NO se implementará funcionalidad hasta que sea explícitamente requerida.

- Las características especulativas están PROHIBIDAS
- El código "por si acaso" DEBE ser removido
- Las abstracciones prematuras DEBEN evitarse

**Rationale**: El código no utilizado es deuda técnica que consume recursos sin valor.

### IV. SOLID

Los principios SOLID son OBLIGATORIOS para todo el código orientado a objetos:

- **S**ingle Responsibility: Una clase = una razón para cambiar
- **O**pen/Closed: Abierto para extensión, cerrado para modificación
- **L**iskov Substitution: Los subtipos DEBEN ser sustituibles por sus tipos base
- **I**nterface Segregation: Interfaces específicas sobre interfaces generales
- **D**ependency Inversion: Depender de abstracciones, no de implementaciones concretas

**Rationale**: SOLID produce código mantenible, testeable y extensible.

## Metodologías de Desarrollo

### V. TDD (Test-Driven Development) — NON-NEGOTIABLE

El desarrollo guiado por pruebas es OBLIGATORIO para toda funcionalidad:

1. **Red**: Escribir test que FALLA primero
2. **Green**: Implementar el código MÍNIMO para pasar el test
3. **Refactor**: Mejorar el código manteniendo tests verdes

- Los tests DEBEN existir ANTES de la implementación
- El código sin tests NO será aceptado en revisión
- Los tests DEBEN ser independientes y repetibles

**Rationale**: TDD garantiza cobertura, diseño emergente y documentación viva.

### VI. SDD (Specification-Driven Development)

El desarrollo DEBE comenzar con especificación clara:

- Cada feature DEBE tener spec.md antes de implementación
- Los requisitos DEBEN ser documentados en formato testeable (Given/When/Then)
- Los cambios de alcance DEBEN actualizar la especificación primero

**Rationale**: SDD previene scope creep y asegura alineación con necesidades del usuario.

## 12-Factor App (Primeros 6 Factores)

### VII. Codebase

Un único repositorio, múltiples deploys:

- TODO el código DEBE estar en control de versiones (Git)
- Un codebase = una aplicación
- Los ambientes (dev/staging/prod) son variaciones de deploy, no de código

### VIII. Dependencias

Declarar y aislar dependencias explícitamente:

- TODAS las dependencias DEBEN estar en `pyproject.toml`
- Usar `uv` como gestor de dependencias
- NO depender de paquetes del sistema implícitamente

### IX. Config

Almacenar configuración en el entorno:

- Las credenciales y configuración NUNCA en código
- Usar variables de entorno o archivos `.env` (excluidos de Git)
- La configuración DEBE ser verificable por ambiente

### X. Backing Services

Tratar backing services como recursos adjuntos:

- PostgreSQL, Redis, APIs externas = recursos intercambiables
- La conexión DEBE ser configurable vía URL de ambiente
- El código NO DEBE asumir localidad del servicio

### XI. Build, Release, Run

Separar estrictamente etapas de build/release/run:

- **Build**: Convertir código en ejecutable
- **Release**: Combinar build + config
- **Run**: Ejecutar release en ambiente

### XII. Processes

Ejecutar la app como uno o más procesos stateless:

- Los procesos DEBEN ser stateless y share-nothing
- El estado persistente DEBE almacenarse en backing services (PostgreSQL)
- Las sesiones DEBEN usar almacenamiento externo si es necesario

## Technology Stack

El proyecto NotebookUM utiliza el siguiente stack tecnológico OBLIGATORIO:

| Componente | Tecnología | Estándar |
|------------|------------|----------|
| Lenguaje | Python 3.11+ | PEP8 |
| Framework | FastAPI | OpenAPI 3.0 |
| Dependencias | uv | pyproject.toml |
| Base de datos | PostgreSQL | SQL estándar |
| Estructura | Clean Architecture | Capas separadas |
| Gestión | SCRUM | Sprints definidos |

## Governance

### Autoridad de la Constitución

Esta constitución SUPERSEDE todas las demás prácticas de desarrollo. En caso de conflicto
entre esta constitución y otras guías, la constitución prevalece.

### Proceso de Enmiendas

1. Proponer cambio con justificación documentada
2. Revisar impacto en templates y código existente
3. Actualizar versión según versionado semántico:
   - **MAJOR**: Cambios incompatibles (remoción de principios)
   - **MINOR**: Nuevas adiciones (principios/secciones)
   - **PATCH**: Clarificaciones y correcciones menores
4. Actualizar todos los templates afectados
5. Comunicar cambios al equipo

### Compliance

- Todo PR DEBE verificar cumplimiento con principios
- Las violaciones DEBEN ser justificadas en la sección Complexity Tracking del plan
- Code review DEBE incluir verificación de constitución

**Version**: 1.0.0 | **Ratified**: 2026-03-31 | **Last Amended**: 2026-03-31
