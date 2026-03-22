"""Inventory module for StreetRace Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Car:
    """Represents a car in inventory."""

    car_id: str
    is_damaged: bool = False


class InventoryModule:
    """Manages vehicles, equipment, and cash balance."""

    def __init__(self) -> None:
        self._cars: Dict[str, Car] = {}
        self._tools: Dict[str, int] = {}
        self._spare_parts: Dict[str, int] = {}
        self._cash: float = 0.0

    def add_car(self, car_id: str, is_damaged: bool = False) -> None:
        normalized_car_id = car_id.strip()
        if not normalized_car_id:
            raise ValueError("Car ID is required.")
        if normalized_car_id in self._cars:
            raise ValueError(f"Car '{normalized_car_id}' already exists in inventory.")
        self._cars[normalized_car_id] = Car(normalized_car_id, is_damaged)

    def has_car(self, car_id: str) -> bool:
        return car_id.strip() in self._cars

    def get_car(self, car_id: str) -> Car:
        normalized_car_id = car_id.strip()
        if normalized_car_id not in self._cars:
            raise ValueError(f"Car '{normalized_car_id}' does not exist.")
        return self._cars[normalized_car_id]

    def set_car_damage(self, car_id: str, is_damaged: bool) -> None:
        car = self.get_car(car_id)
        car.is_damaged = is_damaged

    def add_tool(self, tool_name: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Tool quantity must be non-negative.")
        normalized_name = tool_name.strip().lower()
        if not normalized_name:
            raise ValueError("Tool name is required.")
        self._tools[normalized_name] = self._tools.get(normalized_name, 0) + quantity

    def get_tool_quantity(self, tool_name: str) -> int:
        normalized_name = tool_name.strip().lower()
        return self._tools.get(normalized_name, 0)

    def add_spare_part(self, part_name: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Spare part quantity must be non-negative.")
        normalized_name = part_name.strip().lower()
        if not normalized_name:
            raise ValueError("Spare part name is required.")
        self._spare_parts[normalized_name] = self._spare_parts.get(normalized_name, 0) + quantity

    def consume_spare_part(self, part_name: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

        normalized_name = part_name.strip().lower()
        current_quantity = self._spare_parts.get(normalized_name, 0)
        if current_quantity < quantity:
            raise ValueError(f"Not enough '{normalized_name}' in inventory.")
        self._spare_parts[normalized_name] = current_quantity - quantity

    def get_spare_part_quantity(self, part_name: str) -> int:
        normalized_name = part_name.strip().lower()
        return self._spare_parts.get(normalized_name, 0)

    def update_cash(self, amount: float) -> float:
        self._cash += amount
        return self._cash

    def get_cash_balance(self) -> float:
        return self._cash
