from collections.abc import AsyncGenerator

from app.interfaces import AIAgentInterface, DatabaseManagerInterface


async def add_content_into_db(db: DatabaseManagerInterface, content: str):
    await db.add_text_to_db(content)


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer


async def query_agent_with_stream_response(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> AsyncGenerator[str, None]:
    context = await db.get_context(question)
    async for chunk in ai_agent.get_stream_response(question, context):
        yield chunk
