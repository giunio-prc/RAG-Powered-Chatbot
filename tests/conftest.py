import os
from collections.abc import Generator
from pathlib import Path

import pytest

from app.agents import CohereAgent, FakeAgent
from app.databases import ChromaDatabase, FakeDatabase

data_location = Path(__file__).parent / "data"

missing_cohere_key_in_env = "COHERE_API_KEY" not in os.environ

@pytest.fixture
def fake_database() -> Generator[FakeDatabase]:
    database = FakeDatabase()
    yield database
    database.empty_database()

@pytest.fixture
def chroma_database() -> Generator[ChromaDatabase]:
    if missing_cohere_key_in_env:
        pytest.skip()
    database = ChromaDatabase()
    yield database
    database.empty_database()

@pytest.fixture
def fake_agent() -> FakeAgent:
    agent = FakeAgent()
    return agent

@pytest.fixture
def cohere_agent() -> CohereAgent:
    if missing_cohere_key_in_env:
        pytest.skip()
    agent = CohereAgent()
    return agent
