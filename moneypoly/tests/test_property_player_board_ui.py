"""White-box tests for property, player, board, and ui modules."""

from moneypoly.board import Board
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup
from moneypoly import ui
from moneypoly.config import GO_SALARY


def test_property_rent_mortgage_unmortgage_and_availability():
    # Covers property branches for rent, mortgage/unmortgage, and availability states.
    group = PropertyGroup("Brown", "brown")
    prop = Property("A", 1, (100, 10), group)
    owner = Player("Owner")

    assert prop.get_rent() == 10

    prop.owner = owner
    assert prop.get_rent() == 20

    assert prop.mortgage() == 50
    assert prop.is_mortgaged is True
    assert prop.get_rent() == 0
    assert prop.mortgage() == 0

    assert prop.unmortgage() == 55
    assert prop.is_mortgaged is False
    assert prop.unmortgage() == 0

    prop.owner = None
    assert prop.is_available() is True
    prop.is_mortgaged = True
    assert prop.is_available() is False
    assert "Property(" in repr(prop)


def test_property_group_branches_and_owner_counts():
    # Covers group add_property duplicate path and all_owned_by true/false logic.
    group = PropertyGroup("Blue", "blue")
    p1 = Property("P1", 10, (120, 8), group)
    p2 = Property("P2", 12, (120, 8), group)
    alice = Player("Alice")
    bob = Player("Bob")

    assert group.size() == 2
    group.add_property(p1)
    assert group.size() == 2

    assert group.all_owned_by(None) is False

    p1.owner = alice
    p2.owner = bob
    assert group.all_owned_by(alice) is False

    p2.owner = alice
    assert group.all_owned_by(alice) is True

    counts = group.get_owner_counts()
    assert counts[alice] == 2
    assert "PropertyGroup(" in repr(group)


def test_player_money_and_bankruptcy_branches():
    # Covers add/deduct validation branches and bankruptcy true/false paths.
    player = Player("Tester", balance=100)

    player.add_money(50)
    assert player.balance == 150

    try:
        player.add_money(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative add")

    player.deduct_money(20)
    assert player.balance == 130

    try:
        player.deduct_money(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for negative deduct")

    assert player.is_bankrupt() is False
    player.balance = 0
    assert player.is_bankrupt() is True


def test_player_move_go_jail_and_property_management(capsys):
    # Covers move paths (land/pass go), jail transition, and property list branches.
    player = Player("Mover", balance=100)

    player.position = 39
    player.move(2)
    assert player.position == 1
    assert player.balance == 100 + GO_SALARY

    player.position = 39
    player.move(1)
    assert player.position == 0

    out = capsys.readouterr().out
    assert "landed on Go" in out

    player.go_to_jail()
    assert player.in_jail is True
    assert player.jail_turns == 0

    group = PropertyGroup("Red", "red")
    prop = Property("R", 6, (100, 6), group)

    player.add_property(prop)
    player.add_property(prop)
    assert player.count_properties() == 1

    player.remove_property(prop)
    player.remove_property(prop)
    assert player.count_properties() == 0

    assert "Player(" in repr(player)


def test_player_status_line_jail_and_non_jail():
    # Covers status_line conditional tag branch.
    player = Player("Status", balance=500)
    assert "[JAILED]" not in player.status_line()
    player.in_jail = True
    assert "[JAILED]" in player.status_line()


def test_board_lookup_tile_and_ownership_branches():
    # Covers board tile type branches and ownership filter helpers.
    board = Board()
    alice = Player("Alice")

    assert board.get_property_at(1) is not None
    assert board.get_property_at(0) is None

    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(1) == "property"
    assert board.get_tile_type(11_111) == "blank"

    assert board.is_special_tile(0) is True
    assert board.is_special_tile(1) is False

    prop = board.get_property_at(1)
    assert prop is not None

    assert board.is_purchasable(0) is False
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False
    prop.is_mortgaged = False
    prop.owner = alice
    assert board.is_purchasable(1) is False
    prop.owner = None
    assert board.is_purchasable(1) is True

    prop.owner = alice
    assert board.properties_owned_by(alice) == [prop]
    assert prop not in board.unowned_properties()
    assert "Board(" in repr(board)


def test_ui_output_and_input_branches(monkeypatch, capsys):
    # Covers UI rendering branches and safe input/confirm true-false paths.
    board = Board()
    player = Player("UI", balance=1500)
    prop = board.get_property_at(1)
    assert prop is not None

    ui.print_banner("Demo")

    ui.print_player_card(player)
    player.in_jail = True
    player.jail_turns = 2
    player.get_out_of_jail_cards = 1
    prop.owner = player
    player.add_property(prop)
    ui.print_player_card(player)

    other = Player("Other", balance=900)
    ui.print_standings([player, other])
    ui.print_board_ownership(board)

    out = capsys.readouterr().out
    assert "Properties: none" in out
    assert "IN JAIL" in out
    assert "Standings" in out
    assert "Property Register" in out

    assert ui.format_currency(1500) == "$1,500"

    monkeypatch.setattr("builtins.input", lambda _prompt: "42")
    assert ui.safe_int_input("n? ") == 42

    monkeypatch.setattr("builtins.input", lambda _prompt: "oops")
    assert ui.safe_int_input("n? ", default=7) == 7

    def raise_eof(_prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", raise_eof)
    assert ui.safe_int_input("n? ", default=8) == 8

    monkeypatch.setattr("builtins.input", lambda _prompt: "y")
    assert ui.confirm("?") is True
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")
    assert ui.confirm("?") is False
