from pathlib import Path
from typing import Generator

import pytest

from app.adapters.chroma_database import ChromaDataBase
from app.adapters.fake_database import FakeDatabase
from app.controller.controller import add_content_into_db, load_initial_documents
from app.interfaces.database import DatabaseManagerInterface


@pytest.fixture(
    params=[FakeDatabase(), ChromaDataBase()], ids=["fake_database", "chroma_database"]
)
def vector_database(request) -> Generator[DatabaseManagerInterface, None, None]:
    database = request.param
    yield database
    database.empty_database()


data_location = Path(__file__).parent.parent / "data"


@pytest.mark.asyncio
async def test_load_initial_documents__load_chunks_from_file_in_folder(vector_database):
    await load_initial_documents(vector_database, data_location)
    chunks = vector_database.get_chunks()

    assert len(chunks) == 18
    expected_content_chunk = (
        "Little Steps Baby Shop\nCustomer Q&A (Short Version)\n"
        + "Format: .txt\nLast updated: June 2025\n"
        + "1. Products and Safety"
    )

    assert expected_content_chunk in chunks


@pytest.mark.asyncio
async def test_add_content_into_db__adds_content_from_provided_file(vector_database):
    content = """
Can I modify or cancel my order after placing it?

A: Yes, but only within a short window.
If your order hasn't been packed or shipped yet,
you can contact customer service to modify or cancel it.
Once it's processed by our warehouse, changes are no longer possible.
In that case, you may return the item after delivery following our return policy.
"""
    await add_content_into_db(vector_database, content)

    chunks = vector_database.get_chunks()

    assert len(chunks) == 2
    expected_content_chunk = (
        "Can I modify or cancel my order after placing it?\n"
        + "A: Yes, but only within a short window.\n"
        + "If your order hasn't been packed or shipped yet,\n"
        + "you can contact customer service to modify or cancel it."
    )
    assert expected_content_chunk in chunks
