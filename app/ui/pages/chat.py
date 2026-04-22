"""Chat page implementation using NiceGUI."""

import json
from datetime import datetime

import httpx
from nicegui import app, context, ui

from app.ui.components.layout import page_layout


def format_time(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%I:%M %p")


@ui.page("/")
async def chat_page():
    """Chat interface page."""

    # Get base URL for API calls
    request = context.client.request
    base_url = f"{request.url.scheme}://{request.url.netloc}"

    # Initialize session storage for chat history
    if "chat_history" not in app.storage.user:
        app.storage.user["chat_history"] = []

    # State variables
    is_loading = {"value": False}

    with page_layout(active_page="chat"):
        # Chat header
        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.label("Chat with AI Assistant").classes(
                "text-2xl font-bold text-gray-800"
            )
            clear_btn = ui.button("Clear Chat", icon="delete").classes(
                "bg-red-500 hover:bg-red-600 text-white"
            )

        # Chat container
        with (
            ui.column()
            .classes(
                "w-full bg-white rounded-xl shadow-lg border border-gray-200 p-4 "
                "chat-container overflow-y-auto"
            )
            .style("height: 500px")
        ):
            # Message display area
            messages_area = ui.column().classes("w-full gap-4")

        def add_message_to_ui(role: str, content: str, timestamp: str | None = None):
            """Add a message bubble to the chat UI."""
            if timestamp is None:
                timestamp = format_time(datetime.now())

            is_user = role == "user"
            alignment = "items-end" if is_user else "items-start"
            bg_color = (
                "bg-blue-600 text-white" if is_user else "bg-gray-100 text-gray-800"
            )
            avatar_icon = "person" if is_user else "smart_toy"
            avatar_bg = (
                "bg-blue-100 text-blue-600"
                if is_user
                else "bg-green-100 text-green-600"
            )

            with messages_area:
                with ui.column().classes(f"w-full {alignment}"):
                    with ui.row().classes(
                        "items-end gap-2 max-w-3xl"
                        + (" flex-row-reverse" if is_user else "")
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

        def load_chat_history():
            """Load and display chat history from storage."""
            messages_area.clear()
            history = app.storage.user.get("chat_history", [])

            if not history:
                # Show welcome message
                add_message_to_ui(
                    "assistant",
                    "Hello! I'm your AI assistant powered by RAG technology. "
                    "I can answer questions based on the documents you've uploaded. "
                    "How can I help you today?",
                    format_time(datetime.now()),
                )
            else:
                for msg in history:
                    add_message_to_ui(msg["role"], msg["content"], msg.get("timestamp"))

        async def send_message():
            """Send user message and get AI response."""
            question = input_field.value.strip()
            if not question or is_loading["value"]:
                return

            is_loading["value"] = True
            input_field.value = ""
            send_btn.disable()

            # Add user message
            timestamp = format_time(datetime.now())
            add_message_to_ui("user", question, timestamp)

            # Save to history
            history = app.storage.user.get("chat_history", [])
            history.append(
                {"role": "user", "content": question, "timestamp": timestamp}
            )

            # Create placeholder for AI response
            ai_timestamp = format_time(datetime.now())

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
                                "px-4 py-2 rounded-2xl bg-gray-100 text-gray-800 whitespace-pre-wrap"
                            )
                            ui.label(ai_timestamp).classes("text-xs text-gray-400 px-2")

            # Show loading indicator
            loading_spinner = ui.spinner("dots", size="lg").classes("text-blue-600")

            try:
                # Stream the response from API endpoint
                full_response = ""
                async with httpx.AsyncClient() as client:
                    async with client.stream(
                        "POST",
                        f"{base_url}/query-stream",
                        json=question,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        async for line in response.aiter_lines():
                            # SSE format: "data: <json-encoded-content>"
                            if line.startswith("data: "):
                                chunk_data = line[6:]
                                try:
                                    chunk = json.loads(chunk_data)
                                except json.JSONDecodeError:
                                    chunk = chunk_data
                                full_response += chunk
                                response_label.set_text(full_response)
                                await ui.run_javascript(
                                    "window.scrollTo(0, document.body.scrollHeight)"
                                )

                # Save AI response to history
                history.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "timestamp": ai_timestamp,
                    }
                )
                app.storage.user["chat_history"] = history

            except Exception as e:
                response_label.set_text(f"Error: {e!s}")
                ui.notify(f"Error: {e!s}", type="negative")

            finally:
                is_loading["value"] = False
                send_btn.enable()
                loading_spinner.delete()

        async def clear_chat():
            """Clear chat history."""
            app.storage.user["chat_history"] = []
            load_chat_history()
            ui.notify("Chat cleared", type="info")

        # Load existing chat history
        load_chat_history()

        # Input area
        with ui.row().classes("w-full gap-2 mt-4"):
            input_field = (
                ui.textarea(placeholder="Type your message here...")
                .classes("flex-grow")
                .props("outlined autogrow rows=1")
            )
            send_btn = ui.button("Send", icon="send", on_click=send_message).classes(
                "bg-blue-600 hover:bg-blue-700 text-white"
            )

        # Handle Enter key (without Shift) to send
        input_field.on(
            "keydown.enter",
            lambda e: send_message() if not e.args.get("shiftKey", False) else None,
        )

        # Clear button handler
        clear_btn.on_click(clear_chat)

        # Info banner
        with ui.card().classes("w-full mt-4 bg-blue-50 border-blue-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("info").classes("text-blue-600")
                ui.label(
                    "This chatbot uses RAG (Retrieval-Augmented Generation) technology. "
                    "Upload documents in the Documents section to provide context for more accurate answers."
                ).classes("text-sm text-blue-800")
