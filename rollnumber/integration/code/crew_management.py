"""Crew management module for StreetRace Manager."""

from __future__ import annotations

from typing import Dict, List

from .registration import RegistrationModule


class CrewManagementModule:
    """Assigns roles and tracks skills for registered crew members."""

    ALLOWED_ROLES = {"driver", "mechanic", "strategist"}

    def __init__(self, registration_module: RegistrationModule) -> None:
        self._registration = registration_module
        self._skill_levels: Dict[str, int] = {}

    def assign_role(self, name: str, role: str) -> None:
        normalized_name = name.strip()
        normalized_role = role.strip().lower()

        if not self._registration.is_registered(normalized_name):
            raise ValueError("Role assignment failed: crew member is not registered.")
        if normalized_role not in self.ALLOWED_ROLES:
            raise ValueError(
                f"Invalid role '{normalized_role}'. Allowed roles: {sorted(self.ALLOWED_ROLES)}"
            )

        member = self._registration.get_member(normalized_name)
        member.role = normalized_role

    def set_skill_level(self, name: str, level: int) -> None:
        normalized_name = name.strip()
        if not self._registration.is_registered(normalized_name):
            raise ValueError("Cannot set skill level for an unregistered crew member.")
        if level < 0:
            raise ValueError("Skill level must be non-negative.")

        self._skill_levels[normalized_name] = level

    def get_skill_level(self, name: str) -> int:
        normalized_name = name.strip()
        if not self._registration.is_registered(normalized_name):
            raise ValueError("Crew member is not registered.")
        return self._skill_levels.get(normalized_name, 0)

    def has_role(self, name: str, role: str) -> bool:
        normalized_name = name.strip()
        normalized_role = role.strip().lower()
        if not self._registration.is_registered(normalized_name):
            return False
        member = self._registration.get_member(normalized_name)
        return member.role == normalized_role

    def available_by_role(self, role: str) -> List[str]:
        normalized_role = role.strip().lower()
        return [
            member.name
            for member in self._registration.list_members()
            if member.role == normalized_role
        ]
