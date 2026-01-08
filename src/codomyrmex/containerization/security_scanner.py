from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

from dataclasses import dataclass, field
import csv
import docker

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger







#!/usr/bin/env python3

Container Security Scanner Module for Codomyrmex Containerization.

This module provides container security scanning, vulnerability assessment,
and compliance checking capabilities using Trivy, Grype, or Docker Scout.
"""

logger = get_logger(__name__)

# Try to import Docker SDK
try:
    DOCKER_AVAILABLE = True
except ImportError:
    docker = None
    DOCKER_AVAILABLE = False

@dataclass
class Vulnerability:
    """Container vulnerability information."""
    cve_id: str
    severity: str  # "UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"
    package: str
    version: str
    fixed_version: Optional[str]
    description: str
    cvss_score: float = 0.0
    references: list[str] = field(default_factory=list)
    layer: Optional[str] = None

@dataclass
class SecurityScanResult:
    """Container security scan results."""
    scan_id: str
    image_name: str
    image_tag: str
    scan_timestamp: datetime
    vulnerabilities: list[Vulnerability] = field(default_factory=list)
    compliance_status: str = "unknown"
    scan_duration: float = 0.0
    scanner_version: str = "1.0.0"
    scanner_name: str = "unknown"
    os_info: Optional[dict[str, str]] = None

class ContainerSecurityScanner:
    """Container security scanning and vulnerability assessment system.

    Supports multiple scanning backends:
    - Trivy (recommended)
    - Grype
    - Docker Scout
    """

    def __init__(
        self,
        scanner_config: Optional[dict[str, Any]] = None,
        preferred_scanner: str = "auto"
    ):
        """Initialize security scanner.

        Args:
            scanner_config: Scanner configuration options
            preferred_scanner: Preferred scanner ("trivy", "grype", "docker-scout", "auto")
        """
        self.scanner_config = scanner_config or {}
        self.preferred_scanner = preferred_scanner
        self._scan_results: dict[str, SecurityScanResult] = {}
        self._available_scanner = self._detect_scanner()

        if self._available_scanner:
            logger.info(f"Container security scanner initialized: {self._available_scanner}")
        else:
            logger.warning("No security scanner available. Install trivy, grype, or docker-scout.")

    def _detect_scanner(self) -> Optional[str]:
        """Detect available security scanner."""
        if self.preferred_scanner != "auto":
            if shutil.which(self.preferred_scanner):
                return self.preferred_scanner
            logger.warning(f"Preferred scanner '{self.preferred_scanner}' not found")

        # Check available scanners in order of preference
        scanners = ["trivy", "grype", "docker"]

        for scanner in scanners:
            if shutil.which(scanner):
                if scanner == "docker":
                    # Check if docker scout is available
                    try:
                        result = subprocess.run(
                            ["docker", "scout", "version"],
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode == 0:
                            return "docker-scout"
                    except (subprocess.SubprocessError, FileNotFoundError):
                        continue
                else:
                    return scanner

        return None

    def is_available(self) -> bool:
        """Check if a security scanner is available."""
        return self._available_scanner is not None

    def scan_image(
        self,
        image_name: str,
        image_tag: str = "latest",
        severity_threshold: str = "UNKNOWN"
    ) -> SecurityScanResult:
        """Scan container image for vulnerabilities.

        Args:
            image_name: Name of the image to scan
            image_tag: Image tag
            severity_threshold: Minimum severity to report

        Returns:
            Security scan results
        """
        scan_id = f"scan_{image_name.replace('/', '_')}_{image_tag}_{int(time.time())}"
        full_image = f"{image_name}:{image_tag}"

        if not self.is_available():
            logger.warning(f"No scanner available. Returning empty scan for {full_image}")
            return SecurityScanResult(
                scan_id=scan_id,
                image_name=image_name,
                image_tag=image_tag,
                scan_timestamp=datetime.now(),
                scanner_name="none",
                compliance_status="unknown"
            )

        start_time = time.time()

        try:
            if self._available_scanner == "trivy":
                scan_result = self._scan_with_trivy(full_image, scan_id, severity_threshold)
            elif self._available_scanner == "grype":
                scan_result = self._scan_with_grype(full_image, scan_id, severity_threshold)
            elif self._available_scanner == "docker-scout":
                scan_result = self._scan_with_docker_scout(full_image, scan_id, severity_threshold)
            else:
                raise CodomyrmexError(f"Unknown scanner: {self._available_scanner}")

            scan_result.scan_duration = time.time() - start_time
            scan_result.scanner_name = self._available_scanner

            # Determine compliance status
            critical_count = sum(1 for v in scan_result.vulnerabilities if v.severity == "CRITICAL")
            high_count = sum(1 for v in scan_result.vulnerabilities if v.severity == "HIGH")

            if critical_count > 0:
                scan_result.compliance_status = "critical"
            elif high_count > 5:
                scan_result.compliance_status = "non_compliant"
            elif high_count > 0:
                scan_result.compliance_status = "warning"
            else:
                scan_result.compliance_status = "compliant"

            self._scan_results[scan_id] = scan_result

            logger.info(
                f"Completed security scan for {full_image}: "
                f"{len(scan_result.vulnerabilities)} vulnerabilities found "
                f"({critical_count} critical, {high_count} high)"
            )

            return scan_result

        except Exception as e:
            logger.error(f"Security scan failed for {full_image}: {e}")
            return SecurityScanResult(
                scan_id=scan_id,
                image_name=image_name,
                image_tag=image_tag,
                scan_timestamp=datetime.now(),
                scan_duration=time.time() - start_time,
                scanner_name=self._available_scanner or "error",
                compliance_status="error"
            )

    def _scan_with_trivy(
        self,
        image: str,
        scan_id: str,
        severity_threshold: str
    ) -> SecurityScanResult:
        """Scan image using Trivy."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            cmd = [
                "trivy", "image",
                "--format", "json",
                "--output", output_file,
                "--severity", severity_threshold.upper() if severity_threshold != "UNKNOWN" else "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"
            ]

            # Add timeout from config
            timeout = self.scanner_config.get("timeout", 300)

            cmd.append(image)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            if result.returncode not in [0, 1]:  # Trivy returns 1 if vulnerabilities found
                raise CodomyrmexError(f"Trivy scan failed: {result.stderr}")

            # Parse results
            with open(output_file, 'r') as f:
                trivy_output = json.load(f)

            vulnerabilities = []
            os_info = None

            for target in trivy_output.get("Results", []):
                target_type = target.get("Type", "")

                # Extract OS info
                if target_type == "os" and not os_info:
                    os_info = {
                        "family": trivy_output.get("Metadata", {}).get("OS", {}).get("Family", "unknown"),
                        "name": trivy_output.get("Metadata", {}).get("OS", {}).get("Name", "unknown")
                    }

                for vuln in target.get("Vulnerabilities", []):
                    vulnerabilities.append(Vulnerability(
                        cve_id=vuln.get("VulnerabilityID", "UNKNOWN"),
                        severity=vuln.get("Severity", "UNKNOWN"),
                        package=vuln.get("PkgName", "unknown"),
                        version=vuln.get("InstalledVersion", "unknown"),
                        fixed_version=vuln.get("FixedVersion"),
                        description=vuln.get("Title", vuln.get("Description", ""))[:500],
                        cvss_score=vuln.get("CVSS", {}).get("nvd", {}).get("V3Score", 0.0),
                        references=vuln.get("References", [])[:5]
                    ))

            # Get scanner version
            version_result = subprocess.run(
                ["trivy", "--version"],
                capture_output=True,
                text=True
            )
            version_match = re.search(r'Version:\s*([\d.]+)', version_result.stdout)
            scanner_version = version_match.group(1) if version_match else "unknown"

            return SecurityScanResult(
                scan_id=scan_id,
                image_name=image.rsplit(":", 1)[0],
                image_tag=image.rsplit(":", 1)[1] if ":" in image else "latest",
                scan_timestamp=datetime.now(),
                vulnerabilities=vulnerabilities,
                scanner_version=scanner_version,
                os_info=os_info
            )

        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def _scan_with_grype(
        self,
        image: str,
        scan_id: str,
        severity_threshold: str
    ) -> SecurityScanResult:
        """Scan image using Grype."""
        try:
            cmd = ["grype", image, "-o", "json"]

            if severity_threshold and severity_threshold != "UNKNOWN":
                cmd.extend(["--fail-on", severity_threshold.lower()])

            timeout = self.scanner_config.get("timeout", 300)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            grype_output = json.loads(result.stdout) if result.stdout else {}

            vulnerabilities = []
            for match in grype_output.get("matches", []):
                vuln = match.get("vulnerability", {})
                artifact = match.get("artifact", {})

                vulnerabilities.append(Vulnerability(
                    cve_id=vuln.get("id", "UNKNOWN"),
                    severity=vuln.get("severity", "UNKNOWN"),
                    package=artifact.get("name", "unknown"),
                    version=artifact.get("version", "unknown"),
                    fixed_version=vuln.get("fix", {}).get("versions", [None])[0] if vuln.get("fix", {}).get("versions") else None,
                    description=vuln.get("description", "")[:500],
                    cvss_score=0.0,  # Grype doesn't always provide CVSS in same format
                    references=vuln.get("urls", [])[:5]
                ))

            # Get scanner version
            version_result = subprocess.run(
                ["grype", "version"],
                capture_output=True,
                text=True
            )
            version_match = re.search(r'Version:\s*([\d.]+)', version_result.stdout)
            scanner_version = version_match.group(1) if version_match else "unknown"

            return SecurityScanResult(
                scan_id=scan_id,
                image_name=image.rsplit(":", 1)[0],
                image_tag=image.rsplit(":", 1)[1] if ":" in image else "latest",
                scan_timestamp=datetime.now(),
                vulnerabilities=vulnerabilities,
                scanner_version=scanner_version
            )

        except json.JSONDecodeError as e:
            raise CodomyrmexError(f"Failed to parse Grype output: {e}")

    def _scan_with_docker_scout(
        self,
        image: str,
        scan_id: str,
        severity_threshold: str
    ) -> SecurityScanResult:
        """Scan image using Docker Scout."""
        try:
            cmd = ["docker", "scout", "cves", image, "--format", "json"]

            timeout = self.scanner_config.get("timeout", 300)

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                text=True
            )

            scout_output = json.loads(result.stdout) if result.stdout else {}

            vulnerabilities = []
            for vuln in scout_output.get("vulnerabilities", []):
                severity = vuln.get("severity", "UNKNOWN").upper()

                # Apply severity filter
                severity_order = ["UNKNOWN", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
                if severity_threshold in severity_order:
                    if severity_order.index(severity) < severity_order.index(severity_threshold):
                        continue

                vulnerabilities.append(Vulnerability(
                    cve_id=vuln.get("id", "UNKNOWN"),
                    severity=severity,
                    package=vuln.get("package", {}).get("name", "unknown"),
                    version=vuln.get("package", {}).get("version", "unknown"),
                    fixed_version=vuln.get("fix", {}).get("version"),
                    description=vuln.get("description", "")[:500],
                    cvss_score=vuln.get("cvss", {}).get("score", 0.0),
                    references=[]
                ))

            return SecurityScanResult(
                scan_id=scan_id,
                image_name=image.rsplit(":", 1)[0],
                image_tag=image.rsplit(":", 1)[1] if ":" in image else "latest",
                scan_timestamp=datetime.now(),
                vulnerabilities=vulnerabilities,
                scanner_version="docker-scout"
            )

        except json.JSONDecodeError as e:
            raise CodomyrmexError(f"Failed to parse Docker Scout output: {e}")

    def get_scan_report(self, scan_id: str) -> Optional[SecurityScanResult]:
        """Get scan report by ID.

        Args:
            scan_id: Scan ID

        Returns:
            Scan result or None if not found
        """
        return self._scan_results.get(scan_id)

    def list_scans(self, image_name: Optional[str] = None) -> list[dict[str, Any]]:
        """List security scans.

        Args:
            image_name: Filter by image name

        Returns:
            List of scan summaries
        """
        scans = []

        for scan_id, scan_result in self._scan_results.items():
            if image_name and scan_result.image_name != image_name:
                continue

            scans.append({
                "scan_id": scan_id,
                "image_name": scan_result.image_name,
                "image_tag": scan_result.image_tag,
                "scan_timestamp": scan_result.scan_timestamp.isoformat(),
                "vulnerability_count": len(scan_result.vulnerabilities),
                "compliance_status": scan_result.compliance_status,
                "scanner": scan_result.scanner_name,
                "critical_vulnerabilities": sum(1 for v in scan_result.vulnerabilities if v.severity == "CRITICAL"),
                "high_vulnerabilities": sum(1 for v in scan_result.vulnerabilities if v.severity == "HIGH"),
                "medium_vulnerabilities": sum(1 for v in scan_result.vulnerabilities if v.severity == "MEDIUM"),
                "low_vulnerabilities": sum(1 for v in scan_result.vulnerabilities if v.severity == "LOW")
            })

        scans.sort(key=lambda s: s["scan_timestamp"], reverse=True)
        return scans

    def generate_compliance_report(self, scan_id: str) -> dict[str, Any]:
        """Generate compliance report for a scan.

        Args:
            scan_id: Scan ID

        Returns:
            Compliance report
        """
        scan_result = self._scan_results.get(scan_id)
        if not scan_result:
            raise CodomyrmexError(f"Scan not found: {scan_id}")

        # Count by severity
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "UNKNOWN": 0
        }
        for vuln in scan_result.vulnerabilities:
            severity_counts[vuln.severity] = severity_counts.get(vuln.severity, 0) + 1

        # Find fixable vulnerabilities
        fixable = [v for v in scan_result.vulnerabilities if v.fixed_version]

        # Generate recommendations
        recommendations = []
        if severity_counts["CRITICAL"] > 0:
            recommendations.append(f"URGENT: Fix {severity_counts['CRITICAL']} critical vulnerabilities immediately")
        if severity_counts["HIGH"] > 0:
            recommendations.append(f"Fix {severity_counts['HIGH']} high-severity vulnerabilities")
        if len(fixable) > 0:
            recommendations.append(f"{len(fixable)} vulnerabilities have available fixes - update packages")
        if scan_result.os_info:
            recommendations.append(f"Consider using a minimal base image (current: {scan_result.os_info.get('name', 'unknown')})")

        if not recommendations:
            recommendations.append("No significant vulnerabilities found - image meets security standards")

        return {
            "scan_id": scan_id,
            "image": f"{scan_result.image_name}:{scan_result.image_tag}",
            "compliance_status": scan_result.compliance_status,
            "scanner": scan_result.scanner_name,
            "scanner_version": scan_result.scanner_version,
            "summary": {
                "total_vulnerabilities": len(scan_result.vulnerabilities),
                "critical": severity_counts["CRITICAL"],
                "high": severity_counts["HIGH"],
                "medium": severity_counts["MEDIUM"],
                "low": severity_counts["LOW"],
                "unknown": severity_counts["UNKNOWN"],
                "fixable": len(fixable)
            },
            "top_vulnerabilities": [
                {
                    "cve_id": v.cve_id,
                    "severity": v.severity,
                    "package": v.package,
                    "current_version": v.version,
                    "fixed_version": v.fixed_version,
                    "cvss_score": v.cvss_score
                }
                for v in sorted(
                    scan_result.vulnerabilities,
                    key=lambda x: (
                        ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"].index(x.severity),
                        -x.cvss_score
                    )
                )[:10]
            ],
            "recommendations": recommendations,
            "scan_metadata": {
                "scan_timestamp": scan_result.scan_timestamp.isoformat(),
                "scan_duration": scan_result.scan_duration,
                "os_info": scan_result.os_info
            }
        }

    def export_results(
        self,
        scan_id: str,
        output_path: str,
        format: str = "json"
    ) -> str:
        """Export scan results to file.

        Args:
            scan_id: Scan ID
            output_path: Output file path
            format: Output format ("json", "csv", "sarif")

        Returns:
            Path to exported file
        """
        scan_result = self._scan_results.get(scan_id)
        if not scan_result:
            raise CodomyrmexError(f"Scan not found: {scan_id}")

        output_path = Path(output_path)

        if format == "json":
            data = {
                "scan_id": scan_result.scan_id,
                "image": f"{scan_result.image_name}:{scan_result.image_tag}",
                "timestamp": scan_result.scan_timestamp.isoformat(),
                "scanner": scan_result.scanner_name,
                "compliance_status": scan_result.compliance_status,
                "vulnerabilities": [
                    {
                        "cve_id": v.cve_id,
                        "severity": v.severity,
                        "package": v.package,
                        "version": v.version,
                        "fixed_version": v.fixed_version,
                        "description": v.description,
                        "cvss_score": v.cvss_score
                    }
                    for v in scan_result.vulnerabilities
                ]
            }
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)

        elif format == "csv":
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["CVE ID", "Severity", "Package", "Version", "Fixed Version", "CVSS Score"])
                for v in scan_result.vulnerabilities:
                    writer.writerow([v.cve_id, v.severity, v.package, v.version, v.fixed_version or "N/A", v.cvss_score])

        elif format == "sarif":
            # SARIF format for GitHub Security tab integration
            sarif = {
                "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                "version": "2.1.0",
                "runs": [{
                    "tool": {
                        "driver": {
                            "name": scan_result.scanner_name,
                            "version": scan_result.scanner_version,
                            "rules": []
                        }
                    },
                    "results": [
                        {
                            "ruleId": v.cve_id,
                            "level": {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note"}.get(v.severity, "note"),
                            "message": {"text": f"{v.package}@{v.version}: {v.description}"},
                            "locations": [{"physicalLocation": {"artifactLocation": {"uri": f"package:{v.package}"}}}]
                        }
                        for v in scan_result.vulnerabilities
                    ]
                }]
            }
            with open(output_path, 'w') as f:
                json.dump(sarif, f, indent=2)

        else:
            raise CodomyrmexError(f"Unsupported export format: {format}")

        logger.info(f"Exported scan results to {output_path}")
        return str(output_path)

def scan_container_security(
    image_name: str,
    image_tag: str = "latest",
    scanner_config: Optional[dict[str, Any]] = None,
    severity_threshold: str = "UNKNOWN"
) -> SecurityScanResult:
    """Scan container image for security vulnerabilities.

    Args:
        image_name: Name of the image to scan
        image_tag: Image tag
        scanner_config: Scanner configuration options
        severity_threshold: Minimum severity to report

    Returns:
        Security scan results
    """
    scanner = ContainerSecurityScanner(scanner_config)
    return scanner.scan_image(image_name, image_tag, severity_threshold)
