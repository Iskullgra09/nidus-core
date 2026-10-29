# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY backend/pyproject.toml backend/uv.lock ./backend/
WORKDIR /app/backend
RUN uv sync --frozen --no-dev --no-install-project

COPY backend/ ./
COPY database/ /app/database/
RUN uv sync --frozen --no-dev


FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --system nidus && useradd --system --gid nidus --create-home nidus

WORKDIR /app

COPY --from=builder --chown=nidus:nidus /app /app

RUN mkdir -p /app/media && chown nidus:nidus /app/media

ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MEDIA_ROOT=/app/media

WORKDIR /app/backend

COPY --chown=nidus:nidus infrastructure/docker/api-entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

USER nidus

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
