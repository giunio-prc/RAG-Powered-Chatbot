from abc import ABC, abstractmethod
from os import PathLike
from typing import Any


class DatabaseManagerInterface(ABC):
    db: object

    @abstractmethod
    async def load_initial_documents(self, folder: PathLike):
        pass

    @abstractmethod
    async def add_chunks(self, chunks: list[Any]):
        pass

    @abstractmethod
    async def add_document(self, content: bytes):
        pass

    @abstractmethod
    async def get_context(self, question: str) -> str:
        pass

    @abstractmethod
    def get_chunks(self) -> list[str]:
        pass
