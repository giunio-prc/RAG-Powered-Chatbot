import os
from collections.abc import Generator
from pathlib import Path

import pytest

from app.agents import CohereAgent, FakeAgent
from app.databases import ChromaDatabaseManager, FakeDatabaseManager

data_location = Path(__file__).parent / "data"


@pytest.fixture
def fake_database_manager() -> Generator[FakeDatabaseManager]:
    database_manager = FakeDatabaseManager()
    yield database_manager
    database_manager.empty_database()


@pytest.fixture
def chroma_database_manager() -> Generator[ChromaDatabaseManager]:
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
