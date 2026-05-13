import os
from collections.abc import Generator
from pathlib import Path

import pytest

from app.agents import CohereAgent, FakeAgent
from app.databases import ChromaDatabaseManager, FakeDatabaseManager

data_location = Path(__file__).parent / "data"


@pytest.fixture
def fake_database() -> Generator[FakeDatabaseManager]:
    database = FakeDatabaseManager()
    yield database
    database.empty_database()


@pytest.fixture
def chroma_database() -> Generator[ChromaDatabaseManager]:
    if "COHERE_API_KEY" not in os.environ:
        pytest.skip()
    database = ChromaDatabaseManager()
    yield database
    database.empty_database()


@pytest.fixture
def fake_agent() -> FakeAgent:
    agent = FakeAgent()
    return agent


@pytest.fixture
def cohere_agent() -> CohereAgent:
    if "COHERE_API_KEY" not in os.environ:
        pytest.skip()
    agent = CohereAgent()
    return agent
