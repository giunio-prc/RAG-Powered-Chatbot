import os
from collections.abc import Generator

import pytest

from app.agents.fake_agent import FakeAgent
from app.databases.fake_database import FakeDatabase

missing_cohere_key_in_env = "COHERE_API_KEY" not in os.environ,

skip_due_to_cohere_api_key = pytest.mark.skipif(
    missing_cohere_key_in_env,
    reason="COHERE_API_KEY required"
)

@pytest.fixture
def fake_database() -> Generator[FakeDatabase]:
    database = FakeDatabase()
    yield database
    database.empty_database()

@pytest.fixture
@skip_due_to_cohere_api_key
def chroma_database() -> Generator["_ChromaDatabase"]:
    if missing_cohere_key_in_env:
        pytest.skip()
    from app.databases import ChromaDatabase as _ChromaDatabase  # type: ignore
    database = _ChromaDatabase()
    yield database
    database.empty_database()

@pytest.fixture
def fake_agent() -> FakeAgent:
    agent = FakeAgent()
    return agent

@pytest.fixture
@skip_due_to_cohere_api_key
def cohere_agent() -> "_CohereAgent":
    if missing_cohere_key_in_env:
        pytest.skip()
    from app.agents import CohereAgent as _CohereAgent  # type: ignore
    agent = _CohereAgent()
    return agent
