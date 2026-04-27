import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents import FakeAgent
from app.api.database import router as database_router
from app.api.dependencies import get_agent_from_state, get_db_from_state
from app.api.prompting import router as prompting_router
from app.databases import FakeDatabase


@pytest.fixture
def app_with_mocks(fake_database: FakeDatabase, fake_agent: FakeAgent) -> FastAPI:
    app = FastAPI()
    app.include_router(database_router)
    app.include_router(prompting_router)

    app.dependency_overrides[get_db_from_state] = lambda: fake_database
    app.dependency_overrides[get_agent_from_state] = lambda: fake_agent

    return app


@pytest.fixture
def client(app_with_mocks: FastAPI) -> TestClient:
    return TestClient(app_with_mocks, cookies={"SESSION": "test-session"})
