from tests.conftest import data_location


def test_fake_database__returns_zero_length_of_longest_vector_when_empty(
    fake_database_manager,
):  # bugfix
    assert fake_database_manager.get_length_of_longest_vector() == 0


async def test_fake_database__can_return_context(fake_database_manager):
    fake_database_manager.load_documents_from_folder(data_location)

    context = await fake_database_manager.get_context("What is the tracking method?")
    assert "Tracking provided via email." in context
