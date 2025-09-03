from abc import ABC, abstractmethod
from os import PathLike
from typing import AsyncGenerator, Generic, TypeVar

DB = TypeVar("DB")


class DatabaseManagerInterface(ABC, Generic[DB]):
    db: DB

    @abstractmethod
    def get_chunks(self, cookie: str | None = None) -> list[str]:
        pass

    @abstractmethod
    async def add_text_to_db(
        self, text: str, cookie: str | None = None
    ) -> AsyncGenerator[float, None]:
        pass

    @abstractmethod
    async def get_context(self, question: str, cookie: str | None = None) -> str:
        pass

    @abstractmethod
    def get_number_of_vectors(self, cookie: str | None = None) -> int:
        pass

    @abstractmethod
    def get_length_of_longest_vector(self, cookie: str | None = None) -> int:
        pass

    @abstractmethod
    def empty_database(self, cookie: str | None = None):
        pass

    @abstractmethod
    def load_documents_from_folder(self, folder: PathLike, cookie: str | None = None):
        pass
