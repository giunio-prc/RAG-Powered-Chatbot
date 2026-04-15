import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents import FakeAgent
from app.api.dependencies import get_agent_from_state, get_db_from_state
from app.api.prompting import router
from app.databases import FakeDatabase


@pytest.fixture
def app_with_mocks(fake_database: FakeDatabase, fake_agent: FakeAgent) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[get_db_from_state] = lambda: fake_database
    app.dependency_overrides[get_agent_from_state] = lambda: fake_agent

    return app


@pytest.fixture
def client(app_with_mocks: FastAPI) -> TestClient:
    return TestClient(app_with_mocks)


def test_query_stream_endpoint_returns_sse_response(client: TestClient):
    response = client.post(
        "/query-stream",
        content='"What is the return policy?"',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    content = response.text
    assert "data:" in content

    # Verify SSE data contains expected words
    assert 'data: "You "' in content
    assert 'data: "asked "' in content
    assert 'data: "following "' in content
    assert 'data: "question:\\n "' in content
    assert 'data: "Unfortunately "' in content
    assert 'data: "fake "' in content
    assert 'data: "agent "' in content
