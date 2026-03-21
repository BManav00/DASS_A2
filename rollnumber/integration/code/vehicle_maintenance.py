"""Vehicle maintenance module for StreetRace Manager."""

from __future__ import annotations

from .crew_management import CrewManagementModule
from .inventory import InventoryModule


class VehicleMaintenanceModule:
    """Handles repair and mechanic-dependent car readiness checks."""

    def __init__(self, crew_module: CrewManagementModule, inventory_module: InventoryModule) -> None:
        self._crew = crew_module
        self._inventory = inventory_module

    def has_mechanic_available(self) -> bool:
        return bool(self._crew.available_by_role("mechanic"))

    def validate_car_ready_for_race(self, car_id: str) -> None:
        car = self._inventory.get_car(car_id)
        if car.is_damaged and not self.has_mechanic_available():
            raise ValueError("Damaged car requires mechanic availability.")

    def repair_car(
        self,
        car_id: str,
        spare_part_name: str = "repair_kit",
        spare_part_quantity: int = 1,
        repair_cost: float = 500.0,
    ) -> None:
        if not self.has_mechanic_available():
            raise ValueError("Repair failed: no mechanic is currently available.")

        car = self._inventory.get_car(car_id)
        if not car.is_damaged:
            raise ValueError("Repair failed: car is not damaged.")

        self._inventory.consume_spare_part(spare_part_name, spare_part_quantity)
        self._inventory.set_car_damage(car_id, False)
        self._inventory.update_cash(-abs(repair_cost))
