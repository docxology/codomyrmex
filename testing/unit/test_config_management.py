"""
Comprehensive tests for the config_management module.

This module tests all configuration management functionality including
loading, validation, secrets management, and environment handling.
"""

import pytest
import tempfile
import os
import json
import yaml
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone

from codomyrmex.config_management.config_loader import (
    ConfigurationManager,
    load_configuration,
    validate_configuration,
    Configuration,
    ConfigSchema
)


class TestConfigSchema:
    """Test cases for ConfigSchema functionality."""

    def test_config_schema_creation(self):
        """Test ConfigSchema creation."""
        schema = {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer"}
                    },
                    "required": ["host"]
                }
            },
            "required": ["database"]
        }

        config_schema = ConfigSchema(
            schema=schema,
            title="Test Schema",
            description="A test configuration schema"
        )

        assert config_schema.schema == schema
        assert config_schema.title == "Test Schema"
        assert config_schema.description == "A test configuration schema"

    def test_config_schema_validation_success(self):
        """Test successful schema validation."""
        schema = ConfigSchema(schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        })

        config = {"name": "John", "age": 30}

        errors = schema.validate(config)
        assert len(errors) == 0

    def test_config_schema_validation_failure(self):
        """Test schema validation failure."""
        schema = ConfigSchema(schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        })

        # Missing required field
        config = {"age": 30}

        errors = schema.validate(config)
        assert len(errors) > 0
        assert any("name" in error.lower() for error in errors)

    def test_config_schema_validation_type_error(self):
        """Test schema validation with type errors."""
        schema = ConfigSchema(schema={
            "type": "object",
            "properties": {
                "port": {"type": "integer"}
            }
        })

        # Wrong type
        config = {"port": "8080"}

        errors = schema.validate(config)
        assert len(errors) > 0


class TestConfiguration:
    """Test cases for Configuration dataclass."""

    def test_configuration_creation(self):
        """Test Configuration creation."""
        config_data = {"database": {"host": "localhost", "port": 5432}}
        schema = ConfigSchema(schema={"type": "object"})

        config = Configuration(
            data=config_data,
            source="/path/to/config.yaml",
            environment="development",
            schema=schema
        )

        assert config.data == config_data
        assert config.source == "/path/to/config.yaml"
        assert config.environment == "development"
        assert config.schema == schema

    def test_configuration_auto_timestamp(self):
        """Test Configuration automatic timestamp."""
        config = Configuration(
            data={"test": "value"},
            source="test.yaml"
        )

        assert config.created_at is not None
        assert isinstance(config.created_at, datetime)

    def test_configuration_get_value(self):
        """Test Configuration get_value method."""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "version": "v1"
            }
        }

        config = Configuration(data=config_data, source="test.yaml")

        # Test simple value
        assert config.get_value("database.host") == "localhost"
        assert config.get_value("database.port") == 5432
        assert config.get_value("api.version") == "v1"

        # Test missing value with default
        assert config.get_value("missing.key", "default") == "default"

        # Test missing value without default
        assert config.get_value("missing.key") is None

    def test_configuration_set_value(self):
        """Test Configuration set_value method."""
        config_data = {"database": {"host": "localhost"}}
        config = Configuration(data=config_data, source="test.yaml")

        # Set existing nested value
        config.set_value("database.host", "newhost")
        assert config.data["database"]["host"] == "newhost"

        # Set new nested value
        config.set_value("database.port", 5432)
        assert config.data["database"]["port"] == 5432

        # Set new top-level value
        config.set_value("api.version", "v2")
        assert config.data["api"]["version"] == "v2"

    def test_configuration_to_dict(self):
        """Test Configuration to_dict conversion."""
        config_data = {"test": "value"}
        config = Configuration(
            data=config_data,
            source="test.yaml",
            environment="development",
            version="1.0.0"
        )

        config_dict = config.to_dict()

        assert config_dict["data"] == config_data
        assert config_dict["source"] == "test.yaml"
        assert config_dict["environment"] == "development"
        assert config_dict["version"] == "1.0.0"
        assert "created_at" in config_dict


class TestConfigurationManager:
    """Test cases for ConfigurationManager functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.manager = ConfigurationManager()

    def test_configuration_manager_initialization(self):
        """Test ConfigurationManager initialization."""
        manager = ConfigurationManager()
        assert manager.configurations == {}
        assert manager.schemas == {}
        assert manager.environment == "development"
        assert manager.config_dir.endswith("config")

    def test_configuration_manager_custom_dir(self):
        """Test ConfigurationManager with custom config directory."""
        custom_dir = "/custom/config/dir"
        manager = ConfigurationManager(custom_dir)
        assert manager.config_dir == custom_dir

    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_configuration_manager_environment_detection(self):
        """Test ConfigurationManager environment detection."""
        manager = ConfigurationManager()
        assert manager.environment == "production"

    def test_load_configuration_from_yaml_file(self):
        """Test configuration loading from YAML file."""
        config_content = """
database:
  host: localhost
  port: 5432
api:
  version: v1
  debug: true
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(config_content)
            config_path = f.name

        try:
            config = self.manager.load_configuration("test_config", [config_path])

            assert config.data["database"]["host"] == "localhost"
            assert config.data["database"]["port"] == 5432
            assert config.data["api"]["version"] == "v1"
            assert config.data["api"]["debug"] is True
            assert config.source == config_path

        finally:
            os.unlink(config_path)

    def test_load_configuration_from_json_file(self):
        """Test configuration loading from JSON file."""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "version": "v1"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name

        try:
            config = self.manager.load_configuration("test_config", [config_path])

            assert config.data["database"]["host"] == "localhost"
            assert config.data["database"]["port"] == 5432
            assert config.data["api"]["version"] == "v1"

        finally:
            os.unlink(config_path)

    def test_load_configuration_from_url(self):
        """Test configuration loading from URL."""
        config_data = {"test": "value"}

        with patch('codomyrmex.config_management.config_loader.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = config_data
            mock_get.return_value = mock_response

            config = self.manager.load_configuration("test_config", ["http://example.com/config.json"])

            assert config.data["test"] == "value"

    def test_load_configuration_environment_variables(self):
        """Test configuration loading from environment variables."""
        with patch.dict(os.environ, {"TEST_CONFIG_HOST": "testhost", "TEST_CONFIG_PORT": "8080"}):
            config = self.manager.load_configuration("test_config", [])

            assert config.data["host"] == "testhost"
            assert config.data["port"] == "8080"

    def test_load_configuration_with_schema(self):
        """Test configuration loading with schema validation."""
        schema_content = """
type: object
properties:
  database:
    type: object
    properties:
      host:
        type: string
      port:
        type: integer
    required: [host]
required: [database]
"""

        config_content = """
database:
  host: localhost
  port: 5432
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as schema_file:
            schema_file.write(schema_content)
            schema_path = schema_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as config_file:
            config_file.write(config_content)
            config_path = config_file.name

        try:
            config = self.manager.load_configuration("test_config", [config_path], schema_path)

            assert config.schema is not None
            # Should validate successfully
            errors = config.validate()
            assert len(errors) == 0

        finally:
            os.unlink(schema_path)
            os.unlink(config_path)

    def test_load_configuration_schema_validation_failure(self):
        """Test configuration loading with schema validation failure."""
        schema_content = """
type: object
properties:
  database:
    type: object
    properties:
      host:
        type: string
    required: [host]
required: [database]
"""

        config_content = """
database:
  port: 5432
  # Missing required host field
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as schema_file:
            schema_file.write(schema_content)
            schema_path = schema_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as config_file:
            config_file.write(config_content)
            config_path = config_file.name

        try:
            config = self.manager.load_configuration("test_config", [config_path], schema_path)

            assert config.schema is not None
            # Should have validation errors
            errors = config.validate()
            assert len(errors) > 0
            assert any("host" in error.lower() for error in errors)

        finally:
            os.unlink(schema_path)
            os.unlink(config_path)

    def test_save_configuration_yaml(self):
        """Test configuration saving to YAML."""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "version": "v1"
            }
        }

        config = Configuration(data=config_data, source="test.yaml")
        self.manager.configurations["test"] = config

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            output_path = f.name

        try:
            result = self.manager.save_configuration("test", output_path, "yaml")
            assert result is True

            # Verify file contents
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                saved_data = yaml.safe_load(f)
                assert saved_data["database"]["host"] == "localhost"
                assert saved_data["database"]["port"] == 5432

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_save_configuration_json(self):
        """Test configuration saving to JSON."""
        config_data = {"test": "value"}
        config = Configuration(data=config_data, source="test.json")
        self.manager.configurations["test"] = config

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_path = f.name

        try:
            result = self.manager.save_configuration("test", output_path, "json")
            assert result is True

            # Verify file contents
            assert os.path.exists(output_path)
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
                assert saved_data["test"] == "value"

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_get_configuration(self):
        """Test getting configuration by name."""
        config = Configuration(data={"test": "value"}, source="test.yaml")
        self.manager.configurations["test_config"] = config

        result = self.manager.get_configuration("test_config")
        assert result == config

        # Test non-existent configuration
        result = self.manager.get_configuration("nonexistent")
        assert result is None

    def test_list_configurations(self):
        """Test listing configuration names."""
        # Initially empty
        assert self.manager.list_configurations() == []

        # Add configurations
        self.manager.configurations["config1"] = Configuration(data={}, source="test1.yaml")
        self.manager.configurations["config2"] = Configuration(data={}, source="test2.yaml")

        configs = self.manager.list_configurations()
        assert len(configs) == 2
        assert "config1" in configs
        assert "config2" in configs

    def test_reload_configuration(self):
        """Test configuration reloading."""
        # Mock initial configuration
        original_config = Configuration(data={"version": "1.0"}, source="test.yaml")
        self.manager.configurations["test"] = original_config

        # Mock file reading to return updated data
        with patch.object(self.manager, '_load_source', return_value={"version": "2.0"}):
            result = self.manager.reload_configuration("test")

            assert result is True
            assert self.manager.configurations["test"].data["version"] == "2.0"

    def test_reload_configuration_nonexistent(self):
        """Test reloading non-existent configuration."""
        result = self.manager.reload_configuration("nonexistent")
        assert result is False

    def test_validate_all_configurations(self):
        """Test validating all configurations."""
        # Configuration without schema (should pass)
        config1 = Configuration(data={"test": "value"}, source="test1.yaml")
        self.manager.configurations["config1"] = config1

        # Configuration with schema
        schema = ConfigSchema(schema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        })
        config2 = Configuration(
            data={"name": "test"},
            source="test2.yaml",
            schema=schema
        )
        self.manager.configurations["config2"] = config2

        # Configuration with validation errors
        config3 = Configuration(
            data={"age": 25},  # Missing required "name"
            source="test3.yaml",
            schema=schema
        )
        self.manager.configurations["config3"] = config3

        validation_results = self.manager.validate_all_configurations()

        assert "config1" not in validation_results  # No schema, no errors
        assert "config2" not in validation_results  # Valid
        assert "config3" in validation_results  # Has errors
        assert len(validation_results["config3"]) > 0

    def test_create_configuration_template(self):
        """Test configuration template creation."""
        schema = {
            "type": "object",
            "properties": {
                "database": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string", "default": "localhost"},
                        "port": {"type": "integer", "default": 5432}
                    }
                },
                "api": {
                    "type": "object",
                    "properties": {
                        "version": {"type": "string"}
                    },
                    "required": ["version"]
                }
            },
            "required": ["api"]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as schema_file:
            yaml.dump(schema, schema_file)
            schema_path = schema_file.name

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as template_file:
            template_path = template_file.name

        try:
            result = self.manager.create_configuration_template(schema_path, template_path)
            assert result is True

            # Verify template contents
            assert os.path.exists(template_path)
            with open(template_path, 'r') as f:
                template_data = yaml.safe_load(f)

            assert "database" in template_data
            assert "host" in template_data["database"]
            assert "port" in template_data["database"]
            assert "api" in template_data

        finally:
            if os.path.exists(schema_path):
                os.unlink(schema_path)
            if os.path.exists(template_path):
                os.unlink(template_path)


class TestConvenienceFunctions:
    """Test cases for module-level convenience functions."""

    @patch('codomyrmex.config_management.config_loader.ConfigurationManager')
    def test_load_configuration_function(self, mock_manager_class):
        """Test load_configuration convenience function."""
        mock_manager = MagicMock()
        mock_config = MagicMock()
        mock_manager.load_configuration.return_value = mock_config
        mock_manager_class.return_value = mock_manager

        result = load_configuration("test_config", ["config.yaml"])

        mock_manager_class.assert_called_once()
        mock_manager.load_configuration.assert_called_once_with("test_config", ["config.yaml"], None)
        assert result == mock_config

    def test_validate_configuration_function(self):
        """Test validate_configuration convenience function."""
        mock_config = MagicMock()
        mock_config.validate.return_value = ["Error 1", "Error 2"]

        result = validate_configuration(mock_config)

        mock_config.validate.assert_called_once()
        assert result == ["Error 1", "Error 2"]


class TestIntegration:
    """Integration tests for configuration management components."""

    def test_full_configuration_workflow(self):
        """Test complete configuration management workflow."""
        # Create a configuration with schema
        schema = ConfigSchema(schema={
            "type": "object",
            "properties": {
                "app": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"}
                    },
                    "required": ["name"]
                }
            },
            "required": ["app"]
        })

        config_data = {
            "app": {
                "name": "TestApp",
                "version": "1.0.0"
            },
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }

        config = Configuration(
            data=config_data,
            source="integration_test.yaml",
            environment="development",
            schema=schema
        )

        # Test validation
        errors = config.validate()
        assert len(errors) == 0

        # Test value access
        assert config.get_value("app.name") == "TestApp"
        assert config.get_value("database.port") == 5432

        # Test value modification
        config.set_value("app.version", "2.0.0")
        assert config.get_value("app.version") == "2.0.0"

        # Test serialization
        config_dict = config.to_dict()
        assert config_dict["data"]["app"]["name"] == "TestApp"
        assert config_dict["environment"] == "development"

    def test_configuration_manager_workflow(self):
        """Test ConfigurationManager workflow."""
        manager = ConfigurationManager()

        # Create and save a configuration
        config_data = {"test": "value", "number": 42}
        config = Configuration(data=config_data, source="workflow_test.yaml")
        manager.configurations["workflow_test"] = config

        # Save to file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            save_path = f.name

        try:
            result = manager.save_configuration("workflow_test", save_path, "json")
            assert result is True

            # Load from file
            loaded_config = manager.load_configuration("loaded_test", [save_path])

            # Verify data matches
            assert loaded_config.data["test"] == "value"
            assert loaded_config.data["number"] == 42

        finally:
            if os.path.exists(save_path):
                os.unlink(save_path)

    def test_environment_specific_configuration(self):
        """Test environment-specific configuration handling."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            manager = ConfigurationManager()

            assert manager.environment == "production"

            # Create environment-specific config
            config_data = {"env": "production", "debug": False}
            config = Configuration(
                data=config_data,
                source="prod_config.yaml",
                environment="production"
            )

            assert config.environment == "production"
            assert config.data["debug"] is False


class TestErrorHandling:
    """Test cases for error handling in configuration operations."""

    def test_load_configuration_file_not_found(self):
        """Test loading configuration with non-existent file."""
        manager = ConfigurationManager()

        with pytest.raises(FileNotFoundError):
            manager.load_configuration("test", ["/non/existent/file.yaml"])

    def test_load_configuration_invalid_yaml(self):
        """Test loading configuration with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid: yaml: content: [unbalanced")
            config_path = f.name

        try:
            manager = ConfigurationManager()

            with pytest.raises(Exception):  # YAML parsing error
                manager.load_configuration("test", [config_path])

        finally:
            os.unlink(config_path)

    def test_load_configuration_invalid_json(self):
        """Test loading configuration with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{"invalid": json content}')
            config_path = f.name

        try:
            manager = ConfigurationManager()

            with pytest.raises(Exception):  # JSON parsing error
                manager.load_configuration("test", [config_path])

        finally:
            os.unlink(config_path)

    @patch('codomyrmex.config_management.config_loader.requests.get')
    def test_load_configuration_url_failure(self, mock_get):
        """Test loading configuration from URL failure."""
        mock_get.side_effect = Exception("Network error")

        manager = ConfigurationManager()

        with pytest.raises(Exception):
            manager.load_configuration("test", ["http://example.com/config.json"])

    def test_save_configuration_nonexistent_config(self):
        """Test saving non-existent configuration."""
        manager = ConfigurationManager()

        result = manager.save_configuration("nonexistent", "/tmp/test.yaml")
        assert result is False

    def test_create_configuration_template_invalid_schema(self):
        """Test template creation with invalid schema."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("invalid schema content")
            schema_path = f.name

        with tempfile.NamedTemporaryFile(delete=False) as template_file:
            template_path = template_file.name

        try:
            manager = ConfigurationManager()
            result = manager.create_configuration_template(schema_path, template_path)
            assert result is False

        finally:
            if os.path.exists(schema_path):
                os.unlink(schema_path)
            if os.path.exists(template_path):
                os.unlink(template_path)

    def test_configuration_get_value_invalid_key(self):
        """Test getting value with invalid key format."""
        config_data = {"test": "value"}
        config = Configuration(data=config_data, source="test.yaml")

        # Test with non-dict intermediate value
        result = config.get_value("test.invalid")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
