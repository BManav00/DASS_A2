"""Rigorous edge-case and coverage-focused tests for StreetRace Manager."""

from __future__ import annotations

import runpy
import sys

import pytest

from code import cli as cli_module
from code.crew_management import CrewManagementModule
from code.event_scheduler import EventSchedulerModule
from code.inventory import InventoryModule
from code.mission_planning import MissionPlanningModule
from code.race_management import RaceManagementModule
from code.registration import RegistrationModule
from code.results import ResultsModule
from code.streetrace_manager import StreetRaceManager
from code.vehicle_maintenance import VehicleMaintenanceModule


def test_registration_module_rejects_invalid_and_duplicate_entries() -> None:
    registration = RegistrationModule()

    with pytest.raises(ValueError, match="name is required"):
        registration.register_member("   ")

    registration.register_member("Ava")

    with pytest.raises(ValueError, match="already registered"):
        registration.register_member("Ava")

    with pytest.raises(ValueError, match="not registered"):
        registration.get_member("Ghost")


def test_crew_management_validations_and_skill_queries() -> None:
    registration = RegistrationModule()
    crew = CrewManagementModule(registration)

    registration.register_member("Ava")

    with pytest.raises(ValueError, match="Invalid role"):
        crew.assign_role("Ava", "pilot")

    with pytest.raises(ValueError, match="unregistered crew member"):
        crew.set_skill_level("Ghost", 4)

    with pytest.raises(ValueError, match="non-negative"):
        crew.set_skill_level("Ava", -1)

    assert crew.get_skill_level("Ava") == 0

    with pytest.raises(ValueError, match="not registered"):
        crew.get_skill_level("Ghost")

    assert crew.has_role("Ghost", "driver") is False

    crew.assign_role("Ava", "driver")
    assert crew.available_by_role("driver") == ["Ava"]


def test_inventory_module_edge_cases_and_state_mutations() -> None:
    inventory = InventoryModule()

    with pytest.raises(ValueError, match="Car ID is required"):
        inventory.add_car(" ")

    inventory.add_car("CAR-EDGE")

    with pytest.raises(ValueError, match="already exists"):
        inventory.add_car("CAR-EDGE")

    with pytest.raises(ValueError, match="does not exist"):
        inventory.get_car("UNKNOWN-CAR")

    inventory.set_car_damage("CAR-EDGE", True)
    assert inventory.get_car("CAR-EDGE").is_damaged is True

    inventory.set_car_damage("CAR-EDGE", False)
    assert inventory.get_car("CAR-EDGE").is_damaged is False

    with pytest.raises(ValueError, match="Tool quantity"):
        inventory.add_tool("wrench", -1)

    with pytest.raises(ValueError, match="Tool name is required"):
        inventory.add_tool("  ", 1)

    inventory.add_tool("Wrench", 2)
    inventory.add_tool("wrench", 1)
    assert inventory.get_tool_quantity("WRENCH") == 3

    with pytest.raises(ValueError, match="Spare part quantity"):
        inventory.add_spare_part("engine", -1)

    with pytest.raises(ValueError, match="Spare part name is required"):
        inventory.add_spare_part("   ", 1)

    inventory.add_spare_part("repair_kit", 2)

    with pytest.raises(ValueError, match="Quantity must be positive"):
        inventory.consume_spare_part("repair_kit", 0)

    with pytest.raises(ValueError, match="Not enough 'repair_kit'"):
        inventory.consume_spare_part("repair_kit", 5)

    inventory.consume_spare_part("repair_kit", 1)
    assert inventory.get_spare_part_quantity("repair_kit") == 1

    assert inventory.update_cash(200.5) == pytest.approx(200.5)
    assert inventory.update_cash(-20.5) == pytest.approx(180.0)
    assert inventory.get_cash_balance() == pytest.approx(180.0)


def test_race_management_validation_errors_and_lookup_paths() -> None:
    registration = RegistrationModule()
    crew = CrewManagementModule(registration)
    inventory = InventoryModule()
    races = RaceManagementModule(crew, inventory)

    registration.register_member("Ava")
    crew.assign_role("Ava", "driver")

    with pytest.raises(ValueError, match="Race ID is required"):
        races.create_race("   ", "Ava", "CAR-X")

    with pytest.raises(ValueError, match="does not exist in inventory"):
        races.create_race("RACE-X", "Ava", "CAR-X")

    inventory.add_car("CAR-DMG", is_damaged=True)
    with pytest.raises(ValueError, match="damaged car requires mechanic"):
        races.create_race("RACE-DMG", "Ava", "CAR-DMG")

    registration.register_member("Noah")
    crew.assign_role("Noah", "mechanic")

    race = races.create_race("RACE-EDGE", "Ava", "CAR-DMG")
    assert race.race_id == "RACE-EDGE"

    with pytest.raises(ValueError, match="already exists"):
        races.create_race("RACE-EDGE", "Ava", "CAR-DMG")

    with pytest.raises(ValueError, match="was not found"):
        races.get_race("UNKNOWN-RACE")

    races.mark_race_completed("RACE-EDGE")
    assert races.get_race("RACE-EDGE").status == "completed"


def test_results_module_duplicate_empty_and_missing_result_cases() -> None:
    registration = RegistrationModule()
    crew = CrewManagementModule(registration)
    inventory = InventoryModule()
    races = RaceManagementModule(crew, inventory)
    results = ResultsModule(races, inventory)

    registration.register_member("Ava")
    crew.assign_role("Ava", "driver")

    inventory.add_car("CAR-RESULT")
    races.create_race("RACE-RESULT", "Ava", "CAR-RESULT")

    with pytest.raises(ValueError, match="Finishing order cannot be empty"):
        results.record_race_result("RACE-RESULT", [" ", ""], prize_cash=100.0)

    results.record_race_result(
        "RACE-RESULT",
        ["Ava", "P2", "P3", "P4", "P5", "P6", "P7"],
        prize_cash=500.0,
    )

    assert results.get_ranking_points("Ava") == 10
    assert results.get_ranking_points("P7") == 1

    with pytest.raises(ValueError, match="already been recorded"):
        results.record_race_result("RACE-RESULT", ["Ava"], prize_cash=100.0)

    with pytest.raises(ValueError, match="not found"):
        results.get_result("UNKNOWN-RACE")


def test_mission_planning_validation_and_lookup_edges() -> None:
    registration = RegistrationModule()
    crew = CrewManagementModule(registration)
    missions = MissionPlanningModule(crew)

    with pytest.raises(ValueError, match="at least one required role"):
        missions.validate_required_roles([], ["Ava"])

    with pytest.raises(ValueError, match="must include assigned crew members"):
        missions.validate_required_roles(["driver"], [])

    registration.register_member("Ava")
    crew.assign_role("Ava", "driver")

    with pytest.raises(ValueError, match="Mission ID is required"):
        missions.assign_mission(" ", ["driver"], ["Ava"])

    mission = missions.assign_mission("MISSION-EDGE", ["driver"], ["Ava"])
    assert mission.mission_id == "MISSION-EDGE"

    with pytest.raises(ValueError, match="already exists"):
        missions.assign_mission("MISSION-EDGE", ["driver"], ["Ava"])

    with pytest.raises(ValueError, match="not found"):
        missions.get_mission("UNKNOWN-MISSION")


def test_vehicle_maintenance_repair_paths_and_side_effects() -> None:
    registration = RegistrationModule()
    crew = CrewManagementModule(registration)
    inventory = InventoryModule()
    maintenance = VehicleMaintenanceModule(crew, inventory)

    inventory.add_car("CAR-NEEDS-REPAIR", is_damaged=True)

    with pytest.raises(ValueError, match="no mechanic is currently available"):
        maintenance.repair_car("CAR-NEEDS-REPAIR")

    registration.register_member("Noah")
    crew.assign_role("Noah", "mechanic")

    inventory.add_car("CAR-HEALTHY", is_damaged=False)
    with pytest.raises(ValueError, match="car is not damaged"):
        maintenance.repair_car("CAR-HEALTHY")

    inventory.add_spare_part("repair_kit", 1)
    maintenance.repair_car("CAR-NEEDS-REPAIR", repair_cost=250.0)

    assert inventory.get_car("CAR-NEEDS-REPAIR").is_damaged is False
    assert inventory.get_spare_part_quantity("repair_kit") == 0
    assert inventory.get_cash_balance() == pytest.approx(-250.0)


def test_event_scheduler_validations_listing_and_completion() -> None:
    scheduler = EventSchedulerModule()

    with pytest.raises(ValueError, match="Event ID is required"):
        scheduler.schedule_event("  ", "race", "R1", "2026-03-21T10:00:00")

    scheduler.schedule_event("EVT-1", "race", "R1", "2026-03-21T10:00:00")

    with pytest.raises(ValueError, match="already exists"):
        scheduler.schedule_event("EVT-1", "race", "R2", "2026-03-21T11:00:00")

    with pytest.raises(ValueError, match="either 'race' or 'mission'"):
        scheduler.schedule_event("EVT-2", "parade", "R2", "2026-03-21T11:00:00")

    with pytest.raises(ValueError, match="Reference ID is required"):
        scheduler.schedule_event("EVT-3", "race", " ", "2026-03-21T11:00:00")

    with pytest.raises(ValueError, match="Timestamp is required"):
        scheduler.schedule_event("EVT-4", "mission", "M1", "  ")

    mission_event = scheduler.schedule_event("EVT-5", "mission", "M1", "2026-03-22T12:00:00")
    assert mission_event.event_type == "mission"

    assert {event.event_id for event in scheduler.list_events()} == {"EVT-1", "EVT-5"}
    assert [event.event_id for event in scheduler.list_events("mission")] == ["EVT-5"]

    scheduler.mark_event_completed("EVT-5")
    assert scheduler.get_event("EVT-5").status == "completed"

    with pytest.raises(ValueError, match="not found"):
        scheduler.get_event("UNKNOWN-EVENT")


def test_streetrace_manager_wrapper_methods_and_scheduling_branches() -> None:
    manager = StreetRaceManager()

    manager.register_crew_member("Ava", role="driver", skill_level=4)
    manager.register_crew_member("Noah", role="mechanic", skill_level=3)

    manager.set_skill_level("Ava", 7)
    manager.add_tool("jack", 2)
    manager.add_spare_part("repair_kit", 2)

    manager.add_car("CAR-SCHEDULED")
    manager.mark_car_damaged("CAR-SCHEDULED")
    manager.repair_car("CAR-SCHEDULED", repair_cost=100.0)

    race_id = manager.create_race(
        "RACE-SCHEDULED",
        "Ava",
        "CAR-SCHEDULED",
        schedule_at="2026-03-22T10:00:00",
    )
    assert manager.scheduler.get_event(f"race_event_{race_id}").status == "scheduled"

    manager.record_race_result(race_id, ["Ava"], prize_cash=300.0)
    assert manager.scheduler.get_event(f"race_event_{race_id}").status == "completed"

    manager.add_car("CAR-NO-EVENT")
    unscheduled_race_id = manager.create_race("RACE-NO-EVENT", "Ava", "CAR-NO-EVENT")
    manager.record_race_result(unscheduled_race_id, ["Ava"], prize_cash=100.0)

    mission_id = manager.assign_mission(
        "MISSION-SCHEDULED",
        required_roles=["driver", "mechanic"],
        assigned_crew=["Ava", "Noah"],
        schedule_at="2026-03-23T12:00:00",
    )
    mission_event = manager.scheduler.get_event(f"mission_event_{mission_id}")
    assert mission_event.event_type == "mission"
    assert manager.get_cash_balance() == pytest.approx(300.0)


def test_split_csv_handles_whitespace_and_empty_values() -> None:
    assert cli_module._split_csv(" Ava, ,Noah,, Zoe ") == ["Ava", "Noah", "Zoe"]


class _FakeCLIManager:
    def register_crew_member(self, name: str, role: str | None = None, skill_level: int = 0) -> str:
        return name

    def assign_role(self, name: str, role: str) -> None:
        return None

    def set_skill_level(self, name: str, level: int) -> None:
        return None

    def add_car(self, car_id: str, is_damaged: bool = False) -> None:
        return None

    def add_spare_part(self, part_name: str, quantity: int) -> None:
        return None

    def mark_car_damaged(self, car_id: str) -> None:
        return None

    def repair_car(
        self,
        car_id: str,
        spare_part_name: str = "repair_kit",
        spare_part_quantity: int = 1,
        repair_cost: float = 500.0,
    ) -> None:
        return None

    def create_race(self, race_id: str, driver_name: str, car_id: str, schedule_at: str | None = None) -> str:
        return race_id

    def record_race_result(self, race_id: str, finishing_order: list[str], prize_cash: float) -> str:
        return race_id

    def assign_mission(
        self,
        mission_id: str,
        required_roles: list[str],
        assigned_crew: list[str],
        schedule_at: str | None = None,
    ) -> str:
        return mission_id

    def get_cash_balance(self) -> float:
        return 42.5


@pytest.mark.parametrize(
    ("argv", "expected_output"),
    [
        (["register", "--name", "Ava", "--role", "driver", "--skill", "9"], "Registered crew member: Ava"),
        (["assign-role", "--name", "Ava", "--role", "driver"], "Assigned role 'driver' to 'Ava'."),
        (["set-skill", "--name", "Ava", "--level", "8"], "Updated skill level for 'Ava' to 8."),
        (["add-car", "--car-id", "CAR-CLI", "--damaged"], "Added car 'CAR-CLI'."),
        (["add-spare-part", "--part", "repair_kit", "--quantity", "3"], "Added spare part 'repair_kit' x 3."),
        (["damage-car", "--car-id", "CAR-CLI"], "Marked car 'CAR-CLI' as damaged."),
        (["repair-car", "--car-id", "CAR-CLI", "--part", "repair_kit", "--quantity", "1", "--cost", "150"], "Repaired car 'CAR-CLI'."),
        (["create-race", "--race-id", "RACE-CLI", "--driver", "Ava", "--car", "CAR-CLI", "--schedule", "2026-03-24T09:00:00"], "Created race 'RACE-CLI'."),
        (["record-result", "--race-id", "RACE-CLI", "--order", "Ava,Noah", "--prize", "500"], "Recorded result for race 'RACE-CLI'."),
        (["assign-mission", "--mission-id", "MISSION-CLI", "--required-roles", "driver,mechanic", "--assigned-crew", "Ava,Noah", "--schedule", "2026-03-25T12:30:00"], "Assigned mission 'MISSION-CLI'."),
        (["cash-balance"], "Cash balance: 42.50"),
    ],
)
def test_cli_run_command_success_paths(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    expected_output: str,
) -> None:
    monkeypatch.setattr(cli_module, "StreetRaceManager", _FakeCLIManager)

    exit_code = cli_module.run_cli(argv)
    captured = capsys.readouterr().out.strip()

    assert exit_code == 0
    assert expected_output in captured


class _ErrorCLIManager(_FakeCLIManager):
    def assign_role(self, name: str, role: str) -> None:
        raise ValueError("forced CLI failure")


def test_cli_returns_error_code_on_value_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli_module, "StreetRaceManager", _ErrorCLIManager)

    exit_code = cli_module.run_cli(["assign-role", "--name", "Ava", "--role", "driver"])
    captured = capsys.readouterr().out.strip()

    assert exit_code == 1
    assert captured == "Error: forced CLI failure"


def test_cli_main_entrypoint_executes_with_system_exit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import code.streetrace_manager as streetrace_module

    class _MainEntryManager:
        def get_cash_balance(self) -> float:
            return 12.0

    monkeypatch.setattr(streetrace_module, "StreetRaceManager", _MainEntryManager)
    monkeypatch.setattr(sys, "argv", ["code.cli", "cash-balance"])

    previous_cli_module = sys.modules.pop("code.cli", None)
    try:
        with pytest.raises(SystemExit) as system_exit:
            runpy.run_module("code.cli", run_name="__main__")
    finally:
        if previous_cli_module is not None:
            sys.modules["code.cli"] = previous_cli_module

    assert system_exit.value.code == 0
    assert "Cash balance: 12.00" in capsys.readouterr().out
