# StreetRace Manager - Integration Report

## Module Descriptions

### 1. Registration Module (`registration.py`)
- Purpose: Registers crew members with name and optional role.
- Key functions:
  - `register_member(name, role=None)`
  - `is_registered(name)`
  - `get_member(name)`
- Rule enforced: Crew must be registered before role assignment.

### 2. Crew Management Module (`crew_management.py`)
- Purpose: Assigns valid roles (`driver`, `mechanic`, `strategist`) and tracks skill levels.
- Key functions:
  - `assign_role(name, role)`
  - `set_skill_level(name, level)`
  - `has_role(name, role)`
  - `available_by_role(role)`
- Rules enforced:
  - Role assignment fails for unregistered crew.
  - Driver role required for race participation.

### 3. Inventory Module (`inventory.py`)
- Purpose: Manages cars, tools, spare parts, and cash.
- Key functions:
  - `add_car(car_id, is_damaged=False)`
  - `set_car_damage(car_id, is_damaged)`
  - `add_tool(tool_name, quantity)`
  - `add_spare_part(part_name, quantity)`
  - `consume_spare_part(part_name, quantity)`
  - `update_cash(amount)`
- Rule enforced: Race result updates cash balance through inventory.

### 4. Race Management Module (`race_management.py`)
- Purpose: Creates races and validates selected driver/car.
- Key functions:
  - `select_driver_and_car(driver_name, car_id)`
  - `create_race(race_id, driver_name, car_id)`
  - `mark_race_completed(race_id)`
- Rules enforced:
  - Only drivers can enter races.
  - Selected car must exist in inventory.
  - Damaged car requires mechanic availability.

### 5. Results Module (`results.py`)
- Purpose: Records race results, updates rankings, and updates inventory cash.
- Key functions:
  - `record_race_result(race_id, finishing_order, prize_cash)`
  - `get_ranking_points(driver_name)`
  - `get_result(race_id)`
- Rules enforced:
  - Race completion changes status and propagates financial updates.

### 6. Mission Planning Module (`mission_planning.py`)
- Purpose: Assigns missions and validates required role coverage.
- Key functions:
  - `validate_required_roles(required_roles, assigned_crew)`
  - `assign_mission(mission_id, required_roles, assigned_crew)`
- Rule enforced: Missions require all required roles to be available.

### 7. Additional Module 1 - Vehicle Maintenance (`vehicle_maintenance.py`)
- Purpose: Validates damaged car readiness and performs repairs.
- Key functions:
  - `has_mechanic_available()`
  - `validate_car_ready_for_race(car_id)`
  - `repair_car(car_id, spare_part_name, spare_part_quantity, repair_cost)`
- Value to integration:
  - Connects crew mechanic availability with car condition and inventory spare parts/cash.

### 8. Additional Module 2 - Event Scheduler (`event_scheduler.py`)
- Purpose: Schedules race/mission events and tracks completion status.
- Key functions:
  - `schedule_event(event_id, event_type, reference_id, timestamp)`
  - `mark_event_completed(event_id)`
  - `list_events(event_type=None)`
- Value to integration:
  - Links race/mission lifecycle to timeline management.

### Integration Orchestrator and CLI
- `streetrace_manager.py` integrates all modules and coordinates data flow.
- `cli.py` provides command-line style operations (`register`, `create-race`, `record-result`, `assign-mission`, etc.).

## Integration Test Cases

Test execution command used:

```bash
/tmp/streetrace-venv/bin/python -m pytest rollnumber/integration/tests/ -q
```

Actual overall output:

```text
......                                                                   [100%]
6 passed in 0.01s
```

### Test 1: Register driver -> enter race
- Scenario: Register crew with driver role and create race entry.
- Modules involved: Registration, Crew Management, Inventory, Race Management.
- Expected result: Race creation succeeds and race stores correct driver/car.
- Actual result: Passed. Race was created with `driver_name="Ava"`, `car_id="CAR-101"`.
- Why needed: Verifies registration/role assignment data is consumed correctly by race creation.

### Test 2: Enter race without driver (failure case)
- Scenario: Crew member without driver role tries race entry.
- Modules involved: Registration, Crew Management, Inventory, Race Management.
- Expected result: Race creation fails with validation error.
- Actual result: Passed. `ValueError` raised (`not a driver`).
- Why needed: Ensures the business rule "only drivers can enter races" is enforced across module boundaries.

### Test 3: Complete race -> update results and inventory
- Scenario: Record race result after race creation.
- Modules involved: Registration, Crew Management, Race Management, Results, Inventory.
- Expected result: Result stored, rankings updated, race marked completed, cash increased.
- Actual result: Passed. Ranking points became `Ava=10`, `Zoe=6`; cash updated to `2500.0`; race status `completed`.
- Why needed: Confirms data propagation chain `Race -> Results -> Inventory`.

### Test 4: Assign mission -> validate crew roles (success + failure)
- Scenario: Assign mission once with correct roles, once with missing strategist role.
- Modules involved: Registration, Crew Management, Mission Planning.
- Expected result: First assignment succeeds, second fails with role-validation error.
- Actual result: Passed. `MISSION-1` assigned; `MISSION-2` rejected due to missing strategist.
- Why needed: Ensures mission-role validation depends on real crew role data.

### Test 5: Car damaged -> check mechanic availability
- Scenario: Attempt race entry with damaged car before and after mechanic registration.
- Modules involved: Registration, Crew Management, Inventory, Vehicle Maintenance, Race Management.
- Expected result: Fail without mechanic; succeed after mechanic becomes available.
- Actual result: Passed. First attempt raised validation error; second race creation succeeded.
- Why needed: Verifies cross-module rule tying car condition to crew capability.

### Test 6: Role assignment for unregistered crew (failure case)
- Scenario: Assign role to non-registered crew member.
- Modules involved: Registration, Crew Management.
- Expected result: Role assignment fails.
- Actual result: Passed. `ValueError` raised (`not registered`).
- Why needed: Confirms strict registration dependency for role operations.

## Errors Found

No integration defects were found during this test run.
- Test suite status: `6 passed`.
- Bug-fix commits were therefore not required.

## System Integration Summary

### Interaction flow
- `Registration -> Crew Management`: roles and skills can be set only after registration.
- `Crew + Inventory -> Race Management`: race creation validates driver role and car availability.
- `Inventory(car damage) + Crew(mechanic) -> Vehicle Maintenance -> Race Management`: damaged car race entry requires mechanic availability.
- `Race -> Results -> Inventory`: recording results marks races complete, updates ranking points, and updates cash.
- `Crew -> Mission Planning`: mission assignment validates all required roles are present.
- `Race/Mission -> Event Scheduler`: optional scheduling and completion tracking.

### Data flow highlights
- Crew member identity and role data are central shared entities for race and mission validation.
- Car state (`is_damaged`) in inventory affects race eligibility through maintenance validation.
- Financial state (`cash`) changes only through inventory update calls made by results and maintenance modules.

## Call Graph

Diagram file: `rollnumber/integration/diagrams/call_graph.svg`

### Main call relationships
- `run_cli()` -> `StreetRaceManager` command methods.
- `StreetRaceManager.register_crew_member()` -> `RegistrationModule.register_member()` -> `CrewManagementModule.assign_role()/set_skill_level()`.
- `StreetRaceManager.create_race()` -> `VehicleMaintenanceModule.validate_car_ready_for_race()` -> `RaceManagementModule.create_race()` -> `RaceManagementModule.select_driver_and_car()`.
- `RaceManagementModule.select_driver_and_car()` -> `CrewManagementModule.has_role()` + `InventoryModule.has_car()/get_car()`.
- `StreetRaceManager.record_race_result()` -> `ResultsModule.record_race_result()` -> `RaceManagementModule.mark_race_completed()` + `InventoryModule.update_cash()`.
- `StreetRaceManager.assign_mission()` -> `MissionPlanningModule.assign_mission()` -> `MissionPlanningModule.validate_required_roles()` -> `CrewManagementModule.has_role()`.
- `StreetRaceManager.repair_car()` -> `VehicleMaintenanceModule.repair_car()` -> `InventoryModule.consume_spare_part()/set_car_damage()/update_cash()`.
- `StreetRaceManager.create_race()/assign_mission()` -> `EventSchedulerModule.schedule_event()`; `record_race_result()` -> `EventSchedulerModule.mark_event_completed()`.

### Test-to-call-graph alignment
- Test 1 maps to registration/crew/race call chain.
- Test 2 maps to race validation branch (`has_role` failure).
- Test 3 maps to result propagation branch (`record_race_result -> update_cash`).
- Test 4 maps to mission role-validation branch.
- Test 5 maps to maintenance gate before race creation.
- Test 6 maps to crew assignment precondition (`is_registered` guard).
