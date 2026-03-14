import os
from pathlib import Path
from typing import Any

from codomyrmex.utils.json_helpers import safe_json_loads

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class LockfileParser:
    """Parses standard dependency environment files like uv.lock."""

    def __init__(self, workspace_root: str | None = None):
        if workspace_root:
            self.root = Path(workspace_root)
        else:
            # Try to resolve implicitly by moving up from this file's directory
            # src/codomyrmex/environment_setup/lockfile.py -> src/codomyrmex -> src -> root
            self.root = Path(__file__).parent.parent.parent.parent

    def parse_uv_lock(self) -> dict[str, Any]:
        """Reads and parses the uv.lock TOML file.

        Note: Currently relies on reading raw lines and inferring package presence,
        as TOML parsing natively in Python stdlib is 3.11+ via tomllib, but we
        manually regex/split here to remain universally compatible without importing
        third-party toml libraries if they are exactly what is missing.
        """
        lock_path = self.root / "uv.lock"
        if not lock_path.exists():
            logger.warning(f"No uv.lock found at {lock_path}")
            return {"exists": False, "packages": []}

        packages = set()
        try:
            with open(lock_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("name = "):
                        # Parse `name = "package"`
                        parts = line.split('"')
                        if len(parts) >= 3:
                            packages.add(parts[1])

            return {"exists": True, "packages": sorted(packages)}
        except Exception as e:
            logger.error(f"Failed to parse uv.lock: {e!s}")
            return {"exists": True, "error": str(e), "packages": []}

    def check_dependency(self, package_name: str) -> bool:
        """Checks if a dependency is explicitly present in the uv.lock file."""
        data = self.parse_uv_lock()
        if not data.get("exists", False):
            # If no lockfile, assume true to not overly block
            return True

        # Simplistic normalization (e.g. hyphens to underscores for checking)
        norm_req = package_name.lower().replace("_", "-")
        packages = [p.lower() for p in data.get("packages", [])]

        return norm_req in packages
