from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

from app.controller.controller import (
    add_content_into_db,
    query_agent_with_stream_response,
)
from tests.conftest import skip_due_to_cohere_api_key

data_location = Path(__file__).parent.parent / "data"



@pytest.mark.asyncio
async def test_load_initial_documents__load_chunks_from_file_in_folder(fake_database):
    fake_database.load_documents_from_folder(data_location)

    chunks = fake_database.get_chunks()

    assert len(chunks) == 18
    expected_content_chunk = (
        "Little Steps Baby Shop\nCustomer Q&A (Short Version)\n"
        + "Format: .txt\nLast updated: June 2025\n"
        + "1. Products and Safety"
    )

    assert expected_content_chunk in chunks


@pytest.mark.asyncio
async def test_add_content_into_db__adds_content_from_provided_file(fake_database):
    content = """
Can I modify or cancel my order after placing it?

A: Yes, but only within a short window.
If your order hasn't been packed or shipped yet,
you can contact customer service to modify or cancel it.
Once it's processed by our warehouse, changes are no longer possible.
In that case, you may return the item after delivery following our return policy.
"""
    await add_content_into_db(fake_database, content)

    chunks = fake_database.get_chunks()

    assert len(chunks) == 2
    expected_content_chunk = (
        "Can I modify or cancel my order after placing it?\n"
        + "A: Yes, but only within a short window.\n"
        + "If your order hasn't been packed or shipped yet,\n"
        + "you can contact customer service to modify or cancel it."
    )
    assert expected_content_chunk in chunks


@pytest.mark.asyncio
async def test_controller__can_stream_from_fake_agent(fake_database, fake_agent):
    streaming_response_generator = query_agent_with_stream_response(fake_database, fake_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) == 196
    assert response[0] == "Y"

@skip_due_to_cohere_api_key
@pytest.mark.asyncio
async def test_controller__can_stream_from_cohere_agent(chroma_database, cohere_agent):
    streaming_response_generator = query_agent_with_stream_response(chroma_database, cohere_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) > 20
