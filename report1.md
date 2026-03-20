# Money-Poly Pylint Improvement Report

## Scope
Performed iterative code-quality improvements on the Money-Poly Python project using `pylint`, with small category-focused commits.

## Baseline (Initial Analysis)
- Initial pylint score: **9.08/10**
- Total issues: **60**

### Categorized Findings
- Unused imports / variables:
  - `W0611` (unused-import) x5
  - `W0612` (unused-variable) x1
- Naming convention issues:
  - None reported by pylint in baseline run.
- Formatting / style issues:
  - `C0301` (line-too-long) x24
  - `C0304` (missing-final-newline) x2
  - `C0325` (superfluous-parens) x2
  - `C0121` (singleton-comparison) x1
  - `R1705` (no-else-return) x1
  - `R1723` (no-else-break) x1
  - `W0702` (bare-except) x1
  - `W1309` (f-string-without-interpolation) x1
- Code complexity / structure:
  - `R0902` (too-many-instance-attributes) x3
  - `R0912` (too-many-branches) x1
  - `R0913` (too-many-arguments) x1
  - `R0917` (too-many-positional-arguments) x1
  - `W0201` (attribute-defined-outside-init) x1
- Missing docstrings:
  - `C0114` (missing-module-docstring) x10
  - `C0115` (missing-class-docstring) x2
  - `C0116` (missing-function-docstring) x2

## Iterative Changes

### Iteration 1
- Commit: `e9fc220`
- Message: `Iteration 1: Removed unused imports and variables`
- Focus: Unused imports / variables only
- Changes:
  - Removed unused imports in `bank.py`, `dice.py`, `game.py`, `player.py`
  - Removed unused local variable in `player.py`
- Score after iteration: **9.20/10**

### Iteration 2
- Commit: `f702a4e`
- Message: `Iteration 2: Fixed pylint style and formatting issues`
- Focus: Formatting and style only
- Changes:
  - Reformatted long card definitions in `cards.py`
  - Fixed singleton comparison in `board.py`
  - Replaced bare `except` in `ui.py`
  - Removed unnecessary `else`/`elif` and superfluous parentheses in `game.py` and `property.py`
  - Removed non-interpolated f-string use in `game.py`
- Score after iteration: **9.68/10**

### Iteration 3
- Commit: `359981d`
- Message: `Iteration 3: Added missing module, class, and function docstrings`
- Focus: Docstrings only
- Changes:
  - Added module docstrings across all modules
  - Added missing class/function docstrings (`main.py`, `bank.py`, `property.py`)
- Score after iteration: **9.89/10**

### Iteration 4
- Commit: `6b13327`
- Message: `Iteration 4: Simplified complexity and reduced excess class state`
- Focus: Complexity/state cleanup and small refactors
- Changes:
  - Reduced excessive instance attributes:
    - Removed unused player elimination field
    - Consolidated game decks into a dictionary and removed redundant runtime flag
    - Simplified property state by computing mortgage value dynamically
  - Reduced branching in card handling by introducing card-action handler methods
  - Fixed `attribute-defined-outside-init` in `dice.py`
  - Simplified `Property` constructor argument shape and updated board property definitions
- Score after iteration: **10.00/10**

## Verification Per Iteration
- Re-ran `pylint` after each iteration.
- Performed runtime sanity checks using:
  - `python -m compileall -q .`
  - lightweight import/instantiation smoke checks.

## Final Result
- Initial pylint score: **9.08/10**
- Final pylint score: **10.00/10**
- Major warnings remaining: **None**
- Core game flow preserved; no architecture rewrite performed.
