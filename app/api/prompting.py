from typing import Annotated

from cohere.errors import TooManyRequestsError
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import (
    get_agent_from_state_annotation,
    get_db_from_state_annotation,
)
from app.controller.controller import query_agent, query_agent_with_stream_response

router = APIRouter()


@router.post("/query")
async def query_agent_endpoint(
    db: get_db_from_state_annotation,
    agent: get_agent_from_state_annotation,
    question: Annotated[str, Body()],
):
    try:
        response = await query_agent(db, agent, question)
        return response
    except TooManyRequestsError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

@router.post("/query-stream")
async def query_with_stream_response(
    db: get_db_from_state_annotation,
    agent: get_agent_from_state_annotation,
    question: Annotated[str, Body()],
):
    async def safe_stream():
        try:
            async for chunk in query_agent_with_stream_response(db, agent, question):
                yield chunk
        except TooManyRequestsError:
            yield "Too many requests. Please try again later."

    return StreamingResponse(safe_stream(), media_type="text/plain")
