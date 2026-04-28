FROM python:3.13-slim-trixie AS base

ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=postgresql+psycopg://notebookum:notebookum123@db:5432/notebookum
ENV GEMMA4_API_KEY=
ENV DEBUG=false

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

RUN useradd --create-home --home-dir /home/app app

WORKDIR /home/app

RUN apt-get update 
RUN apt-get install -y curl build-essential ca-certificates
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false
RUN rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

USER app

# ============ DEV STAGE (con pytest y dependencias de desarrollo) ============
FROM base AS dev

COPY pyproject.toml ./
COPY uv.lock* ./

# Instalar TODAS las dependencias (incluyendo dev para tests)
RUN if [ -f uv.lock ]; then \
        uv sync --frozen; \
    else \
        uv sync; \
    fi

COPY . .

EXPOSE 8000

# Por defecto, correr pytest cuando se ejecute el contenedor en modo dev
ENTRYPOINT ["uv", "run", "pytest"]
CMD ["tests/", "-v", "--tb=short"]

# ============ PROD STAGE (sin dependencias de desarrollo) ============
FROM base AS prod

COPY pyproject.toml ./
COPY uv.lock* ./

# Instalar SOLO dependencias de producción
RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-dev; \
    else \
        uv sync --no-dev; \
    fi

COPY . .

EXPOSE 8000

CMD ["uv", "run", "granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "main:app"]

# Usar prod por defecto
FROM prod
