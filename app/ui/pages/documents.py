"""Documents page implementation using NiceGUI."""

from dataclasses import dataclass, field

from nicegui import app, ui
from nicegui.elements.upload import Upload

from app.ui.components.documents import (
    ActivityHandler,
    DatabaseActionsHandler,
    StatsHandler,
    UploadHandler,
)
from app.ui.components.layout import page_layout
from app.ui.services.activity import ActivityService


@dataclass
class UploadState:
    """State container for upload section."""

    progress_bar: ui.linear_progress = field(default=None)  # type: ignore
    upload_status: ui.label = field(default=None)  # type: ignore
    upload_component: Upload = field(default=None)  # type: ignore


@dataclass
class DbActionsState:
    """State container for database actions section."""

    empty_btn: ui.button = field(default=None)  # type: ignore
    confirm_dialog: ui.dialog = field(default=None)  # type: ignore
    confirm_btn: ui.button = field(default=None)  # type: ignore


@ui.page("/documents", favicon="static/favicon.svg", title="RAG Chatbot - Documents")
async def documents_page():
    """Document management page."""
    storage = app.storage.browser
    activity_service = ActivityService(storage)
    upload_state = UploadState()
    db_actions_state = DbActionsState()

    async with page_layout(active_page="documents") as agent_info:
        ui.label("Document Management").classes("text-2xl font-bold text-gray-800 mb-4")

        with ui.row().classes("w-full gap-6 flex-wrap lg:flex-nowrap"):
            # Left column - Upload
            with ui.column().classes("flex-1 min-w-80"):
                _build_upload_section(upload_state)

            # Right column - Stats and actions
            with ui.column().classes("flex-1 min-w-80"):
                stats_handler = _build_stats_section()
                activity_handler = _build_activity_section(activity_service)
                db_actions_handler = _build_database_actions_section(
                    stats_handler, activity_handler, db_actions_state
                )
                _build_health_section(agent_info)

        # Wire up upload handler (needs references from both columns)
        upload_handler = UploadHandler(
            progress_bar=upload_state.progress_bar,
            upload_status=upload_state.upload_status,
            upload_component=upload_state.upload_component,
            stats_handler=stats_handler,
            activity_handler=activity_handler,
        )

        # Set the upload handler on the component
        upload_state.upload_component.on_upload(upload_handler.handle_upload)

        # Wire up database actions
        db_actions_state.empty_btn.on_click(db_actions_state.confirm_dialog.open)
        db_actions_state.confirm_btn.on_click(
            lambda: _confirm_and_delete(
                db_actions_state.confirm_dialog, db_actions_handler
            )
        )

        # Load initial stats
        await stats_handler.refresh_stats()


async def _confirm_and_delete(
    confirm_dialog: ui.dialog, handler: DatabaseActionsHandler
):
    """Close dialog and empty database."""
    confirm_dialog.close()
    await handler.empty_database()


def _build_upload_section(state: UploadState):
    """Build the upload section UI."""
    with ui.card().classes("w-full"):
        ui.label("Upload Documents").classes("text-lg font-semibold mb-4")

        state.upload_status = ui.label("").classes("text-sm text-gray-600 mb-2")
        state.progress_bar = ui.linear_progress(value=0, show_value=False).classes(
            "w-full mb-2"
        )
        state.progress_bar.set_visibility(False)

        def handle_rejected():
            ui.notify("File too large. Maximum size is 100KB.", type="warning")

        state.upload_component = (
            ui.upload(
                label="Drop files here or click to browse",
                on_rejected=handle_rejected,
                auto_upload=True,
                multiple=False,
                max_file_size=100 * 1024,
            )
            .classes("w-full")
            .props('accept=".txt" flat bordered')
        )

        # File requirements info
        with ui.card().classes("w-full mt-4 bg-gray-50"):
            ui.label("File Requirements").classes("font-medium text-sm mb-2")
            with ui.column().classes("gap-1 text-xs text-gray-600"):
                ui.label("- Text files only (.txt)")
                ui.label("- Maximum file size: 100KB (~500 lines)")
                ui.label("- UTF-8 encoding required")


def _build_stats_section() -> StatsHandler:
    """Build the statistics section UI and return its handler."""
    with ui.card().classes("w-full"):
        with ui.row().classes("items-center justify-between mb-4"):
            ui.label("Database Statistics").classes("text-lg font-semibold")
            refresh_btn = ui.button(icon="refresh").classes(
                "bg-gray-100 hover:bg-gray-200 text-gray-700"
            )

        with ui.column().classes("w-full gap-4"):
            # Vector count
            with ui.row().classes(
                "items-center justify-between p-3 bg-blue-50 rounded-lg"
            ):
                with ui.column().classes("gap-0"):
                    ui.label("Total Vectors").classes("text-sm text-gray-600")
                    vector_count_label = ui.label("0").classes(
                        "text-2xl font-bold text-blue-600"
                    )
                ui.icon("storage").classes("text-3xl text-blue-400")

            # Longest vector
            with ui.row().classes(
                "items-center justify-between p-3 bg-green-50 rounded-lg"
            ):
                with ui.column().classes("gap-0"):
                    ui.label("Longest Vector").classes("text-sm text-gray-600")
                    longest_vector_label = ui.label("0").classes(
                        "text-2xl font-bold text-green-600"
                    )
                ui.icon("straighten").classes("text-3xl text-green-400")

            last_updated_label = ui.label("Last updated: Never").classes(
                "text-xs text-gray-400"
            )

    stats_handler = StatsHandler(
        vector_count_label=vector_count_label,
        longest_vector_label=longest_vector_label,
        last_updated_label=last_updated_label,
    )

    refresh_btn.on_click(lambda: stats_handler.refresh_stats(show_toast=True))

    return stats_handler


def _build_activity_section(activity_service: ActivityService) -> ActivityHandler:
    """Build the recent activity section UI and return its handler."""
    with ui.card().classes("w-full mt-4"):
        ui.label("Recent Activity").classes("text-lg font-semibold mb-4")
        activity_container = ui.column().classes("w-full gap-2")

    activity_handler = ActivityHandler(activity_service, activity_container)
    activity_handler.render_activities()

    return activity_handler


def _build_database_actions_section(
    stats_handler: StatsHandler,
    activity_handler: ActivityHandler,
    state: DbActionsState,
) -> DatabaseActionsHandler:
    """Build the database actions section UI and return its handler."""
    with ui.card().classes("w-full mt-4"):
        ui.label("Database Actions").classes("text-lg font-semibold mb-4")

        with ui.row().classes("gap-2"):
            state.empty_btn = ui.button("Empty Database", icon="delete_forever").props(
                "color=red unelevated"
            )

        # Confirmation dialog
        with ui.dialog() as state.confirm_dialog, ui.card():
            ui.label("Are you sure?").classes("text-lg font-semibold")
            ui.label(
                "This will permanently delete all your uploaded documents."
            ).classes("text-gray-600")
            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                ui.button("Cancel", on_click=state.confirm_dialog.close).props("flat")
                state.confirm_btn = ui.button("Delete All").props(
                    "color=red unelevated"
                )

    return DatabaseActionsHandler(stats_handler, activity_handler)


def _build_health_section(agent_info: dict):
    """Build the database health section UI."""
    with ui.card().classes("w-full mt-4"):
        ui.label("Database Health").classes("text-lg font-semibold mb-4")

        with ui.column().classes("gap-3"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("check_circle").classes("text-green-500")
                ui.label("Connection: Active").classes("text-sm")

            with ui.row().classes("items-center gap-2"):
                ui.icon("memory").classes("text-blue-500")
                ui.label(f"Embedding Model: {agent_info['embedding_model']}").classes(
                    "text-sm"
                )
