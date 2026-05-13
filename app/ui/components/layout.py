"""Shared layout components for NiceGUI pages."""

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from loguru import logger
from nicegui import ui

from app.ui.http_client import create_client


def get_qr_code_path() -> Path | None:
    """Return the QR code path if configured and file exists."""
    qr_path = os.getenv("QR_CODE_PATH")
    logger.debug(f"QR_CODE_PATH env var: {qr_path}")
    if qr_path:
        path = Path(qr_path)
        logger.debug(f"QR code path resolved to: {path.absolute()}")
        if path.exists():
            logger.info(f"QR code file found: {path.absolute()}")
            return path
        else:
            logger.warning(f"QR code file not found: {path.absolute()}")
    else:
        logger.debug("QR_CODE_PATH env var not set")
    return None


async def get_agent_info() -> dict:
    """Fetch agent info from the API."""
    try:
        async with create_client() as client:
            response = await client.get("/agent-info")
            response.raise_for_status()
            return response.json()
    except Exception:
        # Default to production settings if API call fails
        return {
            "icon": "smart_toy",
            "label": "RAG Chatbot",
            "embedding_model": "Cohere",
        }


@asynccontextmanager
async def page_layout(active_page: Literal["chat", "documents"] = "chat"):
    """
    Shared page layout with navigation header and footer.

    Args:
        active_page: The currently active page for nav highlighting
    """
    # Fetch agent info for dynamic header
    agent_info = await get_agent_info()

    # Add Tailwind CSS and custom styles
    ui.add_head_html(
        "<link href='https://fonts.googleapis.com/css2"
        "?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>"
        "<style>"
        "body { font-family: 'Inter', sans-serif; }"
        ".chat-container { scrollbar-width: thin; }"
        ".chat-container::-webkit-scrollbar { width: 6px; }"
        ".chat-container::-webkit-scrollbar-thumb "
        "{ background-color: #cbd5e1; border-radius: 3px; }"
        ".qr-desktop { display: block; }"
        ".qr-mobile { display: none; }"
        "@media (max-width: 768px) {"
        ".qr-desktop { display: none; }"
        ".qr-mobile { display: flex; }"
        "}"
        "</style>"
    )

    # Header with navigation
    with ui.header().classes("bg-blue-600 text-white"):
        with ui.row().classes(
            "w-full max-w-6xl mx-auto items-center justify-between px-4"
        ):
            # Logo/Title
            with ui.row().classes("items-center gap-2"):
                ui.icon(agent_info["icon"]).classes("text-2xl")
                ui.label(agent_info["label"]).classes("text-xl font-semibold")

            # Navigation links
            with ui.row().classes("gap-1"):
                chat_classes = "px-4 py-2 rounded-lg font-medium transition-colors "
                chat_classes += (
                    "bg-blue-700" if active_page == "chat" else "hover:bg-blue-500"
                )
                ui.link("Chat", "/").classes(chat_classes).style(
                    "color: #ffffff; text-decoration: none"
                )

                docs_classes = "px-4 py-2 rounded-lg font-medium transition-colors "
                docs_classes += (
                    "bg-blue-700" if active_page == "documents" else "hover:bg-blue-500"
                )
                ui.link("Documents", "/documents").classes(docs_classes).style(
                    "color: #ffffff; text-decoration: none"
                )

    # Get QR code path once for both desktop and mobile versions
    qr_path = get_qr_code_path()

    # QR code overlay - fixed on desktop (hidden on mobile via media query)
    if qr_path:
        with ui.element("div").classes(
            "fixed bottom-16 right-4 z-50 bg-white rounded-xl shadow-xl p-3 qr-desktop"
        ):
            ui.image(str(qr_path)).classes("w-40 h-40")
            ui.label("Scan to connect").classes(
                "text-sm text-gray-600 text-center w-full mt-1 font-medium"
            )

    # Main content area
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 flex-grow"):
        yield agent_info

        # QR code inline for mobile - shown at bottom of content, scrollable
        if qr_path:
            with ui.column().classes(
                "w-full items-center mt-8 mb-4 bg-white "
                "rounded-xl shadow-lg p-4 qr-mobile"
            ):
                ui.image(str(qr_path)).classes("w-48 h-48")
                ui.label("Scan to connect").classes(
                    "text-base text-gray-600 text-center mt-2 font-medium"
                )

    # Footer
    with ui.footer().classes("bg-gray-100 border-t"):
        with ui.row().classes(
            "w-full max-w-6xl mx-auto items-center justify-between px-4 py-3"
        ):
            ui.label("RAG-Powered Chatbot").classes("text-gray-600 text-sm")
            with ui.row().classes("gap-4"):
                ui.link(
                    "GitHub",
                    "https://github.com/giunio-prc/rag-powered-chatbot",
                    new_tab=True,
                ).classes("text-gray-600 hover:text-blue-600 text-sm")
