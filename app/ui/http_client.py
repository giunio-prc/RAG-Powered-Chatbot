"""Shared HTTP client utilities for NiceGUI pages."""

import os

import httpx
from nicegui import context


def get_base_url() -> str:
    port = os.getenv("PORT", "8000")
    return f"http://127.0.0.1:{port}"


def get_session_cookie() -> dict[str, str]:
    """Extract the SESSION cookie from the current request context."""
    request = context.client.request
    session_cookie = request.cookies.get("SESSION")
    if session_cookie:
        return {"SESSION": session_cookie}
    return {}


def create_client() -> httpx.AsyncClient:
    """Create an httpx AsyncClient configured with the base URL and session cookie.

    Forwards the SESSION cookie from the browser request to maintain session
    consistency with the API endpoints.

    Usage:
        async with create_client() as client:
            response = await client.get("/endpoint")
    """
    return httpx.AsyncClient(
        base_url=get_base_url(),
        cookies=get_session_cookie(),
    )
