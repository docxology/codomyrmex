"""Container Security Scanner for Codomyrmex.

Provides container security scanning capabilities including:
- Vulnerability detection via Trivy
- Configuration audit
- Compliance checking
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class VulnerabilitySeverity(Enum):
    """Severity levels for vulnerabilities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Represents a detected vulnerability."""
    id: str
    severity: VulnerabilitySeverity
    title: str
    description: str
    package: str | None = None
    version: str | None = None
    fixed_version: str | None = None
    cve_ids: list[str] = field(default_factory=list)


@dataclass
class SecurityScanResult:
    """Result of a security scan."""
    image: str
    scan_time: datetime
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    passed: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def critical_count(self) -> int:
        """Count critical vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL])

    @property
    def high_count(self) -> int:
        """Count high-severity vulnerabilities."""
        return len([v for v in self.vulnerabilities if v.severity == VulnerabilitySeverity.HIGH])

    def summary(self) -> dict[str, int]:
        """Get vulnerability count by severity."""
        counts = {s.value: 0 for s in VulnerabilitySeverity}
        for v in self.vulnerabilities:
            counts[v.severity.value] += 1
        return counts


def _trivy_cli() -> str:
    """Return path to Trivy CLI or raise NotImplementedError."""
    cli = shutil.which("trivy")
    if not cli:
        raise NotImplementedError(
            "Trivy CLI not available. Install Trivy to perform container security scanning. "
            "See https://trivy.dev/latest/getting-started/installation/"
        )
    return cli


def _parse_trivy_results(data: dict) -> list[Vulnerability]:
    """Parse Trivy JSON output into Vulnerability objects."""
    vulns: list[Vulnerability] = []
    severity_map = {
        "CRITICAL": VulnerabilitySeverity.CRITICAL,
        "HIGH": VulnerabilitySeverity.HIGH,
        "MEDIUM": VulnerabilitySeverity.MEDIUM,
        "LOW": VulnerabilitySeverity.LOW,
        "UNKNOWN": VulnerabilitySeverity.INFO,
    }
    for result in data.get("Results", []):
        for v in result.get("Vulnerabilities") or []:
            sev = severity_map.get(v.get("Severity", "UNKNOWN"), VulnerabilitySeverity.INFO)
            vulns.append(Vulnerability(
                id=v.get("VulnerabilityID", "UNKNOWN"),
                severity=sev,
                title=v.get("Title", v.get("VulnerabilityID", "")),
                description=v.get("Description", ""),
                package=v.get("PkgName"),
                version=v.get("InstalledVersion"),
                fixed_version=v.get("FixedVersion"),
                cve_ids=[v["VulnerabilityID"]] if v.get("VulnerabilityID", "").startswith("CVE-") else [],
            ))
    return vulns


class SecurityScanner:
    """Security scanner backed by Trivy CLI."""

    def __init__(self):
        """Initialize the security scanner."""
        self._rules = []

    def scan(self, image: str) -> dict:
        """Scan an image for vulnerabilities using Trivy.

        Raises:
            NotImplementedError: If Trivy CLI is not installed.
        """
        cli = _trivy_cli()
        try:
            result = subprocess.run(
                [cli, "image", "--format", "json", "--quiet", image],
                check=True, capture_output=True, text=True, timeout=120,
            )
            data = json.loads(result.stdout)
            vulns = _parse_trivy_results(data)
            return {
                "image": image,
                "status": "scanned",
                "vulnerabilities": [
                    {"id": v.id, "severity": v.severity.value, "title": v.title,
                     "package": v.package, "version": v.version}
                    for v in vulns
                ],
            }
        except subprocess.CalledProcessError as e:
            raise NotImplementedError(
                f"Trivy scan failed for image '{image}': {e.stderr.strip()}"
            ) from e


class ContainerSecurityScanner:
    """
    Container security scanner for vulnerability detection via Trivy.

    Requires Trivy CLI: https://trivy.dev/latest/getting-started/installation/
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the security scanner.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._scan_history: list[SecurityScanResult] = []

    def scan_image(self, image: str, **kwargs) -> SecurityScanResult:
        """
        Scan a container image for vulnerabilities using Trivy.

        Args:
            image: Image name/tag to scan
            **kwargs: Additional options (severity_filter: list[str])

        Returns:
            SecurityScanResult with real findings from Trivy

        Raises:
            NotImplementedError: If Trivy CLI is not installed
        """
        cli = _trivy_cli()
        severity_filter = kwargs.get("severity_filter", [])
        cmd = [cli, "image", "--format", "json", "--quiet"]
        if severity_filter:
            cmd.extend(["--severity", ",".join(s.upper() for s in severity_filter)])
        cmd.append(image)

        try:
            proc = subprocess.run(
                cmd, check=True, capture_output=True, text=True, timeout=120,
            )
            data = json.loads(proc.stdout)
            vulns = _parse_trivy_results(data)
            passed = not any(
                v.severity in (VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH)
                for v in vulns
            )
            result = SecurityScanResult(
                image=image,
                scan_time=datetime.now(),
                vulnerabilities=vulns,
                passed=passed,
                metadata={"trivy_schema_version": data.get("SchemaVersion")},
            )
        except subprocess.CalledProcessError as e:
            result = SecurityScanResult(
                image=image,
                scan_time=datetime.now(),
                passed=False,
                error=f"Trivy scan failed: {e.stderr.strip()}",
            )

        self._scan_history.append(result)
        return result

    def scan_container(self, container_id: str, **kwargs) -> SecurityScanResult:
        """
        Scan a running container for vulnerabilities using Trivy.

        Args:
            container_id: Container ID or name
            **kwargs: Additional options

        Returns:
            SecurityScanResult with real findings

        Raises:
            NotImplementedError: If Trivy CLI is not installed
        """
        cli = _trivy_cli()
        try:
            proc = subprocess.run(
                [cli, "image", "--format", "json", "--quiet", container_id],
                check=True, capture_output=True, text=True, timeout=120,
            )
            data = json.loads(proc.stdout)
            vulns = _parse_trivy_results(data)
            passed = not any(
                v.severity in (VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH)
                for v in vulns
            )
            result = SecurityScanResult(
                image=container_id,
                scan_time=datetime.now(),
                vulnerabilities=vulns,
                passed=passed,
            )
        except subprocess.CalledProcessError as e:
            result = SecurityScanResult(
                image=container_id,
                scan_time=datetime.now(),
                passed=False,
                error=f"Trivy scan failed: {e.stderr.strip()}",
            )

        self._scan_history.append(result)
        return result

    def check_compliance(self, image: str, policy: str = "default") -> SecurityScanResult:
        """
        Check container against compliance policy using Trivy misconfiguration scan.

        Args:
            image: Image to check
            policy: Policy name to apply (used as metadata label)

        Returns:
            SecurityScanResult with compliance status from Trivy

        Raises:
            NotImplementedError: If Trivy CLI is not installed
        """
        cli = _trivy_cli()
        try:
            proc = subprocess.run(
                [cli, "image", "--format", "json", "--quiet",
                 "--scanners", "vuln,misconfig", image],
                check=True, capture_output=True, text=True, timeout=120,
            )
            data = json.loads(proc.stdout)
            vulns = _parse_trivy_results(data)
            passed = not any(
                v.severity in (VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH)
                for v in vulns
            )
            result = SecurityScanResult(
                image=image,
                scan_time=datetime.now(),
                vulnerabilities=vulns,
                passed=passed,
                metadata={"policy": policy},
            )
        except subprocess.CalledProcessError as e:
            result = SecurityScanResult(
                image=image,
                scan_time=datetime.now(),
                passed=False,
                error=f"Trivy compliance check failed: {e.stderr.strip()}",
                metadata={"policy": policy},
            )

        self._scan_history.append(result)
        return result

    def get_scan_history(self) -> list[SecurityScanResult]:
        """Get history of all scans performed."""
        return self._scan_history.copy()

    def clear_history(self) -> None:
        """Clear scan history."""
        self._scan_history.clear()


def scan_container_security(
    image: str,
    scanner: ContainerSecurityScanner | None = None,
    **kwargs
) -> SecurityScanResult:
    """Scan a container image for security issues.

    Args:
        image: Image name/tag to scan
        scanner: Optional pre-configured scanner instance
        **kwargs: Additional options passed to scan_image

    Returns:
        SecurityScanResult with findings

    Raises:
        NotImplementedError: If Trivy CLI is not installed
    """
    if scanner is None:
        scanner = ContainerSecurityScanner()
    return scanner.scan_image(image, **kwargs)
