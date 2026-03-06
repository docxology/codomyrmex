"""Zero-mock tests for new configuration features: deep merge, env var substitution, and precedence."""

import json
import os

import pytest
import yaml

from codomyrmex.config_management.core.config_loader import (
    ConfigurationManager,
    deep_merge,
    resolve_env_vars,
)


@pytest.mark.unit
class TestConfigFeatures:
    """Test suite for deep merge, env var resolution, and precedence."""

    def test_deep_merge(self):
        """Verify deep_merge recursively merges dictionaries."""
        base = {
            "a": 1,
            "nested": {"b": 2, "c": 3},
            "other": [1, 2]
        }
        extension = {
            "nested": {"c": 30, "d": 4},
            "other": [3],
            "new": "val"
        }
        result = deep_merge(base, extension)

        assert result["a"] == 1
        assert result["nested"]["b"] == 2
        assert result["nested"]["c"] == 30
        assert result["nested"]["d"] == 4
        assert result["other"] == [3]
        assert result["new"] == "val"

    def test_resolve_env_vars(self):
        """Verify resolve_env_vars substitutes ${VAR} and ${VAR:-default}."""
        os.environ["TEST_VAR_1"] = "resolved_1"
        os.environ["TEST_VAR_2"] = "resolved_2"

        data = {
            "k1": "${TEST_VAR_1}",
            "k2": "${TEST_VAR_2:-default_2}",
            "k3": "${MISSING_VAR:-default_3}",
            "k4": "${MISSING_VAR_NO_DEFAULT}",
            "nested": {
                "list": ["prefix_${TEST_VAR_1}_suffix", 42]
            }
        }

        resolved = resolve_env_vars(data)

        assert resolved["k1"] == "resolved_1"
        assert resolved["k2"] == "resolved_2"
        assert resolved["k3"] == "default_3"
        assert resolved["k4"] == "${MISSING_VAR_NO_DEFAULT}"
        assert resolved["nested"]["list"][0] == "prefix_resolved_1_suffix"
        assert resolved["nested"]["list"][1] == 42

    def test_precedence_and_substitution(self, tmp_path):
        """Verify precedence: Defaults < Files < Env Vars, and substitution in final step."""
        # 1. Defaults
        defaults = {
            "app": {
                "name": "DefaultApp",
                "port": 8080,
                "db": {
                    "host": "localhost",
                    "user": "admin"
                }
            },
            "env_test": "${ENV_VAR_SUBST:-default_subst}"
        }

        # 2. File override
        config_file = tmp_path / "myapp.yaml"
        config_file.write_text(yaml.dump({
            "app": {
                "name": "FileApp",
                "db": {
                    "host": "db.production.com"
                }
            }
        }))

        # 3. Environment variable overrides (including nested via double underscore)
        os.environ["MYAPP_APP__DB__USER"] = "prod_user"
        os.environ["ENV_VAR_SUBST"] = "overridden_subst"

        try:
            manager = ConfigurationManager(config_dir=str(tmp_path))
            config = manager.load_configuration(
                "myapp",
                sources=["myapp.yaml"],
                defaults=defaults
            )

            # Check precedence
            assert config.data["app"]["name"] == "FileApp"  # File > Default
            assert config.data["app"]["port"] == 8080      # Default (not overridden)
            assert config.data["app"]["db"]["host"] == "db.production.com" # File > Default
            assert config.data["app"]["db"]["user"] == "prod_user"         # Env > File/Default

            # Check substitution
            assert config.data["env_test"] == "overridden_subst"

        finally:
            os.environ.pop("MYAPP_APP__DB__USER", None)
            os.environ.pop("ENV_VAR_SUBST", None)

    def test_yaml_json_loading(self, tmp_path):
        """Verify loading from both YAML and JSON files works as expected."""
        yaml_data = {"format": "yaml", "shared": "yaml_val"}
        json_data = {"format": "json", "shared": "json_val"}

        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(yaml.dump(yaml_data))

        json_file = tmp_path / "config.json"
        json_file.write_text(json.dumps(json_data))

        manager = ConfigurationManager(config_dir=str(tmp_path))

        # Load YAML
        config_yaml = manager.load_configuration("config_yaml", sources=["config.yaml"])
        assert config_yaml.data["format"] == "yaml"

        # Load JSON
        config_json = manager.load_configuration("config_json", sources=["config.json"])
        assert config_json.data["format"] == "json"

        # Merge YAML then JSON
        config_merged = manager.load_configuration("config_merged", sources=["config.yaml", "config.json"])
        assert config_merged.data["shared"] == "json_val" # Later wins

    def test_missing_env_var_substitution_no_default(self):
        """Verify ${VAR} remains unchanged if VAR is missing and no default is provided."""
        data = {"key": "${NON_EXISTENT_VAR_12345}"}
        resolved = resolve_env_vars(data)
        assert resolved["key"] == "${NON_EXISTENT_VAR_12345}"
