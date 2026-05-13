"""Tests for UI services - pure business logic, no mocks needed."""

from datetime import datetime

import pytest

from app.ui.services.activity import ActivityService
from app.ui.services.chat import WELCOME_MESSAGE, ChatService, Message


class TestChatService:
    """Tests for the ChatService class."""

    @pytest.fixture
    def storage(self):
        """Create an empty storage dict."""
        return {}

    @pytest.fixture
    def fixed_time(self):
        """Return a fixed datetime for testing."""
        return datetime(2024, 1, 15, 10, 30, 0)

    @pytest.fixture
    def chat_service(self, storage, fixed_time):
        """Create a ChatService with fixed time."""
        return ChatService(storage, time_provider=lambda: fixed_time)

    def test_get_history_returns_empty_list_when_no_history(self, chat_service):
        """Should return empty list when storage has no history."""
        assert chat_service.get_history() == []

    def test_get_or_create_history_creates_welcome_message(self, chat_service, storage):
        """Should create welcome message when history is empty."""
        history = chat_service.get_or_create_history()

        assert len(history) == 1
        assert history[0].role == "assistant"
        assert history[0].content == WELCOME_MESSAGE
        assert "chat_history" in storage

    def test_get_or_create_history_returns_existing_history(
        self, chat_service, storage
    ):
        """Should return existing history without modification."""
        storage["chat_history"] = [
            {"role": "user", "content": "Hello", "timestamp": "10:00 AM"}
        ]

        history = chat_service.get_or_create_history()

        assert len(history) == 1
        assert history[0].content == "Hello"

    def test_add_user_message_appends_to_history(self, chat_service, storage):
        """Should add user message to history."""
        chat_service.get_or_create_history()  # Initialize with welcome

        message = chat_service.add_user_message("Hello, AI!")

        assert message.role == "user"
        assert message.content == "Hello, AI!"
        assert len(storage["chat_history"]) == 2

    def test_add_assistant_message_appends_to_history(self, chat_service, storage):
        """Should add assistant message to history."""
        chat_service.get_or_create_history()

        message = chat_service.add_assistant_message("Hi there!")

        assert message.role == "assistant"
        assert message.content == "Hi there!"
        assert len(storage["chat_history"]) == 2

    def test_add_assistant_message_with_custom_timestamp(self, chat_service):
        """Should use provided timestamp if given."""
        chat_service.get_or_create_history()

        message = chat_service.add_assistant_message(
            "Response", timestamp="Custom Time"
        )

        assert message.timestamp == "Custom Time"

    def test_clear_history_resets_and_adds_welcome(self, chat_service, storage):
        """Should clear history and add new welcome message."""
        storage["chat_history"] = [
            {"role": "user", "content": "Old message", "timestamp": "10:00"}
        ]

        history = chat_service.clear_history()

        assert len(history) == 1
        assert history[0].role == "assistant"
        assert history[0].content == WELCOME_MESSAGE

    def test_create_pending_timestamp_returns_formatted_time(self, chat_service):
        """Should return formatted current timestamp."""
        timestamp = chat_service.create_pending_timestamp()

        assert timestamp == "10:30 AM"  # Based on fixed_time fixture


class TestMessage:
    """Tests for the Message dataclass."""

    def test_to_dict_returns_correct_format(self):
        """Should convert to dictionary correctly."""
        msg = Message(role="user", content="Hello", timestamp="10:00 AM")

        result = msg.to_dict()

        assert result == {"role": "user", "content": "Hello", "timestamp": "10:00 AM"}

    def test_from_dict_creates_message(self):
        """Should create Message from dictionary."""
        data = {"role": "assistant", "content": "Hi", "timestamp": "10:01 AM"}

        msg = Message.from_dict(data)

        assert msg.role == "assistant"
        assert msg.content == "Hi"
        assert msg.timestamp == "10:01 AM"

    def test_from_dict_handles_missing_timestamp(self):
        """Should handle missing timestamp gracefully."""
        data = {"role": "user", "content": "Test"}

        msg = Message.from_dict(data)

        assert msg.timestamp == ""


class TestActivityService:
    """Tests for the ActivityService class."""

    @pytest.fixture
    def storage(self):
        """Create an empty storage dict."""
        return {}

    @pytest.fixture
    def fixed_time(self):
        """Return a fixed datetime for testing."""
        return datetime(2024, 1, 15, 14, 45, 0)

    @pytest.fixture
    def activity_service(self, storage, fixed_time):
        """Create an ActivityService with fixed time."""
        return ActivityService(storage, time_provider=lambda: fixed_time)

    def test_get_activities_returns_empty_list_initially(self, activity_service):
        """Should return empty list when no activities exist."""
        assert activity_service.get_activities() == []

    def test_is_empty_returns_true_when_no_activities(self, activity_service):
        """Should return True when there are no activities."""
        assert activity_service.is_empty() is True

    def test_add_activity_stores_activity(self, activity_service, storage):
        """Should store new activity in storage."""
        activity = activity_service.add_activity("Uploaded: test.txt")

        assert activity.message == "Uploaded: test.txt"
        assert activity.timestamp == "02:45 PM"
        assert len(storage["recent_activity"]) == 1

    def test_add_activity_prepends_to_list(self, activity_service):
        """New activities should appear at the beginning."""
        activity_service.add_activity("First")
        activity_service.add_activity("Second")

        activities = activity_service.get_activities()

        assert activities[0].message == "Second"
        assert activities[1].message == "First"

    def test_add_activity_keeps_only_max_activities(self, activity_service):
        """Should only keep the configured max number of activities."""
        for i in range(7):
            activity_service.add_activity(f"Activity {i}")

        activities = activity_service.get_activities()

        assert len(activities) == 5  # Default max
        assert activities[0].message == "Activity 6"
        assert activities[4].message == "Activity 2"

    def test_custom_max_activities(self, storage, fixed_time):
        """Should respect custom max_activities setting."""
        service = ActivityService(
            storage, time_provider=lambda: fixed_time, max_activities=3
        )

        for i in range(5):
            service.add_activity(f"Activity {i}")

        assert len(service.get_activities()) == 3

    def test_is_empty_returns_false_after_adding(self, activity_service):
        """Should return False after adding an activity."""
        activity_service.add_activity("Test")

        assert activity_service.is_empty() is False
