from os import PathLike

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents.base import Document

from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: list[Document]

    text_splitter: CharacterTextSplitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=0, separator="\n"
    )

    def __init__(self):
        self.db = []

    async def add_chunks(self, chunks: list[str]):
        self.db.extend([Document(page_content=chunk) for chunk in chunks])

    async def get_context(self, question) -> str:
        return "\n\n".join([document.page_content for document in self.db])

    async def add_text_to_db(self, text: str):
        chunks = self.text_splitter.split_text(text)
        self.db.extend([Document(page_content=chunk) for chunk in chunks])

    def get_chunks(self) -> list[str]:
        return [document.page_content for document in self.db]

    def get_number_of_vectors(self) -> int:
        return len(self.db)

    def get_length_of_longest_vector(self) -> int:
        if not self.db:
            return 0
        return len(max(self.db, key=lambda x: len(x.page_content)))

    def empty_database(self):
        self.db = []

    def load_documents_from_folder(self, folder: PathLike):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        self.db.extend(self.text_splitter.split_documents(documents))
