from abc import ABC, abstractmethod
from typing import Any

from langchain.text_splitter import TextSplitter


class DatabaseManagerInterface(ABC):
    db: object
    text_splitter: TextSplitter

    @abstractmethod
    def get_chunks(self) -> list[Any]:
        pass

    @abstractmethod
    async def add_chunks(self, chunks: list[Any]):
        pass

    @abstractmethod
    async def add_text_to_db(self, text: str):
        pass

    @abstractmethod
    async def get_context(self, question: str) -> str:
        pass

    @abstractmethod
    def get_number_of_vectors(self) -> int:
        pass

    @abstractmethod
    def get_length_of_longest_vector(self) -> int:
        pass
