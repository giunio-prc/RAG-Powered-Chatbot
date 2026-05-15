import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from nicegui.ui_run_with import run_with
from starlette.middleware.sessions import SessionMiddleware

from app.agents import CohereAgent, FakeAgent
from app.api import database, prompting
from app.databases import ChromaDatabaseManager, FakeDatabaseManager
from app.ports import AIAgentInterface, DatabaseManagerInterface
from app.ports.errors import TooManyRequestsError
from app.ui import setup_pages

logger = logging.getLogger("uvicorn")


class State(TypedDict):
    db: DatabaseManagerInterface
    agent: AIAgentInterface


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    _ = app
    if not os.getenv("COHERE_API_KEY"):
        logger.warning(
            "COHERE_API_KEY is not set. "
            "Using FakeDatabase and FakeAgent for testing purposes."
        )
        # Use fake implementations for testing purposes
        db = FakeDatabaseManager()
        agent = FakeAgent()
    else:
        db = ChromaDatabaseManager()
        agent = CohereAgent()

    yield {"db": db, "agent": agent}


app = FastAPI(title="AI RAG Assistant", lifespan=lifespan)

# include analytics
if analytics_id := os.getenv("ANALYTICS_ID"):
    from api_analytics.fastapi import Analytics

    app.add_middleware(Analytics, api_key=analytics_id)

# Include API routers
app.include_router(database.router)
app.include_router(prompting.router)

# Set up static files (for favicon)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "ok"})


@app.exception_handler(TooManyRequestsError)
async def too_many_request_error(request: Request, exc: TooManyRequestsError):
    _ = request
    return JSONResponse(
        status_code=exc.status_code or status.HTTP_429_TOO_MANY_REQUESTS,
        content={"message": "Too Many requests"},
    )


# Initialize NiceGUI pages and mount on FastAPI
setup_pages()

# Run NiceGUI with FastAPI
run_with(
    app,
    storage_secret=os.getenv("NICEGUI_STORAGE_SECRET", "rag-chatbot-secret-key"),
)

# Add SessionMiddleware after run_with to ensure it wraps all routes including NiceGUI
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "rag-chatbot-session-secret"),
    session_cookie="SESSION",
    max_age=60 * 60 * 24 * 30,  # 30 days
    https_only=False,  # Set to True in production with HTTPS
)
