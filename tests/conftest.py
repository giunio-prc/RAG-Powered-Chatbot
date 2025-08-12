import os
from collections.abc import Generator

import pytest

from app.agents.fake_agent import FakeAgent
from app.databases.fake_database import FakeDatabase

skip_due_to_cohere_api_key = pytest.mark.skipif(
    "COHERE_API_KEY" not in os.environ,
    reason="COHERE_API_KEY required"
)

@pytest.fixture
def fake_database() -> Generator[FakeDatabase]:
    database = FakeDatabase()
    yield database
    database.empty_database()

@pytest.fixture
def chroma_database() -> Generator["_ChromaDatabase"]:
    from app.databases import ChromaDatabase as _ChromaDatabase  # type: ignore
    database = _ChromaDatabase()
    yield database
    database.empty_database()

@pytest.fixture
def fake_agent() -> FakeAgent:
    agent = FakeAgent()
    return agent

@pytest.fixture
def cohere_agent() -> "_CohereAgent":
    from app.agents import CohereAgent as _CohereAgent  # type: ignore
    agent = _CohereAgent()
    return agent
