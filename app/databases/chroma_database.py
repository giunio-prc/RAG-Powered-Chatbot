from os import PathLike, getenv

from chromadb import HttpClient
from chromadb.api import ClientAPI
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents.base import Document

from app.interfaces.database import DatabaseManagerInterface

load_dotenv()


CHROMA_SERVER_HOST = getenv("CHROMA_SERVER_HOST")
CHROMA_SERVER_PORT = getenv("CHROMA_SERVER_PORT")

client: ClientAPI | None = None

if CHROMA_SERVER_HOST is not None and CHROMA_SERVER_PORT is not None:
    try:
        port = int(CHROMA_SERVER_PORT)
        client = HttpClient(host=CHROMA_SERVER_HOST, port=port)
    except ValueError:
        raise ValueError(
            f"Invalid CHROMA_SERVER_PORT: {CHROMA_SERVER_PORT}. Must be a valid integer."
        )
elif CHROMA_SERVER_HOST is not None:
    client = HttpClient(host=CHROMA_SERVER_HOST)


class ChromaDatabase(DatabaseManagerInterface):
    db: Chroma = Chroma(
        embedding_function=CohereEmbeddings(
            model="embed-v4.0"  # type: ignore
        ),
        client=client,
    )
    text_splitter: CharacterTextSplitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=0, separator="\n"
    )

    async def add_chunks(self, chunks: list[str]):
        await self.db.aadd_documents([Document(chunk) for chunk in chunks])

    async def add_text_to_db(self, text: str):
        chunks = [Document(chunk) for chunk in self.text_splitter.split_text(text)]
        await self.db.aadd_documents(chunks)

    def get_chunks(self) -> list[str]:
        return self.db.get()["documents"]

    async def get_context(self, question) -> str:
        documents = self.db.similarity_search(question)
        return "\n\n".join(doc.page_content for doc in documents)

    def get_number_of_vectors(self) -> int:
        return len(self.db.get()["documents"])

    def get_length_of_longest_vector(self) -> int:
        return len(max(self.db.get()["documents"], key=len))

    def empty_database(self):
        self.db.reset_collection()

    def load_documents_from_folder(self, folder: PathLike):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        self.db.add_documents(self.text_splitter.split_documents(documents))
