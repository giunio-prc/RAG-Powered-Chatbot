from os import PathLike

from rag_powered_chatbot.controller.helpers import chunk_document
from rag_powered_chatbot.interfaces import AIAgentInterface, DatabaseManagerInterface


async def load_initial_documents(db: DatabaseManagerInterface, folder: PathLike):
    # TODO check if folder exists
    await db.load_initial_documents(folder)


async def add_document_into_db(db: DatabaseManagerInterface, document: bytes):
    chunks = chunk_document(document)
    await db.add_chunks(chunks)


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer
