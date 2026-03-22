"""Registration module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CrewMember:
    """Represents a registered crew member."""

    name: str
    role: Optional[str] = None


class RegistrationModule:
    """Handles registration and retrieval of crew members."""

    def __init__(self) -> None:
        self._members: Dict[str, CrewMember] = {}

    def register_member(self, name: str, role: Optional[str] = None) -> CrewMember:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Crew member name is required.")
        if normalized_name in self._members:
            raise ValueError(f"Crew member '{normalized_name}' is already registered.")

        member = CrewMember(name=normalized_name, role=role)
        self._members[normalized_name] = member
        return member

    def is_registered(self, name: str) -> bool:
        return name.strip() in self._members

    def get_member(self, name: str) -> CrewMember:
        normalized_name = name.strip()
        if normalized_name not in self._members:
            raise ValueError(f"Crew member '{normalized_name}' is not registered.")
        return self._members[normalized_name]

    def list_members(self) -> List[CrewMember]:
        return list(self._members.values())
