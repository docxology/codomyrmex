"""API Versioning Implementation for Codomyrmex

This module provides API versioning capabilities with version management,
backward compatibility, and migration support.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


# Simple semantic version implementation (no external dependencies)
class SimpleVersion:
    """Simple semantic version implementation."""

    def __init__(self, version_str: str):
        parts = version_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid semantic version: {version_str}")
        try:
            self.major = int(parts[0])
            self.minor = int(parts[1])
            self.patch = int(parts[2])
        except ValueError:
            raise ValueError(f"Invalid semantic version components: {version_str}")

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other):
        if not isinstance(other, SimpleVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other):
        if not isinstance(other, SimpleVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def is_compatible(self, other):
        """Check if compatible (same major version)."""
        return self.major == other.major


class VersionFormat(Enum):
    """Supported API version formats."""
    SEMVER = "semver"  # 1.0.0
    DATE = "date"      # 2024-01-01
    INTEGER = "int"    # 1, 2, 3


@dataclass
class APIVersion:
    """Represents an API version."""
    version: str
    format: VersionFormat
    release_date: datetime
    description: str = ""
    deprecated: bool = False
    deprecated_date: datetime | None = None
    breaking_changes: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate version format."""
        if self.format == VersionFormat.SEMVER:
            try:
                SimpleVersion(self.version)
            except ValueError:
                raise ValueError(f"Invalid semantic version: {self.version}")
        elif self.format == VersionFormat.DATE:
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.version):
                raise ValueError(f"Invalid date format (expected YYYY-MM-DD): {self.version}")
        elif self.format == VersionFormat.INTEGER:
            if not self.version.isdigit():
                raise ValueError(f"Invalid integer version: {self.version}")

    def is_compatible_with(self, other_version: 'APIVersion') -> bool:
        """
        Check if this version is compatible with another version.

        Args:
            other_version: Version to check compatibility with

        Returns:
            True if compatible
        """
        if self.format != other_version.format:
            return False

        if self.format == VersionFormat.SEMVER:
            self_ver = SimpleVersion(self.version)
            other_ver = SimpleVersion(other_version.version)
            # Compatible if major version is the same
            return self_ver.is_compatible(other_ver)

        # For date and integer versions, assume backward compatibility
        return True

    def __lt__(self, other: 'APIVersion') -> bool:
        """Compare versions for ordering."""
        if self.format != other.format:
            return False

        if self.format == VersionFormat.SEMVER:
            return SimpleVersion(self.version) < SimpleVersion(other.version)
        elif self.format == VersionFormat.DATE:
            return self.version < other.version
        else:  # INTEGER
            return int(self.version) < int(other.version)

    def __str__(self) -> str:
        """String representation."""
        return f"v{self.version}"


@dataclass
class VersionedEndpoint:
    """Represents a versioned API endpoint."""
    path: str
    versions: dict[str, Callable]  # version -> handler
    default_version: str
    supported_methods: list[str] = field(default_factory=list)
    deprecated_versions: list[str] = field(default_factory=list)

    def get_handler(self, version: str | None = None) -> Callable:
        """
        Get the handler for a specific version.

        Args:
            version: Version to get handler for

        Returns:
            Handler function
        """
        if version is None:
            version = self.default_version

        if version in self.deprecated_versions:
            logger.warning(f"Using deprecated version {version} for endpoint {self.path}")

        if version not in self.versions:
            raise ValueError(f"Version {version} not supported for endpoint {self.path}")

        return self.versions[version]

    def add_version(self, version: str, handler: Callable) -> None:
        """
        Add a version handler.

        Args:
            version: Version string
            handler: Handler function
        """
        self.versions[version] = handler
        if version not in self.supported_methods:
            self.supported_methods.append(version)

    def deprecate_version(self, version: str) -> None:
        """
        Mark a version as deprecated.

        Args:
            version: Version to deprecate
        """
        if version in self.versions and version not in self.deprecated_versions:
            self.deprecated_versions.append(version)
            logger.info(f"Deprecated version {version} for endpoint {self.path}")


class APIVersionManager:
    """
    Manages API versions and versioned endpoints.
    """

    def __init__(self, default_version: str = "1.0.0", version_format: VersionFormat = VersionFormat.SEMVER):
        """
        Initialize the version manager.

        Args:
            default_version: Default API version
            version_format: Version format to use
        """
        self.default_version = default_version
        self.version_format = version_format
        self.versions: dict[str, APIVersion] = {}
        self.endpoints: dict[str, VersionedEndpoint] = {}
        self.version_headers = ["X-API-Version", "X-Version"]
        self.migration_rules: dict[str, dict[str, Callable]] = {}  # from_version -> {to_version: migrator}

        # Register default version
        self.register_version(APIVersion(
            version=default_version,
            format=version_format,
            release_date=datetime.now(),
            description="Default API version"
        ))

        logger.info(f"API Version Manager initialized with default version {default_version}")

    def register_version(self, version: APIVersion) -> None:
        """
        Register a new API version.

        Args:
            version: Version to register
        """
        if version.format != self.version_format:
            raise ValueError(f"Version format {version.format} does not match manager format {self.version_format}")

        self.versions[version.version] = version
        logger.info(f"Registered API version: {version}")

    def get_version(self, version_str: str) -> APIVersion | None:
        """
        Get a version by string.

        Args:
            version_str: Version string

        Returns:
            APIVersion if found
        """
        return self.versions.get(version_str)

    def get_supported_versions(self) -> list[APIVersion]:
        """
        Get all supported versions.

        Returns:
            List of supported versions
        """
        return list(self.versions.values())

    def get_latest_version(self) -> APIVersion:
        """
        Get the latest version.

        Returns:
            Latest version
        """
        if not self.versions:
            # Handle empty versions case
            return None # type: ignore

        versions = list(self.versions.values())
        return max(versions, key=lambda v: v.version) # type: ignore

    def parse_version_from_request(self, headers: dict[str, str], query_params: dict[str, list[str]]) -> str:
        """
        Parse API version from request headers or query parameters.

        Args:
            headers: Request headers
            query_params: Query parameters

        Returns:
            Version string
        """
        # Check headers
        for header_name in self.version_headers:
            version = headers.get(header_name.lower())
            if version:
                return version

        # Check query parameters
        version = query_params.get("version", [None])[0]
        if version:
            return version # type: ignore

        # Check Accept header for versioned content types
        accept = headers.get("accept", "")
        version_match = re.search(r'application/vnd\.[^.]+\.v([0-9]+\.[0-9]+)', accept)
        if version_match:
            return version_match.group(1)

        return self.default_version

    def validate_version(self, version_str: str) -> bool:
        """
        Validate that a version string is supported.

        Args:
            version_str: Version to validate

        Returns:
            True if valid
        """
        return version_str in self.versions

    def register_endpoint(self, endpoint: VersionedEndpoint) -> None:
        """
        Register a versioned endpoint.

        Args:
            endpoint: Endpoint to register
        """
        self.endpoints[endpoint.path] = endpoint
        logger.debug(f"Registered versioned endpoint: {endpoint.path}")

    def get_endpoint(self, path: str, version: str | None = None) -> VersionedEndpoint | None:
        """
        Get a versioned endpoint.

        Args:
            path: Endpoint path
            version: Specific version (optional)

        Returns:
            VersionedEndpoint if found
        """
        return self.endpoints.get(path)

    def add_migration_rule(self, from_version: str, to_version: str, migrator: Callable) -> None:
        """
        Add a migration rule between versions.

        Args:
            from_version: Source version
            to_version: Target version
            migrator: Migration function
        """
        if from_version not in self.migration_rules:
            self.migration_rules[from_version] = {}

        self.migration_rules[from_version][to_version] = migrator
        logger.debug(f"Added migration rule: {from_version} -> {to_version}")

    def migrate_data(self, data: Any, from_version: str, to_version: str) -> Any:
        """
        Migrate data from one version to another.

        Args:
            data: Data to migrate
            from_version: Source version
            to_version: Target version

        Returns:
            Migrated data
        """
        if from_version == to_version:
            return data

        # Find migration path
        current_version = from_version
        migrated_data = data

        while current_version != to_version:
            if current_version not in self.migration_rules:
                raise ValueError(f"No migration path from {current_version} to {to_version}")

            # Find next version in migration path
            migration_options = self.migration_rules[current_version]
            if to_version in migration_options:
                migrator = migration_options[to_version]
                migrated_data = migrator(migrated_data)
                current_version = to_version
            else:
                # Try to find intermediate migration
                next_version = None
                for target_ver in migration_options:
                    if self.versions[target_ver].is_compatible_with(self.versions[to_version]):
                        next_version = target_ver
                        break

                if next_version is None:
                    raise ValueError(f"No migration path from {current_version} to {to_version}")

                migrator = migration_options[next_version]
                migrated_data = migrator(migrated_data)
                current_version = next_version

        return migrated_data

    def get_version_info(self) -> dict[str, Any]:
        """
        Get information about all versions.

        Returns:
            Version information dictionary
        """
        versions_info = {}
        for version_str, version in self.versions.items():
            versions_info[version_str] = {
                "release_date": version.release_date.isoformat(),
                "description": version.description,
                "deprecated": version.deprecated,
                "breaking_changes": version.breaking_changes,
                "features": version.features
            }

        return {
            "default_version": self.default_version,
            "supported_versions": list(self.versions.keys()),
            "latest_version": self.get_latest_version().version if self.versions else None,
            "versions": versions_info
        }

    def check_deprecated_usage(self, version: str, endpoint: str) -> bool:
        """
        Check if using a deprecated version for an endpoint.

        Args:
            version: Version being used
            endpoint: Endpoint path

        Returns:
            True if deprecated
        """
        if endpoint in self.endpoints:
            return version in self.endpoints[endpoint].deprecated_versions

        # Check if version itself is deprecated
        if version in self.versions:
            return self.versions[version].deprecated

        return False


# Decorators for version management
def version(version_str: str):
    """
    Decorator to specify API version for an endpoint.

    Args:
        version_str: Version string

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        func._api_version = version_str
        return func
    return decorator


def deprecated_version(version_str: str):
    """
    Decorator to mark a version as deprecated.

    Args:
        version_str: Version string

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        func._deprecated_version = version_str
        return func
    return decorator


# Convenience functions
def create_version_manager(default_version: str = "1.0.0") -> APIVersionManager:
    """
    Create a new API version manager.

    Args:
        default_version: Default version

    Returns:
        APIVersionManager instance
    """
    return APIVersionManager(default_version=default_version)


def create_versioned_endpoint(path: str, default_version: str) -> VersionedEndpoint:
    """
    Create a new versioned endpoint.

    Args:
        path: Endpoint path
        default_version: Default version

    Returns:
        VersionedEndpoint instance
    """
    return VersionedEndpoint(
        path=path,
        versions={},
        default_version=default_version
    )
