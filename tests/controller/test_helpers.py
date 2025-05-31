import pytest

from app.controller.helpers import chunk_document


@pytest.fixture
def document():
    return """
Lorem Ipsum
"""


def test_a_document__can_be_reduced_in_chunks(document):
    chunks = chunk_document(document)
    assert False
