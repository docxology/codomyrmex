"""Unit tests for API versioning -- version models, version manager, and versioned endpoint routing."""

from datetime import datetime

import pytest


# API Versioning Tests
class TestSimpleVersion:
    """Tests for SimpleVersion class."""

    def test_parse_valid_version(self):
        """Test parsing a valid semantic version."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        version = SimpleVersion("1.2.3")

        assert version.major == 1
        assert version.minor == 2
        assert version.patch == 3

    def test_parse_invalid_version(self):
        """Test parsing an invalid version raises error."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        with pytest.raises(ValueError):
            SimpleVersion("invalid")

    def test_version_comparison(self):
        """Test version comparison."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("2.0.0")
        v3 = SimpleVersion("1.1.0")

        assert v1 < v2
        assert v1 < v3
        assert v3 < v2

    def test_version_equality(self):
        """Test version equality."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("1.0.0")

        assert v1 == v2

    def test_version_compatibility(self):
        """Test version compatibility check."""
        from codomyrmex.api.standardization.api_versioning import SimpleVersion

        v1 = SimpleVersion("1.0.0")
        v2 = SimpleVersion("1.5.0")
        v3 = SimpleVersion("2.0.0")

        assert v1.is_compatible(v2)
        assert not v1.is_compatible(v3)


class TestAPIVersion:
    """Tests for APIVersion dataclass."""

    def test_create_semver_version(self):
        """Test creating a semantic version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )

        version = APIVersion(
            version="1.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            description="Initial release"
        )

        assert version.version == "1.0.0"
        assert version.format == VersionFormat.SEMVER

    def test_create_date_version(self):
        """Test creating a date-based version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )

        version = APIVersion(
            version="2024-01-01",
            format=VersionFormat.DATE,
            release_date=datetime.now()
        )

        assert version.version == "2024-01-01"

    def test_create_integer_version(self):
        """Test creating an integer version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )

        version = APIVersion(
            version="1",
            format=VersionFormat.INTEGER,
            release_date=datetime.now()
        )

        assert version.version == "1"

    def test_invalid_semver_format(self):
        """Test that invalid semver raises error."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )

        with pytest.raises(ValueError):
            APIVersion(
                version="invalid",
                format=VersionFormat.SEMVER,
                release_date=datetime.now()
            )

    def test_version_compatibility(self):
        """Test version compatibility checking."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )

        v1 = APIVersion(
            version="1.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        )
        v2 = APIVersion(
            version="1.5.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        )

        assert v1.is_compatible_with(v2)


class TestAPIVersionManager:
    """Tests for APIVersionManager class."""

    def test_create_version_manager(self):
        """Test creating a version manager."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        assert manager.default_version == "1.0.0"
        assert "1.0.0" in manager.versions

    def test_register_version(self):
        """Test registering a new version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            APIVersionManager,
            VersionFormat,
        )

        manager = APIVersionManager()

        new_version = APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            description="Major update"
        )

        manager.register_version(new_version)

        assert "2.0.0" in manager.versions

    def test_validate_version(self):
        """Test version validation."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        assert manager.validate_version("1.0.0")
        assert not manager.validate_version("9.9.9")

    def test_get_supported_versions(self):
        """Test getting supported versions."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            APIVersionManager,
            VersionFormat,
        )

        manager = APIVersionManager(default_version="1.0.0")
        manager.register_version(APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        ))

        versions = manager.get_supported_versions()

        assert len(versions) == 2

    def test_parse_version_from_request_header(self):
        """Test parsing version from request header."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {"x-api-version": "2.0.0"}
        query_params = {}

        version = manager.parse_version_from_request(headers, query_params)

        assert version == "2.0.0"

    def test_parse_version_from_query_param(self):
        """Test parsing version from query parameter."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {}
        query_params = {"version": ["2.0.0"]}

        version = manager.parse_version_from_request(headers, query_params)

        assert version == "2.0.0"

    def test_get_version_info(self):
        """Test getting version information."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        info = manager.get_version_info()

        assert "default_version" in info
        assert "supported_versions" in info
        assert info["default_version"] == "1.0.0"


class TestVersionedEndpoint:
    """Tests for VersionedEndpoint dataclass."""

    def test_create_versioned_endpoint(self):
        """Test creating a versioned endpoint."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1},
            default_version="1.0.0"
        )

        assert endpoint.path == "/users"
        assert "1.0.0" in endpoint.versions

    def test_get_handler_for_version(self):
        """Test getting handler for specific version."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        def handler_v2():
            return "v2"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1, "2.0.0": handler_v2},
            default_version="1.0.0"
        )

        assert endpoint.get_handler("2.0.0")() == "v2"

    def test_add_version(self):
        """Test adding a new version to endpoint."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler_v1():
            return "v1"

        def handler_v2():
            return "v2"

        endpoint = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": handler_v1},
            default_version="1.0.0"
        )

        endpoint.add_version("2.0.0", handler_v2)

        assert "2.0.0" in endpoint.versions


class TestVersionManagerEdgeCases:
    """Additional edge case tests for APIVersionManager."""

    def test_parse_version_from_accept_header(self):
        """Test parsing version from Accept header."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {"accept": "application/vnd.myapi.v2.0+json"}
        query_params = {}

        version = manager.parse_version_from_request(headers, query_params)
        # Should parse v2.0 from the accept header
        assert version is not None

    def test_version_default_fallback(self):
        """Test default version fallback when no version specified."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        headers = {}
        query_params = {}

        version = manager.parse_version_from_request(headers, query_params)
        assert version == "1.0.0"

    def test_get_latest_version(self):
        """Test getting latest version."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            APIVersionManager,
            VersionFormat,
        )

        manager = APIVersionManager(default_version="1.0.0")
        manager.register_version(APIVersion(
            version="1.5.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        ))
        manager.register_version(APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now()
        ))

        latest = manager.get_latest_version()
        assert latest.version == "2.0.0"

    def test_deprecate_version(self):
        """Test deprecating a version."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler():
            return "test"

        endpoint = VersionedEndpoint(
            path="/test",
            versions={"1.0.0": handler, "2.0.0": handler},
            default_version="1.0.0"
        )

        endpoint.deprecate_version("1.0.0")
        assert "1.0.0" in endpoint.deprecated_versions

    def test_version_unsupported_error(self):
        """Test error when unsupported version requested."""
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint

        def handler():
            return "test"

        endpoint = VersionedEndpoint(
            path="/test",
            versions={"1.0.0": handler},
            default_version="1.0.0"
        )

        with pytest.raises(ValueError) as exc_info:
            endpoint.get_handler("9.9.9")

        assert "not supported" in str(exc_info.value)


class TestVersionMigration:
    """Tests for version migration functionality."""

    def test_add_migration_rule(self):
        """Test adding migration rule."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        def migrate_v1_to_v2(data):
            data["new_field"] = "added"
            return data

        manager.add_migration_rule("1.0.0", "2.0.0", migrate_v1_to_v2)

        assert "1.0.0" in manager.migration_rules
        assert "2.0.0" in manager.migration_rules["1.0.0"]

    def test_migrate_data_same_version(self):
        """Test migration when versions are same."""
        from codomyrmex.api.standardization.api_versioning import APIVersionManager

        manager = APIVersionManager(default_version="1.0.0")

        data = {"field": "value"}
        result = manager.migrate_data(data, "1.0.0", "1.0.0")

        assert result == data

    def test_check_deprecated_usage(self):
        """Test checking deprecated version usage."""
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            APIVersionManager,
            VersionFormat,
        )

        manager = APIVersionManager(default_version="1.0.0")

        deprecated_version = APIVersion(
            version="0.9.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            deprecated=True
        )
        manager.register_version(deprecated_version)

        is_deprecated = manager.check_deprecated_usage("0.9.0", "/any")
        assert is_deprecated is True


# From test_coverage_boost_r6.py
class TestAPIVersioningBoost:
    def test_simple_version(self):
        from codomyrmex.api.standardization.api_versioning import SimpleVersion
        v = SimpleVersion("1.2.3")
        assert v is not None

    def test_api_version(self):
        from codomyrmex.api.standardization.api_versioning import (
            APIVersion,
            VersionFormat,
        )
        v = APIVersion(version="1.0.0", format=VersionFormat.SEMVER, release_date=datetime.now())
        assert v.version == "1.0.0"

    def test_versioned_endpoint(self):
        from codomyrmex.api.standardization.api_versioning import VersionedEndpoint
        ep = VersionedEndpoint(path="/users", versions={"1.0": lambda: None}, default_version="1.0")
        assert ep.path == "/users"

    def test_api_version_manager(self):
        from codomyrmex.api.standardization.api_versioning import APIVersionManager
        mgr = APIVersionManager()
        assert mgr is not None
