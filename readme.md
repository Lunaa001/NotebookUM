# NotebookUM

Aplicación Python moderna construida con FastAPI y OpenAI, gestionada con [uv](https://github.com/astral-sh/uv).

## 📋 Prerrequisitos

- **Python 3.13+**
- **uv** - Gestor de paquetes Python ultrarrápido
  - **macOS/Linux:** `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - **Windows:** `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

## 🚀 Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPO>
   cd NotebookUM
   ```

2. **Sincronizar dependencias:**
   
   `uv` creará automáticamente un entorno virtual en `.venv` e instalará todas las dependencias:
   ```bash
   uv venv
   source .venv/bin/activate
   uv sync
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Edita .env con tus claves API
   ```

## ▶️ Ejecución

### Ejecutar el script principal:
```bash
uv run python main.py
```

### Ejecutar con FastAPI + Uvicorn (desarrollo):
```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

## 📁 Estructura del Proyecto

```
NotebookUM/
├── app/
│   ├── controllers/     # Endpoints y rutas de la API
│   ├── models/          # Esquemas de datos (Pydantic/ORM)
│   ├── services/        # Lógica de negocio
│   ├── utils/           # Funciones auxiliares
│   └── tests/           # Tests unitarios e integración
├── config.py            # Configuración global de la aplicación
├── main.py              # Punto de entrada
├── pyproject.toml       # Dependencias y metadatos del proyecto
└── uv.lock              # Lockfile para reproducibilidad
```

### Convenciones de Arquitectura

- **Controllers:** Manejan las peticiones HTTP y validan entrada/salida
- **Services:** Contienen la lógica de negocio pura (sin HTTP)
- **Models:** Define estructuras de datos y validaciones
- **Utils:** Funciones reutilizables (helpers, formatters, etc.)

## 🛠️ Comandos Útiles

### Gestión de Dependencias

```bash
# Añadir una nueva dependencia
uv add nombre-paquete

# Añadir dependencia de desarrollo
uv add --dev pytest

# Actualizar dependencias
uv sync --upgrade

# Eliminar una dependencia
uv remove nombre-paquete
```

### Testing

```bash
# Ejecutar tests
uv run pytest

# Con cobertura
uv run pytest --cov=app
```

### Linting y Formateo

```bash
# Formatear código (si usas ruff)
uv run ruff format .

# Linter
uv run ruff check .
```

## 📝 Desarrollo

### Añadir un Nuevo Endpoint

1. Crear el controlador en `app/controllers/`
2. Implementar la lógica en `app/services/`
3. Definir modelos en `app/models/`
4. Registrar la ruta en el router principal

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

[Especifica tu licencia aquí]
