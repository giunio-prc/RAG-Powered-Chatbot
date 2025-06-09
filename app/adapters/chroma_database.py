from os import PathLike

from dotenv import load_dotenv
from langchain.text_splitter import TextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_core.documents.base import Document

from app.interfaces.database import DatabaseManagerInterface

load_dotenv()


class ChromaDataBase(DatabaseManagerInterface):
    db: Chroma
    text_splitter: TextSplitter

    def __init__(self):
        self.db = Chroma(embedding_function=CohereEmbeddings())
        self.db = TextSplitter(chunk_size=100, chunk_overlap=0)

    async def load_initial_documents(self, folder: PathLike):
        raw_documents = DirectoryLoader(str(folder), "*.txt").load()
        await self.db.aadd_documents(raw_documents)

    async def add_chunks(self, chunks: list[Document]):
        await self.db.aadd_documents(chunks)

    async def get_context(self, question) -> str:
        docs = self.db.similarity_search(question)
        return "\n\n".join(doc.page_content for doc in docs)

    def get_chunks(self) -> list[str]:
        # TODO get list of chunks
        return []
