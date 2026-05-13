"""Chat service - pure business logic for chat history management."""

from collections.abc import Callable, MutableMapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.ui.utils import format_time

WELCOME_MESSAGE = (
    "Hello! I'm your AI assistant powered by RAG technology. "
    "I can answer questions based on the documents you've uploaded. "
    "How can I help you today?"
)


@dataclass
class Message:
    """Represents a chat message."""

    role: str
    content: str
    timestamp: str

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary for storage."""
        return {"role": self.role, "content": self.content, "timestamp": self.timestamp}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp", ""),
        )


class ChatService:
    """Pure business logic for chat history management.

    This service handles all chat-related logic without any UI dependencies,
    making it easily testable.
    """

    STORAGE_KEY = "chat_history"

    def __init__(
        self,
        storage: MutableMapping[str, Any],
        time_provider: Callable | None = None,
    ):
        """Initialize the chat service.

        Args:
            storage: Storage backend for persisting chat history.
            time_provider: Optional callable that returns current datetime.
                          Defaults to datetime.now. Useful for testing.
        """
        self.storage = storage
        self._time_provider = time_provider or datetime.now

    def _get_timestamp(self) -> str:
        """Get formatted current timestamp."""
        return format_time(self._time_provider())

    def get_history(self) -> list[Message]:
        """Get chat history as list of Message objects."""
        raw_history = self.storage.get(self.STORAGE_KEY, [])
        return [Message.from_dict(msg) for msg in raw_history]

    def _save_history(self, messages: list[Message]) -> None:
        """Save messages to storage."""
        self.storage[self.STORAGE_KEY] = [msg.to_dict() for msg in messages]

    def get_or_create_history(self) -> list[Message]:
        """Get existing history or create with welcome message.

        Returns:
            List of messages. If history was empty, returns list with welcome message.
        """
        history = self.get_history()
        if not history:
            welcome = Message(
                role="assistant",
                content=WELCOME_MESSAGE,
                timestamp=self._get_timestamp(),
            )
            self._save_history([welcome])
            return [welcome]
        return history

    def add_user_message(self, content: str) -> Message:
        """Add a user message to history.

        Args:
            content: The message content.

        Returns:
            The created Message object.
        """
        message = Message(
            role="user",
            content=content,
            timestamp=self._get_timestamp(),
        )
        history = self.get_history()
        history.append(message)
        self._save_history(history)
        return message

    def add_assistant_message(
        self, content: str, timestamp: str | None = None
    ) -> Message:
        """Add an assistant message to history.

        Args:
            content: The message content.
            timestamp: Optional timestamp. If not provided, uses current time.

        Returns:
            The created Message object.
        """
        message = Message(
            role="assistant",
            content=content,
            timestamp=timestamp or self._get_timestamp(),
        )
        history = self.get_history()
        history.append(message)
        self._save_history(history)
        return message

    def clear_history(self) -> list[Message]:
        """Clear chat history and return fresh history with welcome message.

        Returns:
            New history with welcome message.
        """
        self.storage[self.STORAGE_KEY] = []
        return self.get_or_create_history()

    def create_pending_timestamp(self) -> str:
        """Create a timestamp for a pending AI response.

        This is used when we create a placeholder for an AI response
        that will be filled in later via streaming.
        """
        return self._get_timestamp()
