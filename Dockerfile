# Stage 1: Builder - Instalar dependencias
FROM python:3.13-slim AS builder

# Variables para logs en tiempo real y reducir .pyc
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /build

# Instalar uv (gestor de paquetes rápido)
RUN pip install --no-cache-dir uv

# Copiar especificaciones (permite reutilizar layers)
COPY pyproject.toml uv.lock* ./

# Crear virtual environment e instalar dependencias
RUN uv venv /opt/venv && \
    uv pip install --no-cache-dir . granian

# Stage 2: Runtime - Imagen final (sin herramientas build)
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

# Crear usuario no-root por seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar venv del builder (solo lo necesario)
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser main.py config.py alembic.ini ./

# Ejecutar como usuario no-root
USER appuser

EXPOSE 8000

# Health check cada 30s
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=5); exit(0)" || exit 1

# Servidor ASGI en puerto 8000
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "main:app"] 