import pytest

from tests.conftest import data_location


def test_fake_database__returns_zero_length_of_longest_vector_when_empty(fake_database): # bugfix

    assert fake_database.get_length_of_longest_vector() == 0

@pytest.mark.asyncio
async def test_fake_database__can_return_context(fake_database):
    fake_database.load_documents_from_folder(data_location)

    context = await fake_database.get_context("What is the tracking method?")
    assert "Tracking provided via email." in context
