"""Integrated StreetRace Manager orchestration layer."""

from __future__ import annotations

from typing import Iterable, List, Optional

from .crew_management import CrewManagementModule
from .event_scheduler import EventSchedulerModule
from .inventory import InventoryModule
from .mission_planning import MissionPlanningModule
from .race_management import RaceManagementModule
from .registration import RegistrationModule
from .results import ResultsModule
from .vehicle_maintenance import VehicleMaintenanceModule


class StreetRaceManager:
    """Coordinates all modules and exposes CLI-friendly operations."""

    def __init__(self) -> None:
        self.registration = RegistrationModule()
        self.crew = CrewManagementModule(self.registration)
        self.inventory = InventoryModule()
        self.maintenance = VehicleMaintenanceModule(self.crew, self.inventory)
        self.races = RaceManagementModule(self.crew, self.inventory)
        self.results = ResultsModule(self.races, self.inventory)
        self.missions = MissionPlanningModule(self.crew)
        self.scheduler = EventSchedulerModule()

    def register_crew_member(self, name: str, role: Optional[str] = None, skill_level: int = 0) -> str:
        member = self.registration.register_member(name)
        if role:
            self.crew.assign_role(member.name, role)
        if skill_level:
            self.crew.set_skill_level(member.name, skill_level)
        return member.name

    def assign_role(self, name: str, role: str) -> None:
        self.crew.assign_role(name, role)

    def set_skill_level(self, name: str, level: int) -> None:
        self.crew.set_skill_level(name, level)

    def add_car(self, car_id: str, is_damaged: bool = False) -> None:
        self.inventory.add_car(car_id, is_damaged=is_damaged)

    def add_tool(self, tool_name: str, quantity: int) -> None:
        self.inventory.add_tool(tool_name, quantity)

    def add_spare_part(self, part_name: str, quantity: int) -> None:
        self.inventory.add_spare_part(part_name, quantity)

    def mark_car_damaged(self, car_id: str) -> None:
        self.inventory.set_car_damage(car_id, True)

    def repair_car(
        self,
        car_id: str,
        spare_part_name: str = "repair_kit",
        spare_part_quantity: int = 1,
        repair_cost: float = 500.0,
    ) -> None:
        self.maintenance.repair_car(
            car_id=car_id,
            spare_part_name=spare_part_name,
            spare_part_quantity=spare_part_quantity,
            repair_cost=repair_cost,
        )

    def create_race(self, race_id: str, driver_name: str, car_id: str, schedule_at: Optional[str] = None) -> str:
        # Validation is shared between maintenance and race modules.
        self.maintenance.validate_car_ready_for_race(car_id)
        race = self.races.create_race(race_id, driver_name, car_id)

        if schedule_at:
            self.scheduler.schedule_event(
                event_id=f"race_event_{race.race_id}",
                event_type="race",
                reference_id=race.race_id,
                timestamp=schedule_at,
            )
        return race.race_id

    def record_race_result(self, race_id: str, finishing_order: Iterable[str], prize_cash: float) -> str:
        result = self.results.record_race_result(race_id, list(finishing_order), prize_cash)

        event_id = f"race_event_{result.race_id}"
        try:
            self.scheduler.mark_event_completed(event_id)
        except ValueError:
            pass
        return result.race_id

    def assign_mission(
        self,
        mission_id: str,
        required_roles: List[str],
        assigned_crew: List[str],
        schedule_at: Optional[str] = None,
    ) -> str:
        mission = self.missions.assign_mission(mission_id, required_roles, assigned_crew)

        if schedule_at:
            self.scheduler.schedule_event(
                event_id=f"mission_event_{mission.mission_id}",
                event_type="mission",
                reference_id=mission.mission_id,
                timestamp=schedule_at,
            )
        return mission.mission_id

    def get_cash_balance(self) -> float:
        return self.inventory.get_cash_balance()
