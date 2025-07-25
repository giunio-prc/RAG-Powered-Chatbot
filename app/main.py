import logging
from contextlib import asynccontextmanager
from pathlib import Path

from cohere.errors import TooManyRequestsError
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.agents.cohere_agent import CohereAgent
from app.api import database, prompting
from app.databases.chroma_database import ChromaDatabase

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = ChromaDatabase()
    logger.info("Loading initial documents into the vector database")
    documents_folder = Path(__file__).parent.parent / "docs"
    db.load_documents_from_folder(documents_folder)
    yield {"db": db, "agent": CohereAgent()}


app = FastAPI(title="Baby Shop AI Assistant", lifespan=lifespan)
app.include_router(database.router)
app.include_router(prompting.router)


@app.exception_handler(TooManyRequestsError)
async def too_many_request_error(request: Request, exc: TooManyRequestsError):
    return JSONResponse(
        status_code=exc.status_code or status.HTTP_429_TOO_MANY_REQUESTS,
        content={"message": "Too Many requests"},
    )
