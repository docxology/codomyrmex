"""
SBOM (Software Bill of Materials) Generation

Generate and manage SBOMs for supply chain security.
"""

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class SBOMFormat(Enum):
    """SBOM output formats."""

    SPDX = "spdx"
    CYCLONEDX = "cyclonedx"
    SWID = "swid"


class LicenseType(Enum):
    """Common license types."""

    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    BSD_3 = "BSD-3-Clause"
    ISC = "ISC"
    UNKNOWN = "unknown"


@dataclass
class Component:
    """A software component/dependency."""

    name: str
    version: str
    purl: str = ""  # Package URL
    license: LicenseType = LicenseType.UNKNOWN
    supplier: str = ""
    checksum: str = ""
    dependencies: list[str] = field(default_factory=list)
    vulnerabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "purl": self.purl,
            "license": self.license.value,
            "supplier": self.supplier,
            "checksum": self.checksum,
            "dependencies": self.dependencies,
            "vulnerabilities": self.vulnerabilities,
        }


@dataclass
class SBOM:
    """Software Bill of Materials."""

    name: str
    version: str
    components: list[Component] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    format: SBOMFormat = SBOMFormat.CYCLONEDX
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "format": self.format.value,
            "created_at": self.created_at.isoformat(),
            "components": [c.to_dict() for c in self.components],
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def save(self, path: str) -> None:
        """Save data to the specified destination."""
        with open(path, "w") as f:
            f.write(self.to_json())


class SBOMGenerator:
    """Generate SBOMs from various sources."""

    def __init__(self):
        self._components: list[Component] = []

    def from_requirements(self, requirements_path: str) -> list[Component]:
        """Parse requirements.txt file."""
        components = []

        try:
            with open(requirements_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Parse package==version
                    if "==" in line:
                        name, version = line.split("==", 1)
                    elif ">=" in line:
                        name, version = line.split(">=", 1)
                    else:
                        name, version = line, "unknown"

                    name = name.strip()
                    version = version.split("[")[0].strip()  # Remove extras

                    components.append(
                        Component(
                            name=name,
                            version=version,
                            purl=f"pkg:pypi/{name}@{version}",
                        )
                    )
        except FileNotFoundError as e:
            logger.warning("SBOM: requirements file not found: %s", e)

        self._components.extend(components)
        return components

    def from_package_json(self, package_json_path: str) -> list[Component]:
        """Parse package.json file."""
        components = []

        try:
            with open(package_json_path) as f:
                data = json.load(f)

            deps = data.get("dependencies", {})
            deps.update(data.get("devDependencies", {}))

            for name, version in deps.items():
                # Clean version string
                version = version.lstrip("^~>=<")
                components.append(
                    Component(
                        name=name,
                        version=version,
                        purl=f"pkg:npm/{name}@{version}",
                    )
                )
        except FileNotFoundError as e:
            logger.warning("SBOM: package.json not found, skipping npm deps: %s", e)
        except json.JSONDecodeError as e:
            logger.warning(
                "SBOM: malformed package.json, skipping npm deps: %s", str(e)
            )

        self._components.extend(components)
        return components

    def from_pyproject(self, pyproject_path: str) -> list[Component]:
        """Parse pyproject.toml dependencies."""
        components = []

        try:
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            deps = data.get("project", {}).get("dependencies", [])
            for dep in deps:
                # Simple parsing
                if ">=" in dep:
                    name, version = dep.split(">=", 1)
                elif "==" in dep:
                    name, version = dep.split("==", 1)
                else:
                    name, version = dep, "latest"

                components.append(
                    Component(
                        name=name.strip(),
                        version=version.strip(),
                        purl=f"pkg:pypi/{name.strip()}@{version.strip()}",
                    )
                )
        except (FileNotFoundError, ImportError) as e:
            logger.warning("SBOM: failed to parse pyproject.toml: %s", e)

        self._components.extend(components)
        return components

    def generate(
        self,
        name: str,
        version: str,
        sbom_format: SBOMFormat = SBOMFormat.CYCLONEDX,
    ) -> SBOM:
        """Generate SBOM from collected components."""
        return SBOM(
            name=name,
            version=version,
            components=self._components,
            format=sbom_format,
        )


class VulnerabilityScanner:
    """Scan components for known vulnerabilities."""

    def __init__(self):
        self._known_vulns: dict[str, list[str]] = {}

    def add_vulnerability_db(self, vulns: dict[str, list[str]]) -> None:
        """Add vulnerability database."""
        self._known_vulns.update(vulns)

    def scan(self, sbom: SBOM) -> dict[str, list[str]]:
        """Scan SBOM for vulnerabilities."""
        findings = {}

        for component in sbom.components:
            key = f"{component.name}:{component.version}"
            if key in self._known_vulns:
                findings[key] = self._known_vulns[key]
                component.vulnerabilities = self._known_vulns[key]

        return findings


class SupplyChainVerifier:
    """Verify supply chain integrity."""

    def verify_checksum(self, component: Component, expected: str) -> bool:
        """Verify component checksum."""
        return component.checksum == expected

    def verify_digest(
        self, path: str, digest_path: str, algorithm: str = "sha256"
    ) -> bool:
        """Check a file against a published hex digest (e.g. a ``.sha256`` file).

        This proves integrity against the published digest only, not who
        published it; use :meth:`verify_signature` for authenticity. The digest
        file may be in ``sha256sum`` format (``<hex>  <filename>``).
        """
        try:
            with open(digest_path) as f:
                expected = f.read().split()[0].strip().lower()
            actual = self.compute_file_hash(path, algorithm)
        except (OSError, IndexError, ValueError) as e:
            logger.warning("Digest verification failed for %s: %s", path, e)
            return False
        return hmac.compare_digest(actual, expected)

    def verify_signature(
        self, path: str, signature_path: str, public_key_path: str
    ) -> bool:
        """Verify a detached signature over a file with a PEM public key.

        Supports Ed25519 and Ed448 keys, RSA (PKCS#1 v1.5 with SHA-256, as
        produced by ``openssl dgst -sha256 -sign``) and ECDSA with SHA-256.
        The signature file holds the raw signature bytes or their base64
        encoding.

        Returns:
            True only if the signature is valid for the file and key. Unreadable
            files and invalid signatures return False (and are logged).

        Raises:
            ValueError: If the public key type is not supported.
        """
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import (
            ec,
            ed448,
            ed25519,
            padding,
            rsa,
        )

        try:
            with open(path, "rb") as f:
                data = f.read()
            with open(signature_path, "rb") as f:
                signature = _decode_signature(f.read())
            with open(public_key_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
        except (OSError, ValueError) as e:
            logger.warning("Signature verification failed for %s: %s", path, e)
            return False

        try:
            if isinstance(public_key, (ed25519.Ed25519PublicKey, ed448.Ed448PublicKey)):
                public_key.verify(signature, data)
            elif isinstance(public_key, rsa.RSAPublicKey):
                public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
            elif isinstance(public_key, ec.EllipticCurvePublicKey):
                public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            else:
                raise ValueError(
                    f"Unsupported public key type: {type(public_key).__name__}"
                )
        except InvalidSignature:
            logger.warning("Invalid signature for %s", path)
            return False
        return True

    def compute_file_hash(self, path: str, algorithm: str = "sha256") -> str:
        """Compute file hash."""
        h = hashlib.new(algorithm)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


def _decode_signature(raw: bytes) -> bytes:
    """Return signature bytes from a raw or base64-encoded signature file."""
    text = raw.strip()
    try:
        decoded = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        return raw
    # Raw binary signatures are almost never valid base64; treat a clean decode
    # of printable input as the base64 form.
    return decoded if text.isascii() and text else raw


__all__ = [
    "SBOM",
    "Component",
    "LicenseType",
    "SBOMFormat",
    "SBOMGenerator",
    "SupplyChainVerifier",
    "VulnerabilityScanner",
]
