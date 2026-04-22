"""Shared layout components for NiceGUI pages."""

from contextlib import contextmanager
from typing import Literal

from nicegui import ui


@contextmanager
def page_layout(active_page: Literal["chat", "documents"] = "chat"):
    """
    Shared page layout with navigation header and footer.

    Args:
        active_page: The currently active page for nav highlighting
    """
    # Add Tailwind CSS and custom styles
    ui.add_head_html("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; }
            .chat-container { scrollbar-width: thin; }
            .chat-container::-webkit-scrollbar { width: 6px; }
            .chat-container::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 3px; }
        </style>
    """)

    # Header with navigation
    with ui.header().classes("bg-blue-600 text-white shadow-lg"):
        with ui.row().classes(
            "w-full max-w-6xl mx-auto items-center justify-between px-4"
        ):
            # Logo/Title
            with ui.row().classes("items-center gap-2"):
                ui.icon("smart_toy").classes("text-2xl")
                ui.label("RAG Chatbot").classes("text-xl font-semibold")

            # Navigation links
            with ui.row().classes("gap-1"):
                chat_classes = "px-4 py-2 rounded-lg font-medium transition-colors "
                chat_classes += (
                    "bg-blue-700" if active_page == "chat" else "hover:bg-blue-500"
                )
                ui.link("Chat", "/").classes(chat_classes)

                docs_classes = "px-4 py-2 rounded-lg font-medium transition-colors "
                docs_classes += (
                    "bg-blue-700" if active_page == "documents" else "hover:bg-blue-500"
                )
                ui.link("Documents", "/documents").classes(docs_classes)

    # Main content area
    with ui.column().classes("w-full max-w-6xl mx-auto p-4 flex-grow"):
        yield

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
