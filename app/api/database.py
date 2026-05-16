from collections.abc import AsyncIterable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.agents import FakeAgent
from app.api.dependencies import (
    get_agent_from_state_annotation,
    get_cookie_session,
    get_db_from_state_annotation,
)
from app.usecases import add_content_into_db

router = APIRouter()


MAX_FILE_SIZE = 1024 * 1024  # 1 MB


async def get_valid_file_content(file: UploadFile) -> str:
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Invalid file. The app only support text files",
        )
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // 1024} KB",
        )
    try:
        return file.file.read().decode()
    except UnicodeError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="The file cannot be uploaded",
        )


class EventStreamResponse(StreamingResponse):
    media_type = "text/event-stream"


@router.post(
    "/add-document",
    response_class=EventStreamResponse,
    responses={
        406: {"description": "File cannot be decoded as UTF-8"},
        413: {"description": "File exceeds maximum size limit"},
        415: {"description": "Invalid file type. Only text/plain is supported"},
    },
)
async def add_document_endpoint(
    db: get_db_from_state_annotation,
    file_content: Annotated[str, Depends(get_valid_file_content)],
    cookie_session: Annotated[str, Depends(get_cookie_session)],
) -> AsyncIterable[str]:
    async for percentage in add_content_into_db(db, file_content, cookie_session):
        yield percentage


@router.get("/get-vectors-data")
async def get_vectors_data(
    db: get_db_from_state_annotation,
    cookie_session: Annotated[str, Depends(get_cookie_session)],
):
    number_of_vectors = db.get_number_of_vectors(cookie_session)
    longest_vector = db.get_length_of_longest_vector(cookie_session)
    return {"number_of_vectors": number_of_vectors, "longest_vector": longest_vector}


@router.delete("/empty-database")
async def empty_database(
    db: get_db_from_state_annotation,
    cookie_session: Annotated[str, Depends(get_cookie_session)],
):
    db.empty_database(cookie_session)
    return {"message": "Database emptied successfully"}


@router.get("/agent-info")
async def get_agent_info(agent: get_agent_from_state_annotation):
    """Return information about the current AI agent configuration."""
    is_fake = isinstance(agent, FakeAgent)
    return {
        "is_fake": is_fake,
        "icon": "pets" if is_fake else "smart_toy",
        "label": "RAG Parrot" if is_fake else "RAG Chatbot",
        "embedding_model": "No Embedding Model" if is_fake else "Cohere",
    }
