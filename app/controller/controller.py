from app.interfaces import AIAgentInterface, DatabaseManagerInterface


async def add_content_into_db(db: DatabaseManagerInterface, content: str):
    await db.add_text_to_db(content)


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer
