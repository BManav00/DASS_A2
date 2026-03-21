"""Results module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .inventory import InventoryModule
from .race_management import RaceManagementModule


@dataclass
class RaceResult:
    """Stores race completion details."""

    race_id: str
    finishing_order: List[str]
    prize_cash: float


class ResultsModule:
    """Records race results and updates rankings and cash balance."""

    POINTS_BY_POSITION = [10, 6, 4, 3, 2, 1]

    def __init__(self, race_module: RaceManagementModule, inventory_module: InventoryModule) -> None:
        self._race = race_module
        self._inventory = inventory_module
        self._rankings: Dict[str, int] = {}
        self._results: Dict[str, RaceResult] = {}

    def record_race_result(self, race_id: str, finishing_order: List[str], prize_cash: float) -> RaceResult:
        race = self._race.get_race(race_id)
        if race.race_id in self._results:
            raise ValueError(f"Result for race '{race.race_id}' has already been recorded.")

        normalized_finishing_order = [driver.strip() for driver in finishing_order if driver.strip()]
        if not normalized_finishing_order:
            raise ValueError("Finishing order cannot be empty.")

        for index, driver_name in enumerate(normalized_finishing_order):
            points = self.POINTS_BY_POSITION[index] if index < len(self.POINTS_BY_POSITION) else 1
            self._rankings[driver_name] = self._rankings.get(driver_name, 0) + points

        self._inventory.update_cash(prize_cash)
        self._race.mark_race_completed(race_id)

        result = RaceResult(race_id=race.race_id, finishing_order=normalized_finishing_order, prize_cash=prize_cash)
        self._results[race.race_id] = result
        return result

    def get_ranking_points(self, driver_name: str) -> int:
        return self._rankings.get(driver_name.strip(), 0)

    def get_result(self, race_id: str) -> RaceResult:
        normalized_race_id = race_id.strip()
        if normalized_race_id not in self._results:
            raise ValueError(f"Race result for '{normalized_race_id}' not found.")
        return self._results[normalized_race_id]
