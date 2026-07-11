"""Repository path constants for the top-level ``tests/`` layout."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "codomyrmex"
