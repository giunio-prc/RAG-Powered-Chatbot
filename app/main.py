import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.adapters.chroma_database import ChromaDataBase
from app.adapters.cohere_agent import CohereAgent
from app.api import database, prompting
from app.controller.controller import load_initial_documents

logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = ChromaDataBase()
    logger.info("Loading initial documents into the vector database")
    documents_folder = Path(__file__).parent.parent / "docs"
    await load_initial_documents(db, documents_folder)
    yield {"db": db, "agent": CohereAgent()}


app = FastAPI(title="Baby Shop AI Assistant", lifespan=lifespan)
app.include_router(database.router)
app.include_router(prompting.router)
