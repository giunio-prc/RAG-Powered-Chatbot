from collections import defaultdict
from difflib import get_close_matches
from os import PathLike
from typing import AsyncGenerator

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: defaultdict[str, list[str]]

    text_splitter: CharacterTextSplitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=0, separator="\n"
    )

    def __init__(self):
        self.db = defaultdict(list)

    async def get_context(self, question: str, cookie: str | None = None) -> str:
        user_db = self.db[cookie or "default"]
        context = get_close_matches(question, user_db, n=1, cutoff=0.1)
        return (
            "\n\n".join(context)
            if context
            else "there is no context, you are not allowed to answer"
        )

    async def add_text_to_db(
        self, text: str, cookie: str | None = None
    ) -> AsyncGenerator[float, None]:
        chunks = self.text_splitter.split_text(text)
        for progress, chunk in enumerate(chunks):
            self.db[cookie or "default"].append(chunk)
            yield (progress + 1) / len(chunks) * 100

    def get_chunks(self, cookie: str | None = None) -> list[str]:
        return self.db[cookie or "default"]

    def get_number_of_vectors(self, cookie: str | None = None) -> int:
        return len(self.db[cookie or "default"])

    def get_length_of_longest_vector(self, cookie: str | None = None) -> int:
        if not self.db[cookie or "default"]:
            return 0
        return len(max(self.db[cookie or "default"], key=len))

    def empty_database(self, cookie: str | None = None):
        self.db[cookie or "default"] = []

    def load_documents_from_folder(self, folder: PathLike, cookie: str | None = None):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        self.db[cookie or "default"].extend(
            document.page_content
            for document in self.text_splitter.split_documents(documents)
        )
