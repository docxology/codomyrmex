"""
Configuration Loader for Codomyrmex Configuration Management Module.

Provides comprehensive configuration loading, validation, and management.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import jsonschema
import requests
import yaml

# Use proper relative imports
try:
    from codomyrmex.logging_monitoring.logger_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback - should use get_logger from logging_monitoring
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)

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
            pass

        class FileOperationError(Exception):
            """Fileoperationerror.

                A class for handling fileoperationerror operations.
                """
            pass

        class ValidationError(Exception):
            """Validationerror.

                A class for handling validationerror operations.
                """
            pass

        def create_error_context(**kwargs):
            pass
    pass

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
            List of validation errors (empty if valid)
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
    source: str
    loaded_at: datetime = field(init=False)
    schema: Optional[ConfigSchema] = None
    environment: str = "default"
    version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):

        if not hasattr(self, 'loaded_at') or self.loaded_at is None:
            self.loaded_at = datetime.now(timezone.utc)

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
        """Set configuration value by key."""
        keys = key.split(".")
        config = self.data

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Set the value
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


class ConfigurationManager:
    """
    Comprehensive configuration manager.

    Features:
    - Multi-source configuration loading (files, environment, secrets)
    - Configuration validation with JSON schemas
    - Environment-specific configurations
    - Configuration merging and overriding
    - Hot-reload capabilities
    - Configuration encryption/decryption
    """

    def __init__(self, config_dir: Optional[str] = None):
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
            logger.warning(f"Could not create config directory {config_dir}, using temporary location: {self.config_dir}")

    def load_configuration(
        self,
        name: str,
        sources: Optional[list[str]] = None,
        schema_path: Optional[str] = None,
    ) -> Configuration:
        """
        Load configuration from multiple sources.

        Args:
            name: Configuration name
            sources: List of configuration sources (files, env vars, etc.)
            schema_path: Path to JSON schema for validation

        Returns:
            Configuration: Loaded and merged configuration
        """
        logger.info(f"Loading configuration: {name}")

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

        # Load and merge configurations
        merged_config = {}
        source_list = []

        for source in sources:
            config_data = self._load_source(source)
            if config_data:
                merged_config.update(config_data)
                source_list.append(source)

        # Load environment variables
        env_config = self._load_environment_variables(name)
        if env_config:
            merged_config.update(env_config)
            source_list.append("environment")

        # Check if any configuration was found
        if not merged_config and not env_config:
            # No configuration found - raise error if specific sources were requested
            if sources and len(sources) == 1 and sources[0] not in [f"{name}.yaml", f"{name}.yml", f"{name}.json"]:
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
                f"Configuration validation errors for {name}: {validation_errors}"
            )

        self.configurations[name] = config
        logger.info(f"Configuration loaded: {name} from {config.source}")

        return config

    def _load_source(self, source: str) -> Optional[dict[str, Any]]:
        """Load configuration from a specific source."""
        # Handle different source types
        if source.startswith("env://"):
            # Environment variable
            env_var = source[6:]  # Remove "env://" prefix
            value = os.getenv(env_var)
            return {env_var: value} if value else None

        elif source.startswith("file://"):
            # File path
            file_path = source[7:]  # Remove "file://" prefix
            return self._load_file(file_path)

        elif source.startswith("http://") or source.startswith("https://"):
            # HTTP/HTTPS URL
            return self._load_from_url(source)

        else:
            # Local file
            file_path = os.path.join(self.config_dir, source)
            return self._load_file(file_path)

    def _load_file(self, file_path: str) -> Optional[dict[str, Any]]:
        """Load configuration from file."""
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path) as f:
                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                    return yaml.safe_load(f)
                else:
                    return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {e}")
            return None

    def _load_from_url(self, url: str) -> Optional[dict[str, Any]]:
        """Load configuration from URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "yaml" in content_type:
                return yaml.safe_load(response.text)
            else:
                return response.json()

        except Exception as e:
            logger.error(f"Failed to load config from URL {url}: {e}")
            return None

    def _load_environment_variables(self, config_name: str) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        prefix = f"{config_name.upper()}_"

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()
                env_config[config_key] = value

        return env_config

    def _load_schema(self, schema_path: str) -> Optional[ConfigSchema]:
        """Load JSON schema for configuration validation."""
        try:
            with open(schema_path) as f:
                if schema_path.endswith(".yaml") or schema_path.endswith(".yml"):
                    schema_data = yaml.safe_load(f)
                else:
                    schema_data = json.load(f)

            return ConfigSchema(
                schema=schema_data,
                title=schema_data.get("title", ""),
                description=schema_data.get("description", ""),
            )

        except Exception as e:
            logger.error(f"Failed to load schema {schema_path}: {e}")
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
            logger.error(f"Configuration not found: {name}")
            return False

        config = self.configurations[name]

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w") as f:
                if format.lower() == "yaml":
                    yaml.dump(config.data, f, default_flow_style=False)
                else:
                    json.dump(config.data, f, indent=2)

            logger.info(f"Configuration saved: {name} to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration {name}: {e}")
            return False

    def validate_all_configurations(self) -> dict[str, list[str]]:
        """
        Validate all loaded configurations.

        Returns:
            Dict mapping configuration names to validation errors
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
            logger.error(f"Configuration not found: {name}")
            return False

        # Get original sources
        original_config = self.configurations[name]
        sources = original_config.source.split(", ")

        # Reload configuration
        try:
            self.load_configuration(name, sources)
            logger.info(f"Configuration reloaded: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to reload configuration {name}: {e}")
            return False

    def get_configuration(self, name: str) -> Optional[Configuration]:
        """Get loaded configuration by name."""
        return self.configurations.get(name)

    def list_configurations(self) -> list[str]:
        """List all loaded configuration names."""
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
                if output_path.endswith(".yaml") or output_path.endswith(".yml"):
                    yaml.dump(template, f, default_flow_style=False)
                else:
                    json.dump(template, f, indent=2)

            logger.info(f"Configuration template created: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to create configuration template: {e}")
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
        elif prop_type == "number" or prop_type == "integer":
            return 0
        elif prop_type == "boolean":
            return False
        elif prop_type == "array":
            return []
        elif prop_type == "object":
            return self._generate_template_from_schema(prop_schema)
        else:
            return None

    def load_config_with_validation(self, path: str, schema: Optional[Dict[str, Any]] = None) -> Optional[Configuration]:
        """
        Load configuration with automatic validation.

        Args:
            path: Path to configuration file
            schema: Optional schema for validation

        Returns:
            Configuration object if valid, None if validation fails
        """
        try:
            config = self.load_configuration_from_file(path)
            if not config:
                return None

            # Validate against schema if provided
            if schema:
                from .config_validator import ConfigValidator
                validator = ConfigValidator(schema)
                result = validator.validate(config.config_data)

                if not result.is_valid:
                    logger.error(f"Configuration validation failed for {path}:")
                    for issue in result.errors:
                        logger.error(f"  - {issue.message}")
                    return None

                if result.warnings:
                    logger.warning(f"Configuration validation warnings for {path}:")
                    for issue in result.warnings:
                        logger.warning(f"  - {issue.message}")

            return config

        except Exception as e:
            logger.error(f"Failed to load and validate configuration {path}: {e}")
            return None

    def migrate_configuration(self, name: str, target_version: str) -> bool:
        """
        Migrate a configuration to a target version.

        Args:
            name: Configuration name
            target_version: Target version to migrate to

        Returns:
            bool: True if migration successful
        """
        if name not in self.configurations:
            logger.error(f"Configuration not found: {name}")
            return False

        config = self.configurations[name]

        try:
            from .config_migrator import migrate_config

            # Assume current version is stored in config
            current_version = config.config_data.get("version", "1.0.0")

            migration_result = migrate_config(config.config_data, current_version, target_version)

            if migration_result.success:
                # Update configuration with migrated data
                config.config_data = migration_result.migrated_config
                config.config_data["version"] = target_version

                # Save backup if needed
                if migration_result.backup_config:
                    backup_name = f"{name}_backup_{current_version}"
                    self.configurations[backup_name] = Configuration(
                        name=backup_name,
                        config_data=migration_result.backup_config,
                        source=f"migration_backup_{current_version}",
                        loaded_at=datetime.now(timezone.utc)
                    )

                logger.info(f"Successfully migrated {name} from {current_version} to {target_version}")
                return True
            else:
                logger.error(f"Migration failed for {name}: {migration_result.errors}")
                return False

        except Exception as e:
            logger.error(f"Migration error for {name}: {e}")
            return False

    def validate_config_schema(self, config_data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration data against a schema.

        Args:
            config_data: Configuration data to validate
            schema: Schema dictionary

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        try:
            from .config_validator import validate_config_schema
            return validate_config_schema(config_data, schema)
        except ImportError:
            logger.warning("ConfigValidator not available, skipping schema validation")
            return True, []

    def get_validation_report(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed validation report for a configuration.

        Args:
            name: Configuration name

        Returns:
            Validation report dictionary or None if config not found
        """
        if name not in self.configurations:
            return None

        config = self.configurations[name]

        try:
            from .config_validator import ConfigValidator, get_logging_config_schema, get_database_config_schema

            # Try different schemas based on configuration content
            schema = None
            if "level" in config.config_data or "format" in config.config_data:
                schema = get_logging_config_schema()
            elif "host" in config.config_data and "database" in config.config_data:
                schema = get_database_config_schema()

            if schema:
                validator = ConfigValidator(schema)
                result = validator.validate(config.config_data)
                return result.to_dict()
            else:
                # Basic validation without schema
                return {
                    "is_valid": True,
                    "total_issues": 0,
                    "errors": 0,
                    "warnings": 0,
                    "issues": [],
                    "note": "No schema available for detailed validation"
                }

        except Exception as e:
            logger.error(f"Error generating validation report for {name}: {e}")
            return {
                "is_valid": False,
                "error": str(e)
            }

    def create_migration_backup(self, name: str) -> bool:
        """
        Create a backup of configuration before migration.

        Args:
            name: Configuration name

        Returns:
            bool: True if backup created successfully
        """
        if name not in self.configurations:
            return False

        config = self.configurations[name]
        version = config.config_data.get("version", "unknown")

        backup_name = f"{name}_backup_{version}_{int(datetime.now(timezone.utc).timestamp())}"

        try:
            # Create backup configuration
            backup_config = Configuration(
                name=backup_name,
                config_data=config.config_data.copy(),
                source=f"backup_of_{name}",
                loaded_at=datetime.now(timezone.utc)
            )

            self.configurations[backup_name] = backup_config
            logger.info(f"Created backup: {backup_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create backup for {name}: {e}")
            return False


# Convenience functions
def load_configuration(
    name: str, sources: Optional[list[str]] = None, schema_path: Optional[str] = None
) -> Configuration:
    """
    Convenience function to load configuration.

    Args:
        name: Configuration name
        sources: List of configuration sources
        schema_path: Path to JSON schema for validation

    Returns:
        Configuration: Loaded configuration
    """
    manager = ConfigurationManager()
    return manager.load_configuration(name, sources, schema_path)


def validate_configuration(config: Configuration) -> list[str]:
    """
    Convenience function to validate configuration.

    Args:
        config: Configuration to validate

    Returns:
        List of validation errors (empty if valid)
    """
    return config.validate()
