"""White-box tests for game flow and branch-heavy logic."""

from types import SimpleNamespace

from moneypoly.config import GO_SALARY, JAIL_FINE, MAX_TURNS
from moneypoly.game import Game
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


class _DiceStub:
    def __init__(self, roll_value=4, doubles=False, streak=0):
        self._roll_value = roll_value
        self._doubles = doubles
        self.doubles_streak = streak

    def roll(self):
        return self._roll_value

    def describe(self):
        return "stub"

    def is_doubles(self):
        return self._doubles


def _sample_property(name="Sample", position=1):
    group = PropertyGroup("G", "g")
    return Property(name, position, (100, 10), group)


def test_current_player_and_advance_turn_rotation():
    # Covers turn-rotation branch in advance_turn and current_player lookup.
    game = Game(["A", "B"])
    assert game.current_player().name == "A"
    game.advance_turn()
    assert game.current_player().name == "B"
    assert game.turn_number == 1


def test_play_turn_when_player_is_in_jail(monkeypatch):
    # Covers play_turn jail early-return branch.
    game = Game(["A", "B"])
    player = game.current_player()
    player.in_jail = True

    called = {"jail": 0, "advance": 0}
    monkeypatch.setattr(game, "_handle_jail_turn", lambda _p: called.__setitem__("jail", called["jail"] + 1))
    monkeypatch.setattr(game, "advance_turn", lambda: called.__setitem__("advance", called["advance"] + 1))

    game.play_turn()

    assert called == {"jail": 1, "advance": 1}


def test_play_turn_three_doubles_sends_to_jail(monkeypatch):
    # Covers play_turn branch where doubles streak reaches 3.
    game = Game(["A", "B"])
    player = game.current_player()
    game.dice = _DiceStub(roll_value=6, doubles=True, streak=3)

    called = {"advance": 0, "move": 0}
    monkeypatch.setattr(game, "advance_turn", lambda: called.__setitem__("advance", called["advance"] + 1))
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _r: called.__setitem__("move", called["move"] + 1))

    game.play_turn()

    assert player.in_jail is True
    assert called == {"advance": 1, "move": 0}


def test_play_turn_doubles_grants_extra_turn(monkeypatch):
    # Covers play_turn branch where doubles avoids advancing turn.
    game = Game(["A", "B"])
    game.dice = _DiceStub(roll_value=5, doubles=True, streak=1)

    called = {"advance": 0, "move": 0}
    monkeypatch.setattr(game, "advance_turn", lambda: called.__setitem__("advance", called["advance"] + 1))
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _r: called.__setitem__("move", called["move"] + 1))

    game.play_turn()

    assert called == {"advance": 0, "move": 1}


def test_play_turn_non_doubles_advances_turn(monkeypatch):
    # Covers play_turn normal branch with turn advancement.
    game = Game(["A", "B"])
    game.dice = _DiceStub(roll_value=5, doubles=False, streak=0)

    called = {"advance": 0, "move": 0}
    monkeypatch.setattr(game, "advance_turn", lambda: called.__setitem__("advance", called["advance"] + 1))
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _r: called.__setitem__("move", called["move"] + 1))

    game.play_turn()

    assert called == {"advance": 1, "move": 1}


def test_move_and_resolve_tile_branches(monkeypatch):
    # Covers _move_and_resolve branches for every tile category and property lookup path.
    game = Game(["A", "B"])
    player = game.current_player()

    actions = []
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _p: actions.append("check"))

    for tile in [
        "go_to_jail",
        "income_tax",
        "luxury_tax",
        "free_parking",
        "chance",
        "community_chest",
        "railroad",
        "property",
        "blank",
    ]:
        player.in_jail = False
        player.position = 0

        monkeypatch.setattr(player, "move", lambda _steps: None)
        monkeypatch.setattr(game.board, "get_tile_type", lambda _pos, t=tile: t)

        if tile in {"railroad", "property"}:
            monkeypatch.setattr(game.board, "get_property_at", lambda _pos: _sample_property("X", 5))
        else:
            monkeypatch.setattr(game.board, "get_property_at", lambda _pos: None)

        monkeypatch.setattr(game, "_apply_card", lambda _p, _c: actions.append(f"card-{tile}"))
        monkeypatch.setattr(game, "_handle_property_tile", lambda _p, _prop: actions.append(f"prop-{tile}"))

        if tile == "chance":
            game.decks["chance"] = SimpleNamespace(draw=lambda: {"action": "collect", "value": 1, "description": "d"})
        if tile == "community_chest":
            game.decks["community_chest"] = SimpleNamespace(draw=lambda: {"action": "collect", "value": 1, "description": "d"})

        game._move_and_resolve(player, 2)

    assert "check" in actions
    assert "card-chance" in actions
    assert "card-community_chest" in actions
    assert "prop-railroad" in actions
    assert "prop-property" in actions


def test_move_and_resolve_property_lookup_none_branch(monkeypatch):
    # Covers railroad/property branch where get_property_at returns None.
    game = Game(["A", "B"])
    player = game.current_player()
    monkeypatch.setattr(player, "move", lambda _steps: None)
    monkeypatch.setattr(game.board, "get_property_at", lambda _pos: None)
    monkeypatch.setattr(game, "_check_bankruptcy", lambda _p: None)

    called = {"handled": 0}
    monkeypatch.setattr(game, "_handle_property_tile", lambda _p, _prop: called.__setitem__("handled", 1))

    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "railroad")
    game._move_and_resolve(player, 1)
    monkeypatch.setattr(game.board, "get_tile_type", lambda _pos: "property")
    game._move_and_resolve(player, 1)

    assert called["handled"] == 0


def test_handle_property_tile_branches(monkeypatch):
    # Covers _handle_property_tile unowned buy/auction/skip, owner-self, and rent-to-other paths.
    game = Game(["A", "B"])
    player = game.players[0]
    other = game.players[1]
    prop = _sample_property()

    decisions = iter(["b", "a", "s"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(decisions))

    called = {"buy": 0, "auction": 0, "rent": 0}
    monkeypatch.setattr(game, "buy_property", lambda _p, _prop: called.__setitem__("buy", called["buy"] + 1))
    monkeypatch.setattr(game, "auction_property", lambda _prop: called.__setitem__("auction", called["auction"] + 1))
    monkeypatch.setattr(game, "pay_rent", lambda _p, _prop: called.__setitem__("rent", called["rent"] + 1))

    prop.owner = None
    game._handle_property_tile(player, prop)
    game._handle_property_tile(player, prop)
    game._handle_property_tile(player, prop)

    prop.owner = player
    game._handle_property_tile(player, prop)

    prop.owner = other
    game._handle_property_tile(player, prop)

    assert called == {"buy": 1, "auction": 1, "rent": 1}


def test_buy_property_branches_and_exact_balance_case():
    # Covers buy_property insufficient and success paths, including exact-balance edge case.
    game = Game(["A", "B"])
    player = game.players[0]
    prop = _sample_property()

    player.balance = prop.price - 1
    assert game.buy_property(player, prop) is False

    player.balance = prop.price
    assert game.buy_property(player, prop) is True
    assert prop.owner == player


def test_pay_rent_branches_and_transfer_to_owner():
    # Covers pay_rent branches and validates owner receives rent transfer.
    game = Game(["A", "B"])
    tenant = game.players[0]
    owner = game.players[1]
    prop = _sample_property()

    prop.is_mortgaged = True
    prop.owner = owner
    before_tenant = tenant.balance
    game.pay_rent(tenant, prop)
    assert tenant.balance == before_tenant

    prop.is_mortgaged = False
    prop.owner = None
    game.pay_rent(tenant, prop)
    assert tenant.balance == before_tenant

    prop.owner = owner
    before_owner = owner.balance
    game.pay_rent(tenant, prop)
    assert owner.balance == before_owner + prop.get_rent()


def test_mortgage_property_branches():
    # Covers mortgage_property not-owner, already-mortgaged, and successful mortgage paths.
    game = Game(["A", "B"])
    owner = game.players[0]
    other = game.players[1]
    prop = _sample_property()

    prop.owner = other
    assert game.mortgage_property(owner, prop) is False

    prop.owner = owner
    prop.is_mortgaged = True
    assert game.mortgage_property(owner, prop) is False

    prop.is_mortgaged = False
    start = owner.balance
    assert game.mortgage_property(owner, prop) is True
    assert owner.balance == start + prop.mortgage_value


def test_unmortgage_property_branches():
    # Covers unmortgage_property not-owner, not-mortgaged, cannot-afford, and success paths.
    game = Game(["A", "B"])
    owner = game.players[0]
    other = game.players[1]
    prop = _sample_property()

    prop.owner = other
    assert game.unmortgage_property(owner, prop) is False

    prop.owner = owner
    prop.is_mortgaged = False
    assert game.unmortgage_property(owner, prop) is False

    prop.is_mortgaged = True
    owner.balance = 1
    assert game.unmortgage_property(owner, prop) is False

    prop.is_mortgaged = True
    owner.balance = 1_000
    assert game.unmortgage_property(owner, prop) is True


def test_trade_branches_and_cash_transfer_to_seller():
    # Covers trade failure branches and successful branch with seller cash transfer.
    game = Game(["A", "B"])
    seller = game.players[0]
    buyer = game.players[1]
    prop = _sample_property()

    prop.owner = buyer
    assert game.trade(seller, buyer, prop, 50) is False

    prop.owner = seller
    buyer.balance = 10
    assert game.trade(seller, buyer, prop, 50) is False

    buyer.balance = 200
    seller_start = seller.balance
    assert game.trade(seller, buyer, prop, 50) is True
    assert prop.owner == buyer
    assert seller.balance == seller_start + 50


def test_auction_property_with_winner(monkeypatch):
    # Covers auction bid branches (pass/low/too-high/valid) and winner assignment path.
    game = Game(["A", "B", "C", "D"])
    prop = _sample_property()
    bids = iter([0, 5, 9999, 30])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(bids))

    game.auction_property(prop)

    assert prop.owner == game.players[3]


def test_auction_property_no_bids(monkeypatch):
    # Covers auction final branch where no highest bidder exists.
    game = Game(["A", "B"])
    prop = _sample_property()
    bids = iter([0, 0])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(bids))

    game.auction_property(prop)

    assert prop.owner is None


def test_handle_jail_turn_use_card(monkeypatch):
    # Covers jail branch where player uses a Get Out of Jail Free card.
    game = Game(["A", "B"])
    player = game.current_player()
    player.in_jail = True
    player.get_out_of_jail_cards = 1

    monkeypatch.setattr("moneypoly.ui.confirm", lambda _prompt: True)
    monkeypatch.setattr(game.dice, "roll", lambda: 4)

    called = {"move": 0}
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _roll: called.__setitem__("move", called["move"] + 1))

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.get_out_of_jail_cards == 0
    assert called["move"] == 1


def test_handle_jail_turn_pay_fine_branch(monkeypatch):
    # Covers jail branch where player declines card usage and pays voluntary fine.
    game = Game(["A", "B"])
    player = game.current_player()
    player.in_jail = True
    player.get_out_of_jail_cards = 1
    start_balance = player.balance

    answers = iter([False, True])
    monkeypatch.setattr("moneypoly.ui.confirm", lambda _prompt: next(answers))
    monkeypatch.setattr(game.dice, "roll", lambda: 3)
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _roll: None)

    game._handle_jail_turn(player)

    assert player.in_jail is False
    assert player.balance == start_balance - JAIL_FINE


def test_handle_jail_turn_no_action_and_mandatory_release(monkeypatch):
    # Covers jail no-action path and mandatory release at 3rd turn branch.
    game = Game(["A", "B"])
    player = game.current_player()
    player.in_jail = True
    player.get_out_of_jail_cards = 0
    player.jail_turns = 1

    monkeypatch.setattr("moneypoly.ui.confirm", lambda _prompt: False)
    monkeypatch.setattr(game, "_move_and_resolve", lambda _p, _roll: None)

    game._handle_jail_turn(player)
    assert player.jail_turns == 2
    assert player.in_jail is True

    monkeypatch.setattr(game.dice, "roll", lambda: 2)
    game._handle_jail_turn(player)
    assert player.jail_turns == 0
    assert player.in_jail is False


def test_apply_card_none_and_unknown_action():
    # Covers _apply_card branch for None card and unrecognized action.
    game = Game(["A", "B"])
    player = game.current_player()

    game._apply_card(player, None)
    game._apply_card(player, {"description": "unknown", "action": "mystery", "value": 1})


def test_apply_card_known_actions(monkeypatch):
    # Covers _apply_card routing for collect/pay/jail/jail_free actions.
    game = Game(["A", "B"])
    player = game.current_player()

    game._apply_card(player, {"description": "collect", "action": "collect", "value": 30})
    assert player.balance >= 1530

    start = player.balance
    game._apply_card(player, {"description": "pay", "action": "pay", "value": 20})
    assert player.balance == start - 20

    game._apply_card(player, {"description": "jail", "action": "jail", "value": 0})
    assert player.in_jail is True

    player.in_jail = False
    cards = player.get_out_of_jail_cards
    game._apply_card(player, {"description": "free", "action": "jail_free", "value": 0})
    assert player.get_out_of_jail_cards == cards + 1

    prop = _sample_property("M", 5)
    monkeypatch.setattr(game.board, "get_tile_type", lambda _v: "property")
    monkeypatch.setattr(game.board, "get_property_at", lambda _v: prop)
    called = {"handled": 0}
    monkeypatch.setattr(game, "_handle_property_tile", lambda _p, _prop: called.__setitem__("handled", 1))
    player.position = 39
    game._handle_move_to_card(player, 1)
    assert called["handled"] == 1

    monkeypatch.setattr(game.board, "get_tile_type", lambda _v: "blank")
    game._handle_move_to_card(player, 5)

    monkeypatch.setattr(game.board, "get_tile_type", lambda _v: "property")
    monkeypatch.setattr(game.board, "get_property_at", lambda _v: None)
    game._handle_move_to_card(player, 8)


def test_collect_from_all_action_branches():
    # Covers collect_from_all loop condition branches for self/insufficient/sufficient players.
    game = Game(["A", "B", "C"])
    player = game.players[0]
    payer = game.players[1]
    poor = game.players[2]
    payer.balance = 20
    poor.balance = 5

    start_player = player.balance
    start_payer = payer.balance
    game._handle_collect_from_all_card(player, 10)

    assert payer.balance == start_payer - 10
    assert poor.balance == 5
    assert player.balance == start_player + 10


def test_check_bankruptcy_branches():
    # Covers _check_bankruptcy for healthy player, removal path, and non-membership path.
    game = Game(["A", "B"])
    player = game.players[0]

    player.balance = 10
    game._check_bankruptcy(player)
    assert player in game.players

    prop = _sample_property("Owned", 8)
    prop.owner = player
    player.properties.append(prop)
    player.balance = 0
    game.current_index = 5
    game._check_bankruptcy(player)
    assert player not in game.players
    assert prop.owner is None

    ghost = Player("Ghost", balance=0)
    game._check_bankruptcy(ghost)


def test_find_winner_branches_expect_highest_net_worth():
    # Covers find_winner empty-list and winner-selection branches.
    game = Game(["A", "B"])
    game.players = []
    assert game.find_winner() is None

    p1 = Player("P1", balance=100)
    p2 = Player("P2", balance=200)
    game.players = [p1, p2]
    assert game.find_winner() == p2


def test_run_branches_with_and_without_winner(monkeypatch, capsys):
    # Covers run loop branch, standings print path, and both winner/no-winner end branches.
    game = Game(["A", "B"])

    monkeypatch.setattr(game, "play_turn", lambda: setattr(game, "turn_number", MAX_TURNS))
    monkeypatch.setattr("moneypoly.ui.print_standings", lambda _players: print("standings"))
    game.run()
    out = capsys.readouterr().out
    assert "standings" in out
    assert "GAME OVER" in out

    game2 = Game(["X", "Y"])
    game2.players = []
    game2.run()
    assert "no players remaining" in capsys.readouterr().out


def test_interactive_menu_branches(monkeypatch):
    # Covers interactive_menu branches for all menu options and loan amount sub-branch.
    game = Game(["A", "B"])
    player = game.current_player()

    choices = iter([1, 2, 3, 4, 5, 6, 50, 6, 0, 9, 0])

    def fake_safe_int(_prompt, default=0):
        return next(choices)

    monkeypatch.setattr("moneypoly.ui.safe_int_input", fake_safe_int)

    called = {"s": 0, "b": 0, "m": 0, "u": 0, "t": 0, "loan": 0}
    monkeypatch.setattr("moneypoly.ui.print_standings", lambda _p: called.__setitem__("s", called["s"] + 1))
    monkeypatch.setattr("moneypoly.ui.print_board_ownership", lambda _b: called.__setitem__("b", called["b"] + 1))
    monkeypatch.setattr(game, "_menu_mortgage", lambda _p: called.__setitem__("m", called["m"] + 1))
    monkeypatch.setattr(game, "_menu_unmortgage", lambda _p: called.__setitem__("u", called["u"] + 1))
    monkeypatch.setattr(game, "_menu_trade", lambda _p: called.__setitem__("t", called["t"] + 1))
    monkeypatch.setattr(game.bank, "give_loan", lambda _p, _a: called.__setitem__("loan", called["loan"] + 1))

    game.interactive_menu(player)

    assert called == {"s": 1, "b": 1, "m": 1, "u": 1, "t": 1, "loan": 1}


def test_menu_mortgage_branches(monkeypatch):
    # Covers _menu_mortgage no-options, valid-selection, and invalid-selection paths.
    game = Game(["A", "B"])
    player = game.current_player()

    game._menu_mortgage(player)

    prop = _sample_property("M", 9)
    prop.owner = player
    player.properties = [prop]

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: 1)
    called = {"mortgaged": 0}
    monkeypatch.setattr(game, "mortgage_property", lambda _p, _prop: called.__setitem__("mortgaged", 1))
    game._menu_mortgage(player)
    assert called["mortgaged"] == 1

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: 9)
    called["mortgaged"] = 0
    game._menu_mortgage(player)
    assert called["mortgaged"] == 0


def test_menu_unmortgage_branches(monkeypatch):
    # Covers _menu_unmortgage no-options, valid-selection, and invalid-selection paths.
    game = Game(["A", "B"])
    player = game.current_player()

    game._menu_unmortgage(player)

    prop = _sample_property("U", 10)
    prop.owner = player
    prop.is_mortgaged = True
    player.properties = [prop]

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: 1)
    called = {"unmortgaged": 0}
    monkeypatch.setattr(game, "unmortgage_property", lambda _p, _prop: called.__setitem__("unmortgaged", 1))
    game._menu_unmortgage(player)
    assert called["unmortgaged"] == 1

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: 7)
    called["unmortgaged"] = 0
    game._menu_unmortgage(player)
    assert called["unmortgaged"] == 0


def test_menu_trade_branches(monkeypatch):
    # Covers _menu_trade branches: no others, invalid partner, no props, invalid prop index, and success path.
    game = Game(["Solo"])
    player = game.current_player()
    game._menu_trade(player)

    game = Game(["A", "B"])
    player = game.players[0]
    partner = game.players[1]

    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: 9)
    game._menu_trade(player)

    sequence = iter([1])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(sequence))
    game._menu_trade(player)

    prop = _sample_property("T", 11)
    prop.owner = player
    player.properties = [prop]

    sequence = iter([1, 9])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(sequence))
    game._menu_trade(player)

    called = {"trade": 0}
    monkeypatch.setattr(game, "trade", lambda _s, _b, _p, _c: called.__setitem__("trade", called["trade"] + 1))
    sequence = iter([1, 1, 25])
    monkeypatch.setattr("moneypoly.ui.safe_int_input", lambda _prompt, default=0: next(sequence))
    game._menu_trade(player)

    assert called["trade"] == 1
    assert partner in game.players
