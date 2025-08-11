from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest

from app.agents import CohereAgent, FakeAgent
from app.controller.controller import (
    add_content_into_db,
    query_agent,
    query_agent_with_stream_response,
)
from app.databases import ChromaDatabase, FakeDatabase
from app.interfaces.database import DatabaseManagerInterface

data_location = Path(__file__).parent.parent / "data"


@pytest.fixture(
    params=[FakeDatabase(), ChromaDatabase()], ids=["fake_database", "chroma_database"]
)
def vector_database(request) -> Generator[DatabaseManagerInterface]:
    database = request.param
    yield database
    database.empty_database()

@pytest.mark.asyncio
async def test_load_initial_documents__load_chunks_from_file_in_folder(vector_database):
    vector_database.load_documents_from_folder(data_location)

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

@pytest.mark.asyncio
@pytest.mark.parametrize("vector_database", [pytest.param(FakeDatabase(), id="fake_database")])
@pytest.mark.parametrize("ai_agent", [pytest.param(CohereAgent(), id="cohere_agent")])
async def test_controller__cohere_agent_avoid_answer_without_context(vector_database, ai_agent):
    response = await query_agent(vector_database, ai_agent, "What time is the capital of Belgium?")
    assert "sorry" in response.lower()
    assert "support@shop.com" in response.lower()


@pytest.mark.asyncio
@pytest.mark.parametrize("vector_database", [pytest.param(FakeDatabase(), id="fake_database")])
@pytest.mark.parametrize("ai_agent", [pytest.param(FakeAgent(), id="fake_agent")])
async def test_controller__can_stream_from_fake_agent(vector_database, ai_agent):
    streaming_response_generator = query_agent_with_stream_response(vector_database, ai_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) == 196
    assert response[0] == "Y"

@pytest.mark.skip("Using real agent")
@pytest.mark.asyncio
@pytest.mark.parametrize("vector_database", [pytest.param(ChromaDatabase(), id="chroma_database")])
@pytest.mark.parametrize("ai_agent", [pytest.param(CohereAgent(), id="cohere_agent")])
async def test_controller__can_stream_from_cohere_agent(vector_database, ai_agent):
    streaming_response_generator = query_agent_with_stream_response(vector_database, ai_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) > 20
