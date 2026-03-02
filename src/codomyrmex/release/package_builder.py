"""Package building for distribution.

Validates package metadata, builds distribution artifacts,
and ensures package integrity.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class PackageMetadata:
    """Package distribution metadata.

    Attributes:
        name: Package name.
        version: Version string.
        description: Package description.
        author: Author name.
        license: License identifier.
        python_requires: Python version requirement.
        dependencies: Required dependencies.
        entry_points: CLI entry points.
    """

    name: str = "codomyrmex"
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    python_requires: str = ">=3.11"
    dependencies: list[str] = field(default_factory=list)
    entry_points: dict[str, str] = field(default_factory=dict)


@dataclass
class BuildArtifact:
    """A built distribution artifact.

    Attributes:
        filename: Artifact filename.
        format: Distribution format (sdist, wheel).
        size_bytes: File size.
        checksum: SHA-256 checksum.
        built_at: Build timestamp.
    """

    filename: str
    format: str = "wheel"
    size_bytes: int = 0
    checksum: str = ""
    built_at: float = field(default_factory=time.time)


@dataclass
class BuildReport:
    """Report from a package build.

    Attributes:
        metadata: Package metadata.
        artifacts: Built artifacts.
        warnings: Build warnings.
        success: Whether build succeeded.
    """

    metadata: PackageMetadata = field(default_factory=PackageMetadata)
    artifacts: list[BuildArtifact] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    success: bool = True


class PackageBuilder:
    """Build and validate distribution packages.

    Example::

        builder = PackageBuilder(PackageMetadata(name="mypackage", version="1.0.0"))
        report = builder.build()
        assert report.success
    """

    def __init__(self, metadata: PackageMetadata | None = None) -> None:
        self._metadata = metadata or PackageMetadata()

    @property
    def metadata(self) -> PackageMetadata:
        """metadata ."""
        return self._metadata

    def validate_metadata(self) -> list[str]:
        """Validate package metadata.

        Returns:
            List of validation errors (empty = valid).
        """
        errors: list[str] = []
        if not self._metadata.name:
            errors.append("Package name is required")
        if not self._metadata.version:
            errors.append("Version is required")
        if not self._metadata.python_requires:
            errors.append("Python version requirement is missing")
        return errors

    def build(self) -> BuildReport:
        """Build distribution artifacts.

        Returns:
            BuildReport with artifacts and status.
        """
        errors = self.validate_metadata()
        if errors:
            return BuildReport(
                metadata=self._metadata,
                warnings=errors,
                success=False,
            )

        # Simulate building sdist and wheel
        artifacts = [
            self._build_sdist(),
            self._build_wheel(),
        ]

        return BuildReport(
            metadata=self._metadata,
            artifacts=artifacts,
            success=True,
        )

    def _build_sdist(self) -> BuildArtifact:
        """Simulate building a source distribution."""
        filename = f"{self._metadata.name}-{self._metadata.version}.tar.gz"
        content = f"{self._metadata.name}:{self._metadata.version}:sdist"
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        return BuildArtifact(
            filename=filename,
            format="sdist",
            size_bytes=len(content),
            checksum=checksum,
        )

    def _build_wheel(self) -> BuildArtifact:
        """Simulate building a wheel."""
        filename = f"{self._metadata.name}-{self._metadata.version}-py3-none-any.whl"
        content = f"{self._metadata.name}:{self._metadata.version}:wheel"
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        return BuildArtifact(
            filename=filename,
            format="wheel",
            size_bytes=len(content),
            checksum=checksum,
        )


__all__ = ["BuildArtifact", "BuildReport", "PackageBuilder", "PackageMetadata"]
