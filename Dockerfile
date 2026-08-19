FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY pyproject.toml .
RUN uv pip install --system --no-cache -e .

COPY app/ ./app/
COPY static/ ./static/
COPY docs/ ./docs/

ENV PORT=8080
EXPOSE 8080

CMD exec uv run --no-dev fastapi run app/main.py --host 0.0.0.0 --port ${PORT}
