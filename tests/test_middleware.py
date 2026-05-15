import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from app.middleware import SessionCookieMiddleware


@pytest.fixture
def app():
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[dict]:
        _ = app
        # Set up state similar to main app
        yield {"cookies": set()}

    test_app = FastAPI(lifespan=lifespan)
    test_app.add_middleware(SessionCookieMiddleware, cookie_name="TEST_SESSION")

    @test_app.get("/test")
    async def test_endpoint(request: Request):
        _ = request
        return {"message": "test"}

    return test_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


class TestSessionCookieMiddleware:
    def test_creates_new_session_when_no_cookie(self, client):
        """Test that middleware creates a new session when no cookie is present."""
        response = client.get("/test")

        assert response.status_code == 200
        assert "TEST_SESSION" in response.cookies

        session_id = response.cookies["TEST_SESSION"]
        # Verify it's a valid UUID
        uuid.UUID(session_id)

    def test_creates_new_session_when_invalid_cookie(self, client):
        """Test that middleware creates a new session when cookie is invalid."""
        # Send request with invalid session cookie
        response = client.get("/test", cookies={"TEST_SESSION": "invalid-session-id"})

        assert response.status_code == 200
        assert "TEST_SESSION" in response.cookies

        # Should get a new session ID (different from the invalid one)
        session_id = response.cookies["TEST_SESSION"]
        assert session_id != "invalid-session-id"
        uuid.UUID(session_id)  # Verify it's a valid UUID

    def test_reuses_existing_valid_session(self, client):
        """Test that middleware reuses an existing valid session."""
        # First request to establish a session
        first_response = client.get("/test")
        session_id = first_response.cookies["TEST_SESSION"]

        # Second request with the established session
        second_response = client.get("/test", cookies={"TEST_SESSION": session_id})

        assert second_response.status_code == 200
        # Should not set a new cookie since session is valid
        assert "TEST_SESSION" not in second_response.cookies

    def test_cookie_security_settings(self, client):
        """Test that cookies are set with proper security settings."""
        response = client.get("/test")

        # Check that cookie has httponly flag
        cookie_header = response.headers.get("set-cookie", "")
        assert "HttpOnly" in cookie_header
        assert "Max-Age" in cookie_header

    def test_concurrent_sessions(self, client):
        """Test that multiple sessions can be created and tracked."""
        # Create first session
        response1 = client.get("/test")
        session1 = response1.cookies["TEST_SESSION"]

        client.cookies.clear()  # Clear cookies to simulate a new client
        # Create second session (simulate different client)
        response2 = client.get("/test")
        session2 = response2.cookies["TEST_SESSION"]

        # Sessions should be different
        assert session1 != session2

        # Both should be valid UUIDs
        uuid.UUID(session1)
        uuid.UUID(session2)
