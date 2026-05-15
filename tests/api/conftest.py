from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware

from app.agents import FakeAgent
from app.api.database import router as database_router
from app.api.dependencies import (
    get_agent_from_state,
    get_cookie_session,
    get_db_from_state,
)
from app.api.prompting import router as prompting_router
from app.databases import FakeDatabaseManager

TEST_SECRET = "test-secret"


@pytest.fixture
def app_with_mocks(
    fake_database_manager: FakeDatabaseManager, fake_agent: FakeAgent
) -> FastAPI:
    app = FastAPI()
    app.include_router(database_router)
    app.include_router(prompting_router)

    app.dependency_overrides[get_db_from_state] = lambda: fake_database_manager
    app.dependency_overrides[get_agent_from_state] = lambda: fake_agent

    app.add_middleware(SessionMiddleware, secret_key=TEST_SECRET)

    @app.get("/cookie")
    async def _get_cookie_session_endpoint(
        cookie_session: Annotated[str, Depends(get_cookie_session)],
    ) -> str:
        return cookie_session

    return app


@pytest.fixture
def client(app_with_mocks: FastAPI) -> TestClient:
    return TestClient(app_with_mocks)
