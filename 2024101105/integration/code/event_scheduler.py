"""Event scheduler module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ScheduledEvent:
    """Represents a scheduled mission or race event."""

    event_id: str
    event_type: str
    reference_id: str
    timestamp: str
    status: str = "scheduled"


class EventSchedulerModule:
    """Schedules and tracks upcoming race and mission events."""

    def __init__(self) -> None:
        self._events: Dict[str, ScheduledEvent] = {}

    def schedule_event(self, event_id: str, event_type: str, reference_id: str, timestamp: str) -> ScheduledEvent:
        normalized_event_id = event_id.strip()
        normalized_event_type = event_type.strip().lower()
        normalized_reference_id = reference_id.strip()
        normalized_timestamp = timestamp.strip()

        if not normalized_event_id:
            raise ValueError("Event ID is required.")
        if normalized_event_id in self._events:
            raise ValueError(f"Event '{normalized_event_id}' already exists.")
        if normalized_event_type not in {"race", "mission"}:
            raise ValueError("Event type must be either 'race' or 'mission'.")
        if not normalized_reference_id:
            raise ValueError("Reference ID is required.")
        if not normalized_timestamp:
            raise ValueError("Timestamp is required.")

        event = ScheduledEvent(
            event_id=normalized_event_id,
            event_type=normalized_event_type,
            reference_id=normalized_reference_id,
            timestamp=normalized_timestamp,
        )
        self._events[normalized_event_id] = event
        return event

    def mark_event_completed(self, event_id: str) -> None:
        event = self.get_event(event_id)
        event.status = "completed"

    def get_event(self, event_id: str) -> ScheduledEvent:
        normalized_event_id = event_id.strip()
        if normalized_event_id not in self._events:
            raise ValueError(f"Event '{normalized_event_id}' not found.")
        return self._events[normalized_event_id]

    def list_events(self, event_type: str | None = None) -> List[ScheduledEvent]:
        if event_type is None:
            return list(self._events.values())
        normalized_event_type = event_type.strip().lower()
        return [event for event in self._events.values() if event.event_type == normalized_event_type]
