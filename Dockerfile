# Stage 1: Builder - Install dependencies with uv
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /build

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./

RUN uv venv /opt/venv && \
    uv pip install --no-cache-dir . granian

# Stage 2: Runtime
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    VIRTUAL_ENV=/opt/venv

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Crear usuario sin root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copiar venv del builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copiar código de la aplicación
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser main.py config.py alembic.ini ./

USER appuser

EXPOSE 8000

# HEALTHCHECK mejorado
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 8000), timeout=5); exit(0)" || exit 1

# CMD optimizado - usar granian directamente
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "main:app"] 