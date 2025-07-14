from abc import ABC, abstractmethod


class DatabaseManagerInterface(ABC):
    db: object
    text_splitter: object

    @abstractmethod
    def get_chunks(self) -> list[str]:
        pass

    @abstractmethod
    async def add_chunks(self, chunks: list[str]):
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

    @abstractmethod
    def empty_database(self):
        pass
