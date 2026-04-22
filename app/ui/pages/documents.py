"""Documents page implementation using NiceGUI."""

from datetime import datetime

from nicegui import app, ui
from nicegui.events import UploadEventArguments

from app.ui.components.layout import page_layout
from app.ui.http_client import create_client
from app.ui.utils import format_time


def format_number(num: int) -> str:
    """Format number with locale-aware separators."""
    return f"{num:,}"


@ui.page("/documents", favicon="static/favicon.svg", title="RAG Chatbot - Documents")
async def documents_page():
    """Document management page."""

    # Use browser local storage
    storage = app.storage.browser

    with page_layout(active_page="documents"):
        ui.label("Document Management").classes("text-2xl font-bold text-gray-800 mb-4")

        with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
            # Left column - Upload
            with ui.column().classes("flex-1 min-w-80"):
                with ui.card().classes("w-full"):
                    ui.label("Upload Documents").classes("text-lg font-semibold mb-4")

                    # Upload area
                    upload_status = ui.label("").classes("text-sm text-gray-600 mb-2")
                    progress_bar = ui.linear_progress(
                        value=0, show_value=False
                    ).classes("w-full mb-2")
                    progress_bar.visible = False

                    async def handle_upload(e: UploadEventArguments):
                        """Handle file upload."""

                        filename = e.file.name
                        try:
                            content = await e.file.text()
                        except UnicodeDecodeError:
                            ui.notify(
                                f"Invalid encoding: {filename}. UTF-8 is required.",
                                type="negative",
                            )
                            return
                        # Validate file type
                        if not filename.endswith(".txt"):
                            ui.notify(
                                f"Invalid file type: {filename}. Only .txt files allowed.",
                                type="negative",
                            )
                            return

                        # Show progress
                        progress_bar.visible = True
                        progress_bar.set_value(0)
                        upload_status.set_text(f"Uploading {filename}...")

                        try:
                            # Upload via API endpoint
                            async with create_client() as client:
                                async with client.stream(
                                    "POST",
                                    "/add-document",
                                    files={
                                        "file": (
                                            filename,
                                            content,
                                            "text/plain",
                                        )
                                    },
                                ) as response:
                                    async for line in response.aiter_lines():
                                        progress_text = line.strip()
                                        if progress_text == "API_LIMIT_EXCEEDED":
                                            ui.notify(
                                                "API limit exceeded. Please try again later.",
                                                type="warning",
                                            )
                                            return
                                        try:
                                            pct = int(progress_text)
                                            progress_bar.set_value(pct / 100)
                                            upload_status.set_text(
                                                f"Processing {filename}: {pct}%"
                                            )
                                        except ValueError:
                                            pass

                            # Success
                            progress_bar.set_value(1)
                            upload_status.set_text(f"Uploaded: {filename}")
                            ui.notify(
                                f"Successfully uploaded {filename}",
                                type="positive",
                            )

                            # Add to recent activity
                            add_activity(f"Uploaded: {filename}")

                            # Refresh stats
                            await refresh_stats()

                        except Exception as ex:
                            ui.notify(f"Upload failed: {ex!s}", type="negative")
                            upload_status.set_text(f"Failed: {filename}")

                        finally:
                            progress_bar.visible = False

                    ui.upload(
                        label="Drop files here or click to browse",
                        on_upload=handle_upload,
                        auto_upload=True,
                        multiple=False,
                        max_file_size=10 * 1024 * 1024,
                    ).classes("w-full").props('accept=".txt" flat bordered')

                    # File requirements info
                    with ui.card().classes("w-full mt-4 bg-gray-50"):
                        ui.label("File Requirements").classes(
                            "font-medium text-sm mb-2"
                        )
                        with ui.column().classes("gap-1 text-xs text-gray-600"):
                            ui.label("- Text files only (.txt)")
                            ui.label("- Maximum file size: 10MB")
                            ui.label("- UTF-8 encoding required")

            # Right column - Stats
            with ui.column().classes("flex-1 min-w-80"):
                # Statistics card
                with ui.card().classes("w-full"):
                    with ui.row().classes("items-center justify-between mb-4"):
                        ui.label("Database Statistics").classes("text-lg font-semibold")
                        refresh_btn = ui.button(icon="refresh").classes(
                            "bg-gray-100 hover:bg-gray-200 text-gray-700"
                        )

                    stats_container = ui.column().classes("w-full gap-4")

                    with stats_container:
                        # Vector count
                        with ui.row().classes(
                            "items-center justify-between p-3 bg-blue-50 rounded-lg"
                        ):
                            with ui.column().classes("gap-0"):
                                ui.label("Total Vectors").classes(
                                    "text-sm text-gray-600"
                                )
                                vector_count_label = ui.label("0").classes(
                                    "text-2xl font-bold text-blue-600"
                                )
                            ui.icon("storage").classes("text-3xl text-blue-400")

                        # Longest vector
                        with ui.row().classes(
                            "items-center justify-between p-3 bg-green-50 rounded-lg"
                        ):
                            with ui.column().classes("gap-0"):
                                ui.label("Longest Vector").classes(
                                    "text-sm text-gray-600"
                                )
                                longest_vector_label = ui.label("0").classes(
                                    "text-2xl font-bold text-green-600"
                                )
                            ui.icon("straighten").classes("text-3xl text-green-400")

                        # Last updated
                        last_updated_label = ui.label("Last updated: Never").classes(
                            "text-xs text-gray-400"
                        )

                    async def refresh_stats(show_toast: bool = False):
                        """Refresh database statistics."""
                        try:
                            async with create_client() as client:
                                response = await client.get("/get-vectors-data")
                                data = response.json()

                            num_vectors = data.get("number_of_vectors", 0)
                            longest = data.get("longest_vector", 0)

                            vector_count_label.set_text(format_number(num_vectors))
                            longest_vector_label.set_text(format_number(longest))
                            last_updated_label.set_text(
                                f"Last updated: {format_time(datetime.now())}"
                            )

                            if show_toast:
                                ui.notify("Statistics refreshed", type="info")

                        except Exception as ex:
                            ui.notify(f"Failed to load stats: {ex!s}", type="negative")

                    refresh_btn.on_click(lambda: refresh_stats(show_toast=True))

                # Health card
                with ui.card().classes("w-full mt-4"):
                    ui.label("Database Health").classes("text-lg font-semibold mb-4")

                    with ui.column().classes("gap-3"):
                        with ui.row().classes("items-center gap-2"):
                            ui.icon("check_circle").classes("text-green-500")
                            ui.label("Connection: Active").classes("text-sm")

                        with ui.row().classes("items-center gap-2"):
                            ui.icon("memory").classes("text-blue-500")
                            ui.label("Embedding Model: Cohere").classes("text-sm")

                # Recent activity card
                with ui.card().classes("w-full mt-4"):
                    ui.label("Recent Activity").classes("text-lg font-semibold mb-4")
                    activity_container = ui.column().classes("w-full gap-2")

                    def add_activity(message: str):
                        """Add an activity to the recent activity list."""
                        activities = storage.get("recent_activity", [])
                        activities.insert(
                            0,
                            {
                                "message": message,
                                "timestamp": format_time(datetime.now()),
                            },
                        )
                        # Keep only last 5
                        activities = activities[:5]
                        storage["recent_activity"] = activities
                        render_activities()

                    def render_activities():
                        """Render the activity list."""
                        activity_container.clear()
                        activities = storage.get("recent_activity", [])

                        if not activities:
                            with activity_container:
                                ui.label("No recent activity").classes(
                                    "text-sm text-gray-400"
                                )
                        else:
                            for activity in activities:
                                with activity_container:
                                    with ui.row().classes(
                                        "items-center justify-between text-sm "
                                        "p-2 bg-gray-50 rounded"
                                    ):
                                        ui.label(activity["message"]).classes(
                                            "text-gray-700"
                                        )
                                        ui.label(activity["timestamp"]).classes(
                                            "text-gray-400"
                                        )

                    # Initial render
                    render_activities()

        # Load initial stats
        await refresh_stats()
