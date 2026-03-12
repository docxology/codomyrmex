"""Software Bill of Materials (SBOM) generator.

Generates CycloneDX-compatible SBOM JSON from the project's dependency tree.
Uses ``pyproject.toml`` and ``uv.lock`` as data sources.

Example::

    from codomyrmex.ci_cd_automation.sbom import SBOMGenerator

    gen = SBOMGenerator()
    sbom = gen.generate()
    gen.write_json(sbom, "sbom.json")
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class SBOMComponent:
    """A single SBOM component (dependency).

    Attributes:
        name: Package name.
        version: Package version.
        purl: Package URL (purl spec).
        scope: Dependency scope (``"required"``/``"optional"``).
        hashes: Optional hash digests.
    """

    name: str
    version: str
    purl: str = ""
    scope: str = "required"
    hashes: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.purl:
            self.purl = f"pkg:pypi/{self.name}@{self.version}"


class SBOMGenerator:
    """Generate CycloneDX-compatible SBOM.

    Args:
        repo_root: Repository root path.

    Example::

        gen = SBOMGenerator()
        sbom = gen.generate()
        assert sbom["bomFormat"] == "CycloneDX"
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self._root = repo_root or _REPO_ROOT

    def _parse_pyproject_deps(self) -> list[SBOMComponent]:
        """Extract dependencies from pyproject.toml."""
        pyproject = self._root / "pyproject.toml"
        if not pyproject.exists():
            return []

        content = pyproject.read_text()
        components: list[SBOMComponent] = []

        in_deps = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped == "dependencies = [":
                in_deps = True
                continue
            if in_deps and stripped == "]":
                break
            if in_deps and stripped.startswith('"'):
                # Parse dependency line like "click>=8.0"
                dep = stripped.strip('",').strip()
                name = dep.split(">=")[0].split("<=")[0].split("==")[0].split(">")[0].split("<")[0].split("!=")[0].strip()
                version = "unknown"
                for sep in (">=", "==", "<=", ">", "<"):
                    if sep in dep:
                        version = dep.split(sep, 1)[1].split(",")[0].strip()
                        break
                if name:
                    components.append(SBOMComponent(name=name, version=version))

        return components

    def _parse_lock_deps(self) -> list[SBOMComponent]:
        """Extract pinned dependencies from uv.lock if available."""
        lock = self._root / "uv.lock"
        if not lock.exists():
            return []

        content = lock.read_text()
        components: list[SBOMComponent] = []
        current_name = ""
        current_version = ""

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("name = "):
                current_name = stripped.split('"')[1] if '"' in stripped else ""
            elif stripped.startswith("version = ") and current_name:
                current_version = stripped.split('"')[1] if '"' in stripped else ""
                if current_name and current_version and current_name != "codomyrmex":
                    components.append(SBOMComponent(
                        name=current_name,
                        version=current_version,
                        scope="required",
                    ))
                current_name = ""
                current_version = ""

        return components

    def generate(self) -> dict[str, Any]:
        """Generate a CycloneDX SBOM.

        Returns:
            CycloneDX-compatible dict with ``bomFormat``, ``specVersion``,
            ``components``, and ``metadata``.
        """
        # Prefer lock file for pinned versions, fall back to pyproject.toml
        components = self._parse_lock_deps()
        if not components:
            components = self._parse_pyproject_deps()

        # Deduplicate by name
        seen: set[str] = set()
        unique: list[SBOMComponent] = []
        for c in components:
            if c.name not in seen:
                seen.add(c.name)
                unique.append(c)

        # Read project version
        pyproject = self._root / "pyproject.toml"
        project_version = "unknown"
        if pyproject.exists():
            for line in pyproject.read_text().splitlines():
                if line.strip().startswith("version"):
                    project_version = line.split('"')[1]
                    break

        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "version": 1,
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "tools": [
                    {
                        "vendor": "codomyrmex",
                        "name": "sbom-generator",
                        "version": project_version,
                    }
                ],
                "component": {
                    "type": "application",
                    "name": "codomyrmex",
                    "version": project_version,
                    "purl": f"pkg:pypi/codomyrmex@{project_version}",
                },
            },
            "components": [
                {
                    "type": "library",
                    "name": c.name,
                    "version": c.version,
                    "purl": c.purl,
                    "scope": c.scope,
                }
                for c in unique
            ],
        }

        logger.info("Generated SBOM with %d components", len(unique))
        return sbom

    def write_json(self, sbom: dict, output: str = "sbom.json") -> Path:
        """Write SBOM to a JSON file.

        Args:
            sbom: SBOM dict.
            output: Output file path.

        Returns:
            Path to the written file.
        """
        out = Path(output)
        out.write_text(json.dumps(sbom, indent=2) + "\n")
        logger.info("SBOM written to %s", out)
        return out

    def get_summary(self) -> dict[str, Any]:
        """Get a brief summary of the SBOM.

        Returns:
            Dict with ``total_components``, ``from_lock``, ``project_version``.
        """
        lock_deps = self._parse_lock_deps()
        pyproject_deps = self._parse_pyproject_deps()

        return {
            "total_components": len(lock_deps) if lock_deps else len(pyproject_deps),
            "from_lock": bool(lock_deps),
            "pyproject_deps": len(pyproject_deps),
            "lock_deps": len(lock_deps),
        }


__all__ = [
    "SBOMComponent",
    "SBOMGenerator",
]
