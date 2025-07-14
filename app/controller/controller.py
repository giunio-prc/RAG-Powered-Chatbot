from os import PathLike

from langchain_community.document_loaders import DirectoryLoader

from app.interfaces import AIAgentInterface, DatabaseManagerInterface


async def load_initial_documents(db: DatabaseManagerInterface, folder: PathLike):
    documents = DirectoryLoader(str(folder), "*.txt").load()
    chunks = db.text_splitter.split_documents(documents)
    await db.add_chunks([chunk.page_content for chunk in chunks])


async def add_content_into_db(db: DatabaseManagerInterface, content: str):
    await db.add_text_to_db(content)


async def query_agent(
    db: DatabaseManagerInterface, ai_agent: AIAgentInterface, question: str
) -> str:
    context = await db.get_context(question)
    answer = await ai_agent.query_with_context(question, context)
    return answer
