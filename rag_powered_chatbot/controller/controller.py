from os import PathLike

from rag_powered_chatbot.interfaces.database import DatabaseManagerInterface


async def load_initial_documents(db: DatabaseManagerInterface, folder: PathLike):
    # check if folder exists
    await db.load_initial_documents(folder)
