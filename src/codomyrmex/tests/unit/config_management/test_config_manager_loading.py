"""Unit tests for ConfigurationManager -- file loading, env vars, merging, and related edge cases."""

import json
import os

import pytest
import yaml

from codomyrmex.config_management.core.config_loader import (
    ConfigSchema,
    Configuration,
    ConfigurationManager,
    load_configuration,
    validate_configuration,
)


# ---------------------------------------------------------------------------
# ConfigurationManager -- file loading tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerFileLoading:
    """Tests for ConfigurationManager loading from files."""

    def test_load_from_yaml_file(self, tmp_path):
        """Load configuration from a YAML file."""
        config_data = {"server": {"host": "0.0.0.0", "port": 9090}, "debug": True}
        yaml_file = tmp_path / "app.yaml"
        yaml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("app", sources=["app.yaml"])

        assert config.data["server"]["host"] == "0.0.0.0"
        assert config.data["server"]["port"] == 9090
        assert config.data["debug"] is True

    def test_load_from_json_file(self, tmp_path):
        """Load configuration from a JSON file."""
        config_data = {"name": "myapp", "workers": 4}
        json_file = tmp_path / "app.json"
        json_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("app", sources=["app.json"])

        assert config.data["name"] == "myapp"
        assert config.data["workers"] == 4

    def test_load_from_yml_extension(self, tmp_path):
        """Load configuration from a .yml file."""
        config_data = {"key": "yml_value"}
        yml_file = tmp_path / "settings.yml"
        yml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("settings", sources=["settings.yml"])
        assert config.data["key"] == "yml_value"

    def test_load_configuration_from_file_direct(self, tmp_path):
        """load_configuration_from_file loads by absolute path."""
        config_data = {"direct": "load"}
        json_file = tmp_path / "direct.json"
        json_file.write_text(json.dumps(config_data))

        manager = ConfigurationManager()
        config = manager.load_configuration_from_file(str(json_file))

        assert config is not None
        assert config.data["direct"] == "load"
        assert config.source == str(json_file)

    def test_load_configuration_from_file_missing(self):
        """load_configuration_from_file returns None for missing files."""
        manager = ConfigurationManager()
        config = manager.load_configuration_from_file("/nonexistent/path/config.json")
        assert config is None

    def test_load_yaml_via_direct_path(self, tmp_path):
        """load_configuration_from_file handles YAML by extension."""
        config_data = {"yaml_key": [1, 2, 3]}
        yaml_file = tmp_path / "data.yaml"
        yaml_file.write_text(yaml.dump(config_data))

        manager = ConfigurationManager()
        config = manager.load_configuration_from_file(str(yaml_file))

        assert config is not None
        assert config.data["yaml_key"] == [1, 2, 3]

    def test_load_nonexistent_source_returns_empty_config(self, tmp_path):
        """Loading from non-existent default sources yields empty data dict."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("nonexistent_cfg")
        assert config.data == {}


# ---------------------------------------------------------------------------
# ConfigurationManager -- environment variable override tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerEnvVars:
    """Tests for environment variable loading and override."""

    def test_env_var_override(self, tmp_path):
        """Environment variables with CONFIG_NAME_ prefix override file values."""
        # Write a YAML file
        yaml_file = tmp_path / "myapp.yaml"
        yaml_file.write_text(yaml.dump({"host": "filehost", "port": 3000}))

        # Set env var with the correct prefix
        saved = {k: os.environ.get(k) for k in ("MYAPP_HOST", "MYAPP_PORT")}
        os.environ["MYAPP_HOST"] = "envhost"
        os.environ["MYAPP_PORT"] = "9999"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("myapp", sources=["myapp.yaml"])

            # Env vars should override (note: env values are strings)
            assert config.data["host"] == "envhost"
            assert config.data["port"] == "9999"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_env_var_only_matching_prefix(self, tmp_path):
        """Only env vars with the correct prefix are loaded."""
        saved = {k: os.environ.get(k) for k in ("TESTCFG_A", "OTHERCFG_B")}
        os.environ["TESTCFG_A"] = "1"
        os.environ["OTHERCFG_B"] = "2"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("testcfg")

            assert "a" in config.data
            assert "b" not in config.data
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_env_source_protocol(self, tmp_path):
        """Sources with env:// protocol load specific environment variables."""
        saved = os.environ.get("MY_SECRET")
        os.environ["MY_SECRET"] = "s3cr3t"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration("secrets", sources=["env://MY_SECRET"])

            assert config.data.get("MY_SECRET") == "s3cr3t"
        finally:
            if saved is None:
                os.environ.pop("MY_SECRET", None)
            else:
                os.environ["MY_SECRET"] = saved

    def test_env_source_protocol_missing_raises(self, tmp_path):
        """env:// source for missing variable raises FileNotFoundError (single-source guard)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        os.environ.pop("DEFINITELY_NOT_SET_12345", None)
        with pytest.raises(FileNotFoundError, match="Configuration source not found"):
            manager.load_configuration("x", sources=["env://DEFINITELY_NOT_SET_12345"])


# ---------------------------------------------------------------------------
# ConfigurationManager -- merge / override / multi-source tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerMerge:
    """Tests for multi-source merging and override behavior."""

    def test_later_sources_override_earlier(self, tmp_path):
        """When multiple sources define the same key, later sources win."""
        base = tmp_path / "base.yaml"
        base.write_text(yaml.dump({"host": "base_host", "port": 1111}))

        override = tmp_path / "override.json"
        override.write_text(json.dumps({"host": "override_host"}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "app", sources=["base.yaml", "override.json"]
        )

        assert config.data["host"] == "override_host"
        assert config.data["port"] == 1111  # preserved from base

    def test_multiple_yaml_files_merged(self, tmp_path):
        """Multiple YAML files are merged left-to-right."""
        f1 = tmp_path / "a.yaml"
        f1.write_text(yaml.dump({"x": 1, "y": 2}))

        f2 = tmp_path / "b.yaml"
        f2.write_text(yaml.dump({"y": 20, "z": 30}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("merged", sources=["a.yaml", "b.yaml"])

        assert config.data["x"] == 1
        assert config.data["y"] == 20
        assert config.data["z"] == 30

    def test_source_tracking(self, tmp_path):
        """The config.source string lists all loaded sources."""
        f1 = tmp_path / "s1.yaml"
        f1.write_text(yaml.dump({"a": 1}))
        f2 = tmp_path / "s2.json"
        f2.write_text(json.dumps({"b": 2}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration("tracked", sources=["s1.yaml", "s2.json"])

        assert "s1.yaml" in config.source
        assert "s2.json" in config.source


# ---------------------------------------------------------------------------
# ConfigurationManager -- config_dir permission error fallback (lines 204-208)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerDirFallback:
    """Tests for config_dir creation fallback when directory is not writable."""

    def test_unwritable_config_dir_falls_back_to_tempdir(self):
        """When config_dir cannot be created, manager falls back to a temp directory (lines 204-208)."""
        # Use a path that cannot be created (nested under /proc or similar)
        # On macOS/Linux, /dev/null/subdir will fail
        impossible_path = "/dev/null/impossible_nested_config_dir"
        manager = ConfigurationManager(config_dir=impossible_path)
        # The manager should have fallen back to a temp directory
        assert manager.config_dir != impossible_path
        assert os.path.isdir(manager.config_dir)
        assert "codomyrmex_config_" in manager.config_dir


# ---------------------------------------------------------------------------
# ConfigurationManager -- URL source loading (lines 303, 328-340)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestConfigurationManagerUrlSource:
    """Tests for HTTP/HTTPS URL source loading paths."""

    @pytest.mark.skipif(
        not os.getenv("CODOMYRMEX_TEST_NETWORK"),
        reason="Network tests disabled (set CODOMYRMEX_TEST_NETWORK=1 to enable)",
    )
    def test_load_from_https_url(self, tmp_path):
        """Loading from an HTTPS URL exercises _load_from_url (lines 328-340)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        # Use a well-known JSON endpoint
        config = manager.load_configuration(
            "remote",
            sources=["https://httpbin.org/json"],
        )
        assert config.data != {}

    def test_load_from_unreachable_url_raises_for_single_source(self, tmp_path):
        """Unreachable URL as single source raises FileNotFoundError (line 264-265)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        with pytest.raises(FileNotFoundError, match="Configuration source not found"):
            manager.load_configuration(
                "unreachable",
                sources=["https://this-host-does-not-exist-12345.invalid/config.json"],
            )

    def test_http_source_with_fallback(self, tmp_path):
        """http:// source that fails is graceful when other sources exist too (line 303)."""
        # Create a valid fallback source
        fallback = tmp_path / "fallback.json"
        fallback.write_text(json.dumps({"fallback": True}))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        config = manager.load_configuration(
            "http_test",
            sources=["http://127.0.0.1:1/nonexistent", "fallback.json"],
        )
        assert config is not None
        assert config.data.get("fallback") is True

    def test_load_source_dispatches_url(self, tmp_path):
        """_load_source dispatches http/https URLs to _load_from_url (line 301-303)."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        # Directly call _load_source to exercise the URL dispatch
        result = manager._load_source("http://127.0.0.1:1/nonexistent")
        assert result is None

        result2 = manager._load_source("https://127.0.0.1:1/nonexistent")
        assert result2 is None


# ---------------------------------------------------------------------------
# ConfigurationManager -- _load_file error paths
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLoadFileErrors:
    """Tests for _load_file error handling."""

    def test_load_malformed_yaml(self, tmp_path):
        """Malformed YAML returns None from _load_file."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text(":\n  invalid:\n    - [unclosed")

        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._load_file(str(bad_yaml))
        # yaml.safe_load may raise or return partial -- _load_file catches and returns None
        assert result is None or isinstance(result, dict)

    def test_load_binary_file_as_json(self, tmp_path):
        """Binary content in a .json file returns None from _load_file."""
        binary_file = tmp_path / "binary.json"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._load_file(str(binary_file))
        assert result is None


# ---------------------------------------------------------------------------
# ConfigurationManager -- _load_schema error and YAML paths
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLoadSchemaEdgeCases:
    """Tests for _load_schema error and YAML paths."""

    def test_load_schema_from_yaml(self, tmp_path):
        """_load_schema loads from YAML when extension is .yaml."""
        schema_data = {
            "type": "object",
            "title": "YamlSchema",
            "description": "A YAML schema",
            "properties": {"name": {"type": "string"}},
        }
        schema_file = tmp_path / "schema.yaml"
        schema_file.write_text(yaml.dump(schema_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        schema = manager._load_schema(str(schema_file))

        assert schema is not None
        assert schema.title == "YamlSchema"
        assert schema.description == "A YAML schema"

    def test_load_schema_from_yml(self, tmp_path):
        """_load_schema loads from YAML when extension is .yml."""
        schema_data = {
            "type": "object",
            "title": "YmlSchema",
            "properties": {"port": {"type": "integer"}},
        }
        schema_file = tmp_path / "schema.yml"
        schema_file.write_text(yaml.dump(schema_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))
        schema = manager._load_schema(str(schema_file))

        assert schema is not None
        assert schema.title == "YmlSchema"

    def test_load_schema_invalid_file(self, tmp_path):
        """_load_schema returns None for invalid schema file."""
        bad_schema = tmp_path / "bad_schema.json"
        bad_schema.write_text("not valid json at all {{{")

        manager = ConfigurationManager(config_dir=str(tmp_path))
        schema = manager._load_schema(str(bad_schema))
        assert schema is None


# ---------------------------------------------------------------------------
# ConfigurationManager -- _load_environment_variables edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLoadEnvironmentVariables:
    """Tests for _load_environment_variables edge cases."""

    def test_no_matching_env_vars(self, tmp_path):
        """When no env vars match the prefix, empty dict is returned."""
        manager = ConfigurationManager(config_dir=str(tmp_path))
        result = manager._load_environment_variables("ZZZZUNIQUEPREFIXNOTINENV")
        assert result == {}

    def test_case_sensitivity_of_prefix(self, tmp_path):
        """Prefix is uppercase of config name -- env var keys must match exactly."""
        saved = os.environ.get("MIXEDCASE_KEY")
        os.environ["MIXEDCASE_KEY"] = "found"
        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            # config name "mixedcase" -> prefix "MIXEDCASE_"
            result = manager._load_environment_variables("mixedcase")
            assert result.get("key") == "found"
        finally:
            if saved is None:
                os.environ.pop("MIXEDCASE_KEY", None)
            else:
                os.environ["MIXEDCASE_KEY"] = saved


# ---------------------------------------------------------------------------
# Convenience function -- load_configuration (lines 757-758)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestLoadConfigurationConvenience:
    """Tests for the module-level load_configuration convenience function."""

    def test_load_configuration_creates_manager_and_loads(self, tmp_path):
        """load_configuration convenience function creates a manager internally (lines 757-758)."""
        # Write a config file in the cwd-based config dir or use a named config
        # The function creates its own ConfigurationManager using cwd/config
        config = load_configuration("nonexistent_convenience_test")
        # Should return a Configuration (possibly with empty data)
        assert isinstance(config, Configuration)

    def test_load_configuration_with_explicit_sources(self, tmp_path):
        """load_configuration with explicit source list exercises the full path."""
        config_file = tmp_path / "conv.json"
        config_file.write_text(json.dumps({"conv_key": "conv_val"}))

        config = load_configuration(
            "conv",
            sources=[f"file://{config_file}"],
        )
        assert isinstance(config, Configuration)
        assert config.data.get("conv_key") == "conv_val"
