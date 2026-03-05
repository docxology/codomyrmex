"""Security Audit — demonstrates codomyrmex security, crypto, maintenance, system_discovery.

Integrates with:
- codomyrmex.security for vulnerability scanning, secret detection, code audit
- codomyrmex.crypto.graphy.hashing for cryptographic hash operations
- codomyrmex.maintenance for project structure and dependency analysis
- codomyrmex.system_discovery for module health and capability scanning
- codomyrmex.logging_monitoring for structured logging

Example:
    >>> auditor = SecurityAudit()
    >>> health = auditor.system_health()
    >>> print(health["modules_found"])
    >>> hashed = auditor.hash_and_verify(b"secret data")
    >>> print(hashed["verified"])
"""

from pathlib import Path
from typing import Any

from codomyrmex.crypto.graphy.hashing import hash_data, verify_hash
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.maintenance import analyze_project_structure, check_dependencies
from codomyrmex.system_discovery import CapabilityScanner, HealthChecker, SystemDiscovery

HAS_SECURITY_MODULES = True  # Exported for integration tests

logger = get_logger(__name__)

# Security imports are conditional since some backends may not be available
try:
    from codomyrmex.security import (
        audit_code_security,
        scan_directory_for_secrets,
        scan_vulnerabilities,
    )
    HAS_DIGITAL_SECURITY = True
except ImportError:
    HAS_DIGITAL_SECURITY = False
    audit_code_security = None  # type: ignore[assignment]
    scan_directory_for_secrets = None  # type: ignore[assignment]
    scan_vulnerabilities = None  # type: ignore[assignment]


class SecurityAudit:
    """Demonstrates security + crypto + maintenance + system_discovery integration.

    Provides a unified interface for security scanning, cryptographic
    operations, project health checking, and system introspection.

    Attributes:
        discovery: SystemDiscovery instance for module discovery.
        scanner: CapabilityScanner for scanning module capabilities.

    Example:
        >>> auditor = SecurityAudit()
        >>> print(auditor.hash_and_verify(b"hello world")["algorithm"])
    """

    def __init__(self) -> None:
        """Initialize SecurityAudit with system discovery."""
        self.discovery = SystemDiscovery()
        self.scanner = CapabilityScanner()
        logger.info("SecurityAudit initialized")

    def hash_and_verify(
        self,
        data: bytes | str,
        algorithm: str = "sha256",
    ) -> dict[str, Any]:
        """Hash data and verify the hash using codomyrmex.crypto.

        Demonstrates the crypto.graphy.hashing submodule for
        SHA-256 (default) hashing and hash verification.

        Args:
            data: Data to hash. Strings are UTF-8 encoded.
            algorithm: Hash algorithm (sha256, sha512, md5, blake2b).

        Returns:
            Dictionary with:
            - data_length: int
            - algorithm: str
            - hex_digest: str
            - verified: bool (re-verified against same data)
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        hex_digest = hash_data(data, algorithm)
        verified = verify_hash(data, hex_digest, algorithm)

        logger.debug(f"Hashed {len(data)} bytes with {algorithm}, verified={verified}")
        return {
            "data_length": len(data),
            "algorithm": algorithm,
            "hex_digest": hex_digest,
            "verified": verified,
        }

    def audit_path(self, path: str | Path) -> dict[str, Any]:
        """Run security audit on a file or directory.

        Invokes vulnerability scanning and secret detection from
        codomyrmex.security.digital when available.

        Args:
            path: Path to file or directory to audit.

        Returns:
            Dictionary with vulnerability and secrets findings.
        """
        path_str = str(path)
        logger.info(f"Running security audit on: {path_str}")

        result: dict[str, Any] = {
            "path": path_str,
            "security_available": HAS_DIGITAL_SECURITY,
            "vulnerabilities": {},
            "secrets": {},
            "code_audit": {},
        }

        if not HAS_DIGITAL_SECURITY:
            result["note"] = "Digital security backend not installed"
            return result

        try:
            vuln = scan_vulnerabilities(path_str)
            result["vulnerabilities"] = {
                "count": len(vuln.findings) if hasattr(vuln, "findings") else 0,
                "type": type(vuln).__name__,
            }
        except Exception as e:
            logger.warning(f"scan_vulnerabilities failed: {e}")
            result["vulnerabilities"] = {"error": str(e)}

        try:
            secrets = scan_directory_for_secrets(path_str)
            result["secrets"] = {
                "count": len(secrets) if secrets else 0,
            }
        except Exception as e:
            logger.warning(f"scan_directory_for_secrets failed: {e}")
            result["secrets"] = {"error": str(e)}

        try:
            audit = audit_code_security(path_str)
            result["code_audit"] = audit if isinstance(audit, dict) else {"result": str(audit)}
        except Exception as e:
            logger.warning(f"audit_code_security failed: {e}")
            result["code_audit"] = {"error": str(e)}

        return result

    def system_health(self) -> dict[str, Any]:
        """Run system health check using system_discovery.

        Uses SystemDiscovery and CapabilityScanner to enumerate
        available codomyrmex modules and their health status.

        Returns:
            Dictionary with:
            - modules_found: int (discovered modules)
            - discovery_type: str (class name)
            - scanner_type: str (class name)
            - health_checker: str (class name)
        """
        logger.info("Running system health check")

        result: dict[str, Any] = {
            "discovery_type": type(self.discovery).__name__,
            "scanner_type": type(self.scanner).__name__,
            "health_checker": HealthChecker.__name__,
            "modules_found": 0,
        }

        try:
            modules = self.discovery.discover_modules()
            result["modules_found"] = len(modules) if modules else 0
            result["module_names"] = list(modules.keys())[:10] if isinstance(modules, dict) else []
        except Exception as e:
            logger.warning(f"discover_modules failed: {e}")
            result["error"] = str(e)

        return result

    def project_deps(self, path: str | Path = ".") -> dict[str, Any]:
        """Analyze project structure and dependencies via maintenance.

        Uses codomyrmex.maintenance functions to inspect project
        layout and dependency configuration.

        Args:
            path: Path to project root directory.

        Returns:
            Dictionary with structure and dependency analysis.
        """
        path_str = str(path)
        logger.info(f"Analyzing project deps at: {path_str}")

        result: dict[str, Any] = {
            "path": path_str,
            "structure": {},
            "dependencies": {},
        }

        try:
            structure = analyze_project_structure(path_str)
            result["structure"] = structure if isinstance(structure, dict) else {"raw": str(structure)}
        except Exception as e:
            logger.warning(f"analyze_project_structure failed: {e}")
            result["structure"] = {"error": str(e)}

        try:
            deps = check_dependencies(path_str)
            result["dependencies"] = deps if isinstance(deps, dict) else {"raw": str(deps)}
        except Exception as e:
            logger.warning(f"check_dependencies failed: {e}")
            result["dependencies"] = {"error": str(e)}

        return result
