"""Shared HTTP client utilities for NiceGUI pages."""

import httpx
from nicegui import context


def get_base_url() -> str:
    """Get the base URL for API calls from the current request context."""
    request = context.client.request
    return f"{request.url.scheme}://{request.url.netloc}"


def create_client() -> httpx.AsyncClient:
    """Create an httpx AsyncClient configured with the base URL.

    Usage:
        async with create_client() as client:
            response = await client.get("/endpoint")
    """
    return httpx.AsyncClient(base_url=get_base_url())
