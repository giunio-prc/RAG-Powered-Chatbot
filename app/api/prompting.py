from typing import Annotated

from fastapi import APIRouter, Body, Request

from app.controller.controller import query_agent
from app.interfaces.agent import AIAgentInterface
from app.interfaces.database import DatabaseManagerInterface

router = APIRouter()


@router.post("/query")
async def query_agent_endpoint(request: Request, question: Annotated[str, Body()]):
    db: DatabaseManagerInterface = request.state.db
    agent: AIAgentInterface = request.state.agent

    response = await query_agent(db, agent, question)

    return response
