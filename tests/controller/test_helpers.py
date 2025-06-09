import pytest

from app.controller.helpers import chunk_document


@pytest.fixture
def paragraph(faker):
    return faker.paragraph(nb_sentences=10)


def test_a_document__can_be_reduced_in_chunks(paragraph):
    chunks = chunk_document(paragraph)
    assert False
