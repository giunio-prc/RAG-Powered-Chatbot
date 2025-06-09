from os import PathLike

from langchain.text_splitter import CharacterTextSplitter, TextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents.base import Document

from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: list[str]
    text_splitter: TextSplitter

    def __init__(self):
        self.db = []
        self.text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)

    async def load_initial_documents(self, folder: PathLike):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        chunks_documents = self.text_splitter.split_documents(documents)
        self.db.extend([document.page_content for document in chunks_documents])

    async def add_chunks(self, chunks: list[Document]):
        self.db.extend([document.page_content for document in chunks])

    async def get_context(self, question) -> str:
        return " ".join(self.db)

    async def add_document(self, content: bytes):
        pass

    def get_chunks(self) -> list[str]:
        return self.db
