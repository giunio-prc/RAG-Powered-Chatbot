from langchain.text_splitter import CharacterTextSplitter
from langchain_core.documents.base import Document

from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: list[str]

    def __init__(self):
        self.db = []
        self.text_splitter = CharacterTextSplitter(
            chunk_size=200, chunk_overlap=0, separator="\n"
        )

    async def add_chunks(self, chunks: list[Document]):
        self.db.extend([document.page_content for document in chunks])

    async def get_context(self, question) -> str:
        return " ".join(self.db)

    async def add_text_to_db(self, text: str):
        chunks = self.text_splitter.split_text(text)
        self.db.extend(chunks)

    def get_chunks(self) -> list[str]:
        return self.db

    def get_number_of_vectors(self) -> int:
        return len(self.db)

    def get_length_of_longest_vector(self) -> int:
        return len(max(self.db, key=len))
