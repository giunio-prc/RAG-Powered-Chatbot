from os import PathLike

from app.controller.helpers import chunk_document
from app.interfaces import AIAgentInterface, DatabaseManagerInterface


async def load_initial_documents(db: DatabaseManagerInterface, folder: PathLike):
    await db.load_initial_documents(folder)


async def add_content_into_db(db: DatabaseManagerInterface, content: str):
    chunks = chunk_document(content)
    await db.add_chunks(chunks)


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer
