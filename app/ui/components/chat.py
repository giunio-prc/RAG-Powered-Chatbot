"""Chat UI components and handlers."""

import json
from datetime import datetime

import httpx
from httpx_sse import aconnect_sse
from nicegui import ui
from nicegui.elements.scroll_area import ScrollArea

from app.ui.http_client import create_client
from app.ui.utils import format_time


def add_message_to_ui(
    messages_area: ui.column,
    role: str,
    content: str,
    timestamp: str | None = None,
) -> ui.label:
    """Add a message bubble to the chat UI."""
    if timestamp is None:
        timestamp = format_time(datetime.now())

    is_user = role == "user"
    alignment = "items-end" if is_user else "items-start"
    bg_color = "bg-blue-600 text-white" if is_user else "bg-gray-100 text-gray-800"
    avatar_icon = "person" if is_user else "smart_toy"
    avatar_bg = (
        "bg-blue-100 text-blue-600" if is_user else "bg-green-100 text-green-600"
    )

    with messages_area:
        with ui.column().classes(f"w-full {alignment}"):
            with ui.row().classes(
                "items-end gap-2 max-w-3xl" + (" flex-row-reverse" if is_user else "")
            ):
                # Avatar
                with ui.element("div").classes(
                    f"w-8 h-8 rounded-full flex items-center justify-center {avatar_bg}"
                ):
                    ui.icon(avatar_icon).classes("text-sm")
                # Message bubble
                with ui.column().classes("gap-1"):
                    msg_label = ui.label(content).classes(
                        f"px-4 py-2 rounded-2xl {bg_color} whitespace-pre-wrap"
                    )
                    ui.label(timestamp).classes("text-xs text-gray-400 px-2")

    return msg_label


def create_ai_response_placeholder(
    messages_area: ui.column,
    ai_timestamp: str,
) -> ui.label:
    """Create a placeholder for AI response with avatar."""
    with messages_area:
        with ui.column().classes("w-full items-start"):
            with ui.row().classes("items-end gap-2 max-w-3xl"):
                # Avatar
                with ui.element("div").classes(
                    "w-8 h-8 rounded-full flex items-center justify-center "
                    "bg-green-100 text-green-600"
                ):
                    ui.icon("smart_toy").classes("text-sm")
                # Message bubble
                with ui.column().classes("gap-1"):
                    response_label = ui.label("").classes(
                        "px-4 py-2 rounded-2xl bg-gray-100 "
                        "text-gray-800 whitespace-pre-wrap"
                    )
                    ui.label(ai_timestamp).classes("text-xs text-gray-400 px-2")

    return response_label


async def stream_ai_response(
    question: str,
    response_label: ui.label,
    chat_container: ScrollArea,
) -> str:
    """Stream AI response from the API and return the full response."""
    full_response = ""
    async with create_client() as client:
        async with aconnect_sse(
            client, "POST", "/query-stream", json=question
        ) as event_source:
            async for sse in event_source.aiter_sse():
                try:
                    chunk = json.loads(sse.data)
                except json.JSONDecodeError:
                    chunk = sse.data
                full_response += chunk
                response_label.set_text(full_response)
                chat_container.scroll_to(percent=1.01)

    return full_response


class ChatHandler:
    """Handles chat message sending and history management."""

    def __init__(
        self,
        storage: dict,
        messages_area: ui.column,
        chat_container: ScrollArea,
        input_field: ui.textarea,
        send_btn: ui.button,
    ):
        self.storage = storage
        self.messages_area = messages_area
        self.chat_container = chat_container
        self.input_field = input_field
        self.send_btn = send_btn
        self.is_loading = False

    def load_chat_history(self):
        """Load and display chat history from storage."""
        self.messages_area.clear()
        history = self.storage.get("chat_history", [])

        if not history:
            # Show and save welcome message
            welcome_timestamp = format_time(datetime.now())
            welcome_content = (
                "Hello! I'm your AI assistant powered by RAG technology. "
                "I can answer questions based on the documents you've uploaded. "
                "How can I help you today?"
            )
            add_message_to_ui(
                self.messages_area, "assistant", welcome_content, welcome_timestamp
            )
            self.storage["chat_history"] = [
                {
                    "role": "assistant",
                    "content": welcome_content,
                    "timestamp": welcome_timestamp,
                }
            ]
        else:
            for msg in history:
                add_message_to_ui(
                    self.messages_area,
                    msg["role"],
                    msg["content"],
                    msg.get("timestamp"),
                )

    async def send_message(self):
        """Send user message and get AI response."""
        question = self.input_field.value.strip()
        if not question or self.is_loading:
            return

        self.is_loading = True
        self.input_field.value = ""
        self.send_btn.disable()

        # Add user message
        timestamp = format_time(datetime.now())
        add_message_to_ui(self.messages_area, "user", question, timestamp)

        # Save user message to history immediately
        history = self.storage.get("chat_history", [])
        history.append({"role": "user", "content": question, "timestamp": timestamp})
        self.storage["chat_history"] = history

        # Create placeholder for AI response
        ai_timestamp = format_time(datetime.now())
        response_label = create_ai_response_placeholder(
            self.messages_area, ai_timestamp
        )

        # Show loading indicator
        loading_spinner = ui.spinner("dots", size="lg").classes("text-blue-600")

        try:
            full_response = await stream_ai_response(
                question, response_label, self.chat_container
            )

            # Save AI response to history
            history = self.storage.get("chat_history", [])
            history.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": ai_timestamp,
                }
            )
            self.storage["chat_history"] = history
        except httpx.HTTPError as e:
            response_label.set_text(f"Error: {e!s}")
            ui.notify(f"Error: {e!s}", type="negative")

        finally:
            self.is_loading = False
            self.send_btn.enable()
            loading_spinner.delete()
            self.chat_container.scroll_to(percent=1.1)

    async def clear_chat(self):
        """Clear chat history."""
        self.storage["chat_history"] = []
        self.load_chat_history()
        ui.notify("Chat cleared", type="info")
