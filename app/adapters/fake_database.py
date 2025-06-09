from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    db: list[str]

    def __init__(self):
        self.db = ["one", "two", "three"]

    async def load_initial_documents(self, folder):
        self.db.extend["altro"]

    async def add_chunks(self, chunks):
        self.db.extend(chunks)

    async def get_context(self, question) -> str:
        return " ".join(self.db)
