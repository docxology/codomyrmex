"""CycloneDX SBOM generation from project metadata.

Generates a Software Bill of Materials in CycloneDX JSON format
from ``pyproject.toml`` and optional ``uv.lock`` data.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class SBOMComponent:
    """A component in the SBOM.

    Attributes:
        name: Package name.
        version: Package version.
        purl: Package URL (pkg:pypi/name@version).
        component_type: Type (library, application, etc.).
        scope: Scope (required, optional, dev).
    """

    name: str
    version: str = ""
    purl: str = ""
    component_type: str = "library"
    scope: str = "required"

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.purl and self.name:
            version_part = f"@{self.version}" if self.version else ""
            self.purl = f"pkg:pypi/{self.name.lower()}{version_part}"

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "type": self.component_type,
            "name": self.name,
            "version": self.version,
            "purl": self.purl,
            "scope": self.scope,
        }


@dataclass
class SBOMDocument:
    """A CycloneDX SBOM document.

    Attributes:
        project_name: Root project name.
        project_version: Root project version.
        components: All dependency components.
    """

    project_name: str = ""
    project_version: str = ""
    components: list[SBOMComponent] = field(default_factory=list)
    serial_number: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.serial_number:
            self.serial_number = f"urn:uuid:{uuid.uuid4()}"
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def component_count(self) -> int:
        """Execute Component Count operations natively."""
        return len(self.components)

    def to_cyclonedx(self) -> dict[str, Any]:
        """Convert to CycloneDX 1.5 JSON format."""
        return {
            "$schema": "http://cyclonedx.org/schema/bom-1.5.schema.json",
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": self.serial_number,
            "version": 1,
            "metadata": {
                "timestamp": self.timestamp,
                "component": {
                    "type": "application",
                    "name": self.project_name,
                    "version": self.project_version,
                },
            },
            "components": [c.to_dict() for c in self.components],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_cyclonedx(), indent=indent)


class SBOMGenerator:
    """Generate CycloneDX SBOMs from project files.

    Usage::

        gen = SBOMGenerator()
        sbom = gen.from_pyproject("pyproject.toml")
        print(sbom.to_json())
    """

    def from_pyproject(
        self,
        pyproject_path: str | Path,
    ) -> SBOMDocument:
        """Generate SBOM from pyproject.toml.

        Args:
            pyproject_path: Path to pyproject.toml.

        Returns:
            ``SBOMDocument`` with all dependencies.
        """
        path = Path(pyproject_path)
        if not path.exists():
            logger.warning("pyproject.toml not found")
            return SBOMDocument()

        content = path.read_text()

        # Extract project name and version
        name = self._extract_field(content, "name")
        version = self._extract_field(content, "version")

        # Parse dependencies
        deps = self._parse_dependencies(content)

        components = []
        for pkg_name, version_spec in deps.items():
            # Extract version number from spec
            clean_version = re.sub(r"[><=!~\s]", "", version_spec)
            components.append(SBOMComponent(
                name=pkg_name,
                version=clean_version,
            ))

        sbom = SBOMDocument(
            project_name=name,
            project_version=version,
            components=components,
        )

        logger.info(
            "SBOM generated",
            extra={
                "project": name,
                "version": version,
                "components": sbom.component_count,
            },
        )

        return sbom

    def from_dependencies(
        self,
        project_name: str,
        project_version: str,
        dependencies: dict[str, str],
    ) -> SBOMDocument:
        """Generate SBOM from a dict of dependencies.

        Args:
            project_name: Project name.
            project_version: Project version.
            dependencies: {package: version} mapping.

        Returns:
            ``SBOMDocument`` with components.
        """
        components = [
            SBOMComponent(name=name, version=version)
            for name, version in dependencies.items()
        ]

        return SBOMDocument(
            project_name=project_name,
            project_version=project_version,
            components=components,
        )

    @staticmethod
    def _extract_field(content: str, field_name: str) -> str:
        """Extract a field value from TOML content."""
        pattern = re.compile(rf'^{field_name}\s*=\s*"([^"]*)"', re.MULTILINE)
        match = pattern.search(content)
        return match.group(1) if match else ""

    @staticmethod
    def _parse_dependencies(content: str) -> dict[str, str]:
        """Parse dependencies from pyproject.toml content."""
        deps: dict[str, str] = {}
        dep_pattern = re.compile(
            r'"([a-zA-Z0-9_-]+)\s*([><=!~]*\s*[\d.]*[^"]*)"'
        )
        for match in dep_pattern.finditer(content):
            deps[match.group(1)] = match.group(2).strip()
        return deps


__all__ = [
    "SBOMComponent",
    "SBOMDocument",
    "SBOMGenerator",
]
