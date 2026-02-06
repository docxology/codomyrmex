"""
SBOM (Software Bill of Materials) Generation

Generate and manage SBOMs for supply chain security.
"""

import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path
import hashlib


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
    dependencies: List[str] = field(default_factory=list)
    vulnerabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
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
    components: List[Component] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    format: SBOMFormat = SBOMFormat.CYCLONEDX
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
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
        with open(path, 'w') as f:
            f.write(self.to_json())


class SBOMGenerator:
    """Generate SBOMs from various sources."""
    
    def __init__(self):
        self._components: List[Component] = []
    
    def from_requirements(self, requirements_path: str) -> List[Component]:
        """Parse requirements.txt file."""
        components = []
        
        try:
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse package==version
                    if '==' in line:
                        name, version = line.split('==', 1)
                    elif '>=' in line:
                        name, version = line.split('>=', 1)
                    else:
                        name, version = line, "unknown"
                    
                    name = name.strip()
                    version = version.split('[')[0].strip()  # Remove extras
                    
                    components.append(Component(
                        name=name,
                        version=version,
                        purl=f"pkg:pypi/{name}@{version}",
                    ))
        except FileNotFoundError:
            pass
        
        self._components.extend(components)
        return components
    
    def from_package_json(self, package_json_path: str) -> List[Component]:
        """Parse package.json file."""
        components = []
        
        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)
            
            deps = data.get("dependencies", {})
            deps.update(data.get("devDependencies", {}))
            
            for name, version in deps.items():
                # Clean version string
                version = version.lstrip('^~>=<')
                components.append(Component(
                    name=name,
                    version=version,
                    purl=f"pkg:npm/{name}@{version}",
                ))
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        self._components.extend(components)
        return components
    
    def from_pyproject(self, pyproject_path: str) -> List[Component]:
        """Parse pyproject.toml dependencies."""
        components = []
        
        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                data = tomllib.load(f)
            
            deps = data.get("project", {}).get("dependencies", [])
            for dep in deps:
                # Simple parsing
                if '>=' in dep:
                    name, version = dep.split('>=', 1)
                elif '==' in dep:
                    name, version = dep.split('==', 1)
                else:
                    name, version = dep, "latest"
                
                components.append(Component(
                    name=name.strip(),
                    version=version.strip(),
                    purl=f"pkg:pypi/{name.strip()}@{version.strip()}",
                ))
        except (FileNotFoundError, ImportError):
            pass
        
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
        self._known_vulns: Dict[str, List[str]] = {}
    
    def add_vulnerability_db(self, vulns: Dict[str, List[str]]) -> None:
        """Add vulnerability database."""
        self._known_vulns.update(vulns)
    
    def scan(self, sbom: SBOM) -> Dict[str, List[str]]:
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
    
    def verify_signature(self, path: str, signature_path: str) -> bool:
        """Verify file signature (placeholder)."""
        # Would integrate with GPG or similar
        return True
    
    def compute_file_hash(self, path: str, algorithm: str = "sha256") -> str:
        """Compute file hash."""
        h = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()


__all__ = [
    "SBOM",
    "SBOMFormat",
    "SBOMGenerator",
    "Component",
    "LicenseType",
    "VulnerabilityScanner",
    "SupplyChainVerifier",
]
