"""Shared HTTP client utilities for NiceGUI pages."""

import httpx
from nicegui import context


def get_base_url() -> str:
    """Get the base URL for API calls from the current request context."""
    request = context.client.request
    return f"{request.url.scheme}://{request.url.netloc}"


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
