from os import PathLike, getenv
from typing import AsyncIterator

from chromadb import HttpClient
from chromadb.api import ClientAPI
from cohere.errors import TooManyRequestsError as CohereTooManyRequestsError
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_cohere import CohereEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents.base import Document

from app.interfaces.database import DatabaseManagerInterface
from app.interfaces.errors import EmbeddingAPILimitError, TooManyRequestsError

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
    db: Chroma
    text_splitter: CharacterTextSplitter

    def __init__(self):
        self.db = Chroma(
            embedding_function=CohereEmbeddings(  # type: ignore
                model="embed-v4.0"
            ),
            client=client,
        )
        self.text_splitter = CharacterTextSplitter(
            chunk_size=200, chunk_overlap=0, separator="\n"
        )

    async def add_text_to_db(self, text: str) -> AsyncIterator[float]:
        chunks = [Document(chunk) for chunk in self.text_splitter.split_text(text)]
        uploaded_chunk_ids = []

        try:
            for progress, chunk in enumerate(chunks):
                # Add document and capture the IDs for potential rollback
                result = await self.db.aadd_documents([chunk])
                uploaded_chunk_ids.extend(result)
                yield (progress + 1) / len(chunks) * 100

        except CohereTooManyRequestsError as err:
            # If we have uploaded chunks, we need to roll them back
            if uploaded_chunk_ids:
                await self.db.adelete(ids=uploaded_chunk_ids)
            raise EmbeddingAPILimitError(
                content=err.body, chunks_uploaded=len(uploaded_chunk_ids)
            )

    def get_chunks(self) -> list[str]:
        return self.db.get()["documents"]

    async def get_context(self, question) -> str:
        try:
            documents = await self.db.asimilarity_search(question)
        except CohereTooManyRequestsError as err:
            raise TooManyRequestsError(content=err.body)
        if not documents:
            return "there is no context, you are not allowed to answer"

        return "\n\n".join(doc.page_content for doc in documents)

    def get_number_of_vectors(self) -> int:
        return len(self.db.get()["documents"])

    def get_length_of_longest_vector(self) -> int:
        documents = self.db.get()["documents"]
        if not documents:
            return 0
        return len(max(documents, key=len))

    def empty_database(self):
        self.db.reset_collection()

    def load_documents_from_folder(self, folder: PathLike):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        self.db.add_documents(self.text_splitter.split_documents(documents))
