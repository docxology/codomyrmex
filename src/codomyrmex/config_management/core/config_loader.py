"""
Configuration Loader for Codomyrmex Configuration Management Module.

Provides comprehensive configuration loading, validation, and management.
"""

import copy
import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import jsonschema
import requests
import yaml

# Use proper relative imports
try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback - should use get_logger from logging_monitoring
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)

from ._config_validation import ConfigValidationMixin

# Import exceptions
try:
    from codomyrmex.exceptions import (
        ConfigurationError,
        FileOperationError,
        ValidationError,
        create_error_context,
    )
except ImportError:
    try:
        from codomyrmex.exceptions import (
            ConfigurationError,
            FileOperationError,
            ValidationError,
            create_error_context,
        )
    except ImportError:
        # Fallback to standard exceptions
        class ConfigurationError(Exception):
            """Configurationerror.

            A class for handling configurationerror operations.
            """

        class FileOperationError(Exception):
            """Fileoperationerror.

            A class for handling fileoperationerror operations.
            """

        class ValidationError(Exception):
            """Validationerror.

            A class for handling validationerror operations.
            """

        def create_error_context(**kwargs):
            return dict(kwargs)


def deep_merge(base: dict[str, Any], extension: dict[str, Any]) -> dict[str, Any]:
    """
    Deeply merge two dictionaries.

    Values from extension override values from base. Nested dictionaries
    are merged recursively.

    Args:
        base: The base dictionary to merge into.
        extension: The dictionary with overrides.

    Returns:
        The merged dictionary (modified in-place if possible, but returns it).
    """
    for key, value in extension.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def resolve_env_vars(data: Any) -> Any:
    """
    Recursively resolve environment variables in a configuration structure.

    Supports ${VAR} and ${VAR:-default} syntax.

    Args:
        data: The configuration data structure (dict, list, or scalar).

    Returns:
        The data structure with resolved environment variables.
    """
    if isinstance(data, dict):
        return {k: resolve_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [resolve_env_vars(item) for item in data]
    if isinstance(data, str):
        # Match ${VAR} or ${VAR:-default}
        # Variable name must be alphanumeric or underscore
        pattern = re.compile(r"\$\{(?P<var>[A-Z0-9_]+)(?::-(?P<default>[^}]*))?\}")

        def replace(match):
            var_name = match.group("var")
            default_value = match.group("default")
            # If variable not found, use default if provided, otherwise leave as is
            val = os.getenv(var_name)
            if val is not None:
                return val
            if default_value is not None:
                return default_value
            return match.group(0)

        return pattern.sub(replace, data)
    return data


@dataclass
class ConfigSchema:
    """JSON schema for configuration validation."""

    schema: dict[str, Any]
    version: str = "draft7"
    title: str = ""
    description: str = ""

    def validate(self, config: dict[str, Any]) -> list[str]:
        """
        Validate configuration against schema.

        Args:
            config: Configuration to validate

        Returns:
            list of validation errors (empty if valid)
        """
        errors = []

        try:
            # Convert draft version to format string
            if self.version.startswith("draft"):
                # Use the newer format checker API
                from jsonschema import FormatChecker

                format_checker = FormatChecker()
            else:
                format_checker = None

            jsonschema.validate(config, self.schema, format_checker=format_checker)

        except jsonschema.ValidationError as e:
            errors.append(f"Validation error at {e.absolute_path}: {e.message}")
        except jsonschema.SchemaError as e:
            errors.append(f"Schema error: {e.message}")
        except Exception as e:
            errors.append(f"Validation failed: {e}")

        return errors


@dataclass
class Configuration:
    """Configuration object with validation and metadata."""

    data: dict[str, Any]
    source: str = "unknown"
    loaded_at: datetime = field(init=False)
    schema: ConfigSchema | None = None
    environment: str = "default"
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):

        if not hasattr(self, "loaded_at") or self.loaded_at is None:
            self.loaded_at = datetime.now(UTC)

    def validate(self) -> list[str]:
        """Validate configuration against schema."""
        if self.schema:
            return self.schema.validate(self.data)
        return []

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split(".")
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set_value(self, key: str, value: Any):
        """set configuration value by key."""
        keys = key.split(".")
        config = self.data

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # set the value
        config[keys[-1]] = value

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            "data": self.data,
            "source": self.source,
            "loaded_at": self.loaded_at.isoformat(),
            "environment": self.environment,
            "version": self.version,
            "metadata": self.metadata,
        }


class ConfigurationManager(ConfigValidationMixin):
    """
    Comprehensive configuration manager.

    Features:
    - Multi-source configuration loading (files, environment, secrets)
    - Configuration validation with JSON schemas
    - Environment-specific configurations
    - Configuration merging and overriding
    - Hot-reload capabilities
    - Configuration encryption/decryption

    Validation, migration, and backup methods are provided by
    :class:`._config_validation.ConfigValidationMixin`.
    """

    def __init__(self, config_dir: str | None = None):
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), "config")
        self.configurations: dict[str, Configuration] = {}
        self.schemas: dict[str, ConfigSchema] = {}
        self.environment = os.getenv("ENVIRONMENT", "development")

        # Create config directory if it doesn't exist and path is writable
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except (OSError, PermissionError):
            # If we can't create the directory, use a temporary location
            import tempfile

            self.config_dir = tempfile.mkdtemp(prefix="codomyrmex_config_")
            logger.warning(
                "Could not create config directory %s, using temporary location: %s",
                config_dir,
                self.config_dir,
            )

    def load_configuration(
        self,
        name: str,
        sources: list[str] | None = None,
        schema_path: str | None = None,
        defaults: dict[str, Any] | None = None,
    ) -> Configuration:
        """
        Load configuration from multiple sources.

        Args:
            name: Configuration name
            sources: list of configuration sources (files, env vars, etc.)
            schema_path: Path to JSON schema for validation
            defaults: Optional default values (lowest precedence)

        Returns:
            Configuration: Loaded and merged configuration
        """
        logger.info("Loading configuration: %s", name)

        # Load schema if provided
        schema = None
        if schema_path and os.path.exists(schema_path):
            schema = self._load_schema(schema_path)

        # Default sources
        if sources is None:
            sources = [
                f"{name}.yaml",
                f"{name}.yml",
                f"{name}.json",
                f"environments/{self.environment}/{name}.yaml",
                f"environments/{self.environment}/{name}.yml",
                f"environments/{self.environment}/{name}.json",
            ]

        # Start with defaults
        merged_config = copy.deepcopy(defaults) if defaults else {}
        source_list = ["defaults"] if defaults else []

        # Load and merge configurations from sources
        for source in sources:
            config_data = self._load_source(source)
            if config_data:
                deep_merge(merged_config, config_data)
                source_list.append(source)

        # Load environment variables
        env_config = self._load_environment_variables(name)
        if env_config:
            deep_merge(merged_config, env_config)
            source_list.append("environment")

        # Resolve environment variable substitutions
        merged_config = resolve_env_vars(merged_config)

        # Check if any configuration was found
        if not merged_config:
            # No configuration found - raise error if specific sources were requested
            if (
                sources
                and len(sources) == 1
                and sources[0] not in [f"{name}.yaml", f"{name}.yml", f"{name}.json"]
            ):
                raise FileNotFoundError(f"Configuration source not found: {sources[0]}")

        # Create configuration object
        config = Configuration(
            data=merged_config,
            source=", ".join(source_list) if source_list else "no sources found",
            environment=self.environment,
            schema=schema,
        )

        # Validate configuration
        validation_errors = config.validate()
        if validation_errors:
            logger.warning(
                "Configuration validation errors for %s: %s", name, validation_errors
            )

        self.configurations[name] = config
        logger.info("Configuration loaded: %s from %s", name, config.source)

        return config

    def _load_source(self, source: str) -> dict[str, Any] | None:
        """Load configuration from a specific source."""
        # Handle different source types
        if source.startswith("env://"):
            # Environment variable
            env_var = source[6:]  # Remove "env://" prefix
            value = os.getenv(env_var)
            return {env_var: value} if value else None

        if source.startswith("file://"):
            # File path
            file_path = source[7:]  # Remove "file://" prefix
            return self._load_file(file_path)

        if source.startswith(("http://", "https://")):
            # HTTP/HTTPS URL
            return self._load_from_url(source)

        # Local file
        file_path = os.path.join(self.config_dir, source)
        return self._load_file(file_path)

    def _load_file(self, file_path: str) -> dict[str, Any] | None:
        """Load configuration from file."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path) as f:
                if file_path.endswith((".yaml", ".yml")):
                    return yaml.safe_load(f)
                return json.load(f)

        except Exception as e:
            logger.error("Failed to load config file %s: %s", file_path, e)
            return None

    def _load_from_url(self, url: str) -> dict[str, Any] | None:
        """Load configuration from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "yaml" in content_type:
                return yaml.safe_load(response.text)
            return response.json()

        except Exception as e:
            logger.error("Failed to load config from URL %s: %s", url, e)
            return None

    def _load_environment_variables(self, config_name: str) -> dict[str, Any]:
        """
        Load configuration from environment variables.

        Supports nested keys using double underscore:
        APP_DATABASE__HOST -> {"database": {"host": ...}}
        """
        env_config = {}
        prefix = f"{config_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()

                # Handle nesting with double underscores
                if "__" in config_key:
                    parts = config_key.split("__")
                    current = env_config
                    for part in parts[:-1]:
                        if part not in current or not isinstance(current[part], dict):
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    env_config[config_key] = value

        return env_config

    def _load_schema(self, schema_path: str) -> ConfigSchema | None:
        """Load JSON schema for configuration validation."""
        try:
            with open(schema_path) as f:
                if schema_path.endswith((".yaml", ".yml")):
                    schema_data = yaml.safe_load(f)
                else:
                    schema_data = json.load(f)

            return ConfigSchema(
                schema=schema_data,
                title=schema_data.get("title", ""),
                description=schema_data.get("description", ""),
            )

        except Exception as e:
            logger.error("Failed to load schema %s: %s", schema_path, e)
            return None

    def save_configuration(
        self, name: str, output_path: str, format: str = "yaml"
    ) -> bool:
        """
        Save configuration to file.

        Args:
            name: Configuration name
            output_path: Output file path
            format: Output format (yaml, json)

        Returns:
            bool: True if save successful
        """
        if name not in self.configurations:
            logger.error("Configuration not found: %s", name)
            return False

        config = self.configurations[name]

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w") as f:
                if format.lower() == "yaml":
                    yaml.dump(config.data, f, default_flow_style=False)
                else:
                    json.dump(config.data, f, indent=2)

            logger.info("Configuration saved: %s to %s", name, output_path)
            return True

        except Exception as e:
            logger.error("Failed to save configuration %s: %s", name, e)
            return False

    def validate_all_configurations(self) -> dict[str, list[str]]:
        """
        Validate all loaded configurations.

        Returns:
            dict mapping configuration names to validation errors
        """
        validation_results = {}

        for name, config in self.configurations.items():
            errors = config.validate()
            if errors:
                validation_results[name] = errors

        return validation_results

    def reload_configuration(self, name: str) -> bool:
        """
        Reload configuration from sources.

        Args:
            name: Configuration name to reload

        Returns:
            bool: True if reload successful
        """
        if name not in self.configurations:
            logger.error("Configuration not found: %s", name)
            return False

        # Get original sources
        original_config = self.configurations[name]
        sources = original_config.source.split(", ")

        # Reload configuration
        try:
            self.load_configuration(name, sources)
            logger.info("Configuration reloaded: %s", name)
            return True

        except Exception as e:
            logger.error("Failed to reload configuration %s: %s", name, e)
            return False

    def get_configuration(self, name: str) -> Configuration | None:
        """Get loaded configuration by name."""
        return self.configurations.get(name)

    def list_configurations(self) -> list[str]:
        """list all loaded configuration names."""
        return list(self.configurations.keys())

    def create_configuration_template(self, schema_path: str, output_path: str) -> bool:
        """
        Create configuration template from schema.

        Args:
            schema_path: Path to JSON schema
            output_path: Output template file path

        Returns:
            bool: True if template creation successful
        """
        try:
            schema = self._load_schema(schema_path)
            if not schema:
                return False

            # Generate template from schema
            template = self._generate_template_from_schema(schema.schema)

            with open(output_path, "w") as f:
                if output_path.endswith((".yaml", ".yml")):
                    yaml.dump(template, f, default_flow_style=False)
                else:
                    json.dump(template, f, indent=2)

            logger.info("Configuration template created: %s", output_path)
            return True

        except Exception as e:
            logger.error("Failed to create configuration template: %s", e)
            return False

    def _generate_template_from_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Generate configuration template from JSON schema."""
        template = {}

        if "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                template[prop_name] = self._generate_property_template(prop_schema)

        return template

    def _generate_property_template(self, prop_schema: dict[str, Any]) -> Any:
        """Generate template for a single property."""
        prop_type = prop_schema.get("type", "string")
        default = prop_schema.get("default")

        if default is not None:
            return default

        if prop_type == "string":
            return "example_value"
        if prop_type in {"number", "integer"}:
            return 0
        if prop_type == "boolean":
            return False
        if prop_type == "array":
            return []
        if prop_type == "object":
            return self._generate_template_from_schema(prop_schema)
        return None

    def load_configuration_from_file(self, path: str) -> Configuration | None:
        """
        Load configuration directly from a file path.

        Args:
            path: Path to configuration file

        Returns:
            Configuration object or None if loading fails
        """
        config_data = self._load_file(path)
        if config_data is None:
            return None

        config = Configuration(
            data=config_data,
            source=path,
            environment=self.environment,
        )
        return config


# Convenience functions
def load_configuration(
    name: str,
    sources: list[str] | None = None,
    schema_path: str | None = None,
    defaults: dict[str, Any] | None = None,
) -> Configuration:
    """
    Convenience function to load configuration.

    Args:
        name: Configuration name
        sources: list of configuration sources
        schema_path: Path to JSON schema for validation
        defaults: Optional default values

    Returns:
        Configuration: Loaded configuration
    """
    manager = ConfigurationManager()
    return manager.load_configuration(name, sources, schema_path, defaults=defaults)


def validate_configuration(config: Configuration) -> list[str]:
    """
    Convenience function to validate configuration.

    Args:
        config: Configuration to validate

    Returns:
        list of validation errors (empty if valid)
    """
    return config.validate()
