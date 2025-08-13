from collections.abc import AsyncGenerator

import pytest

from app.controller.controller import (
    add_content_into_db,
    query_agent_with_stream_response,
)
from tests.conftest import data_location


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
async def test_add_content_into_db__streams_progress_updates(fake_database):
    content = """
First chunk of content that should be split.
This is line 2.

Second chunk of content starts here.
This is another line.
This should be split into multiple chunks.

Third chunk starts here with more content.
"""

    progress_updates = []
    async for progress_str in add_content_into_db(fake_database, content):
        # Verify each progress update is a string with newline
        assert isinstance(progress_str, str)
        assert progress_str.endswith("\n")

        # Parse the progress value
        progress = float(progress_str.strip())
        progress_updates.append(progress)

        # Verify progress is between 0 and 100
        assert 0 < progress <= 100

    # Verify we got multiple progress updates
    assert len(progress_updates) > 1

    # Verify progress increases monotonically
    for i in range(1, len(progress_updates)):
        assert progress_updates[i] > progress_updates[i-1]

    # Verify final progress is 100%
    assert progress_updates[-1] == 100.0

    # Verify content was actually added to database
    chunks = fake_database.get_chunks()
    assert len(chunks) > 0


@pytest.mark.asyncio
async def test_controller__can_stream_from_fake_agent(fake_database, fake_agent):
    streaming_response_generator = query_agent_with_stream_response(fake_database, fake_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) == 196
    assert response[0] == "Y"

@pytest.mark.asyncio
async def test_controller__can_stream_from_cohere_agent(chroma_database, cohere_agent):
    streaming_response_generator = query_agent_with_stream_response(chroma_database, cohere_agent, "What time is it?")
    assert isinstance(streaming_response_generator, AsyncGenerator)
    response = [chunk async for chunk in streaming_response_generator]
    assert len(response) > 20
