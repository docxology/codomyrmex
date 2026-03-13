"""Extended zero-mock tests for config_management module.

Covers:
- defaults.py constants
- core/config_loader.py: deep_merge, resolve_env_vars, ConfigSchema.validate,
  Configuration extra paths, ConfigurationManager edge cases
- secrets/secret_manager.py: SecretManager full API
- deployment/config_deployer.py: ConfigurationDeployer full API
- validation/config_validator.py: predefined schemas, validate_config_schema,
  constraint types, custom validators
- migration/config_migrator.py: nested values, custom transform, split/merge stubs

Zero-mock policy: NO unittest.mock, MagicMock, or monkeypatch on application logic.
All tests use real objects, real file I/O, and real behavior.
"""

import json
import os

import pytest
import yaml

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    deep_merge,
    resolve_env_vars,
)
from codomyrmex.config_management.deployment.config_deployer import (
    ConfigurationDeployer,
    DeploymentStatus,
    Environment,
    EnvironmentType,
)
from codomyrmex.config_management.migration.config_migrator import (
    ConfigMigrator,
    MigrationAction,
    MigrationRule,
    create_database_migration_rules,
    create_logging_migration_rules,
    migrate_config,
)
from codomyrmex.config_management.validation.config_validator import (
    ConfigSchema as ValidatorConfigSchema,
)
from codomyrmex.config_management.validation.config_validator import (
    ConfigValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    get_ai_model_config_schema,
    get_database_config_schema,
    get_logging_config_schema,
    validate_config_schema,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CRYPTO_AVAILABLE = True
try:
    from codomyrmex.config_management.secrets.secret_manager import (
        SecretManager,
        encrypt_configuration,
        manage_secrets,
    )
except ImportError:
    _CRYPTO_AVAILABLE = False

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# TestDefaults — constants from defaults.py
# ---------------------------------------------------------------------------


class TestDefaults:
    """Verify all centralized default constants have expected types and values."""

    def test_ollama_url_type_and_prefix(self):
        from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL

        assert isinstance(DEFAULT_OLLAMA_URL, str)
        assert DEFAULT_OLLAMA_URL.startswith("http://localhost")

    def test_ollama_model_is_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_MODEL

        assert isinstance(DEFAULT_OLLAMA_MODEL, str)
        assert len(DEFAULT_OLLAMA_MODEL) > 0

    def test_postgres_host(self):
        from codomyrmex.config_management.defaults import DEFAULT_POSTGRES_HOST

        assert isinstance(DEFAULT_POSTGRES_HOST, str)
        assert DEFAULT_POSTGRES_HOST == "localhost"

    def test_postgres_port_is_numeric_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_POSTGRES_PORT

        assert isinstance(DEFAULT_POSTGRES_PORT, str)
        assert DEFAULT_POSTGRES_PORT.isdigit()
        assert int(DEFAULT_POSTGRES_PORT) > 0

    def test_redis_url_starts_with_redis_scheme(self):
        from codomyrmex.config_management.defaults import DEFAULT_REDIS_URL

        assert isinstance(DEFAULT_REDIS_URL, str)
        assert DEFAULT_REDIS_URL.startswith("redis://")

    def test_api_port_is_numeric_string(self):
        from codomyrmex.config_management.defaults import DEFAULT_API_PORT

        assert isinstance(DEFAULT_API_PORT, str)
        assert DEFAULT_API_PORT.isdigit()

    def test_api_base_url_contains_port(self):
        from codomyrmex.config_management.defaults import (
            DEFAULT_API_BASE_URL,
            DEFAULT_API_PORT,
        )

        assert DEFAULT_API_PORT in DEFAULT_API_BASE_URL

    def test_otel_endpoint_is_grpc_port(self):
        from codomyrmex.config_management.defaults import DEFAULT_OTEL_ENDPOINT

        assert "4317" in DEFAULT_OTEL_ENDPOINT


# ---------------------------------------------------------------------------
# TestDeepMerge
# ---------------------------------------------------------------------------


class TestDeepMerge:
    """Test deep_merge behaviour — edge cases beyond existing tests."""

    def test_flat_merge_base_and_extension(self):
        base = {"a": 1, "b": 2}
        ext = {"c": 3}
        result = deep_merge(base, ext)
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_nested_merge_recurses(self):
        base = {"db": {"host": "localhost", "port": 5432}}
        ext = {"db": {"port": 5433, "name": "mydb"}}
        result = deep_merge(base, ext)
        assert result["db"]["host"] == "localhost"
        assert result["db"]["port"] == 5433
        assert result["db"]["name"] == "mydb"

    def test_extension_overrides_scalar(self):
        base = {"key": "old"}
        ext = {"key": "new"}
        result = deep_merge(base, ext)
        assert result["key"] == "new"

    def test_empty_extension_returns_base_unchanged(self):
        base = {"x": 1}
        result = deep_merge(base, {})
        assert result == {"x": 1}

    def test_empty_base_returns_extension_values(self):
        ext = {"x": 99}
        result = deep_merge({}, ext)
        assert result == {"x": 99}

    def test_dict_does_not_replace_scalar_with_dict(self):
        # When base has a scalar, extension has dict → extension wins
        base = {"key": "scalar"}
        ext = {"key": {"nested": True}}
        result = deep_merge(base, ext)
        assert result["key"] == {"nested": True}

    def test_scalar_replaces_nested_dict(self):
        # When base has a dict, extension has scalar → extension wins
        base = {"key": {"nested": True}}
        ext = {"key": "scalar"}
        result = deep_merge(base, ext)
        assert result["key"] == "scalar"


# ---------------------------------------------------------------------------
# TestResolveEnvVars
# ---------------------------------------------------------------------------


class TestResolveEnvVars:
    """Test environment variable interpolation."""

    def test_resolves_set_variable(self):
        key = "_TEST_RESOLVE_VAR_XYZ"
        os.environ[key] = "resolved_value"
        try:
            result = resolve_env_vars(f"${{{key}}}")
            assert result == "resolved_value"
        finally:
            del os.environ[key]

    def test_uses_default_when_unset(self):
        key = "_TEST_UNSET_VAR_ABC"
        os.environ.pop(key, None)
        result = resolve_env_vars(f"${{{key}:-mydefault}}")
        assert result == "mydefault"

    def test_leaves_unknown_var_unreplaced(self):
        key = "_TEST_TOTALLY_UNKNOWN_VAR_42"
        os.environ.pop(key, None)
        result = resolve_env_vars(f"${{{key}}}")
        assert result == f"${{{key}}}"

    def test_resolves_nested_dict_values(self):
        key = "_TEST_NESTED_DICT_VAR"
        os.environ[key] = "db_host"
        try:
            result = resolve_env_vars({"host": f"${{{key}}}"})
            assert result["host"] == "db_host"
        finally:
            del os.environ[key]

    def test_resolves_list_items(self):
        key = "_TEST_LIST_ITEM_VAR"
        os.environ[key] = "item_value"
        try:
            result = resolve_env_vars([f"${{{key}}}", "plain"])
            assert result[0] == "item_value"
            assert result[1] == "plain"
        finally:
            del os.environ[key]

    def test_non_string_passthrough(self):
        assert resolve_env_vars(42) == 42
        assert resolve_env_vars(3.14) == 3.14
        assert resolve_env_vars(True) is True
        assert resolve_env_vars(None) is None

    def test_multiple_vars_in_one_string(self):
        os.environ["_TMPA"] = "hello"
        os.environ["_TMPB"] = "world"
        try:
            result = resolve_env_vars("${_TMPA} ${_TMPB}")
            assert result == "hello world"
        finally:
            del os.environ["_TMPA"]
            del os.environ["_TMPB"]


# ---------------------------------------------------------------------------
# TestConfigSchemaJsonschema — ConfigSchema.validate (jsonschema-backed)
# ---------------------------------------------------------------------------


class TestConfigSchemaJsonschema:
    """Test the JSON-schema-backed ConfigSchema.validate method."""

    def _make_schema(self, props, required=None):
        schema = {"type": "object", "properties": props}
        if required:
            schema["required"] = required
        return ConfigSchema(schema=schema)

    def test_valid_config_passes(self):
        cs = self._make_schema(
            {"name": {"type": "string"}, "port": {"type": "integer"}}
        )
        errors = cs.validate({"name": "myapp", "port": 8080})
        assert errors == []

    def test_missing_required_field_gives_error(self):
        cs = self._make_schema({"name": {"type": "string"}}, required=["name"])
        errors = cs.validate({})
        assert len(errors) > 0
        assert any("name" in e for e in errors)

    def test_wrong_type_gives_error(self):
        cs = self._make_schema({"port": {"type": "integer"}})
        errors = cs.validate({"port": "not-a-number"})
        assert len(errors) > 0

    def test_empty_schema_accepts_anything(self):
        cs = ConfigSchema(schema={})
        errors = cs.validate({"random": "data"})
        assert errors == []

    def test_version_defaults_to_draft7(self):
        cs = ConfigSchema(schema={})
        assert cs.version == "draft7"

    def test_non_draft_version_uses_no_format_checker(self):
        cs = ConfigSchema(schema={"type": "object"}, version="draft4")
        errors = cs.validate({"key": "val"})
        assert isinstance(errors, list)


# ---------------------------------------------------------------------------
# TestConfigurationExtra — Configuration dataclass edge paths
# ---------------------------------------------------------------------------


class TestConfigurationExtra:
    """Additional tests for Configuration methods not covered by existing suite."""

    def test_get_value_returns_default_when_missing(self):
        config = Configuration(data={"a": 1})
        assert config.get_value("missing_key", default="fallback") == "fallback"

    def test_get_value_returns_none_by_default(self):
        config = Configuration(data={})
        assert config.get_value("key") is None

    def test_set_value_creates_intermediate_dicts(self):
        config = Configuration(data={})
        config.set_value("a.b.c", "deep_value")
        assert config.data["a"]["b"]["c"] == "deep_value"

    def test_set_value_overwrites_existing(self):
        config = Configuration(data={"x": "old"})
        config.set_value("x", "new")
        assert config.data["x"] == "new"

    def test_to_dict_has_required_keys(self):
        config = Configuration(data={"k": "v"}, source="file.yaml", environment="test")
        d = config.to_dict()
        for key in ("data", "source", "loaded_at", "environment", "version", "metadata"):
            assert key in d

    def test_to_dict_loaded_at_is_iso_string(self):
        config = Configuration(data={})
        d = config.to_dict()
        # ISO format: must contain 'T' separator
        assert "T" in d["loaded_at"]

    def test_validate_without_schema_returns_empty_list(self):
        config = Configuration(data={"a": 1})
        assert config.validate() == []

    def test_validate_with_failing_schema_returns_errors(self):
        cs = ConfigSchema(
            schema={
                "type": "object",
                "properties": {"port": {"type": "integer"}},
                "required": ["port"],
            }
        )
        config = Configuration(data={}, schema=cs)
        errors = config.validate()
        assert len(errors) > 0

    def test_source_attribute_stored(self):
        config = Configuration(data={}, source="env://MYVAR")
        assert config.source == "env://MYVAR"


# ---------------------------------------------------------------------------
# TestConfigurationManagerEdge
# ---------------------------------------------------------------------------


class TestConfigurationManagerEdge:
    """Edge-case tests for ConfigurationManager not covered by existing suite."""

    def test_get_nonexistent_config_returns_none(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        assert mgr.get_configuration("nonexistent") is None

    def test_list_configurations_after_load(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        mgr.load_configuration("test_ns", defaults={"key": "val"})
        names = mgr.list_configurations()
        assert "test_ns" in names

    def test_save_configuration_not_found_returns_false(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.save_configuration("missing", str(tmp_path / "out.yaml"))
        assert result is False

    def test_reload_missing_config_returns_false(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.reload_configuration("nonexistent")
        assert result is False

    def test_create_migration_backup_creates_entry(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        mgr.load_configuration("cfg", defaults={"version": "1.0", "key": "val"})
        result = mgr.create_migration_backup("cfg")
        assert result is True
        # A backup key should exist in configurations
        backup_keys = [k for k in mgr.configurations if k.startswith("cfg_backup_")]
        assert len(backup_keys) == 1

    def test_create_migration_backup_missing_returns_false(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        assert mgr.create_migration_backup("nonexistent") is False

    def test_validate_all_configurations_empty(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.validate_all_configurations()
        assert isinstance(result, dict)
        assert len(result) == 0

    def test_load_configuration_with_defaults(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        cfg = mgr.load_configuration("ns", defaults={"env": "test", "debug": True})
        assert cfg.get_value("env") == "test"
        assert cfg.get_value("debug") is True

    def test_save_and_reload_yaml(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        mgr.load_configuration("save_test", defaults={"answer": 42})
        out_path = str(tmp_path / "save_test.yaml")
        assert mgr.save_configuration("save_test", out_path, format="yaml") is True
        assert os.path.exists(out_path)

    def test_save_as_json(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        mgr.load_configuration("json_test", defaults={"x": 1})
        out_path = str(tmp_path / "json_test.json")
        assert mgr.save_configuration("json_test", out_path, format="json") is True
        with open(out_path) as f:
            data = json.load(f)
        assert data["x"] == 1

    def test_load_configuration_from_file_yaml(self, tmp_path):
        cfg_file = tmp_path / "app.yaml"
        cfg_file.write_text("host: localhost\nport: 9000\n")
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        cfg = mgr.load_configuration_from_file(str(cfg_file))
        assert cfg is not None
        assert cfg.get_value("host") == "localhost"

    def test_load_configuration_from_file_json(self, tmp_path):
        cfg_file = tmp_path / "app.json"
        cfg_file.write_text('{"debug": true, "workers": 4}')
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        cfg = mgr.load_configuration_from_file(str(cfg_file))
        assert cfg is not None
        assert cfg.get_value("workers") == 4

    def test_load_configuration_from_file_missing_returns_none(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.load_configuration_from_file(str(tmp_path / "nonexistent.yaml"))
        assert result is None

    def test_env_var_loading_from_prefix(self, tmp_path):
        # MYAPP_HOST env var should be picked up when loading 'myapp' namespace
        os.environ["MYAPP_HOST"] = "env_host_value"
        try:
            mgr = ConfigurationManager(config_dir=str(tmp_path))
            cfg = mgr.load_configuration("myapp")
            assert cfg.get_value("host") == "env_host_value"
        finally:
            del os.environ["MYAPP_HOST"]

    def test_env_var_nested_via_double_underscore(self, tmp_path):
        os.environ["MYAPP_DATABASE__HOST"] = "nested_host"
        try:
            mgr = ConfigurationManager(config_dir=str(tmp_path))
            cfg = mgr.load_configuration("myapp")
            assert cfg.get_value("database.host") == "nested_host"
        finally:
            del os.environ["MYAPP_DATABASE__HOST"]

    def test_validate_config_schema_valid(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        valid, errors = mgr.validate_config_schema(
            {"port": 8080},
            {"port": ValidatorConfigSchema(type="int", required=True)},
        )
        assert valid is True
        assert errors == []

    def test_validate_config_schema_invalid(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        valid, errors = mgr.validate_config_schema(
            {"port": "not_int"},
            {"port": ValidatorConfigSchema(type="int", required=True)},
        )
        assert valid is False
        assert len(errors) > 0

    def test_get_validation_report_missing_config_returns_none(self, tmp_path):
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.get_validation_report("nonexistent")
        assert result is None

    def test_generate_template_from_schema(self, tmp_path):
        schema_file = tmp_path / "schema.json"
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "port": {"type": "integer"},
                "debug": {"type": "boolean"},
                "tags": {"type": "array"},
                "extra": {"type": "object"},
            },
        }
        schema_file.write_text(json.dumps(schema))
        out = tmp_path / "template.yaml"
        mgr = ConfigurationManager(config_dir=str(tmp_path))
        result = mgr.create_configuration_template(str(schema_file), str(out))
        assert result is True
        assert out.exists()
        with open(out) as f:
            template = yaml.safe_load(f)
        assert "name" in template
        assert "port" in template


# ---------------------------------------------------------------------------
# TestSecretManager
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _CRYPTO_AVAILABLE, reason="cryptography not installed")
class TestSecretManager:
    """Full API coverage for SecretManager using real Fernet encryption."""

    @pytest.fixture
    def mgr(self, tmp_path):
        key_file = str(tmp_path / "test_secrets.key")
        return SecretManager(key_file=key_file)

    def test_store_and_retrieve_by_id(self, mgr):
        secret_id = mgr.store_secret("db_password", "s3cr3t!")
        assert isinstance(secret_id, str)
        retrieved = mgr.get_secret(secret_id)
        assert retrieved == "s3cr3t!"

    def test_retrieve_nonexistent_returns_none(self, mgr):
        assert mgr.get_secret("nonexistent_id") is None

    def test_get_secret_by_name(self, mgr):
        mgr.store_secret("api_key", "key_value_123")
        result = mgr.get_secret_by_name("api_key")
        assert result == "key_value_123"

    def test_get_secret_by_name_missing_returns_none(self, mgr):
        assert mgr.get_secret_by_name("unknown_name") is None

    def test_list_secrets_excludes_values(self, mgr):
        mgr.store_secret("token", "abc123")
        listing = mgr.list_secrets()
        assert len(listing) == 1
        assert "value" not in listing[0]
        assert listing[0]["name"] == "token"

    def test_delete_secret_removes_entry(self, mgr):
        sid = mgr.store_secret("temp", "temp_val")
        assert mgr.delete_secret(sid) is True
        assert mgr.get_secret(sid) is None

    def test_delete_nonexistent_returns_false(self, mgr):
        assert mgr.delete_secret("bad_id") is False

    def test_rotate_key_re_encrypts_secrets(self, mgr):
        sid = mgr.store_secret("rotate_test", "original_value")
        mgr.rotate_key()
        # Secret should still be retrievable with new key
        assert mgr.get_secret(sid) == "original_value"

    def test_rotate_secret_replaces_old(self, mgr):
        mgr.store_secret("my_token", "old_value")
        event = mgr.rotate_secret("my_token", "new_value")
        assert event["secret_name"] == "my_token"
        assert isinstance(event["new_id"], str)
        # Old value no longer accessible by name
        assert mgr.get_secret_by_name("my_token") == "new_value"

    def test_get_rotation_history_all(self, mgr):
        mgr.store_secret("s", "v1")
        mgr.rotate_secret("s", "v2")
        history = mgr.get_rotation_history()
        assert len(history) == 1
        assert history[0]["secret_name"] == "s"

    def test_get_rotation_history_filtered_by_name(self, mgr):
        mgr.store_secret("x", "v1")
        mgr.rotate_secret("x", "v2")
        mgr.store_secret("y", "a")
        mgr.rotate_secret("y", "b")
        assert len(mgr.get_rotation_history(name="x")) == 1
        assert len(mgr.get_rotation_history(name="y")) == 1

    def test_check_key_age_fresh_secret(self, mgr):
        mgr.store_secret("fresh", "value")
        info = mgr.check_key_age("fresh", max_age_days=90)
        assert info["name"] == "fresh"
        assert info["age_days"] == 0
        assert info["stale"] is False

    def test_check_key_age_missing_secret(self, mgr):
        info = mgr.check_key_age("missing_secret")
        assert info["age_days"] == -1
        assert info["stale"] is False

    def test_store_secret_with_metadata(self, mgr):
        sid = mgr.store_secret("meta_test", "val", metadata={"owner": "team_a"})
        listing = mgr.list_secrets()
        entry = next(s for s in listing if s["id"] == sid)
        assert entry["metadata"]["owner"] == "team_a"

    def test_key_persists_to_file(self, tmp_path):
        key_file = str(tmp_path / "persistent.key")
        mgr1 = SecretManager(key_file=key_file)
        mgr1.store_secret("persist", "persist_val")
        # Load key from file and decrypt
        SecretManager(key_file=key_file)
        # mgr2 has same key so can decrypt if we copy secrets
        assert os.path.exists(key_file)


# ---------------------------------------------------------------------------
# TestConfigurationDeployer
# ---------------------------------------------------------------------------


class TestConfigurationDeployer:
    """Full API for ConfigurationDeployer — real file I/O."""

    @pytest.fixture
    def deployer(self, tmp_path):
        return ConfigurationDeployer(workspace_dir=str(tmp_path))

    def test_init_creates_directories(self, deployer, tmp_path):
        assert (tmp_path / "config_deployments").exists()
        assert (tmp_path / "environments").exists()

    def test_create_environment(self, deployer, tmp_path):
        env = deployer.create_environment(
            "dev",
            EnvironmentType.DEVELOPMENT,
            config_path=str(tmp_path / "cfg"),
        )
        assert isinstance(env, Environment)
        assert env.name == "dev"
        assert env.type == EnvironmentType.DEVELOPMENT

    def test_create_environment_saves_json_file(self, deployer, tmp_path):
        deployer.create_environment(
            "staging", EnvironmentType.STAGING, config_path=str(tmp_path)
        )
        env_file = tmp_path / "environments" / "staging.json"
        assert env_file.exists()
        data = json.loads(env_file.read_text())
        assert data["name"] == "staging"
        assert data["type"] == "staging"

    def test_get_environment_config(self, deployer, tmp_path):
        deployer.create_environment("prod", EnvironmentType.PRODUCTION, config_path=str(tmp_path))
        env = deployer.get_environment_config("prod")
        assert env is not None
        assert env.type == EnvironmentType.PRODUCTION

    def test_get_environment_config_missing_returns_none(self, deployer):
        assert deployer.get_environment_config("nonexistent") is None

    def test_list_environments_after_creation(self, deployer, tmp_path):
        deployer.create_environment("e1", EnvironmentType.DEVELOPMENT, config_path=str(tmp_path))
        deployer.create_environment("e2", EnvironmentType.TESTING, config_path=str(tmp_path))
        envs = deployer.list_environments()
        names = [e.name for e in envs]
        assert "e1" in names
        assert "e2" in names

    def test_deploy_configuration_success(self, deployer, tmp_path):
        cfg_file = tmp_path / "app.yaml"
        cfg_file.write_text("key: value\n")
        dest = tmp_path / "dest"
        dest.mkdir()
        deployer.create_environment("test", EnvironmentType.TESTING, config_path=str(dest))
        deployment = deployer.deploy_configuration(
            "test", [str(cfg_file)], deployed_by="pytest"
        )
        assert deployment.status == DeploymentStatus.SUCCESS
        assert deployment.environment == "test"
        assert deployment.deployed_by == "pytest"

    def test_deploy_saves_deployment_file(self, deployer, tmp_path):
        cfg_file = tmp_path / "conf.yaml"
        cfg_file.write_text("x: 1\n")
        dest = tmp_path / "dest2"
        dest.mkdir()
        deployer.create_environment("qa", EnvironmentType.TESTING, config_path=str(dest))
        deployment = deployer.deploy_configuration("qa", [str(cfg_file)])
        dep_file = tmp_path / "config_deployments" / f"{deployment.deployment_id}.json"
        assert dep_file.exists()

    def test_deploy_to_missing_environment_raises(self, deployer, tmp_path):
        from codomyrmex.exceptions import CodomyrmexError

        with pytest.raises(CodomyrmexError, match="Environment not found"):
            deployer.deploy_configuration("no_such_env", [])

    def test_get_deployment_status(self, deployer, tmp_path):
        cfg_file = tmp_path / "x.yaml"
        cfg_file.write_text("a: b\n")
        dest = tmp_path / "d3"
        dest.mkdir()
        deployer.create_environment("s3", EnvironmentType.STAGING, config_path=str(dest))
        dep = deployer.deploy_configuration("s3", [str(cfg_file)])
        fetched = deployer.get_deployment_status(dep.deployment_id)
        assert fetched is not None
        assert fetched.deployment_id == dep.deployment_id

    def test_get_deployment_status_missing_returns_none(self, deployer):
        assert deployer.get_deployment_status("no_such_id") is None

    def test_list_deployments_filtered_by_environment(self, deployer, tmp_path):
        cfg_file = tmp_path / "f.yaml"
        cfg_file.write_text("z: 1\n")
        dest = tmp_path / "d4"
        dest.mkdir()
        deployer.create_environment("filter_env", EnvironmentType.TESTING, config_path=str(dest))
        deployer.deploy_configuration("filter_env", [str(cfg_file)])
        all_deps = deployer.list_deployments()
        filtered = deployer.list_deployments(environment="filter_env")
        assert len(filtered) <= len(all_deps)
        for dep in filtered:
            assert dep.environment == "filter_env"

    def test_rollback_deployment(self, deployer, tmp_path):
        cfg_file = tmp_path / "rb.yaml"
        cfg_file.write_text("rollback: true\n")
        dest = tmp_path / "d5"
        dest.mkdir()
        deployer.create_environment("rb_env", EnvironmentType.TESTING, config_path=str(dest))
        dep = deployer.deploy_configuration("rb_env", [str(cfg_file)])
        rollback_dep = deployer.rollback_deployment(dep.deployment_id)
        assert rollback_dep.status == DeploymentStatus.SUCCESS

    def test_rollback_nonexistent_deployment_raises(self, deployer):
        from codomyrmex.exceptions import CodomyrmexError

        with pytest.raises(CodomyrmexError, match="Deployment not found"):
            deployer.rollback_deployment("bad_id")

    def test_apply_environment_variables(self, deployer):
        content = "host: ${DB_HOST}\nport: $PORT"
        result = deployer._apply_environment_variables(
            content, {"DB_HOST": "db_server", "PORT": "5432"}
        )
        assert "db_server" in result
        assert "5432" in result

    def test_deployment_status_enum_values(self):
        assert DeploymentStatus.PENDING.value == "pending"
        assert DeploymentStatus.SUCCESS.value == "success"
        assert DeploymentStatus.FAILED.value == "failed"
        assert DeploymentStatus.ROLLED_BACK.value == "rolled_back"

    def test_environment_type_enum_values(self):
        assert EnvironmentType.DEVELOPMENT.value == "development"
        assert EnvironmentType.STAGING.value == "staging"
        assert EnvironmentType.PRODUCTION.value == "production"
        assert EnvironmentType.TESTING.value == "testing"


# ---------------------------------------------------------------------------
# TestPredefinedSchemas — validation/config_validator.py predefined schemas
# ---------------------------------------------------------------------------


class TestPredefinedSchemas:
    """Test get_logging_config_schema, get_database_config_schema, get_ai_model_config_schema."""

    def test_logging_schema_valid_config(self):
        schema = get_logging_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"level": "INFO", "format": "TEXT"})
        assert result.is_valid

    def test_logging_schema_invalid_level(self):
        schema = get_logging_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"level": "VERBOSE"})
        assert not result.is_valid

    def test_logging_schema_invalid_format(self):
        schema = get_logging_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"format": "XML"})
        assert not result.is_valid

    def test_database_schema_valid_config(self):
        schema = get_database_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate(
            {
                "host": "localhost",
                "database": "mydb",
                "username": "admin",
                "password": "secret",
            }
        )
        assert result.is_valid

    def test_database_schema_missing_required_field(self):
        schema = get_database_config_schema()
        validator = ConfigValidator(schema=schema)
        # Missing 'password'
        result = validator.validate(
            {"host": "localhost", "database": "mydb", "username": "admin"}
        )
        assert not result.is_valid

    def test_database_schema_invalid_ssl_mode(self):
        schema = get_database_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate(
            {
                "host": "localhost",
                "database": "mydb",
                "username": "admin",
                "password": "secret",
                "ssl_mode": "invalid_mode",
            }
        )
        assert not result.is_valid

    def test_ai_model_schema_valid(self):
        schema = get_ai_model_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"provider": "openai", "model": "gpt-4"})
        assert result.is_valid

    def test_ai_model_schema_invalid_provider(self):
        schema = get_ai_model_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate({"provider": "unknown_provider", "model": "x"})
        assert not result.is_valid

    def test_ai_model_schema_temperature_out_of_range(self):
        schema = get_ai_model_config_schema()
        validator = ConfigValidator(schema=schema)
        result = validator.validate(
            {"provider": "anthropic", "model": "claude-3", "temperature": 5.0}
        )
        assert not result.is_valid

    def test_validate_config_schema_convenience_function_valid(self):
        schema = get_logging_config_schema()
        valid, errors = validate_config_schema({"level": "DEBUG", "format": "JSON"}, schema)
        assert valid is True
        assert errors == []

    def test_validate_config_schema_convenience_function_invalid(self):
        schema = get_logging_config_schema()
        valid, errors = validate_config_schema({"level": "OOPS"}, schema)
        assert valid is False
        assert len(errors) > 0


# ---------------------------------------------------------------------------
# TestConstraintValidation — additional constraint types
# ---------------------------------------------------------------------------


class TestConstraintValidation:
    """Test all constraint types in ConfigValidator._validate_field_constraints."""

    def test_min_length_string_violation(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"name": "ab"}, {"name": {"min_length": 5}}
        )
        assert len(issues) > 0

    def test_min_length_string_ok(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"name": "hello"}, {"name": {"min_length": 3}}
        )
        assert len(issues) == 0

    def test_max_length_string_violation(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"name": "toolongname"}, {"name": {"max_length": 5}}
        )
        assert len(issues) > 0

    def test_pattern_constraint_match(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"email": "user@example.com"}, {"email": {"pattern": r"^[^@]+@[^@]+\.[^@]+$"}}
        )
        assert len(issues) == 0

    def test_pattern_constraint_no_match(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"email": "not_an_email"}, {"email": {"pattern": r"^[^@]+@[^@]+\.[^@]+$"}}
        )
        assert len(issues) > 0

    def test_enum_constraint_valid(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"env": "production"}, {"env": {"enum": ["development", "staging", "production"]}}
        )
        assert len(issues) == 0

    def test_enum_constraint_invalid(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"env": "unknown"}, {"env": {"enum": ["development", "staging", "production"]}}
        )
        assert len(issues) > 0

    def test_custom_constraint_passes(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"value": 10}, {"value": {"custom": lambda v: v > 0}}
        )
        assert len(issues) == 0

    def test_custom_constraint_fails(self):
        validator = ConfigValidator()
        issues = validator.validate_values(
            {"value": -1}, {"value": {"custom": lambda v: v > 0}}
        )
        assert len(issues) > 0

    def test_check_type_any_always_passes(self):
        validator = ConfigValidator()
        assert validator._check_type("anything", "any") is True
        assert validator._check_type(42, "any") is True
        assert validator._check_type(None, "any") is True

    def test_check_type_unknown_type_returns_false(self):
        validator = ConfigValidator()
        assert validator._check_type("val", "unknown_type") is False


# ---------------------------------------------------------------------------
# TestMigratorExtended — additional migrator paths
# ---------------------------------------------------------------------------


class TestMigratorExtended:
    """Additional ConfigMigrator tests for stubs and nested value operations."""

    def test_split_field_adds_warning(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.SPLIT_FIELD,
                description="Split name",
                from_version="1.0",
                to_version="2.0",
                old_path="full_name",
            )
        )
        result = m.migrate_config({"full_name": "John Doe"}, "1.0", "2.0")
        assert result.success
        assert any("split" in w.lower() for w in result.warnings)

    def test_merge_fields_adds_warning(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.MERGE_FIELDS,
                description="Merge fields",
                from_version="1.0",
                to_version="2.0",
            )
        )
        result = m.migrate_config({"a": 1, "b": 2}, "1.0", "2.0")
        assert result.success
        assert any("merge" in w.lower() for w in result.warnings)

    def test_rename_missing_field_adds_warning(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.RENAME_FIELD,
                description="Rename nonexistent",
                from_version="1.0",
                to_version="2.0",
                old_path="ghost_field",
                new_path="real_field",
            )
        )
        result = m.migrate_config({}, "1.0", "2.0")
        assert result.success
        assert any("ghost_field" in w for w in result.warnings)

    def test_add_field_when_already_exists_adds_warning(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Add existing field",
                from_version="1.0",
                to_version="2.0",
                new_path="existing",
                new_value="new_val",
            )
        )
        result = m.migrate_config({"existing": "original_val"}, "1.0", "2.0")
        assert result.success
        # Original value preserved
        assert result.migrated_config["existing"] == "original_val"
        assert any("already exists" in w for w in result.warnings)

    def test_remove_missing_field_adds_warning(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.REMOVE_FIELD,
                description="Remove missing",
                from_version="1.0",
                to_version="2.0",
                old_path="missing_field",
            )
        )
        result = m.migrate_config({}, "1.0", "2.0")
        assert result.success
        assert any("missing_field" in w for w in result.warnings)

    def test_same_version_migration_returns_warning(self):
        m = ConfigMigrator()
        result = m.migrate_config({"key": "val"}, "1.0", "1.0")
        assert result.success
        assert any("same" in w.lower() for w in result.warnings)

    def test_no_migration_path_returns_failure(self):
        m = ConfigMigrator()
        result = m.migrate_config({"key": "val"}, "1.0", "99.0")
        assert not result.success
        assert any("No migration path" in e for e in result.errors)

    def test_custom_transform_applies_function(self):
        m = ConfigMigrator()
        m.register_migration("1.0", "2.0", lambda cfg: {**cfg, "transformed": True})
        result = m.migrate_config({"name": "app"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config.get("transformed") is True

    def test_transform_value_with_direct_replacement(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.TRANSFORM_VALUE,
                description="Replace value directly",
                from_version="1.0",
                to_version="2.0",
                old_path="mode",
                new_value="production",
            )
        )
        result = m.migrate_config({"mode": "dev"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config["mode"] == "production"

    def test_move_field_nested_to_nested(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.MOVE_FIELD,
                description="Move timeout to connection_pool",
                from_version="1.0",
                to_version="2.0",
                old_path="timeout",
                new_path="connection_pool.timeout",
            )
        )
        result = m.migrate_config({"timeout": 30, "host": "db"}, "1.0", "2.0")
        assert result.success
        assert "timeout" not in result.migrated_config
        assert result.migrated_config["connection_pool"]["timeout"] == 30

    def test_create_logging_migration_rules_count(self):
        rules = create_logging_migration_rules()
        assert len(rules) == 3
        assert all(isinstance(r, MigrationRule) for r in rules)

    def test_create_database_migration_rules_count(self):
        rules = create_database_migration_rules()
        assert len(rules) == 3
        assert all(isinstance(r, MigrationRule) for r in rules)

    def test_migrate_config_convenience_function_same_version(self):
        result = migrate_config({"key": "val"}, "1.0.0", "1.0.0")
        assert result.success

    def test_get_nested_value_deep_path(self):
        m = ConfigMigrator()
        config = {"a": {"b": {"c": "deep"}}}
        assert m._get_nested_value(config, "a.b.c") == "deep"

    def test_get_nested_value_missing_returns_none(self):
        m = ConfigMigrator()
        config = {"a": {"b": "val"}}
        assert m._get_nested_value(config, "a.x.y") is None

    def test_set_nested_value_creates_path(self):
        m = ConfigMigrator()
        config = {}
        m._set_nested_value(config, "x.y.z", 42)
        assert config["x"]["y"]["z"] == 42

    def test_delete_nested_value_removes_key(self):
        m = ConfigMigrator()
        config = {"db": {"host": "localhost", "port": 5432}}
        m._delete_nested_value(config, "db.port")
        assert "port" not in config["db"]
        assert config["db"]["host"] == "localhost"

    def test_condition_skips_rule_when_false(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Conditional add",
                from_version="1.0",
                to_version="2.0",
                new_path="added",
                new_value="yes",
                condition=lambda cfg: "trigger" in cfg,
            )
        )
        # No 'trigger' key → condition is False → rule skipped
        result = m.migrate_config({"name": "app"}, "1.0", "2.0")
        assert result.success
        assert "added" not in result.migrated_config

    def test_condition_applies_rule_when_true(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Conditional add",
                from_version="1.0",
                to_version="2.0",
                new_path="added",
                new_value="yes",
                condition=lambda cfg: "trigger" in cfg,
            )
        )
        result = m.migrate_config({"trigger": True, "name": "app"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config.get("added") == "yes"


# ---------------------------------------------------------------------------
# TestCustomValidatorIntegration
# ---------------------------------------------------------------------------


class TestCustomValidatorIntegration:
    """Integration tests for custom validators returning ValidationResult."""

    def test_custom_validator_returning_validation_result(self):
        validator = ConfigValidator()

        def strict_validator(config):
            result = ValidationResult(is_valid=True)
            if config.get("debug") is True and config.get("environment") == "production":
                result.add_issue(
                    ValidationIssue(
                        field_path="debug",
                        message="debug must be False in production",
                        severity=ValidationSeverity.ERROR,
                    )
                )
            return result

        validator.add_custom_validator("prod_debug_check", strict_validator)
        result = validator.validate({"debug": True, "environment": "production"})
        assert not result.is_valid

    def test_custom_validator_returning_list_of_issues(self):
        validator = ConfigValidator()

        def list_validator(config):
            issues = []
            if "version" not in config:
                issues.append(
                    ValidationIssue(
                        field_path="version",
                        message="version is required",
                        severity=ValidationSeverity.ERROR,
                    )
                )
            return issues

        validator.add_custom_validator("version_check", list_validator)
        result = validator.validate({"name": "app"})
        assert not result.is_valid

    def test_failing_custom_validator_produces_error_issue(self):
        validator = ConfigValidator()

        def broken_validator(config):
            raise RuntimeError("validator exploded")

        validator.add_custom_validator("broken", broken_validator)
        result = validator.validate({})
        # Should capture the error as an issue rather than propagating
        assert not result.is_valid
        assert any("broken" in issue.message for issue in result.errors)
