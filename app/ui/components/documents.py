"""Documents page UI components and handlers."""

from collections.abc import Callable
from datetime import datetime

import httpx
from nicegui import ui
from nicegui.elements.upload import Upload
from nicegui.events import UploadEventArguments

from app.ui.http_client import create_client
from app.ui.services.activity import Activity, ActivityService
from app.ui.utils import format_time


def format_number(num: int) -> str:
    """Format number with locale-aware separators."""
    return f"{num:,}"


class StatsHandler:
    """Handles database statistics display and refresh."""

    def __init__(
        self,
        vector_count_label: ui.label,
        longest_vector_label: ui.label,
        last_updated_label: ui.label,
        time_provider: Callable | None = None,
    ):
        self.vector_count_label = vector_count_label
        self.longest_vector_label = longest_vector_label
        self.last_updated_label = last_updated_label

        self._time_provider = time_provider or datetime.now
        self._format_time = format_time

    async def refresh_stats(self, show_toast: bool = False):
        """Refresh database statistics."""
        try:
            async with create_client() as client:
                response = await client.get("/get-vectors-data")
                response.raise_for_status()
                data = response.json()

            num_vectors = data.get("number_of_vectors", 0)
            longest = data.get("longest_vector", 0)

            self.vector_count_label.set_text(format_number(num_vectors))
            self.longest_vector_label.set_text(format_number(longest))
            self.last_updated_label.set_text(
                f"Last updated: {self._format_time(self._time_provider())}"
            )

            if show_toast:
                ui.notify("Statistics refreshed", type="info")

        except httpx.HTTPError as ex:
            ui.notify(f"Failed to load stats: {ex!s}", type="negative")


class ActivityHandler:
    """Thin UI handler that delegates business logic to ActivityService."""

    def __init__(self, service: ActivityService, activity_container: ui.column):
        self.service = service
        self.activity_container = activity_container

    def add_activity(self, message: str):
        """Add an activity and re-render the list."""
        self.service.add_activity(message)
        self.render_activities()

    def render_activities(self):
        """Render the activity list."""
        self.activity_container.clear()
        activities = self.service.get_activities()

        if not activities:
            with self.activity_container:
                ui.label("No recent activity").classes("text-sm text-gray-400")
        else:
            for activity in activities:
                self._render_activity(activity)

    def _render_activity(self, activity: Activity):
        """Render a single activity item."""
        with self.activity_container:
            with ui.row().classes(
                "items-center justify-between text-sm p-2 bg-gray-50 rounded"
            ):
                ui.label(activity.message).classes("text-gray-700")
                ui.label(activity.timestamp).classes("text-gray-400")


class UploadHandler:
    """Handles file upload processing."""

    def __init__(
        self,
        progress_bar: ui.linear_progress,
        upload_status: ui.label,
        upload_component: Upload,
        stats_handler: StatsHandler,
        activity_handler: ActivityHandler,
    ):
        self.progress_bar = progress_bar
        self.upload_status = upload_status
        self.upload_component = upload_component
        self.stats_handler = stats_handler
        self.activity_handler = activity_handler

    async def handle_upload(self, e: UploadEventArguments):
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
        self.progress_bar.set_visibility(True)
        self.progress_bar.set_value(0)
        self.upload_status.set_text(f"Ingesting {filename} into the database")
        await ui.context.client.connected()

        try:
            await self._process_upload(filename, content)
        except httpx.HTTPError as ex:
            ui.notify(f"Upload failed: {ex!s}", type="negative")
            self.upload_status.set_text(f"Failed: {filename}")
        finally:
            self.progress_bar.set_visibility(False)
            self.upload_component.reset()

    async def _process_upload(self, filename: str, content: str):
        """Process the file upload via API."""
        async with create_client() as client:
            async with client.stream(
                "POST",
                "/add-document",
                files={"file": (filename, content, "text/plain")},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    progress_text = line.strip()
                    if progress_text == "API_LIMIT_EXCEEDED":
                        ui.notify(
                            "API limit exceeded. Please try again later.",
                            type="warning",
                        )
                        return
                    try:
                        pct = int(float(progress_text))
                        self.progress_bar.set_value(pct / 100)
                        self.upload_status.set_text(f"Processing {filename}: {pct}%")
                    except ValueError:
                        pass

        # Success
        self.progress_bar.set_value(1)
        self.upload_status.set_text(f"Uploaded: {filename}")
        self.activity_handler.add_activity(f"Uploaded: {filename}")
        await self.stats_handler.refresh_stats()


class DatabaseActionsHandler:
    """Handles database actions like emptying."""

    def __init__(
        self,
        stats_handler: StatsHandler,
        activity_handler: ActivityHandler,
    ):
        self.stats_handler = stats_handler
        self.activity_handler = activity_handler

    async def empty_database(self):
        """Empty the database for the current session."""
        try:
            async with create_client() as client:
                response = await client.delete("/empty-database")
                response.raise_for_status()

            ui.notify("Database emptied successfully", type="positive")
            self.activity_handler.add_activity("Emptied database")
            await self.stats_handler.refresh_stats()

        except httpx.HTTPError as ex:
            ui.notify(f"Failed to empty database: {ex!s}", type="negative")
