"""Configuration validation and migration methods for ConfigurationManager."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from .config_loader import Configuration

logger = get_logger(__name__)


class ConfigValidationMixin:
    """Validation, migration, and backup methods for ConfigurationManager."""

    configurations: dict[str, Configuration]

    def load_config_with_validation(
        self, path: str, schema: dict[str, Any] | None = None
    ) -> Configuration | None:
        """
        Load configuration with automatic validation.

        Args:
            path: Path to configuration file
            schema: Optional schema for validation

        Returns:
            Configuration object if valid, None if validation fails
        """
        try:
            config = self.load_configuration_from_file(path)  # type: ignore[attr-defined]
            if not config:
                return None

            if schema:
                from codomyrmex.config_management.validation.config_validator import (
                    ConfigValidator,
                )

                validator = ConfigValidator(schema)
                result = validator.validate(config.data)

                if not result.is_valid:
                    logger.error("Configuration validation failed for %s:", path)
                    for issue in result.errors:
                        logger.error("  - %s", issue.message)
                    return None

                if result.warnings:
                    logger.warning("Configuration validation warnings for %s:", path)
                    for issue in result.warnings:
                        logger.warning("  - %s", issue.message)

            return config

        except Exception as e:
            logger.error("Failed to load and validate configuration %s: %s", path, e)
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
            logger.error("Configuration not found: %s", name)
            return False

        config = self.configurations[name]

        try:
            from codomyrmex.config_management.migration.config_migrator import (
                migrate_config,
            )

            current_version = config.data.get("version", "1.0.0")

            migration_result = migrate_config(
                config.data, current_version, target_version
            )

            if migration_result.success:
                config.data = migration_result.migrated_config
                config.data["version"] = target_version

                if migration_result.backup_config:
                    from .config_loader import Configuration

                    backup_name = f"{name}_backup_{current_version}"
                    backup_config = Configuration(
                        data=migration_result.backup_config,
                        source=f"migration_backup_{current_version}",
                    )
                    self.configurations[backup_name] = backup_config

                logger.info(
                    "Successfully migrated %s from %s to %s",
                    name,
                    current_version,
                    target_version,
                )
                return True
            logger.error("Migration failed for %s: %s", name, migration_result.errors)
            return False

        except Exception as e:
            logger.error("Migration error for %s: %s", name, e)
            return False

    def validate_config_schema(
        self, config_data: dict[str, Any], schema: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate configuration data against a schema.

        Args:
            config_data: Configuration data to validate
            schema: Schema dictionary

        Returns:
            tuple of (is_valid, list_of_error_messages)
        """
        try:
            from codomyrmex.config_management.validation.config_validator import (
                validate_config_schema,
            )

            return validate_config_schema(config_data, schema)
        except ImportError:
            logger.warning("ConfigValidator not available, skipping schema validation")
            return True, []

    def get_validation_report(self, name: str) -> dict[str, Any] | None:
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
            from codomyrmex.config_management.validation.config_validator import (
                ConfigValidator,
                get_database_config_schema,
                get_logging_config_schema,
            )

            schema = None
            if "level" in config.data or "format" in config.data:
                schema = get_logging_config_schema()
            elif "host" in config.data and "database" in config.data:
                schema = get_database_config_schema()

            if schema:
                validator = ConfigValidator(schema)
                result = validator.validate(config.data)
                return result.to_dict()
            return {
                "is_valid": True,
                "total_issues": 0,
                "errors": 0,
                "warnings": 0,
                "issues": [],
                "note": "No schema available for detailed validation",
            }

        except Exception as e:
            logger.error("Error generating validation report for %s: %s", name, e)
            return {"is_valid": False, "error": str(e)}

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
        version = config.data.get("version", "unknown")

        backup_name = f"{name}_backup_{version}_{int(datetime.now(UTC).timestamp())}"

        try:
            from .config_loader import Configuration

            backup_config = Configuration(
                data=config.data.copy(),
                source=f"backup_of_{name}",
            )

            self.configurations[backup_name] = backup_config
            logger.info("Created backup: %s", backup_name)
            return True

        except Exception as e:
            logger.error("Failed to create backup for %s: %s", name, e)
            return False
