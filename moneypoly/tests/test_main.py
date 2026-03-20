"""White-box tests for main.py entry-point flow."""

import main


class _GameRuns:
    def __init__(self, names):
        self.names = names
        self.run_called = False

    def run(self):
        self.run_called = True


class _GameRaisesKeyboard:
    def __init__(self, _names):
        pass

    def run(self):
        raise KeyboardInterrupt


class _GameRaisesValueError:
    def __init__(self, _names):
        raise ValueError("bad setup")


def test_get_player_names_filters_empty_entries(monkeypatch):
    # Covers list-comprehension path by including empty/spaced CSV entries.
    monkeypatch.setattr("builtins.input", lambda _prompt: " Alice, ,Bob ,,  Carol  ")
    assert main.get_player_names() == ["Alice", "Bob", "Carol"]


def test_main_runs_game_successfully(monkeypatch):
    # Covers main() try-path where Game is created and run() executes.
    holder = {}

    def fake_game(names):
        game = _GameRuns(names)
        holder["game"] = game
        return game

    monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
    monkeypatch.setattr(main, "Game", fake_game)

    main.main()

    assert holder["game"].names == ["A", "B"]
    assert holder["game"].run_called is True


def test_main_handles_keyboard_interrupt(monkeypatch, capsys):
    # Covers main() KeyboardInterrupt except-branch.
    monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
    monkeypatch.setattr(main, "Game", _GameRaisesKeyboard)

    main.main()

    assert "Game interrupted" in capsys.readouterr().out


def test_main_handles_value_error(monkeypatch, capsys):
    # Covers main() ValueError except-branch.
    monkeypatch.setattr(main, "get_player_names", lambda: ["A", "B"])
    monkeypatch.setattr(main, "Game", _GameRaisesValueError)

    main.main()

    assert "Setup error: bad setup" in capsys.readouterr().out
