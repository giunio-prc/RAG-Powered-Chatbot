import os
from collections.abc import Generator

import pytest

from app.databases import FakeDatabase
from app.interfaces.database import DatabaseManagerInterface

skip_due_to_cohere_api_key = pytest.mark.skipif(
    "COHERE_API_KEY" not in os.environ,
    reason="COHERE_API_KEY required"
)

@pytest.fixture(
    params=[
        pytest.param("fake_database"),
        pytest.param("chroma_database", marks=skip_due_to_cohere_api_key)],
)
def vector_database(request) -> Generator[DatabaseManagerInterface]:
    param = request.param
    if param == "fakedatabase":
        database = FakeDatabase()
    elif param == "chromadatabase":
        # Lazy import to avoid import-time failures when COHERE_API_KEY is missing
        from app.databases import ChromaDatabase as _ChromaDatabase  # type: ignore
        database = _ChromaDatabase()
    else:
        raise ValueError(f"Unknown vector_database param: {param}")

    yield database

    database.empty_database()
