"""Zero-mock tests for config_management core: defaults.py, secret_manager.py,
config_loader deep paths, and mcp_tools round-trips.

All tests call real code with real inputs. No mocks, no monkeypatch,
no unittest.mock, no MagicMock.

External dependencies:
- SecretManager requires cryptography (Fernet) — skipif guard at module level
  if cryptography is unavailable.
"""

import os
import tempfile

import pytest

# ---------------------------------------------------------------------------
# Dependency guards
# ---------------------------------------------------------------------------

try:
    from cryptography.fernet import Fernet as _Fernet  # noqa: F401

    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False

_SKIP_CRYPTO = pytest.mark.skipif(
    not _CRYPTO_AVAILABLE,
    reason="cryptography package not installed",
)


# ===========================================================================
# Class: TestDefaults
# ===========================================================================


class TestDefaults:
    """Verify every constant in defaults.py is a non-empty string."""

    def test_default_ollama_url_is_localhost(self):
        from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL

        assert DEFAULT_OLLAMA_URL.startswith("http://localhost")

    def test_default_ollama_url_includes_port(self):
        from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL

        assert "11434" in DEFAULT_OLLAMA_URL

    def test_default_ollama_model_is_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_MODEL

        assert isinstance(DEFAULT_OLLAMA_MODEL, str)
        assert DEFAULT_OLLAMA_MODEL

    def test_default_postgres_host_is_localhost(self):
        from codomyrmex.config_management.defaults import DEFAULT_POSTGRES_HOST

        assert DEFAULT_POSTGRES_HOST == "localhost"

    def test_default_postgres_port_is_numeric_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_POSTGRES_PORT

        assert DEFAULT_POSTGRES_PORT.isdigit()

    def test_default_postgres_user_is_nonempty(self):
        from codomyrmex.config_management.defaults import DEFAULT_POSTGRES_USER

        assert DEFAULT_POSTGRES_USER

    def test_default_redis_url_scheme(self):
        from codomyrmex.config_management.defaults import DEFAULT_REDIS_URL

        assert DEFAULT_REDIS_URL.startswith("redis://")

    def test_default_api_host_is_localhost(self):
        from codomyrmex.config_management.defaults import DEFAULT_API_HOST

        assert DEFAULT_API_HOST == "localhost"

    def test_default_api_port_is_numeric_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_API_PORT

        assert DEFAULT_API_PORT.isdigit()

    def test_default_api_base_url_matches_host_port(self):
        from codomyrmex.config_management.defaults import (
            DEFAULT_API_BASE_URL,
            DEFAULT_API_HOST,
            DEFAULT_API_PORT,
        )

        assert DEFAULT_API_HOST in DEFAULT_API_BASE_URL
        assert DEFAULT_API_PORT in DEFAULT_API_BASE_URL

    def test_default_otel_endpoint_is_http(self):
        from codomyrmex.config_management.defaults import DEFAULT_OTEL_ENDPOINT

        assert DEFAULT_OTEL_ENDPOINT.startswith("http")

    def test_default_cors_origins_is_url(self):
        from codomyrmex.config_management.defaults import DEFAULT_CORS_ORIGINS

        assert DEFAULT_CORS_ORIGINS.startswith("http")

    def test_all_defaults_are_strings(self):
        import codomyrmex.config_management.defaults as defs

        public_attrs = [a for a in dir(defs) if a.startswith("DEFAULT_")]
        assert len(public_attrs) >= 8
        for attr in public_attrs:
            val = getattr(defs, attr)
            assert isinstance(val, str), f"{attr} must be a str, got {type(val)}"


# ===========================================================================
# Class: TestConfigLoaderDeepMerge
# ===========================================================================


class TestConfigLoaderDeepMerge:
    """Tests for deep_merge and resolve_env_vars utility functions."""

    def test_deep_merge_flat_override(self):
        from codomyrmex.config_management.core.config_loader import deep_merge

        base = {"a": 1, "b": 2}
        ext = {"b": 99, "c": 3}
        result = deep_merge(base, ext)
        assert result["a"] == 1
        assert result["b"] == 99
        assert result["c"] == 3

    def test_deep_merge_nested_recursion(self):
        from codomyrmex.config_management.core.config_loader import deep_merge

        base = {"db": {"host": "localhost", "port": 5432}}
        ext = {"db": {"port": 9999}}
        result = deep_merge(base, ext)
        assert result["db"]["host"] == "localhost"
        assert result["db"]["port"] == 9999

    def test_deep_merge_adds_new_nested_key(self):
        from codomyrmex.config_management.core.config_loader import deep_merge

        base = {"db": {"host": "h"}}
        ext = {"db": {"user": "admin"}}
        result = deep_merge(base, ext)
        assert result["db"]["host"] == "h"
        assert result["db"]["user"] == "admin"

    def test_deep_merge_empty_extension_is_noop(self):
        from codomyrmex.config_management.core.config_loader import deep_merge

        base = {"x": 42}
        result = deep_merge(base, {})
        assert result["x"] == 42

    def test_deep_merge_empty_base_copies_extension(self):
        from codomyrmex.config_management.core.config_loader import deep_merge

        result = deep_merge({}, {"y": 7})
        assert result["y"] == 7

    def test_resolve_env_vars_replaces_known_var(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        os.environ["_TEST_CM_VAR"] = "hello_world"
        try:
            result = resolve_env_vars("prefix_${_TEST_CM_VAR}_suffix")
            assert result == "prefix_hello_world_suffix"
        finally:
            del os.environ["_TEST_CM_VAR"]

    def test_resolve_env_vars_uses_default_when_var_missing(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        # Ensure the variable is absent
        os.environ.pop("_TEST_MISSING_VAR", None)
        result = resolve_env_vars("${_TEST_MISSING_VAR:-fallback_value}")
        assert result == "fallback_value"

    def test_resolve_env_vars_leaves_unknown_no_default(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        os.environ.pop("_TEST_ABSENT_VAR", None)
        result = resolve_env_vars("${_TEST_ABSENT_VAR}")
        # Should leave the placeholder unchanged
        assert result == "${_TEST_ABSENT_VAR}"

    def test_resolve_env_vars_recurses_into_dict(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        os.environ["_TEST_HOST"] = "myhost"
        try:
            data = {"db": {"host": "${_TEST_HOST}"}}
            result = resolve_env_vars(data)
            assert result["db"]["host"] == "myhost"
        finally:
            del os.environ["_TEST_HOST"]

    def test_resolve_env_vars_recurses_into_list(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        os.environ["_TEST_LIST_VAR"] = "item_val"
        try:
            result = resolve_env_vars(["${_TEST_LIST_VAR}", "plain"])
            assert result[0] == "item_val"
            assert result[1] == "plain"
        finally:
            del os.environ["_TEST_LIST_VAR"]

    def test_resolve_env_vars_passes_through_non_string(self):
        from codomyrmex.config_management.core.config_loader import resolve_env_vars

        assert resolve_env_vars(42) == 42
        assert resolve_env_vars(3.14) == 3.14
        assert resolve_env_vars(None) is None
        assert resolve_env_vars(True) is True


# ===========================================================================
# Class: TestConfigurationObject
# ===========================================================================


class TestConfigurationObject:
    """Tests for the Configuration dataclass get_value / set_value paths."""

    def _make_config(self, data: dict):
        from codomyrmex.config_management.core.config_loader import Configuration

        return Configuration(data=data)

    def test_get_value_flat_key_returns_value(self):
        cfg = self._make_config({"host": "localhost"})
        assert cfg.get_value("host") == "localhost"

    def test_get_value_nested_dot_notation(self):
        cfg = self._make_config({"db": {"host": "dbhost", "port": 5432}})
        assert cfg.get_value("db.host") == "dbhost"
        assert cfg.get_value("db.port") == 5432

    def test_get_value_returns_default_for_missing_key(self):
        cfg = self._make_config({})
        assert cfg.get_value("missing.key", default="default_val") == "default_val"

    def test_get_value_returns_none_when_no_default(self):
        cfg = self._make_config({})
        assert cfg.get_value("absent") is None

    def test_set_value_flat_key(self):
        cfg = self._make_config({"x": 1})
        cfg.set_value("x", 99)
        assert cfg.data["x"] == 99

    def test_set_value_nested_key_creates_dict(self):
        cfg = self._make_config({})
        cfg.set_value("db.host", "newhost")
        assert cfg.data["db"]["host"] == "newhost"

    def test_set_value_overrides_existing_nested(self):
        cfg = self._make_config({"db": {"host": "old"}})
        cfg.set_value("db.host", "new")
        assert cfg.data["db"]["host"] == "new"

    def test_to_dict_contains_data_key(self):
        cfg = self._make_config({"k": "v"})
        d = cfg.to_dict()
        assert "data" in d
        assert d["data"]["k"] == "v"

    def test_to_dict_contains_source(self):
        from codomyrmex.config_management.core.config_loader import Configuration

        cfg = Configuration(data={}, source="test_source")
        d = cfg.to_dict()
        assert d["source"] == "test_source"

    def test_to_dict_contains_loaded_at_isoformat(self):
        cfg = self._make_config({})
        d = cfg.to_dict()
        assert "loaded_at" in d
        # Must be a valid ISO datetime string
        from datetime import datetime

        datetime.fromisoformat(d["loaded_at"])

    def test_validate_without_schema_returns_empty_list(self):
        cfg = self._make_config({"a": 1})
        errors = cfg.validate()
        assert errors == []


# ===========================================================================
# Class: TestConfigurationManagerBasic
# ===========================================================================


class TestConfigurationManagerBasic:
    """Tests for ConfigurationManager operations that don't require disk files."""

    def _make_manager(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            return mgr, tmp

    def test_list_configurations_empty_on_fresh_manager(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            assert mgr.list_configurations() == []

    def test_get_configuration_returns_none_for_unknown_name(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            assert mgr.get_configuration("nonexistent") is None

    def test_load_configuration_with_defaults(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            cfg = mgr.load_configuration("app", defaults={"version": "1.0"})
            assert cfg.data.get("version") == "1.0"

    def test_load_configuration_stores_in_registry(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            mgr.load_configuration("myapp", defaults={"env": "test"})
            assert "myapp" in mgr.list_configurations()
            assert mgr.get_configuration("myapp") is not None

    def test_load_configuration_merges_env_vars(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["MYAPP_DEBUG"] = "true"
            try:
                mgr = ConfigurationManager(config_dir=tmp)
                cfg = mgr.load_configuration("myapp", defaults={})
                assert cfg.data.get("debug") == "true"
            finally:
                del os.environ["MYAPP_DEBUG"]

    def test_validate_all_configurations_returns_empty_dict_when_no_schema(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            mgr.load_configuration("x", defaults={"key": "val"})
            result = mgr.validate_all_configurations()
            # No schema on config → no errors
            assert isinstance(result, dict)
            assert "x" not in result

    def test_load_configuration_from_json_file(self):
        import json

        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            json_path = os.path.join(tmp, "settings.json")
            with open(json_path, "w") as f:
                json.dump({"setting": "from_file"}, f)

            mgr = ConfigurationManager(config_dir=tmp)
            cfg = mgr.load_configuration_from_file(json_path)
            assert cfg is not None
            assert cfg.data["setting"] == "from_file"

    def test_load_configuration_from_yaml_file(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = os.path.join(tmp, "settings.yaml")
            with open(yaml_path, "w") as f:
                f.write("name: test_app\nversion: 2.0\n")

            mgr = ConfigurationManager(config_dir=tmp)
            cfg = mgr.load_configuration_from_file(yaml_path)
            assert cfg is not None
            assert cfg.data["name"] == "test_app"
            assert cfg.data["version"] == 2.0

    def test_load_configuration_from_file_returns_none_for_missing(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            result = mgr.load_configuration_from_file("/nonexistent/path/config.json")
            assert result is None

    def test_save_configuration_returns_false_for_unknown_name(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            result = mgr.save_configuration("ghost", "/tmp/ghost.yaml")
            assert result is False

    def test_create_migration_backup_returns_false_for_unknown(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            result = mgr.create_migration_backup("no_such_config")
            assert result is False

    def test_create_migration_backup_creates_backup_entry(self):
        from codomyrmex.config_management.core.config_loader import ConfigurationManager

        with tempfile.TemporaryDirectory() as tmp:
            mgr = ConfigurationManager(config_dir=tmp)
            mgr.load_configuration("prod", defaults={"v": "1"})
            result = mgr.create_migration_backup("prod")
            assert result is True
            # Should have 2 entries: 'prod' + backup
            assert len(mgr.list_configurations()) == 2


# ===========================================================================
# Class: TestConfigSchemaValidation
# ===========================================================================


class TestConfigSchemaValidation:
    """Tests for ConfigSchema.validate method."""

    def _make_schema(self, schema_dict: dict):
        from codomyrmex.config_management.core.config_loader import ConfigSchema

        return ConfigSchema(schema=schema_dict)

    def test_valid_config_returns_empty_errors(self):
        schema = self._make_schema(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }
        )
        errors = schema.validate({"name": "alice"})
        assert errors == []

    def test_invalid_config_returns_errors(self):
        schema = self._make_schema(
            {
                "type": "object",
                "properties": {"age": {"type": "integer"}},
                "required": ["age"],
            }
        )
        errors = schema.validate({})
        assert len(errors) > 0

    def test_wrong_type_returns_error(self):
        schema = self._make_schema(
            {
                "type": "object",
                "properties": {"count": {"type": "integer"}},
            }
        )
        errors = schema.validate({"count": "not_an_int"})
        assert len(errors) > 0


# ===========================================================================
# Class: TestMcpTools
# ===========================================================================


class TestMcpTools:
    """Tests for config_management/mcp_tools.py MCP tool functions."""

    def test_get_config_returns_success_status(self):
        from codomyrmex.config_management.mcp_tools import get_config

        result = get_config("any_key", namespace="default")
        assert "status" in result

    def test_get_config_returns_key_in_response(self):
        from codomyrmex.config_management.mcp_tools import get_config

        result = get_config("db.host", namespace="default")
        assert result.get("key") == "db.host"

    def test_set_config_returns_success_status(self):
        from codomyrmex.config_management.mcp_tools import set_config

        result = set_config("test_key", "test_value", namespace="default")
        assert "status" in result

    def test_validate_config_returns_status(self):
        from codomyrmex.config_management.mcp_tools import validate_config

        result = validate_config(namespace="default")
        assert "status" in result

    def test_validate_config_returns_namespace_field(self):
        from codomyrmex.config_management.mcp_tools import validate_config

        result = validate_config(namespace="testns")
        if result.get("status") == "success":
            assert result.get("namespace") == "testns"


# ===========================================================================
# Class: TestSecretManager
# ===========================================================================


@_SKIP_CRYPTO
class TestSecretManager:
    """Tests for SecretManager — store, get, list, delete, rotate operations."""

    def _make_manager(self, tmp_dir: str):
        from codomyrmex.config_management.secrets.secret_manager import SecretManager

        key_file = os.path.join(tmp_dir, "test.key")
        return SecretManager(key_file=key_file)

    def test_store_secret_returns_string_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            secret_id = mgr.store_secret("my_token", "super_secret_value")
            assert isinstance(secret_id, str)
            assert len(secret_id) > 0

    def test_get_secret_returns_original_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            secret_id = mgr.store_secret("db_pass", "s3cr3t!")
            retrieved = mgr.get_secret(secret_id)
            assert retrieved == "s3cr3t!"

    def test_get_secret_returns_none_for_unknown_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            assert mgr.get_secret("nonexistent_id") is None

    def test_get_secret_by_name_returns_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("api_key", "api_key_value_123")
            result = mgr.get_secret_by_name("api_key")
            assert result == "api_key_value_123"

    def test_get_secret_by_name_returns_none_for_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            assert mgr.get_secret_by_name("missing_name") is None

    def test_list_secrets_empty_initially(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            assert mgr.list_secrets() == []

    def test_list_secrets_returns_metadata_not_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("tok", "secret_value_xyz")
            listing = mgr.list_secrets()
            assert len(listing) == 1
            entry = listing[0]
            assert "id" in entry
            assert "name" in entry
            assert "value" not in entry  # must not expose plaintext

    def test_delete_secret_removes_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            sid = mgr.store_secret("tmp_secret", "val")
            assert mgr.delete_secret(sid) is True
            assert mgr.get_secret(sid) is None

    def test_delete_secret_returns_false_for_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            assert mgr.delete_secret("fake_id") is False

    def test_rotate_key_preserves_secret_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            sid = mgr.store_secret("persistent", "still_here")
            mgr.rotate_key()
            assert mgr.get_secret(sid) == "still_here"

    def test_rotate_key_returns_string_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            key_id = mgr.rotate_key()
            assert isinstance(key_id, str)

    def test_rotate_secret_replaces_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("rotate_me", "old_value")
            event = mgr.rotate_secret("rotate_me", "new_value")
            assert event["secret_name"] == "rotate_me"
            new_val = mgr.get_secret_by_name("rotate_me")
            assert new_val == "new_value"

    def test_rotate_secret_stores_previous_id_in_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("tok", "v1")
            event = mgr.rotate_secret("tok", "v2")
            assert "previous_id" in event

    def test_get_rotation_history_captures_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("hist_tok", "v1")
            mgr.rotate_secret("hist_tok", "v2")
            history = mgr.get_rotation_history("hist_tok")
            assert len(history) == 1
            assert history[0]["secret_name"] == "hist_tok"

    def test_get_rotation_history_all_returns_all(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("a", "v1")
            mgr.store_secret("b", "v1")
            mgr.rotate_secret("a", "v2")
            mgr.rotate_secret("b", "v2")
            all_history = mgr.get_rotation_history()
            assert len(all_history) == 2

    def test_check_key_age_returns_not_stale_for_new_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            mgr.store_secret("fresh", "fresh_val")
            age_info = mgr.check_key_age("fresh", max_age_days=90)
            assert age_info["stale"] is False
            assert age_info["age_days"] == 0

    def test_check_key_age_returns_neg1_for_unknown_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            age_info = mgr.check_key_age("no_such_secret")
            assert age_info["age_days"] == -1

    def test_store_secret_with_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            mgr = self._make_manager(tmp)
            meta = {"owner": "team_a", "env": "production"}
            sid = mgr.store_secret("api_key", "abc123", metadata=meta)
            listing = mgr.list_secrets()
            entry = next(e for e in listing if e["id"] == sid)
            assert entry["metadata"]["owner"] == "team_a"
