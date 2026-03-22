"""Integration tests validating module interactions and data flow."""

from __future__ import annotations

import pytest

from code.streetrace_manager import StreetRaceManager


def test_register_driver_then_enter_race_success() -> None:
    """
    Scenario: Register a driver and create a race entry.
    Modules involved: Registration, Crew Management, Inventory, Race Management.
    Expected result: Race is created successfully with correct driver and car mapping.
    """
    manager = StreetRaceManager()
    manager.register_crew_member("Ava", role="driver", skill_level=5)
    manager.add_car("CAR-101")

    race_id = manager.create_race("RACE-1", "Ava", "CAR-101")

    race = manager.races.get_race(race_id)
    assert race.driver_name == "Ava"
    assert race.car_id == "CAR-101"
    assert race.status == "created"


def test_enter_race_without_driver_role_fails() -> None:
    """
    Scenario: Attempt race creation with a non-driver crew member.
    Modules involved: Registration, Crew Management, Inventory, Race Management.
    Expected result: Race creation fails because only drivers can enter races.
    """
    manager = StreetRaceManager()
    manager.register_crew_member("Liam", role="strategist", skill_level=4)
    manager.add_car("CAR-102")

    with pytest.raises(ValueError, match="not a driver"):
        manager.create_race("RACE-2", "Liam", "CAR-102")


def test_complete_race_updates_results_rankings_and_inventory_cash() -> None:
    """
    Scenario: Complete a race and record results.
    Modules involved: Registration, Crew Management, Inventory, Race Management, Results.
    Expected result: Race is marked completed, rankings are updated, and inventory cash increases.
    """
    manager = StreetRaceManager()
    manager.register_crew_member("Ava", role="driver", skill_level=5)
    manager.register_crew_member("Zoe", role="driver", skill_level=4)
    manager.add_car("CAR-103")

    race_id = manager.create_race("RACE-3", "Ava", "CAR-103")
    manager.record_race_result(race_id, ["Ava", "Zoe"], prize_cash=2500.0)

    result = manager.results.get_result(race_id)
    race = manager.races.get_race(race_id)

    assert result.finishing_order == ["Ava", "Zoe"]
    assert manager.results.get_ranking_points("Ava") == 10
    assert manager.results.get_ranking_points("Zoe") == 6
    assert manager.get_cash_balance() == 2500.0
    assert race.status == "completed"


def test_assign_mission_validates_roles_success_and_failure() -> None:
    """
    Scenario: Assign a mission requiring specific roles and verify invalid assignment rejection.
    Modules involved: Registration, Crew Management, Mission Planning.
    Expected result: Mission assignment succeeds when required roles are present and fails when roles are missing.
    """
    manager = StreetRaceManager()
    manager.register_crew_member("Ava", role="driver", skill_level=5)
    manager.register_crew_member("Noah", role="mechanic", skill_level=4)

    mission_id = manager.assign_mission(
        "MISSION-1",
        required_roles=["driver", "mechanic"],
        assigned_crew=["Ava", "Noah"],
    )

    mission = manager.missions.get_mission(mission_id)
    assert mission.required_roles == ["driver", "mechanic"]
    assert mission.assigned_crew == ["Ava", "Noah"]

    with pytest.raises(ValueError, match="required role 'strategist' is unavailable"):
        manager.assign_mission(
            "MISSION-2",
            required_roles=["driver", "strategist"],
            assigned_crew=["Ava", "Noah"],
        )


def test_damaged_car_requires_mechanic_availability() -> None:
    """
    Scenario: Enter race with damaged car with and without mechanic availability.
    Modules involved: Registration, Crew Management, Inventory, Vehicle Maintenance, Race Management.
    Expected result: Race entry fails without mechanic and succeeds after mechanic is available.
    """
    manager = StreetRaceManager()
    manager.register_crew_member("Ava", role="driver", skill_level=5)
    manager.add_car("CAR-104", is_damaged=True)

    with pytest.raises(ValueError, match="Damaged car requires mechanic availability"):
        manager.create_race("RACE-4", "Ava", "CAR-104")

    manager.register_crew_member("Noah", role="mechanic", skill_level=4)
    race_id = manager.create_race("RACE-5", "Ava", "CAR-104")

    race = manager.races.get_race(race_id)
    assert race.race_id == "RACE-5"


def test_role_assignment_fails_for_unregistered_member() -> None:
    """
    Scenario: Attempt to assign a role to an unregistered crew member.
    Modules involved: Registration, Crew Management.
    Expected result: Role assignment fails with validation error.
    """
    manager = StreetRaceManager()

    with pytest.raises(ValueError, match="not registered"):
        manager.assign_role("Ghost", "driver")
