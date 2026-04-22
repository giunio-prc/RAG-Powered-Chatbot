"""NiceGUI page definitions."""

from app.ui.pages.chat import chat_page
from app.ui.pages.documents import documents_page


def setup_pages() -> None:
    """Register all NiceGUI pages. Must be called before ui.run_with()."""
    # Pages are registered via @ui.page decorator when modules are imported
    # This function ensures the modules are loaded
    _ = chat_page
    _ = documents_page


__all__ = ["setup_pages", "chat_page", "documents_page"]
