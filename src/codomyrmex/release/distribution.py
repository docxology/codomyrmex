"""Verified local distribution and non-mutating remote publication plans."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from codomyrmex.release.package_builder import BuildArtifact, BuildReport

logger = get_logger(__name__)


class DistributionTarget(Enum):
    """Supported package distribution targets."""

    PYPI = "pypi"
    TEST_PYPI = "test_pypi"
    GITHUB = "github"
    LOCAL = "local"


@dataclass(frozen=True)
class PreflightResult:
    """Pre-publication verification receipt."""

    target: DistributionTarget
    checks_passed: int = 0
    checks_total: int = 0
    ready: bool = False
    issues: tuple[str, ...] = ()


@dataclass(frozen=True)
class PublishResult:
    """Result of a local copy or remote dry-run planning operation."""

    target: DistributionTarget
    artifacts_published: int = 0
    url: str = ""
    success: bool = False
    executed: bool = False
    dry_run: bool = True
    receipt: dict[str, Any] = field(default_factory=dict)
    error: str = ""


def _hash_file(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_is_verified(artifact: BuildArtifact) -> bool:
    return (
        artifact.path.is_file()
        and artifact.path.stat().st_size == artifact.size_bytes
        and _hash_file(artifact.path, "sha256") == artifact.sha256
        and _hash_file(artifact.path, "sha512") == artifact.sha512
    )


class DistributionManager:
    """Distribute verified files without fabricating remote success."""

    def __init__(self, build: BuildReport | None = None) -> None:
        self._build = build
        self._published: list[PublishResult] = []

    @property
    def has_build(self) -> bool:
        """Whether a successful build receipt is available."""
        return self._build is not None and self._build.success

    def preflight(self, target: DistributionTarget) -> PreflightResult:
        """Verify build status, metadata, files, and complete hashes."""
        issues: list[str] = []
        checks_total = 4
        checks_passed = 0

        if self.has_build:
            checks_passed += 1
        else:
            issues.append("No successful build available")

        if self._build and self._build.artifacts:
            checks_passed += 1
        else:
            issues.append("No build artifacts found")

        if (
            self._build
            and self._build.metadata.name.strip()
            and self._build.metadata.version.strip()
        ):
            checks_passed += 1
        else:
            issues.append("Package metadata incomplete")

        if (
            self._build
            and self._build.artifacts
            and all(
                _artifact_is_verified(artifact) for artifact in self._build.artifacts
            )
        ):
            checks_passed += 1
        else:
            issues.append("Artifact file, size, or digest verification failed")

        return PreflightResult(
            target=target,
            checks_passed=checks_passed,
            checks_total=checks_total,
            ready=checks_passed == checks_total,
            issues=tuple(issues),
        )

    def publish(
        self,
        target: DistributionTarget,
        *,
        dry_run: bool | None = None,
        destination: str | Path | None = None,
    ) -> PublishResult:
        """Plan a remote publication or execute a verified local copy.

        Remote targets default to ``dry_run=True`` and reject execution. A local
        target defaults to execution and requires an explicit destination.
        """
        effective_dry_run = target is not DistributionTarget.LOCAL
        if dry_run is not None:
            effective_dry_run = dry_run

        preflight = self.preflight(target)
        if not preflight.ready:
            return PublishResult(
                target=target,
                dry_run=effective_dry_run,
                error=f"Pre-flight failed: {'; '.join(preflight.issues)}",
            )

        if target is not DistributionTarget.LOCAL:
            if not effective_dry_run:
                return PublishResult(
                    target=target,
                    dry_run=False,
                    error=(
                        "Remote publication is disabled; create a dry-run plan "
                        "and execute it through an authorized release workflow"
                    ),
                )
            result = self._remote_plan(target)
            self._published.append(result)
            return result

        if effective_dry_run:
            receipt = self._receipt(
                target=target,
                action="planned-local-copy",
                destination=str(destination or ""),
            )
            result = PublishResult(
                target=target,
                success=True,
                dry_run=True,
                receipt=receipt,
            )
            self._published.append(result)
            return result

        if destination is None:
            return PublishResult(
                target=target,
                dry_run=False,
                error="Local distribution requires an explicit destination",
            )

        assert self._build is not None
        destination_path = Path(destination).resolve()
        destination_path.mkdir(parents=True, exist_ok=True)
        copied: list[dict[str, Any]] = []
        for artifact in self._build.artifacts:
            copied_path = destination_path / artifact.filename
            shutil.copy2(artifact.path, copied_path)
            if (
                copied_path.stat().st_size != artifact.size_bytes
                or _hash_file(copied_path, "sha256") != artifact.sha256
                or _hash_file(copied_path, "sha512") != artifact.sha512
            ):
                message = f"Copied artifact verification failed: {artifact.filename}"
                logger.error(message)
                return PublishResult(
                    target=target,
                    dry_run=False,
                    error=message,
                )
            copied.append(
                {
                    "filename": artifact.filename,
                    "sha256": artifact.sha256,
                    "sha512": artifact.sha512,
                    "size_bytes": artifact.size_bytes,
                }
            )

        receipt = self._receipt(
            target=target,
            action="verified-local-copy",
            destination=str(destination_path),
            artifacts=copied,
        )
        result = PublishResult(
            target=target,
            artifacts_published=len(copied),
            url=destination_path.as_uri(),
            success=True,
            executed=True,
            dry_run=False,
            receipt=receipt,
        )
        self._published.append(result)
        return result

    def _remote_plan(self, target: DistributionTarget) -> PublishResult:
        assert self._build is not None
        name = self._build.metadata.name
        version = self._build.metadata.version
        urls = {
            DistributionTarget.PYPI: f"https://pypi.org/project/{name}/{version}/",
            DistributionTarget.TEST_PYPI: (
                f"https://test.pypi.org/project/{name}/{version}/"
            ),
            DistributionTarget.GITHUB: (
                f"https://github.com/docxology/{name}/releases/tag/v{version}"
            ),
        }
        receipt = self._receipt(target=target, action="remote-dry-run")
        return PublishResult(
            target=target,
            url=urls[target],
            success=True,
            executed=False,
            dry_run=True,
            receipt=receipt,
        )

    def _receipt(
        self,
        *,
        target: DistributionTarget,
        action: str,
        **details: Any,
    ) -> dict[str, Any]:
        assert self._build is not None
        body: dict[str, Any] = {
            "schema_version": "1",
            "action": action,
            "target": target.value,
            "package": self._build.metadata.name,
            "version": self._build.metadata.version,
            "artifacts": [
                {
                    "filename": artifact.filename,
                    "sha256": artifact.sha256,
                    "sha512": artifact.sha512,
                    "size_bytes": artifact.size_bytes,
                }
                for artifact in self._build.artifacts
            ],
            **details,
        }
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
        body["receipt_sha256"] = hashlib.sha256(canonical).hexdigest()
        return body

    def publish_history(self) -> list[PublishResult]:
        """Return an isolated copy of the in-memory operation history."""
        return list(self._published)


__all__ = [
    "DistributionManager",
    "DistributionTarget",
    "PreflightResult",
    "PublishResult",
]
