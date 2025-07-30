from typing import Annotated

from fastapi import APIRouter, Body
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
    response = await query_agent(db, agent, question)

    return response

@router.post("/query-stream")
async def query_with_stream_response(
    db: get_db_from_state_annotation,
    agent: get_agent_from_state_annotation,
    question: Annotated[str, Body()],
):
    return StreamingResponse(query_agent_with_stream_response(db, agent, question))
