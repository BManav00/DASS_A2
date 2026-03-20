"""White-box tests for bank, cards, dice, and config modules."""

import moneypoly.config as config
from moneypoly.bank import Bank
from moneypoly.cards import CardDeck
from moneypoly.dice import Dice
from moneypoly.player import Player


def test_config_constants_are_accessible():
    # Covers module import and constant access paths in config.
    assert config.BOARD_SIZE == 40
    assert config.STARTING_BALANCE > 0
    assert config.JAIL_POSITION < config.BOARD_SIZE


def test_bank_collect_and_get_balance():
    # Covers collect() accumulation path and get_balance().
    bank = Bank()
    start = bank.get_balance()
    bank.collect(125)
    assert bank.get_balance() == start + 125
    assert "Bank(" in repr(bank)


def test_bank_pay_out_non_positive_and_valid_and_insufficient():
    # Covers pay_out branches: non-positive, normal payout, and insufficient funds.
    bank = Bank()
    start = bank.get_balance()

    assert bank.pay_out(0) == 0
    assert bank.pay_out(-5) == 0

    paid = bank.pay_out(100)
    assert paid == 100
    assert bank.get_balance() == start - 100

    try:
        bank.pay_out(bank.get_balance() + 1)
    except ValueError as exc:
        assert "Bank cannot pay" in str(exc)
    else:
        raise AssertionError("Expected ValueError for insufficient bank funds")


def test_bank_give_loan_and_loan_stats(capsys):
    # Covers give_loan branches (ignored non-positive vs issued positive) and summary stats.
    bank = Bank()
    player = Player("Alice", balance=10)

    bank.give_loan(player, 0)
    assert bank.loan_count() == 0

    bank.give_loan(player, 50)
    assert player.balance == 60
    assert bank.loan_count() == 1
    assert bank.total_loans_issued() == 50

    bank.summary()
    out = capsys.readouterr().out
    assert "Loans issued" in out


def test_bank_handles_large_transactions():
    # Covers large-value branch behavior for collection and payout math.
    bank = Bank()
    big = 10**9
    start = bank.get_balance()

    bank.collect(big)
    assert bank.get_balance() == start + big

    paid = bank.pay_out(big)
    assert paid == big
    assert bank.get_balance() == start


def test_carddeck_draw_peek_cycle_and_empty(monkeypatch):
    # Covers CardDeck draw/peek empty and non-empty paths, plus cycle behavior.
    empty = CardDeck([])
    assert empty.draw() is None
    assert empty.peek() is None

    deck = CardDeck([{"id": 1}, {"id": 2}])
    assert deck.peek() == {"id": 1}
    assert deck.draw() == {"id": 1}
    assert deck.draw() == {"id": 2}
    assert deck.draw() == {"id": 1}
    assert deck.cards_remaining() == 1
    assert len(deck) == 2
    assert "CardDeck(" in repr(deck)

    called = {"shuffled": False}

    def fake_shuffle(cards):
        called["shuffled"] = True
        cards.reverse()

    monkeypatch.setattr("moneypoly.cards.random.shuffle", fake_shuffle)
    deck.reshuffle()
    assert called["shuffled"] is True
    assert deck.index == 0


def test_dice_roll_updates_streak_and_description(monkeypatch):
    # Covers roll() doubles and non-doubles branches plus describe().
    dice = Dice()
    seq = iter([3, 3, 2, 5])

    def fake_randint(low, high):
        assert (low, high) == (1, 6)
        return next(seq)

    monkeypatch.setattr("moneypoly.dice.random.randint", fake_randint)

    assert dice.roll() == 6
    assert dice.is_doubles() is True
    assert dice.doubles_streak == 1
    assert "DOUBLES" in dice.describe()

    assert dice.roll() == 7
    assert dice.is_doubles() is False
    assert dice.doubles_streak == 0
    assert "DOUBLES" not in dice.describe()
    assert "Dice(" in repr(dice)


def test_dice_reset_clears_state():
    # Covers reset() state-clearing path.
    dice = Dice()
    dice.die1 = 6
    dice.die2 = 5
    dice.doubles_streak = 2

    dice.reset()

    assert dice.die1 == 0
    assert dice.die2 == 0
    assert dice.doubles_streak == 0
