from os import PathLike

from langchain.text_splitter import TextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma

from app.interfaces.database import DatabaseManagerInterface


class ChromaDataBase(DatabaseManagerInterface):
    db: Chroma
    text_splitter: TextSplitter

    def __init__(self):
        self.db = Chroma(embedding_function=CohereEmbeddings())
        self.db = TextSplitter(chunk_size=100, chunk_overlap=0)

    async def load_initial_documents(self, folder: PathLike):
        raw_documents = DirectoryLoader(str(folder), "*.txt").load()
        chunks = await self.db.aadd_documents(chunks)

    async def add_chunks(self, chunks: list[str]):
        pass
