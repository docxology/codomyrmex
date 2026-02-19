import copy
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections.abc import Callable

from codomyrmex.logging_monitoring.logger_config import get_logger

"""Configuration Migrator for Codomyrmex."""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class MigrationAction(Enum):
    """Types of migration actions."""
    RENAME_FIELD = "rename_field"
    MOVE_FIELD = "move_field"
    TRANSFORM_VALUE = "transform_value"
    ADD_FIELD = "add_field"
    REMOVE_FIELD = "remove_field"
    SPLIT_FIELD = "split_field"
    MERGE_FIELDS = "merge_fields"
    CUSTOM_TRANSFORM = "custom_transform"

@dataclass
class MigrationRule:
    """A single migration rule."""
    action: MigrationAction
    description: str
    from_version: str
    to_version: str

    # Action-specific parameters
    old_path: str | None = None
    new_path: str | None = None
    old_paths: list[str] | None = None
    new_value: Any = None
    transform_func: Callable | None = None
    condition: Callable[[dict[str, Any]], bool] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "action": self.action.value,
            "description": self.description,
            "from_version": self.from_version,
            "to_version": self.to_version
        }

        if self.old_path:
            result["old_path"] = self.old_path
        if self.new_path:
            result["new_path"] = self.new_path
        if self.old_paths:
            result["old_paths"] = self.old_paths
        if self.new_value is not None:
            result["new_value"] = self.new_value
        if self.condition:
            result["has_condition"] = True

        return result

@dataclass
class MigrationResult:
    """Result of a configuration migration."""
    success: bool
    original_version: str
    target_version: str
    migrated_config: dict[str, Any]
    applied_rules: list[MigrationRule] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    backup_config: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "original_version": self.original_version,
            "target_version": self.target_version,
            "applied_rules": [rule.to_dict() for rule in self.applied_rules],
            "warnings": self.warnings,
            "errors": self.errors,
            "has_backup": self.backup_config is not None
        }

class ConfigMigrator:
    """
    Configuration migrator for handling version upgrades and field changes.

    Provides automatic migration of configuration files between versions,
    with support for field renaming, value transformations, and custom migration logic.
    """

    def __init__(self):
        """Initialize the configuration migrator."""
        self.migration_rules: dict[tuple[str, str], list[MigrationRule]] = {}
        self.version_order = []  # Ordered list of versions for path finding

    def add_migration_rule(self, rule: MigrationRule) -> None:
        """
        Add a migration rule.

        Args:
            rule: Migration rule to add
        """
        key = (rule.from_version, rule.to_version)
        if key not in self.migration_rules:
            self.migration_rules[key] = []
        self.migration_rules[key].append(rule)

        # Update version ordering
        for version in [rule.from_version, rule.to_version]:
            if version not in self.version_order:
                self.version_order.append(version)

    def migrate_config(self, config: dict[str, Any], from_version: str, to_version: str) -> MigrationResult:
        """
        Migrate a configuration from one version to another.

        Args:
            config: Configuration to migrate
            from_version: Source version
            to_version: Target version

        Returns:
            MigrationResult with migrated configuration
        """
        result = MigrationResult(
            success=True,
            original_version=from_version,
            target_version=to_version,
            migrated_config=copy.deepcopy(config),
            backup_config=copy.deepcopy(config)
        )

        if from_version == to_version:
            result.warnings.append("Source and target versions are the same")
            return result

        # Find migration path
        migration_path = self.get_migration_path(from_version, to_version)

        if not migration_path:
            result.success = False
            result.errors.append(f"No migration path found from {from_version} to {to_version}")
            return result

        # Apply migrations step by step
        current_config = copy.deepcopy(config)
        applied_rules = []

        for step_from, step_to in migration_path:
            rules = self.migration_rules.get((step_from, step_to), [])
            if rules:
                logger.info(f"Applying {len(rules)} migration rules from {step_from} to {step_to}")

                for rule in rules:
                    try:
                        self._apply_migration_rule(current_config, rule, result)
                        applied_rules.append(rule)
                    except Exception as e:
                        result.errors.append(f"Failed to apply rule '{rule.description}': {e}")
                        result.success = False
                        break

                if not result.success:
                    break
            else:
                logger.debug(f"No migration rules for {step_from} -> {step_to}")

        result.migrated_config = current_config
        result.applied_rules = applied_rules

        if result.success and applied_rules:
            logger.info(f"Successfully migrated config from {from_version} to {to_version} using {len(applied_rules)} rules")
        elif result.success and not applied_rules:
            logger.info("No migration rules applied (config may already be compatible)")

        return result

    def get_migration_path(self, from_version: str, to_version: str) -> list[tuple[str, str]]:
        """
        Get the migration path between two versions.

        Args:
            from_version: Source version
            to_version: Target version

        Returns:
            List of (from_version, to_version) tuples representing migration steps
        """
        # Simple path finding - assumes linear version progression
        # Could be enhanced with more sophisticated path finding for complex version graphs

        if from_version == to_version:
            return []

        try:
            from_idx = self.version_order.index(from_version)
            to_idx = self.version_order.index(to_version)

            if from_idx < to_idx:
                # Forward migration
                return [(self.version_order[i], self.version_order[i+1])
                       for i in range(from_idx, to_idx)]
            else:
                # Backward migration (if supported)
                return [(self.version_order[i], self.version_order[i-1])
                       for i in range(from_idx, to_idx, -1)]

        except ValueError:
            # Version not in order
            return []

    def validate_migration(self, config: dict[str, Any], target_version: str) -> bool:
        """
        Validate that a configuration is compatible with a target version.

        Args:
            config: Configuration to validate
            target_version: Target version

        Returns:
            True if configuration is valid for the target version
        """
        raise NotImplementedError("Config migration validation requires migration rule definitions")

    def register_migration(self, from_version: str, to_version: str, migrator: Callable) -> None:
        """
        Register a custom migration function.

        Args:
            from_version: Source version
            to_version: Target version
            migrator: Migration function that takes config and returns migrated config
        """
        rule = MigrationRule(
            action=MigrationAction.CUSTOM_TRANSFORM,
            description=f"Custom migration from {from_version} to {to_version}",
            from_version=from_version,
            to_version=to_version,
            transform_func=migrator
        )
        self.add_migration_rule(rule)

    def _apply_migration_rule(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Apply a single migration rule to the configuration."""
        if rule.condition and not rule.condition(config):
            logger.debug(f"Migration rule '{rule.description}' condition not met, skipping")
            return

        if rule.action == MigrationAction.RENAME_FIELD:
            self._rename_field(config, rule, result)
        elif rule.action == MigrationAction.MOVE_FIELD:
            self._move_field(config, rule, result)
        elif rule.action == MigrationAction.TRANSFORM_VALUE:
            self._transform_value(config, rule, result)
        elif rule.action == MigrationAction.ADD_FIELD:
            self._add_field(config, rule, result)
        elif rule.action == MigrationAction.REMOVE_FIELD:
            self._remove_field(config, rule, result)
        elif rule.action == MigrationAction.SPLIT_FIELD:
            self._split_field(config, rule, result)
        elif rule.action == MigrationAction.MERGE_FIELDS:
            self._merge_fields(config, rule, result)
        elif rule.action == MigrationAction.CUSTOM_TRANSFORM:
            self._custom_transform(config, rule, result)
        else:
            result.errors.append(f"Unknown migration action: {rule.action}")

    def _rename_field(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Rename a field in the configuration."""
        if not rule.old_path or not rule.new_path:
            result.errors.append("Rename rule missing old_path or new_path")
            return

        old_value = self._get_nested_value(config, rule.old_path)
        if old_value is not None:
            self._set_nested_value(config, rule.new_path, old_value)
            self._delete_nested_value(config, rule.old_path)
            logger.debug(f"Renamed field {rule.old_path} to {rule.new_path}")
        else:
            result.warnings.append(f"Field {rule.old_path} not found for renaming")

    def _move_field(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Move a field to a new location."""
        if not rule.old_path or not rule.new_path:
            result.errors.append("Move rule missing old_path or new_path")
            return

        old_value = self._get_nested_value(config, rule.old_path)
        if old_value is not None:
            self._set_nested_value(config, rule.new_path, old_value)
            self._delete_nested_value(config, rule.old_path)
            logger.debug(f"Moved field from {rule.old_path} to {rule.new_path}")
        else:
            result.warnings.append(f"Field {rule.old_path} not found for moving")

    def _transform_value(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Transform a field value."""
        if not rule.old_path:
            result.errors.append("Transform rule missing old_path")
            return

        old_value = self._get_nested_value(config, rule.old_path)
        if old_value is not None:
            if rule.transform_func:
                try:
                    new_value = rule.transform_func(old_value)
                    self._set_nested_value(config, rule.old_path, new_value)
                    logger.debug(f"Transformed value at {rule.old_path}")
                except Exception as e:
                    result.errors.append(f"Transform function failed: {e}")
            else:
                # Simple value replacement
                self._set_nested_value(config, rule.old_path, rule.new_value)
                logger.debug(f"Replaced value at {rule.old_path}")
        else:
            result.warnings.append(f"Field {rule.old_path} not found for transformation")

    def _add_field(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Add a new field to the configuration."""
        if not rule.new_path:
            result.errors.append("Add field rule missing new_path")
            return

        if self._get_nested_value(config, rule.new_path) is None:
            self._set_nested_value(config, rule.new_path, rule.new_value)
            logger.debug(f"Added field {rule.new_path}")
        else:
            result.warnings.append(f"Field {rule.new_path} already exists, not adding")

    def _remove_field(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Remove a field from the configuration."""
        if not rule.old_path:
            result.errors.append("Remove field rule missing old_path")
            return

        if self._get_nested_value(config, rule.old_path) is not None:
            self._delete_nested_value(config, rule.old_path)
            logger.debug(f"Removed field {rule.old_path}")
        else:
            result.warnings.append(f"Field {rule.old_path} not found for removal")

    def _split_field(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Split a field into multiple fields."""
        # Implementation would depend on specific splitting logic
        result.warnings.append("Split field migration not fully implemented")

    def _merge_fields(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Merge multiple fields into one."""
        # Implementation would depend on specific merging logic
        result.warnings.append("Merge fields migration not fully implemented")

    def _custom_transform(self, config: dict[str, Any], rule: MigrationRule, result: MigrationResult) -> None:
        """Apply custom transformation function."""
        if rule.transform_func:
            try:
                new_config = rule.transform_func(config)
                config.clear()
                config.update(new_config)
                logger.debug("Applied custom transformation")
            except Exception as e:
                result.errors.append(f"Custom transformation failed: {e}")
        else:
            result.errors.append("Custom transform rule missing transform function")

    def _get_nested_value(self, config: dict[str, Any], path: str) -> Any:
        """Get a nested value from configuration using dot notation."""
        keys = path.split('.')
        current = config

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def _set_nested_value(self, config: dict[str, Any], path: str, value: Any) -> None:
        """Set a nested value in configuration using dot notation."""
        keys = path.split('.')
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _delete_nested_value(self, config: dict[str, Any], path: str) -> None:
        """Delete a nested value from configuration using dot notation."""
        keys = path.split('.')
        current = config

        for key in keys[:-1]:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return

        if isinstance(current, dict) and keys[-1] in current:
            del current[keys[-1]]

# Predefined migration rules for common Codomyrmex configurations

def create_logging_migration_rules() -> list[MigrationRule]:
    """Create migration rules for logging configuration."""
    return [
        MigrationRule(
            action=MigrationAction.RENAME_FIELD,
            description="Rename 'log_level' to 'level'",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="log_level",
            new_path="level"
        ),
        MigrationRule(
            action=MigrationAction.TRANSFORM_VALUE,
            description="Transform log level values to uppercase",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="level",
            transform_func=lambda x: str(x).upper() if isinstance(x, str) else x
        ),
        MigrationRule(
            action=MigrationAction.ADD_FIELD,
            description="Add default JSON format option",
            from_version="2.0.0",
            to_version="3.0.0",
            new_path="format",
            new_value="JSON"
        )
    ]

def create_database_migration_rules() -> list[MigrationRule]:
    """Create migration rules for database configuration."""
    return [
        MigrationRule(
            action=MigrationAction.RENAME_FIELD,
            description="Rename 'db_host' to 'host'",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="db_host",
            new_path="host"
        ),
        MigrationRule(
            action=MigrationAction.MOVE_FIELD,
            description="Move connection settings to nested structure",
            from_version="2.0.0",
            to_version="3.0.0",
            old_path="connection_timeout",
            new_path="connection_pool.connection_timeout"
        ),
        MigrationRule(
            action=MigrationAction.ADD_FIELD,
            description="Add SSL mode configuration",
            from_version="2.0.0",
            to_version="3.0.0",
            new_path="ssl_mode",
            new_value="require"
        )
    ]

# Convenience functions

def migrate_config(config: dict[str, Any], from_version: str, to_version: str) -> MigrationResult:
    """
    Convenience function to migrate configuration.

    Args:
        config: Configuration to migrate
        from_version: Source version
        to_version: Target version

    Returns:
        MigrationResult with migrated configuration
    """
    migrator = ConfigMigrator()

    # Add common migration rules
    for rule in create_logging_migration_rules():
        migrator.add_migration_rule(rule)
    for rule in create_database_migration_rules():
        migrator.add_migration_rule(rule)

    return migrator.migrate_config(config, from_version, to_version)
