"""Command-line interface for StreetRace Manager."""

from __future__ import annotations

import argparse
from typing import List

from .streetrace_manager import StreetRaceManager


def _split_csv(raw_value: str) -> List[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StreetRace Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register")
    register.add_argument("--name", required=True)
    register.add_argument("--role")
    register.add_argument("--skill", type=int, default=0)

    assign_role = subparsers.add_parser("assign-role")
    assign_role.add_argument("--name", required=True)
    assign_role.add_argument("--role", required=True)

    set_skill = subparsers.add_parser("set-skill")
    set_skill.add_argument("--name", required=True)
    set_skill.add_argument("--level", type=int, required=True)

    add_car = subparsers.add_parser("add-car")
    add_car.add_argument("--car-id", required=True)
    add_car.add_argument("--damaged", action="store_true")

    add_part = subparsers.add_parser("add-spare-part")
    add_part.add_argument("--part", required=True)
    add_part.add_argument("--quantity", type=int, required=True)

    mark_damaged = subparsers.add_parser("damage-car")
    mark_damaged.add_argument("--car-id", required=True)

    repair = subparsers.add_parser("repair-car")
    repair.add_argument("--car-id", required=True)
    repair.add_argument("--part", default="repair_kit")
    repair.add_argument("--quantity", type=int, default=1)
    repair.add_argument("--cost", type=float, default=500.0)

    create_race = subparsers.add_parser("create-race")
    create_race.add_argument("--race-id", required=True)
    create_race.add_argument("--driver", required=True)
    create_race.add_argument("--car", required=True)
    create_race.add_argument("--schedule")

    record_result = subparsers.add_parser("record-result")
    record_result.add_argument("--race-id", required=True)
    record_result.add_argument("--order", required=True, help="Comma-separated finishing order")
    record_result.add_argument("--prize", type=float, required=True)

    assign_mission = subparsers.add_parser("assign-mission")
    assign_mission.add_argument("--mission-id", required=True)
    assign_mission.add_argument("--required-roles", required=True, help="Comma-separated roles")
    assign_mission.add_argument("--assigned-crew", required=True, help="Comma-separated crew names")
    assign_mission.add_argument("--schedule")

    balance = subparsers.add_parser("cash-balance")
    balance.set_defaults(no_args=True)

    return parser


def run_cli(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = StreetRaceManager()

    try:
        if args.command == "register":
            member_name = manager.register_crew_member(args.name, role=args.role, skill_level=args.skill)
            print(f"Registered crew member: {member_name}")
        elif args.command == "assign-role":
            manager.assign_role(args.name, args.role)
            print(f"Assigned role '{args.role}' to '{args.name}'.")
        elif args.command == "set-skill":
            manager.set_skill_level(args.name, args.level)
            print(f"Updated skill level for '{args.name}' to {args.level}.")
        elif args.command == "add-car":
            manager.add_car(args.car_id, is_damaged=args.damaged)
            print(f"Added car '{args.car_id}'.")
        elif args.command == "add-spare-part":
            manager.add_spare_part(args.part, args.quantity)
            print(f"Added spare part '{args.part}' x {args.quantity}.")
        elif args.command == "damage-car":
            manager.mark_car_damaged(args.car_id)
            print(f"Marked car '{args.car_id}' as damaged.")
        elif args.command == "repair-car":
            manager.repair_car(args.car_id, args.part, args.quantity, args.cost)
            print(f"Repaired car '{args.car_id}'.")
        elif args.command == "create-race":
            race_id = manager.create_race(args.race_id, args.driver, args.car, schedule_at=args.schedule)
            print(f"Created race '{race_id}'.")
        elif args.command == "record-result":
            race_id = manager.record_race_result(args.race_id, _split_csv(args.order), args.prize)
            print(f"Recorded result for race '{race_id}'.")
        elif args.command == "assign-mission":
            mission_id = manager.assign_mission(
                args.mission_id,
                required_roles=_split_csv(args.required_roles),
                assigned_crew=_split_csv(args.assigned_crew),
                schedule_at=args.schedule,
            )
            print(f"Assigned mission '{mission_id}'.")
        elif args.command == "cash-balance":
            print(f"Cash balance: {manager.get_cash_balance():.2f}")
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
