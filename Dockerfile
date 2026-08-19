FROM python:3.12-slim

WORKDIR /app

RUN pip install uv --no-cache-dir

COPY pyproject.toml .
RUN uv pip install --system --no-cache -e . --no-dev

COPY app/ ./app/
COPY static/ ./static/
COPY docs/ ./docs/

ENV PORT=8080
EXPOSE 8080

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
