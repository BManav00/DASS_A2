# Roll Number Submission Folder

## Structure

- `whitebox/code/` -> Money-Poly source code
- `whitebox/diagrams/` -> diagrams folder (kept empty for now)
- `whitebox/tests/` -> all pytest white-box test files
- `whitebox/report.md` -> combined report (code-quality + white-box testing)

## How To Run The Code

```bash
cd whitebox/code/moneypoly
python3 main.py
```

If dependencies are not installed, create a virtual environment first:

```bash
cd whitebox
python3 -m venv .venv
.venv/bin/pip install pytest pytest-cov pylint
```

## How To Run The Tests

```bash
cd whitebox
.venv/bin/pytest tests --cov=moneypoly --cov=main --cov-branch --cov-report=term-missing
```

The tests are structured for white-box branch coverage and include edge cases and state-based checks.
