"""Comprehensive unit tests for codomyrmex.api.standardization.api_versioning.

Uses direct importlib loading to bypass the circular import chain in the
codomyrmex.api package __init__.  No mocks used — all test doubles are real
callables/objects.
"""

import importlib.util
import sys
from datetime import datetime

import pytest

# ---------------------------------------------------------------------------
# Direct-import helper
# ---------------------------------------------------------------------------


def _load_api_versioning():
    name = "codomyrmex.api.standardization.api_versioning"
    if name in sys.modules:
        return sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        name,
        "src/codomyrmex/api/standardization/api_versioning.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


try:
    _av = _load_api_versioning()
    SimpleVersion = _av.SimpleVersion
    VersionFormat = _av.VersionFormat
    APIVersion = _av.APIVersion
    VersionedEndpoint = _av.VersionedEndpoint
    APIVersionManager = _av.APIVersionManager
    version = _av.version
    deprecated_version = _av.deprecated_version
    create_version_manager = _av.create_version_manager
    create_versioned_endpoint = _av.create_versioned_endpoint
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    _SKIP_REASON = str(_exc)

pytestmark = pytest.mark.skipif(
    not _AVAILABLE,
    reason=f"api_versioning unavailable: {'' if _AVAILABLE else _SKIP_REASON}",
)


# ===========================================================================
# SimpleVersion
# ===========================================================================


class TestSimpleVersion:
    """SimpleVersion — parsing, comparison, compatibility."""

    def test_parse_valid_semver(self):
        v = SimpleVersion("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_str_representation(self):
        assert str(SimpleVersion("2.0.0")) == "2.0.0"

    def test_invalid_two_part_raises(self):
        with pytest.raises(ValueError):
            SimpleVersion("1.0")

    def test_invalid_non_numeric_raises(self):
        with pytest.raises(ValueError):
            SimpleVersion("a.b.c")

    def test_invalid_no_dots_raises(self):
        with pytest.raises(ValueError):
            SimpleVersion("invalid")

    def test_less_than_comparison(self):
        assert SimpleVersion("1.0.0") < SimpleVersion("2.0.0")

    def test_minor_less_than(self):
        assert SimpleVersion("1.0.0") < SimpleVersion("1.1.0")

    def test_patch_less_than(self):
        assert SimpleVersion("1.0.0") < SimpleVersion("1.0.1")

    def test_not_less_than_equal(self):
        assert not (SimpleVersion("1.0.0") < SimpleVersion("1.0.0"))

    def test_equality(self):
        assert SimpleVersion("1.0.0") == SimpleVersion("1.0.0")

    def test_inequality(self):
        assert SimpleVersion("1.0.0") != SimpleVersion("2.0.0")

    def test_compatible_same_major(self):
        assert SimpleVersion("1.0.0").is_compatible(SimpleVersion("1.9.9"))

    def test_incompatible_different_major(self):
        assert not SimpleVersion("1.0.0").is_compatible(SimpleVersion("2.0.0"))

    def test_zero_version(self):
        v = SimpleVersion("0.0.0")
        assert v.major == 0
        assert v.minor == 0
        assert v.patch == 0

    def test_lt_returns_not_implemented_for_non_version(self):
        result = SimpleVersion("1.0.0").__lt__("not a version")
        assert result is NotImplemented

    def test_eq_returns_not_implemented_for_non_version(self):
        result = SimpleVersion("1.0.0").__eq__("not a version")
        assert result is NotImplemented


# ===========================================================================
# VersionFormat enum
# ===========================================================================


class TestVersionFormat:
    def test_semver_value(self):
        assert VersionFormat.SEMVER.value == "semver"

    def test_date_value(self):
        assert VersionFormat.DATE.value == "date"

    def test_integer_value(self):
        assert VersionFormat.INTEGER.value == "int"

    def test_three_members(self):
        assert len(VersionFormat) == 3


# ===========================================================================
# APIVersion
# ===========================================================================


class TestAPIVersion:
    """APIVersion dataclass — format validation, compatibility, ordering."""

    def _make_semver(self, version_str="1.0.0", **kwargs):
        return APIVersion(
            version=version_str,
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
            **kwargs,
        )

    def test_semver_valid(self):
        v = self._make_semver("1.2.3")
        assert v.version == "1.2.3"
        assert v.format == VersionFormat.SEMVER

    def test_semver_invalid_raises(self):
        with pytest.raises(ValueError):
            APIVersion(
                version="bad",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )

    def test_date_valid(self):
        v = APIVersion(
            version="2024-06-15",
            format=VersionFormat.DATE,
            release_date=datetime.now(),
        )
        assert v.version == "2024-06-15"

    def test_date_invalid_format_raises(self):
        with pytest.raises(ValueError):
            APIVersion(
                version="15-06-2024",
                format=VersionFormat.DATE,
                release_date=datetime.now(),
            )

    def test_integer_valid(self):
        v = APIVersion(
            version="3",
            format=VersionFormat.INTEGER,
            release_date=datetime.now(),
        )
        assert v.version == "3"

    def test_integer_non_digit_raises(self):
        with pytest.raises(ValueError):
            APIVersion(
                version="v3",
                format=VersionFormat.INTEGER,
                release_date=datetime.now(),
            )

    def test_str_representation(self):
        v = self._make_semver("1.5.0")
        assert str(v) == "v1.5.0"

    def test_compatibility_same_major(self):
        v1 = self._make_semver("1.0.0")
        v2 = self._make_semver("1.3.0")
        assert v1.is_compatible_with(v2)

    def test_incompatibility_different_major(self):
        v1 = self._make_semver("1.0.0")
        v2 = self._make_semver("2.0.0")
        assert not v1.is_compatible_with(v2)

    def test_incompatibility_different_format(self):
        v1 = self._make_semver("1.0.0")
        v2 = APIVersion(
            version="2", format=VersionFormat.INTEGER, release_date=datetime.now()
        )
        assert not v1.is_compatible_with(v2)

    def test_date_versions_compatible(self):
        v1 = APIVersion(
            version="2024-01-01",
            format=VersionFormat.DATE,
            release_date=datetime.now(),
        )
        v2 = APIVersion(
            version="2024-06-01",
            format=VersionFormat.DATE,
            release_date=datetime.now(),
        )
        assert v1.is_compatible_with(v2)

    def test_integer_versions_compatible(self):
        v1 = APIVersion(
            version="1",
            format=VersionFormat.INTEGER,
            release_date=datetime.now(),
        )
        v2 = APIVersion(
            version="2",
            format=VersionFormat.INTEGER,
            release_date=datetime.now(),
        )
        assert v1.is_compatible_with(v2)

    def test_less_than_semver(self):
        v1 = self._make_semver("1.0.0")
        v2 = self._make_semver("2.0.0")
        assert v1 < v2

    def test_less_than_date(self):
        v1 = APIVersion(
            version="2023-01-01",
            format=VersionFormat.DATE,
            release_date=datetime.now(),
        )
        v2 = APIVersion(
            version="2024-01-01",
            format=VersionFormat.DATE,
            release_date=datetime.now(),
        )
        assert v1 < v2

    def test_less_than_integer(self):
        v1 = APIVersion(
            version="1", format=VersionFormat.INTEGER, release_date=datetime.now()
        )
        v2 = APIVersion(
            version="2", format=VersionFormat.INTEGER, release_date=datetime.now()
        )
        assert v1 < v2

    def test_less_than_different_format_returns_false(self):
        v1 = self._make_semver("1.0.0")
        v2 = APIVersion(
            version="2", format=VersionFormat.INTEGER, release_date=datetime.now()
        )
        assert not (v1 < v2)

    def test_deprecated_flag(self):
        v = self._make_semver("0.9.0", deprecated=True)
        assert v.deprecated is True

    def test_features_list(self):
        v = self._make_semver("1.1.0", features=["streaming", "batch"])
        assert "streaming" in v.features

    def test_breaking_changes_list(self):
        v = self._make_semver("2.0.0", breaking_changes=["removed /v1 endpoint"])
        assert "removed /v1 endpoint" in v.breaking_changes


# ===========================================================================
# VersionedEndpoint
# ===========================================================================


class TestVersionedEndpoint:
    """VersionedEndpoint — handlers, add_version, deprecate_version."""

    def _make_endpoint(self, path="/test", versions=None, default="1.0.0"):
        if versions is None:
            versions = {"1.0.0": lambda: "v1"}
        return VersionedEndpoint(path=path, versions=versions, default_version=default)

    def test_get_default_handler(self):
        ep = self._make_endpoint()
        handler = ep.get_handler()
        assert handler() == "v1"

    def test_get_handler_by_version(self):
        ep = self._make_endpoint(
            versions={"1.0.0": lambda: "v1", "2.0.0": lambda: "v2"}
        )
        assert ep.get_handler("2.0.0")() == "v2"

    def test_get_handler_missing_version_raises(self):
        ep = self._make_endpoint()
        with pytest.raises(ValueError, match="not supported"):
            ep.get_handler("9.9.9")

    def test_get_handler_deprecated_version_still_works(self):
        ep = self._make_endpoint(
            versions={"1.0.0": lambda: "v1", "0.5.0": lambda: "old"},
            default="1.0.0",
        )
        ep.deprecated_versions = ["0.5.0"]
        # Should still return the handler (with a warning logged)
        result = ep.get_handler("0.5.0")
        assert result() == "old"

    def test_add_version_stores_handler(self):
        ep = self._make_endpoint()
        ep.add_version("2.0.0", lambda: "v2")
        assert "2.0.0" in ep.versions
        assert ep.versions["2.0.0"]() == "v2"

    def test_add_version_appends_to_supported_methods(self):
        ep = self._make_endpoint()
        ep.add_version("3.0.0", lambda: "v3")
        assert "3.0.0" in ep.supported_methods

    def test_deprecate_version_adds_to_list(self):
        ep = self._make_endpoint(
            versions={"1.0.0": lambda: "v1", "0.9.0": lambda: "old"},
        )
        ep.deprecate_version("0.9.0")
        assert "0.9.0" in ep.deprecated_versions

    def test_deprecate_unknown_version_is_noop(self):
        ep = self._make_endpoint()
        ep.deprecate_version("non.existent")  # should not raise
        assert "non.existent" not in ep.deprecated_versions

    def test_deprecate_already_deprecated_is_idempotent(self):
        ep = self._make_endpoint(
            versions={"1.0.0": lambda: "v1", "0.1.0": lambda: "old"},
        )
        ep.deprecate_version("0.1.0")
        ep.deprecate_version("0.1.0")
        assert ep.deprecated_versions.count("0.1.0") == 1

    def test_create_versioned_endpoint_factory(self):
        ep = create_versioned_endpoint("/api/users", "1.0.0")
        assert isinstance(ep, VersionedEndpoint)
        assert ep.path == "/api/users"
        assert ep.default_version == "1.0.0"
        assert ep.versions == {}


# ===========================================================================
# APIVersionManager
# ===========================================================================


class TestAPIVersionManager:
    """APIVersionManager — registration, parsing, migration, info."""

    def test_default_version_registered_on_init(self):
        mgr = APIVersionManager(default_version="1.0.0")
        assert "1.0.0" in mgr.versions

    def test_register_additional_version(self):
        mgr = APIVersionManager()
        v2 = APIVersion(
            version="2.0.0",
            format=VersionFormat.SEMVER,
            release_date=datetime.now(),
        )
        mgr.register_version(v2)
        assert "2.0.0" in mgr.versions

    def test_register_wrong_format_raises(self):
        mgr = APIVersionManager(version_format=VersionFormat.SEMVER)
        wrong = APIVersion(
            version="3",
            format=VersionFormat.INTEGER,
            release_date=datetime.now(),
        )
        with pytest.raises(ValueError):
            mgr.register_version(wrong)

    def test_get_version_returns_correct_version(self):
        mgr = APIVersionManager(default_version="1.0.0")
        v = mgr.get_version("1.0.0")
        assert v is not None
        assert v.version == "1.0.0"

    def test_get_version_missing_returns_none(self):
        mgr = APIVersionManager()
        assert mgr.get_version("9.9.9") is None

    def test_get_supported_versions_list(self):
        mgr = APIVersionManager()
        mgr.register_version(
            APIVersion(
                version="2.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        versions = mgr.get_supported_versions()
        assert len(versions) == 2

    def test_validate_version_known(self):
        mgr = APIVersionManager(default_version="1.0.0")
        assert mgr.validate_version("1.0.0") is True

    def test_validate_version_unknown(self):
        mgr = APIVersionManager()
        assert mgr.validate_version("9.9.9") is False

    def test_get_latest_version_single(self):
        mgr = APIVersionManager(default_version="1.0.0")
        latest = mgr.get_latest_version()
        assert latest.version == "1.0.0"

    def test_get_latest_version_multiple(self):
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="1.5.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        mgr.register_version(
            APIVersion(
                version="2.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        latest = mgr.get_latest_version()
        assert latest.version == "2.0.0"

    def test_parse_version_from_x_api_version_header(self):
        mgr = APIVersionManager()
        v = mgr.parse_version_from_request({"x-api-version": "2.0.0"}, {})
        assert v == "2.0.0"

    def test_parse_version_from_x_version_header(self):
        mgr = APIVersionManager()
        v = mgr.parse_version_from_request({"x-version": "1.5.0"}, {})
        assert v == "1.5.0"

    def test_parse_version_from_query_param(self):
        mgr = APIVersionManager()
        v = mgr.parse_version_from_request({}, {"version": ["2.0.0"]})
        assert v == "2.0.0"

    def test_parse_version_from_accept_header(self):
        mgr = APIVersionManager()
        accept = "application/vnd.myapi.v2.0+json"
        v = mgr.parse_version_from_request({"accept": accept}, {})
        assert v == "2.0"

    def test_parse_version_defaults_when_nothing_provided(self):
        mgr = APIVersionManager(default_version="1.0.0")
        v = mgr.parse_version_from_request({}, {})
        assert v == "1.0.0"

    def test_register_and_get_endpoint(self):
        mgr = APIVersionManager()
        ep = VersionedEndpoint(
            path="/users",
            versions={"1.0.0": lambda: None},
            default_version="1.0.0",
        )
        mgr.register_endpoint(ep)
        retrieved = mgr.get_endpoint("/users")
        assert retrieved is ep

    def test_get_endpoint_missing_returns_none(self):
        mgr = APIVersionManager()
        assert mgr.get_endpoint("/unknown") is None

    def test_get_version_info_structure(self):
        mgr = APIVersionManager(default_version="1.0.0")
        info = mgr.get_version_info()
        assert info["default_version"] == "1.0.0"
        assert "1.0.0" in info["supported_versions"]
        assert "1.0.0" in info["versions"]
        assert "release_date" in info["versions"]["1.0.0"]
        assert "deprecated" in info["versions"]["1.0.0"]

    def test_get_version_info_latest_version(self):
        mgr = APIVersionManager(default_version="1.0.0")
        info = mgr.get_version_info()
        assert info["latest_version"] == "1.0.0"

    def test_check_deprecated_usage_via_version_flag(self):
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="0.9.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
                deprecated=True,
            )
        )
        assert mgr.check_deprecated_usage("0.9.0", "/any") is True

    def test_check_deprecated_usage_non_deprecated_version(self):
        mgr = APIVersionManager(default_version="1.0.0")
        assert mgr.check_deprecated_usage("1.0.0", "/any") is False

    def test_check_deprecated_usage_unknown_version_returns_false(self):
        mgr = APIVersionManager()
        assert mgr.check_deprecated_usage("9.9.9", "/anything") is False

    def test_check_deprecated_usage_via_endpoint_deprecated_versions(self):
        mgr = APIVersionManager(default_version="1.0.0")
        ep = VersionedEndpoint(
            path="/legacy",
            versions={"1.0.0": lambda: None, "0.5.0": lambda: None},
            default_version="1.0.0",
            deprecated_versions=["0.5.0"],
        )
        mgr.register_endpoint(ep)
        assert mgr.check_deprecated_usage("0.5.0", "/legacy") is True

    def test_add_migration_rule_and_migrate_direct(self):
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="2.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )

        def migrator(data):
            data["new_field"] = "added"
            return data

        mgr.add_migration_rule("1.0.0", "2.0.0", migrator)
        result = mgr.migrate_data({"old": "value"}, "1.0.0", "2.0.0")
        assert result["new_field"] == "added"
        assert result["old"] == "value"

    def test_migrate_data_same_version_returns_unchanged(self):
        mgr = APIVersionManager(default_version="1.0.0")
        data = {"field": "value"}
        result = mgr.migrate_data(data, "1.0.0", "1.0.0")
        assert result is data

    def test_migrate_data_no_rule_raises(self):
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="2.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        with pytest.raises(ValueError, match="No migration path"):
            mgr.migrate_data({}, "1.0.0", "2.0.0")

    def test_create_version_manager_factory(self):
        mgr = create_version_manager(default_version="2.0.0")
        assert isinstance(mgr, APIVersionManager)
        assert mgr.default_version == "2.0.0"

    def test_integer_format_manager(self):
        mgr = APIVersionManager(
            default_version="1", version_format=VersionFormat.INTEGER
        )
        assert "1" in mgr.versions

    def test_date_format_manager(self):
        mgr = APIVersionManager(
            default_version="2024-01-01", version_format=VersionFormat.DATE
        )
        assert "2024-01-01" in mgr.versions

    def test_get_latest_version_empty_versions_returns_none(self):
        """get_latest_version returns None when no versions are registered."""
        mgr = APIVersionManager.__new__(APIVersionManager)
        mgr.versions = {}
        mgr.version_format = VersionFormat.SEMVER
        mgr.default_version = "1.0.0"
        mgr.endpoints = {}
        mgr.version_headers = []
        mgr.migration_rules = {}
        result = mgr.get_latest_version()
        assert result is None

    def test_migrate_data_intermediate_version_path(self):
        """Migration through an intermediate compatible version (lines 374-386)."""
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="1.5.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        mgr.register_version(
            APIVersion(
                version="1.9.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        # 1.0.0 → 1.5.0 intermediate, then 1.5.0 → 1.9.0 direct
        mgr.add_migration_rule("1.0.0", "1.5.0", lambda d: {**d, "step1": True})
        mgr.add_migration_rule("1.5.0", "1.9.0", lambda d: {**d, "step2": True})
        # Ask for 1.0.0 → 1.9.0 without a direct rule, forcing intermediate lookup
        result = mgr.migrate_data({"original": True}, "1.0.0", "1.9.0")
        assert result["original"] is True
        assert result["step1"] is True
        assert result["step2"] is True

    def test_migrate_data_no_compatible_intermediate_raises(self):
        """When the intermediate path is not compatible, ValueError is raised."""
        mgr = APIVersionManager(default_version="1.0.0")
        mgr.register_version(
            APIVersion(
                version="2.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        mgr.register_version(
            APIVersion(
                version="3.0.0",
                format=VersionFormat.SEMVER,
                release_date=datetime.now(),
            )
        )
        # Only rule: 1.0.0 → 2.0.0, but we want to reach 3.0.0 and 2.x is not compatible with 3.x
        mgr.add_migration_rule("1.0.0", "2.0.0", lambda d: {**d, "v2": True})
        # No rule from 2.0.0 to 3.0.0 and they're incompatible major versions
        with pytest.raises(ValueError, match="No migration path"):
            mgr.migrate_data({"original": True}, "1.0.0", "3.0.0")


# ===========================================================================
# Decorators
# ===========================================================================


class TestVersionDecorators:
    """version and deprecated_version decorators."""

    def test_version_decorator_sets_attribute(self):
        @version("2.0.0")
        def handler():
            return "v2"

        assert hasattr(handler, "_api_version")
        assert handler._api_version == "2.0.0"
        assert handler() == "v2"

    def test_deprecated_version_decorator_sets_attribute(self):
        @deprecated_version("1.0.0")
        def old_handler():
            return "old"

        assert hasattr(old_handler, "_deprecated_version")
        assert old_handler._deprecated_version == "1.0.0"
        assert old_handler() == "old"
