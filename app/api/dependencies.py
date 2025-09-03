from typing import Annotated

from fastapi import Depends, Request

from app.interfaces import AIAgentInterface, DatabaseManagerInterface


async def get_db_from_state(request: Request) -> DatabaseManagerInterface:
    return request.state.db


get_db_from_state_annotation = Annotated[
    DatabaseManagerInterface, Depends(get_db_from_state, use_cache=True)
]


async def get_agent_from_state(request: Request) -> AIAgentInterface:
    return request.state.agent


get_agent_from_state_annotation = Annotated[
    AIAgentInterface, Depends(get_agent_from_state, use_cache=True)
]


async def get_cookie_session(request: Request) -> str:
    return request.cookies.get("SESSION", "default")
