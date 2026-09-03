import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TypedDict

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.agents import CohereAgent, FakeAgent
from app.api.database import router as db_router
from app.api.prompting import router as query_router
from app.databases import ChromaDatabaseManager, FakeDatabaseManager
from app.middleware import SessionCookieMiddleware
from app.ports import AIAgentInterface, DatabaseManagerInterface

logger = logging.getLogger("uvicorn")


class State(TypedDict):
    db: DatabaseManagerInterface
    agent: AIAgentInterface
    cookies: set[str]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[State, None]:
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

    yield {"db": db, "agent": agent, "cookies": set()}


app = FastAPI(title="AI RAG Assistant", lifespan=lifespan)

# include analytics
if analytics_id := os.getenv("ANALYTICS_ID"):
    from api_analytics.fastapi import Analytics

    app.add_middleware(Analytics, api_key=analytics_id)

app.add_middleware(SessionCookieMiddleware, cookie_name="SESSION")

# Include API routers
app.include_router(db_router)
app.include_router(query_router)

# Set up static files (for favicon)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "ok"})


# Serve Vue SPA in production — must be last so API routes take precedence.
# Assets are mounted directly; everything else falls back to index.html so
# client-side routes like /documents are handled by the Vue router.
if os.path.isdir("frontend/dist"):
    if os.path.isdir("frontend/dist/assets"):
        app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="spa-assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        candidate = os.path.join("frontend/dist", full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse("frontend/dist/index.html")
