"""Race management module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .crew_management import CrewManagementModule
from .inventory import InventoryModule


@dataclass
class Race:
    """Represents a single race instance."""

    race_id: str
    driver_name: str
    car_id: str
    status: str = "created"


class RaceManagementModule:
    """Creates races and validates race entries."""

    def __init__(self, crew_module: CrewManagementModule, inventory_module: InventoryModule) -> None:
        self._crew = crew_module
        self._inventory = inventory_module
        self._races: Dict[str, Race] = {}

    def select_driver_and_car(self, driver_name: str, car_id: str) -> None:
        if not self._crew.has_role(driver_name, "driver"):
            raise ValueError("Race creation failed: selected crew member is not a driver.")
        if not self._inventory.has_car(car_id):
            raise ValueError("Race creation failed: selected car does not exist in inventory.")

        car = self._inventory.get_car(car_id)
        if car.is_damaged and not self._crew.available_by_role("mechanic"):
            raise ValueError("Race creation failed: damaged car requires mechanic availability.")

    def create_race(self, race_id: str, driver_name: str, car_id: str) -> Race:
        normalized_race_id = race_id.strip()
        if not normalized_race_id:
            raise ValueError("Race ID is required.")
        if normalized_race_id in self._races:
            raise ValueError(f"Race '{normalized_race_id}' already exists.")

        self.select_driver_and_car(driver_name, car_id)
        race = Race(race_id=normalized_race_id, driver_name=driver_name.strip(), car_id=car_id.strip())
        self._races[normalized_race_id] = race
        return race

    def get_race(self, race_id: str) -> Race:
        normalized_race_id = race_id.strip()
        if normalized_race_id not in self._races:
            raise ValueError(f"Race '{normalized_race_id}' was not found.")
        return self._races[normalized_race_id]

    def mark_race_completed(self, race_id: str) -> None:
        race = self.get_race(race_id)
        race.status = "completed"
