"""Documents page implementation using NiceGUI."""

from datetime import datetime

from nicegui import app, ui

from app.ui.components.layout import page_layout


def format_time(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%I:%M %p")


def format_number(num: int) -> str:
    """Format number with locale-aware separators."""
    return f"{num:,}"


@ui.page("/documents")
async def documents_page():
    """Document management page."""

    # Initialize session storage
    if "recent_activity" not in app.storage.user:
        app.storage.user["recent_activity"] = []

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

                    async def handle_upload(e):
                        """Handle file upload."""
                        files = e.files if hasattr(e, "files") else [e]

                        for file_info in files:
                            # Get file content
                            content = file_info.content.read()

                            # Validate file type
                            if not file_info.name.endswith(".txt"):
                                ui.notify(
                                    f"Invalid file type: {file_info.name}. Only .txt files allowed.",
                                    type="negative",
                                )
                                continue

                            # Validate file size (10MB max)
                            if len(content) > 10 * 1024 * 1024:
                                ui.notify(
                                    f"File too large: {file_info.name}. Max size is 10MB.",
                                    type="negative",
                                )
                                continue

                            try:
                                text_content = content.decode("utf-8")
                            except UnicodeDecodeError:
                                ui.notify(
                                    f"Cannot decode file: {file_info.name}. Ensure UTF-8 encoding.",
                                    type="negative",
                                )
                                continue

                            # Show progress
                            progress_bar.visible = True
                            progress_bar.set_value(0)
                            upload_status.set_text(f"Uploading {file_info.name}...")

                            try:
                                # Get db from storage
                                db = app.storage.general.get("db")
                                if db is None:
                                    ui.notify(
                                        "Database not initialized", type="negative"
                                    )
                                    continue

                                # Get session cookie
                                cookie = app.storage.user.get("session_id", "default")

                                # Import controller function
                                from app.controller.controller import (
                                    add_content_into_db,
                                )

                                # Process upload with streaming progress
                                async for progress in add_content_into_db(
                                    db, text_content, cookie
                                ):
                                    progress = progress.strip()
                                    if progress == "API_LIMIT_EXCEEDED":
                                        ui.notify(
                                            "API limit exceeded. Please try again later.",
                                            type="warning",
                                        )
                                        break
                                    try:
                                        pct = int(progress)
                                        progress_bar.set_value(pct / 100)
                                        upload_status.set_text(
                                            f"Processing {file_info.name}: {pct}%"
                                        )
                                    except ValueError:
                                        pass

                                # Success
                                progress_bar.set_value(1)
                                upload_status.set_text(f"Uploaded: {file_info.name}")
                                ui.notify(
                                    f"Successfully uploaded {file_info.name}",
                                    type="positive",
                                )

                                # Add to recent activity
                                add_activity(f"Uploaded: {file_info.name}")

                                # Refresh stats
                                await refresh_stats()

                            except Exception as ex:
                                ui.notify(f"Upload failed: {ex!s}", type="negative")
                                upload_status.set_text(f"Failed: {file_info.name}")

                            finally:
                                progress_bar.visible = False

                    ui.upload(
                        label="Drop files here or click to browse",
                        on_upload=handle_upload,
                        auto_upload=True,
                        multiple=True,
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
                            db = app.storage.general.get("db")
                            if db is None:
                                return

                            cookie = app.storage.user.get("session_id", "default")
                            num_vectors = db.get_number_of_vectors(cookie)
                            longest = db.get_length_of_longest_vector(cookie)

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
                        activities = app.storage.user.get("recent_activity", [])
                        activities.insert(
                            0,
                            {
                                "message": message,
                                "timestamp": format_time(datetime.now()),
                            },
                        )
                        # Keep only last 5
                        activities = activities[:5]
                        app.storage.user["recent_activity"] = activities
                        render_activities()

                    def render_activities():
                        """Render the activity list."""
                        activity_container.clear()
                        activities = app.storage.user.get("recent_activity", [])

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
