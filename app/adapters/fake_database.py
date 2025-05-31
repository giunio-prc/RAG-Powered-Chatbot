from app.interfaces import DatabaseManagerInterface


class FakeDatabase(DatabaseManagerInterface):
    def __init__(self):
        self.db = ["one", "two", "three"]

    def load_initial_documents(self, folder):
        self.db.extend["altro"]

    def add_chunks(self, chunks):
        self.db.extend(chunks)

    def get_context(self, question) -> str:
        return " ".join(self.db)
