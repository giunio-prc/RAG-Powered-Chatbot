from asyncio import sleep
from collections.abc import AsyncGenerator
from random import random

from app.interfaces import AIAgentInterface, DatabaseManagerInterface
from app.interfaces.errors import EmbeddingAPILimitError, TooManyRequestsError


async def add_content_into_db(db: DatabaseManagerInterface, content: str):
    try:
        async for percentage in db.add_text_to_db(content):  # type: ignore non-iterable
            yield f"{percentage}\n"
    except EmbeddingAPILimitError:
        # Return a special signal to indicate API limit reached
        # The frontend should look for this specific string
        yield "API_LIMIT_EXCEEDED\n"


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer


async def query_agent_with_stream_response(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> AsyncGenerator[str, None]:
    try:
        context = await db.get_context(question)
        async for chunk in ai_agent.get_stream_response( question, context):
            yield chunk
    except TooManyRequestsError:
        for char in "API key limit exceeded. Please try again later.":
            await sleep(0.05 * random())
            yield char
