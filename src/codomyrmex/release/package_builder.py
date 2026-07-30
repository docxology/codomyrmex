"""Build and inspect real Python distribution artifacts."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import zipfile
from dataclasses import dataclass, field
from email.parser import Parser
from pathlib import Path, PurePosixPath

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_FORBIDDEN_ARCHIVE_COMPONENTS = frozenset(
    {
        ".DS_Store",
        ".env",
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".ty",
        "__pycache__",
    }
)


@dataclass(frozen=True)
class PackageMetadata:
    """Expected package metadata used for pre-build validation."""

    name: str = "codomyrmex"
    version: str = "1.3.0"
    description: str = ""
    author: str = ""
    license: str = "MIT"
    python_requires: str = ">=3.11"
    dependencies: tuple[str, ...] = ()
    entry_points: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class BuildArtifact:
    """A wheel or source distribution produced by ``uv build``."""

    filename: str
    path: Path
    format: str
    media_type: str
    size_bytes: int
    sha256: str
    sha512: str
    built_at: float

    @property
    def checksum(self) -> str:
        """Compatibility alias for the complete SHA-256 digest."""
        return self.sha256


@dataclass(frozen=True)
class BuildReport:
    """Receipt for one isolated package build."""

    metadata: PackageMetadata = field(default_factory=PackageMetadata)
    artifacts: tuple[BuildArtifact, ...] = ()
    warnings: tuple[str, ...] = ()
    success: bool = False
    command: tuple[str, ...] = ()
    stdout: str = ""
    stderr: str = ""


def _hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_format(path: Path) -> tuple[str, str]:
    if path.suffix == ".whl":
        return "wheel", "application/zip"
    if path.name.endswith(".tar.gz"):
        return "sdist", "application/gzip"
    message = f"Unsupported distribution artifact: {path.name}"
    raise ValueError(message)


def _distribution_metadata(path: Path) -> tuple[str, str]:
    """Read ``Name`` and ``Version`` from a wheel or sdist without extracting it."""
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            candidates = sorted(
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA")
            )
            if len(candidates) != 1:
                message = f"Wheel has {len(candidates)} METADATA files: {path.name}"
                raise ValueError(message)
            text = archive.read(candidates[0]).decode("utf-8")
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, mode="r:gz") as archive:
            candidates = sorted(
                (
                    member
                    for member in archive.getmembers()
                    if member.isfile() and member.name.endswith("/PKG-INFO")
                ),
                key=lambda member: member.name,
            )
            if len(candidates) != 1:
                message = f"Sdist has {len(candidates)} PKG-INFO files: {path.name}"
                raise ValueError(message)
            extracted = archive.extractfile(candidates[0])
            if extracted is None:
                message = f"Cannot read sdist metadata: {path.name}"
                raise ValueError(message)
            text = extracted.read(1024 * 1024).decode("utf-8")
    else:
        message = f"Unsupported distribution artifact: {path.name}"
        raise ValueError(message)
    parsed = Parser().parsestr(text)
    name = parsed.get("Name", "").strip()
    version = parsed.get("Version", "").strip()
    if not name or not version:
        message = f"Distribution metadata is incomplete: {path.name}"
        raise ValueError(message)
    return name, version


def _archive_member_names(path: Path) -> tuple[str, ...]:
    """Return every member name without extracting the distribution."""
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return tuple(archive.namelist())
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, mode="r:gz") as archive:
            return tuple(member.name for member in archive.getmembers())
    message = f"Unsupported distribution artifact: {path.name}"
    raise ValueError(message)


def _unsafe_archive_members(path: Path) -> tuple[str, ...]:
    """Find traversal, absolute, and private-worktree paths in an artifact."""
    unsafe: list[str] = []
    for raw_name in _archive_member_names(path):
        normalized = raw_name.replace("\\", "/")
        member = PurePosixPath(normalized)
        parts = tuple(part for part in member.parts if part not in {"", "."})
        is_absolute = member.is_absolute() or bool(re.match(r"^[A-Za-z]:/", normalized))
        if (
            is_absolute
            or ".." in parts
            or any(part in _FORBIDDEN_ARCHIVE_COMPONENTS for part in parts)
        ):
            unsafe.append(raw_name)
    return tuple(sorted(set(unsafe)))


def _archive_members_containing(
    path: Path,
    needles: tuple[bytes, ...],
) -> tuple[str, ...]:
    """Find archive files containing checkout-specific byte sequences."""
    active_needles = tuple(needle for needle in needles if len(needle) > 1)
    if not active_needles:
        return ()

    matches: list[str] = []
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                payload = archive.read(info)
                if any(needle in payload for needle in active_needles):
                    matches.append(info.filename)
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, mode="r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                payload = extracted.read()
                if any(needle in payload for needle in active_needles):
                    matches.append(member.name)
    else:
        message = f"Unsupported distribution artifact: {path.name}"
        raise ValueError(message)
    return tuple(sorted(set(matches)))


def _normalized_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


class PackageBuilder:
    """Run an isolated ``uv build`` and inspect the resulting files."""

    def __init__(
        self,
        metadata: PackageMetadata | None = None,
        *,
        source_dir: str | Path | None = None,
        output_dir: str | Path | None = None,
        uv_executable: str = "uv",
        source_date_epoch: int | None = None,
    ) -> None:
        self._metadata = metadata or PackageMetadata()
        self._source_dir = Path(source_dir or Path.cwd()).resolve()
        self._output_dir = (
            Path(output_dir).resolve()
            if output_dir is not None
            else Path(tempfile.mkdtemp(prefix="codomyrmex-dist-")).resolve()
        )
        self._uv_executable = uv_executable
        self._source_date_epoch = source_date_epoch

    @property
    def metadata(self) -> PackageMetadata:
        """Return the expected package metadata."""
        return self._metadata

    @property
    def source_dir(self) -> Path:
        """Return the source tree passed to ``uv build``."""
        return self._source_dir

    @property
    def output_dir(self) -> Path:
        """Return the destination for verified artifacts."""
        return self._output_dir

    def validate_metadata(self) -> list[str]:
        """Validate expected metadata and the source build boundary."""
        errors: list[str] = []
        if not self._metadata.name.strip():
            errors.append("Package name is required")
        if not self._metadata.version.strip():
            errors.append("Version is required")
        if not self._metadata.python_requires.strip():
            errors.append("Python version requirement is missing")
        if not self._source_dir.is_dir():
            errors.append(f"Source directory does not exist: {self._source_dir}")
        elif not (self._source_dir / "pyproject.toml").is_file():
            errors.append(f"Build source has no pyproject.toml: {self._source_dir}")
        if shutil.which(self._uv_executable) is None:
            errors.append(f"Build executable not found: {self._uv_executable}")
        return errors

    def build(self) -> BuildReport:
        """Build wheel and sdist files in an isolated PEP 517 environment."""
        errors = self.validate_metadata()
        if errors:
            return BuildReport(metadata=self._metadata, warnings=tuple(errors))

        self._output_dir.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        if self._source_date_epoch is not None:
            env["SOURCE_DATE_EPOCH"] = str(self._source_date_epoch)

        with tempfile.TemporaryDirectory(prefix="codomyrmex-uv-build-") as stage:
            stage_dir = Path(stage)
            command = (
                self._uv_executable,
                "build",
                "--out-dir",
                str(stage_dir),
                str(self._source_dir),
            )
            logger.info(
                "Building package from %s into isolated staging directory",
                self._source_dir,
            )
            result = subprocess.run(
                command,
                cwd=self._source_dir,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                warning = (
                    f"uv build failed with exit code {result.returncode}: "
                    f"{result.stderr.strip()}"
                )
                return BuildReport(
                    metadata=self._metadata,
                    warnings=(warning,),
                    command=command,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )

            staged = sorted(
                [
                    *stage_dir.glob("*.whl"),
                    *stage_dir.glob("*.tar.gz"),
                ]
            )
            if len(staged) != 2:
                warning = (
                    "uv build must produce exactly one wheel and one sdist; "
                    f"found {len(staged)}"
                )
                return BuildReport(
                    metadata=self._metadata,
                    warnings=(warning,),
                    command=command,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )

            inspection_errors: list[str] = []
            private_fragments = tuple(
                {
                    str(self._source_dir).encode(),
                    str(Path.home()).encode(),
                }
            )
            for staged_path in staged:
                try:
                    built_name, built_version = _distribution_metadata(staged_path)
                    unsafe_members = _unsafe_archive_members(staged_path)
                    private_content = _archive_members_containing(
                        staged_path,
                        private_fragments,
                    )
                except (
                    OSError,
                    ValueError,
                    tarfile.TarError,
                    zipfile.BadZipFile,
                ) as exc:
                    inspection_errors.append(
                        f"{staged_path.name}: artifact inspection failed: {exc}"
                    )
                    continue
                if _normalized_name(built_name) != _normalized_name(
                    self._metadata.name
                ):
                    inspection_errors.append(
                        f"{staged_path.name}: built Name={built_name!r}, "
                        f"expected {self._metadata.name!r}"
                    )
                if built_version != self._metadata.version:
                    inspection_errors.append(
                        f"{staged_path.name}: built Version={built_version!r}, "
                        f"expected {self._metadata.version!r}"
                    )
                if unsafe_members:
                    preview = ", ".join(unsafe_members[:5])
                    remainder = len(unsafe_members) - 5
                    suffix = f" (and {remainder} more)" if remainder > 0 else ""
                    inspection_errors.append(
                        f"{staged_path.name}: unsafe archive members: {preview}{suffix}"
                    )
                if private_content:
                    preview = ", ".join(private_content[:5])
                    remainder = len(private_content) - 5
                    suffix = f" (and {remainder} more)" if remainder > 0 else ""
                    inspection_errors.append(
                        f"{staged_path.name}: local path content in archive "
                        f"members: {preview}{suffix}"
                    )
            if inspection_errors:
                return BuildReport(
                    metadata=self._metadata,
                    warnings=tuple(inspection_errors),
                    command=command,
                    stdout=result.stdout,
                    stderr=result.stderr,
                )

            artifacts: list[BuildArtifact] = []
            built_at = float(self._source_date_epoch or int(time.time()))
            for staged_path in staged:
                destination = self._output_dir / staged_path.name
                shutil.copy2(staged_path, destination)
                artifact_format, media_type = _artifact_format(destination)
                artifacts.append(
                    BuildArtifact(
                        filename=destination.name,
                        path=destination.resolve(),
                        format=artifact_format,
                        media_type=media_type,
                        size_bytes=destination.stat().st_size,
                        sha256=_hash_file(destination, "sha256"),
                        sha512=_hash_file(destination, "sha512"),
                        built_at=built_at,
                    )
                )

        formats = {artifact.format for artifact in artifacts}
        if formats != {"sdist", "wheel"}:
            warning = f"Unexpected artifact formats: {sorted(formats)}"
            return BuildReport(
                metadata=self._metadata,
                artifacts=tuple(artifacts),
                warnings=(warning,),
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        return BuildReport(
            metadata=self._metadata,
            artifacts=tuple(artifacts),
            success=True,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
        )


__all__ = ["BuildArtifact", "BuildReport", "PackageBuilder", "PackageMetadata"]
