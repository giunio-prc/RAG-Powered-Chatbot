"""Chat page implementation using NiceGUI."""

from nicegui import app, ui

from app.ui.components.chat import ChatHandler
from app.ui.components.layout import page_layout


@ui.page("/", favicon="static/favicon.svg", title="RAG Chatbot")
async def chat_page():
    """Chat interface page."""
    # Use user storage for chat history (server-side, persists across navigation)
    storage = app.storage.user
    if "chat_history" not in storage:
        storage["chat_history"] = []

    async with page_layout(active_page="chat"):
        # Chat header
        with ui.row().classes("w-full items-center justify-between mb-4"):
            ui.label("Chat with AI Assistant").classes(
                "text-2xl font-bold text-gray-800"
            )
            clear_btn = ui.button("Clear Chat", icon="delete").props(
                "unelevated color=red"
            )

        # Chat container
        with ui.card().classes(
            "w-full bg-white rounded-xl shadow-lg border border-gray-200"
        ):
            chat_container = ui.scroll_area().classes("p-4").style("height: 500px")
            with chat_container:
                messages_area = ui.column().classes("w-full gap-4")

        # Input area
        with ui.row().classes("w-full gap-2 mt-4"):
            input_field = (
                ui.textarea(placeholder="Type your message here...")
                .classes("flex-grow")
                .props("outlined autogrow rows=1")
            )
            send_btn = ui.button("Send", icon="send").props("unelevated color=primary")

        # Create chat handler
        chat_handler = ChatHandler(
            storage=storage,
            messages_area=messages_area,
            chat_container=chat_container,
            input_field=input_field,
            send_btn=send_btn,
        )

        # Wire up event handlers
        send_btn.on_click(chat_handler.send_message)
        clear_btn.on_click(chat_handler.clear_chat)

        # Handle Enter key (without Shift) to send, Shift+Enter for new line
        input_field.on(
            "keydown.enter.prevent",
            lambda e: (
                chat_handler.send_message()
                if not e.args.get("shiftKey", False)
                else None
            ),
        )
        input_field.on(
            "keydown.shift.enter",
            lambda: input_field.set_value(input_field.value + "\n"),
        )

        # Load existing chat history after the page is fully connected
        ui.timer(0.1, chat_handler.load_chat_history, once=True)

        # Info banner
        with ui.card().classes("w-full mt-4 bg-blue-50 border-blue-200"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("info").classes("text-blue-600")
                ui.label(
                    "This chatbot uses RAG (Retrieval-Augmented Generation) "
                    "technology. Upload documents in the Documents section "
                    "to provide context for more accurate answers."
                ).classes("text-sm text-blue-800")
