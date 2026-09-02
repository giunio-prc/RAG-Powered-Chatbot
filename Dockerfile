# Stage 1: Build Vue frontend
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

ENV PORT=8080
EXPOSE 8080

CMD exec uv run --no-dev fastapi run app/main.py --host 0.0.0.0 --port ${PORT}
