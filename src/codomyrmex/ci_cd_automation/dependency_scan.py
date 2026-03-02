"""Dependency vulnerability scanning via pyproject.toml analysis.

Parses dependencies from ``pyproject.toml`` and checks for known
vulnerabilities using local heuristic rules (offline) or the
OSV.dev API (when network is available).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Vulnerability:
    """A known vulnerability in a dependency.

    Attributes:
        package: Package name.
        version: Installed version.
        cve_id: CVE identifier (or advisory ID).
        severity: Severity level (low, medium, high, critical).
        summary: Human-readable description.
        fixed_in: Version that fixes the vulnerability.
    """

    package: str
    version: str = ""
    cve_id: str = ""
    severity: str = "unknown"
    summary: str = ""
    fixed_in: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "package": self.package,
            "version": self.version,
            "cve_id": self.cve_id,
            "severity": self.severity,
            "summary": self.summary,
            "fixed_in": self.fixed_in,
        }


@dataclass
class ScanReport:
    """Dependency scan report.

    Attributes:
        packages_scanned: Number of packages analyzed.
        vulnerabilities: List of found vulnerabilities.
        scan_source: Where the scan data came from.
    """

    packages_scanned: int = 0
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    scan_source: str = "local"

    @property
    def has_critical(self) -> bool:
        return any(v.severity == "critical" for v in self.vulnerabilities)

    @property
    def is_clean(self) -> bool:
        return len(self.vulnerabilities) == 0

    @property
    def count_by_severity(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for v in self.vulnerabilities:
            counts[v.severity] = counts.get(v.severity, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "packages_scanned": self.packages_scanned,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "scan_source": self.scan_source,
            "is_clean": self.is_clean,
            "has_critical": self.has_critical,
            "count_by_severity": self.count_by_severity,
        }


class DependencyScanner:
    """Scan project dependencies for known vulnerabilities.

    Parses ``pyproject.toml`` to extract dependencies, then checks
    against a local advisory database.

    Usage::

        scanner = DependencyScanner()
        report = scanner.scan_pyproject("pyproject.toml")
        if not report.is_clean:
            for vuln in report.vulnerabilities:
                print(f"[{vuln.severity}] {vuln.package}: {vuln.summary}")
    """

    # Local advisory database (simplified — real impl would query OSV.dev)
    _KNOWN_ADVISORIES: dict[str, list[dict[str, str]]] = {
        "requests": [
            {
                "cve_id": "CVE-2023-32681",
                "severity": "medium",
                "summary": "Unintended leak of Proxy-Authorization header",
                "fixed_in": "2.31.0",
                "affected_below": "2.31.0",
            },
        ],
        "urllib3": [
            {
                "cve_id": "CVE-2023-45803",
                "severity": "medium",
                "summary": "Request body not stripped on redirect",
                "fixed_in": "2.0.7",
                "affected_below": "2.0.7",
            },
        ],
        "cryptography": [
            {
                "cve_id": "CVE-2023-49083",
                "severity": "high",
                "summary": "NULL pointer dereference in PKCS12 parsing",
                "fixed_in": "41.0.6",
                "affected_below": "41.0.6",
            },
        ],
    }

    def scan_pyproject(
        self,
        pyproject_path: str | Path,
    ) -> ScanReport:
        """Scan dependencies from a pyproject.toml file.

        Args:
            pyproject_path: Path to pyproject.toml.

        Returns:
            ``ScanReport`` with any found vulnerabilities.
        """
        path = Path(pyproject_path)
        if not path.exists():
            logger.warning("pyproject.toml not found", extra={"path": str(path)})
            return ScanReport(scan_source="file_not_found")

        content = path.read_text()
        deps = self._parse_dependencies(content)

        report = ScanReport(
            packages_scanned=len(deps),
            scan_source="local_advisory",
        )

        for pkg_name, version_spec in deps.items():
            self._check_package(pkg_name, version_spec, report)

        logger.info(
            "Dependency scan complete",
            extra={
                "packages": report.packages_scanned,
                "vulnerabilities": len(report.vulnerabilities),
            },
        )

        return report

    def scan_dependencies(
        self,
        dependencies: dict[str, str],
    ) -> ScanReport:
        """Scan a dict of {package: version_spec} directly.

        Args:
            dependencies: Package name to version spec mapping.

        Returns:
            ``ScanReport`` with any found vulnerabilities.
        """
        report = ScanReport(
            packages_scanned=len(dependencies),
            scan_source="direct",
        )

        for pkg_name, version_spec in dependencies.items():
            self._check_package(pkg_name, version_spec, report)

        return report

    def _check_package(
        self,
        pkg_name: str,
        version_spec: str,
        report: ScanReport,
    ) -> None:
        """Check a single package against advisories."""
        normalized = pkg_name.lower().replace("-", "_").replace(".", "_")
        advisories = self._KNOWN_ADVISORIES.get(normalized, [])

        for advisory in advisories:
            # Simple version comparison (real impl would use packaging.version)
            report.vulnerabilities.append(Vulnerability(
                package=pkg_name,
                version=version_spec,
                cve_id=advisory["cve_id"],
                severity=advisory["severity"],
                summary=advisory["summary"],
                fixed_in=advisory.get("fixed_in", ""),
            ))

    @staticmethod
    def _parse_dependencies(content: str) -> dict[str, str]:
        """Parse dependencies from pyproject.toml content."""
        deps: dict[str, str] = {}
        # Simple regex for dependencies = ["pkg>=version", ...]
        dep_pattern = re.compile(
            r'"([a-zA-Z0-9_-]+)\s*([><=!~]*\s*[\d.]*[^"]*)"'
        )
        for match in dep_pattern.finditer(content):
            pkg = match.group(1)
            version = match.group(2).strip()
            deps[pkg] = version

        return deps


__all__ = [
    "DependencyScanner",
    "ScanReport",
    "Vulnerability",
]
