"""Activity service - pure business logic for activity tracking."""

from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.ui.utils import format_time

MAX_ACTIVITIES = 5


@dataclass
class Activity:
    """Represents an activity entry."""

    message: str
    timestamp: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for storage."""
        return {"message": self.message, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Activity":
        """Create from dictionary."""
        return cls(message=data["message"], timestamp=data["timestamp"])


class ActivityService:
    """Pure business logic for activity tracking.

    This service handles all activity-related logic without any UI dependencies,
    making it easily testable.
    """

    STORAGE_KEY = "recent_activity"

    def __init__(
        self,
        storage: MutableMapping[str, Any],
        time_provider: Callable | None = None,
        max_activities: int = MAX_ACTIVITIES,
    ):
        """Initialize the activity service.

        Args:
            storage: Storage backend for persisting activities.
            time_provider: Optional callable that returns current datetime.
                          Defaults to datetime.now. Useful for testing.
            max_activities: Maximum number of activities to keep.
        """
        self.storage = storage
        self._time_provider = time_provider or datetime.now
        self._max_activities = max_activities

    def _get_timestamp(self) -> str:
        """Get formatted current timestamp."""
        return format_time(self._time_provider())

    def get_activities(self) -> list[Activity]:
        """Get all activities as list of Activity objects."""
        raw_activities = self.storage.get(self.STORAGE_KEY, [])
        return [Activity.from_dict(act) for act in raw_activities]

    def _save_activities(self, activities: list[Activity]) -> None:
        """Save activities to storage."""
        self.storage[self.STORAGE_KEY] = [act.to_dict() for act in activities]

    def add_activity(self, message: str) -> Activity:
        """Add a new activity.

        The activity is prepended to the list (most recent first).
        Only the last N activities are kept.

        Args:
            message: The activity message.

        Returns:
            The created Activity object.
        """
        activity = Activity(
            message=message,
            timestamp=self._get_timestamp(),
        )
        activities = self.get_activities()
        activities.insert(0, activity)
        # Keep only last N
        activities = activities[: self._max_activities]
        self._save_activities(activities)
        return activity

    def is_empty(self) -> bool:
        """Check if there are no activities."""
        return len(self.get_activities()) == 0
