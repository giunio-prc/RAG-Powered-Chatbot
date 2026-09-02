# Stage 1: Build Vue frontend
# Build-only stage: vulnerabilities here do not affect the runtime image
FROM node:22-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python app
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

COPY pyproject.toml .
RUN uv sync --no-dev --no-install-project --no-cache

COPY app/ ./app/
COPY static/ ./static/
COPY --from=frontend-builder /frontend/dist ./frontend/dist

RUN useradd --no-create-home --shell /bin/false appuser && chown -R appuser /app
USER appuser

ENV PORT=8080
EXPOSE 8080

CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8080"]
