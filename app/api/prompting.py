from collections.abc import AsyncIterable
from typing import Annotated

from cohere.errors import TooManyRequestsError
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.sse import EventSourceResponse

from app.api.dependencies import (
    get_agent_from_state_annotation,
    get_cookie_session,
    get_db_from_state_annotation,
)
from app.controller.controller import query_agent, query_agent_with_stream_response

router = APIRouter()


@router.post("/query")
async def query_agent_endpoint(
    db: get_db_from_state_annotation,
    agent: get_agent_from_state_annotation,
    question: Annotated[str, Body()],
    cookie_session: Annotated[str, Depends(get_cookie_session)],
) -> str:
    try:
        response = await query_agent(db, agent, question, cookie_session)
        return response
    except TooManyRequestsError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )


@router.post("/query-stream", response_class=EventSourceResponse)
async def query_with_stream_response(
    db: get_db_from_state_annotation,
    agent: get_agent_from_state_annotation,
    question: Annotated[str, Body()],
    cookie_session: Annotated[str, Depends(get_cookie_session)],
) -> AsyncIterable[str]:
    async for token in query_agent_with_stream_response(
        db, agent, question, cookie_session
    ):
        yield token
