"""Pytest configuration for repository-local imports."""

import sys
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parents[1] / "code" / "moneypoly"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))
