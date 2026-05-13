"""Chat UI components and handlers."""

import json

import httpx
from httpx_sse import aconnect_sse
from nicegui import ui
from nicegui.elements.scroll_area import ScrollArea

from app.ui.http_client import create_client
from app.ui.services.chat import ChatService, Message


def add_message_to_ui(
    messages_area: ui.column,
    message: Message,
) -> ui.label:
    """Add a message bubble to the chat UI."""
    is_user = message.role == "user"
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
                    msg_label = ui.label(message.content).classes(
                        f"px-4 py-2 rounded-2xl {bg_color} whitespace-pre-wrap"
                    )
                    ui.label(message.timestamp).classes("text-xs text-gray-400 px-2")

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
    """Thin UI handler that delegates business logic to ChatService."""

    def __init__(
        self,
        service: ChatService,
        messages_area: ui.column,
        chat_container: ScrollArea,
        input_field: ui.textarea,
        send_btn: ui.button,
    ):
        self.service = service
        self.messages_area = messages_area
        self.chat_container = chat_container
        self.input_field = input_field
        self.send_btn = send_btn
        self.is_loading = False

    def load_chat_history(self):
        """Load and display chat history from storage."""
        self.messages_area.clear()
        for message in self.service.get_or_create_history():
            add_message_to_ui(self.messages_area, message)

    async def send_message(self):
        """Send user message and get AI response."""
        question = self.input_field.value.strip()
        if not question or self.is_loading:
            return

        self.is_loading = True
        self.input_field.value = ""
        self.send_btn.disable()

        # Add user message (service handles storage)
        user_message = self.service.add_user_message(question)
        add_message_to_ui(self.messages_area, user_message)

        # Create placeholder for AI response
        ai_timestamp = self.service.create_pending_timestamp()
        response_label = create_ai_response_placeholder(
            self.messages_area, ai_timestamp
        )

        # Show loading indicator
        loading_spinner = ui.spinner("dots", size="lg").classes("text-blue-600")

        try:
            full_response = await stream_ai_response(
                question, response_label, self.chat_container
            )
            # Save AI response (service handles storage)
            self.service.add_assistant_message(full_response, ai_timestamp)

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
        self.service.clear_history()
        self.load_chat_history()
        ui.notify("Chat cleared", type="info")
