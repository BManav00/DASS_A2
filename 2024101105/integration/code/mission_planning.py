"""Mission planning module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .crew_management import CrewManagementModule


@dataclass
class Mission:
    """Represents a mission assignment."""

    mission_id: str
    required_roles: List[str]
    assigned_crew: List[str]


class MissionPlanningModule:
    """Assigns missions and validates required crew roles."""

    def __init__(self, crew_module: CrewManagementModule) -> None:
        self._crew = crew_module
        self._missions: Dict[str, Mission] = {}

    def validate_required_roles(self, required_roles: List[str], assigned_crew: List[str]) -> None:
        normalized_roles = [role.strip().lower() for role in required_roles if role.strip()]
        normalized_crew = [name.strip() for name in assigned_crew if name.strip()]

        if not normalized_roles:
            raise ValueError("Mission must define at least one required role.")
        if not normalized_crew:
            raise ValueError("Mission must include assigned crew members.")

        for role in normalized_roles:
            role_available = any(self._crew.has_role(member_name, role) for member_name in normalized_crew)
            if not role_available:
                raise ValueError(f"Mission role validation failed: required role '{role}' is unavailable.")

    def assign_mission(self, mission_id: str, required_roles: List[str], assigned_crew: List[str]) -> Mission:
        normalized_mission_id = mission_id.strip()
        if not normalized_mission_id:
            raise ValueError("Mission ID is required.")
        if normalized_mission_id in self._missions:
            raise ValueError(f"Mission '{normalized_mission_id}' already exists.")

        self.validate_required_roles(required_roles, assigned_crew)

        mission = Mission(
            mission_id=normalized_mission_id,
            required_roles=[role.strip().lower() for role in required_roles if role.strip()],
            assigned_crew=[name.strip() for name in assigned_crew if name.strip()],
        )
        self._missions[normalized_mission_id] = mission
        return mission

    def get_mission(self, mission_id: str) -> Mission:
        normalized_mission_id = mission_id.strip()
        if normalized_mission_id not in self._missions:
            raise ValueError(f"Mission '{normalized_mission_id}' not found.")
        return self._missions[normalized_mission_id]
