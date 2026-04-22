import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from nicegui import ui

from app.agents import CohereAgent, FakeAgent
from app.api import database, prompting
from app.databases import ChromaDatabase, FakeDatabase
from app.interfaces import AIAgentInterface, DatabaseManagerInterface
from app.interfaces.errors import TooManyRequestsError
from app.middleware import SessionCookieMiddleware
from app.ui import setup_pages

logger = logging.getLogger(__name__)


class State(TypedDict):
    db: DatabaseManagerInterface
    agent: AIAgentInterface


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    if not os.getenv("COHERE_API_KEY"):
        logger.warning(
            "COHERE_API_KEY is not set. Using FakeDatabase and FakeAgent for testing purposes."
        )
        # Use fake implementations for testing purposes
        db = FakeDatabase()
        agent = FakeAgent()
    else:
        db = ChromaDatabase()
        agent = CohereAgent()

    yield {"db": db, "agent": agent, "cookies": set()}


app = FastAPI(title="AI RAG Assistant", lifespan=lifespan)

# include analytics
if os.getenv("ANALYTICS_ID"):
    from api_analytics.fastapi import Analytics

    app.add_middleware(Analytics, api_key=os.getenv("ANALYTICS_ID"))

app.add_middleware(SessionCookieMiddleware, cookie_name="SESSION")

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
    return JSONResponse(
        status_code=exc.status_code or status.HTTP_429_TOO_MANY_REQUESTS,
        content={"message": "Too Many requests"},
    )


# Initialize NiceGUI pages and mount on FastAPI
setup_pages()

# Run NiceGUI with FastAPI - storage_secret enables persistent user storage
ui.run_with(
    app,
    storage_secret=os.getenv("NICEGUI_STORAGE_SECRET", "rag-chatbot-secret-key"),
)
