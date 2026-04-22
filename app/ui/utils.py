"""Shared utility functions for NiceGUI pages."""

from datetime import datetime


def format_time(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%I:%M %p")
