from os import PathLike

from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter, TextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents.base import Document

from app.interfaces.database import DatabaseManagerInterface

load_dotenv()


class ChromaDataBase(DatabaseManagerInterface):
    db: Chroma
    text_splitter: TextSplitter

    def __init__(self):
        self.db = Chroma(embedding_function=CohereEmbeddings(model="embed-v4.0"))
        self.text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)

    async def load_initial_documents(self, folder: PathLike):
        raw_documents = DirectoryLoader(str(folder), "*.txt").load()
        await self.db.aadd_documents(raw_documents)

    async def add_chunks(self, chunks: list[Document]):
        await self.db.aadd_documents(chunks)

    async def get_context(self, question) -> str:
        docs = self.db.similarity_search(question)
        return "\n\n".join(doc.page_content for doc in docs)

    def get_number_of_vectors(self) -> int:
        return len(self.db.get()["documents"])

    def get_length_of_longest_vector(self) -> int:
        return len(max(self.db.get()["documents"], key=len))
