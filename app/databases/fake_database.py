from difflib import get_close_matches
from os import PathLike

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: list[str]

    text_splitter: CharacterTextSplitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=0, separator="\n"
    )

    def __init__(self):
        self.db = []

    async def get_context(self, question) -> str:

        context = get_close_matches(question, self.db, n=1, cutoff=0.1 )
        return "\n\n".join(context) if context else "there is no context, you are not allowed to answer"

    async def add_text_to_db(self, text: str):
        chunks = self.text_splitter.split_text(text)
        self.db.extend(chunks)

    def get_chunks(self) -> list[str]:
        return self.db

    def get_number_of_vectors(self) -> int:
        return len(self.db)

    def get_length_of_longest_vector(self) -> int:
        if not self.db:
            return 0
        return len(max(self.db, key=len))

    def empty_database(self):
        self.db = []

    def load_documents_from_folder(self, folder: PathLike):
        documents = DirectoryLoader(str(folder), "*.txt").load()
        self.db.extend(
            document.page_content
            for document in self.text_splitter.split_documents(documents)
        )
