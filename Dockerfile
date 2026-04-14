FROM python:3.13-slim-trixie AS base

ENV HOST=0.0.0.0
ENV PORT=8000
ENV DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/notebookum

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
# Copiar manifiestos primero para aprovechar cache de capas
COPY pyproject.toml ./
COPY uv.lock* ./

RUN if [ -f uv.lock ]; then \
        uv sync --frozen --no-dev; \
    else \
        uv sync --no-dev; \
    fi

COPY . .

EXPOSE 8000

CMD ["uv", "run", "granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "main:app"]
