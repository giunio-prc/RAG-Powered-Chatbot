from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from os import PathLike


class DatabaseManagerInterface[DB](ABC):
    db: DB

    @abstractmethod
    def get_chunks(self, cookie: str | None = None) -> list[str]:
        """Return all chunks stored in the database."""

    @abstractmethod
    def add_text_to_db(  # ty workaround
        self, text: str, cookie: str | None = None
    ) -> AsyncGenerator[float, None]:
        """Add text to the database, yielding progress percentage."""

    @abstractmethod
    async def get_context(self, question: str, cookie: str | None = None) -> str:
        """Retrieve relevant context for a question."""

    @abstractmethod
    def get_number_of_vectors(self, cookie: str | None = None) -> int:
        """Return the number of vectors in the database."""

    @abstractmethod
    def get_length_of_longest_vector(self, cookie: str | None = None) -> int:
        """Return the length of the longest vector."""

    @abstractmethod
    def empty_database(self, cookie: str | None = None):
        """Clear all data from the database."""

    @abstractmethod
    def load_documents_from_folder(self, folder: PathLike, cookie: str | None = None):
        """Load documents from a folder into the database."""
