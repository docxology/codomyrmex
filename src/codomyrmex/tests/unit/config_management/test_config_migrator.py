"""Comprehensive tests for config_management.migration.config_migrator — zero-mock.

Covers: MigrationAction, MigrationRule, MigrationResult, ConfigMigrator
(add/rename/move/remove/transform field operations, version path finding,
validation, and custom migration registration).
"""

from codomyrmex.config_management.migration.config_migrator import (
    ConfigMigrator,
    MigrationAction,
    MigrationResult,
    MigrationRule,
)

# ---------------------------------------------------------------------------
# MigrationAction enum
# ---------------------------------------------------------------------------


class TestMigrationAction:
    def test_all_actions_exist(self):
        assert MigrationAction.RENAME_FIELD.value == "rename_field"
        assert MigrationAction.MOVE_FIELD.value == "move_field"
        assert MigrationAction.TRANSFORM_VALUE.value == "transform_value"
        assert MigrationAction.ADD_FIELD.value == "add_field"
        assert MigrationAction.REMOVE_FIELD.value == "remove_field"
        assert MigrationAction.SPLIT_FIELD.value == "split_field"
        assert MigrationAction.MERGE_FIELDS.value == "merge_fields"
        assert MigrationAction.CUSTOM_TRANSFORM.value == "custom_transform"


# ---------------------------------------------------------------------------
# MigrationRule
# ---------------------------------------------------------------------------


class TestMigrationRule:
    def test_create_rename_rule(self):
        rule = MigrationRule(
            action=MigrationAction.RENAME_FIELD,
            description="Rename api_key to api_token",
            from_version="1.0",
            to_version="2.0",
            old_path="api_key",
            new_path="api_token",
        )
        assert rule.action == MigrationAction.RENAME_FIELD
        assert rule.old_path == "api_key"

    def test_create_add_rule(self):
        rule = MigrationRule(
            action=MigrationAction.ADD_FIELD,
            description="Add debug flag",
            from_version="1.0",
            to_version="2.0",
            new_path="debug",
            new_value=False,
        )
        assert rule.new_value is False

    def test_to_dict(self):
        rule = MigrationRule(
            action=MigrationAction.REMOVE_FIELD,
            description="Remove deprecated option",
            from_version="1.0",
            to_version="2.0",
            old_path="old_option",
        )
        d = rule.to_dict()
        assert isinstance(d, dict)
        assert d["action"] == "remove_field"


# ---------------------------------------------------------------------------
# MigrationResult
# ---------------------------------------------------------------------------


class TestMigrationResult:
    def test_successful_result(self):
        result = MigrationResult(
            success=True,
            original_version="1.0",
            target_version="2.0",
            migrated_config={"key": "value"},
        )
        assert result.success
        assert result.original_version == "1.0"

    def test_result_with_warnings(self):
        result = MigrationResult(
            success=True,
            original_version="1.0",
            target_version="2.0",
            migrated_config={},
            warnings=["Field 'x' was removed"],
        )
        assert len(result.warnings) == 1

    def test_to_dict(self):
        result = MigrationResult(
            success=True,
            original_version="1.0",
            target_version="2.0",
            migrated_config={"a": 1},
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["success"] is True


# ---------------------------------------------------------------------------
# ConfigMigrator — Core Operations
# ---------------------------------------------------------------------------


class TestConfigMigratorCore:
    def test_init(self):
        migrator = ConfigMigrator()
        assert migrator is not None

    def test_add_migration_rule(self):
        migrator = ConfigMigrator()
        rule = MigrationRule(
            action=MigrationAction.ADD_FIELD,
            description="Add timeout",
            from_version="1.0",
            to_version="2.0",
            new_path="timeout",
            new_value=30,
        )
        migrator.add_migration_rule(rule)
        # Rule should be retrievable via migration path
        path = migrator.get_migration_path("1.0", "2.0")
        assert len(path) > 0


# ---------------------------------------------------------------------------
# ConfigMigrator — Field Operations
# ---------------------------------------------------------------------------


class TestConfigMigratorFieldOps:
    def _setup_migrator(self, *rules):
        """Helper: build a migrator with given rules."""
        m = ConfigMigrator()
        for r in rules:
            m.add_migration_rule(r)
        return m

    def test_add_field(self):
        m = self._setup_migrator(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Add debug",
                from_version="1.0",
                to_version="2.0",
                new_path="debug",
                new_value=True,
            )
        )
        result = m.migrate_config({"name": "app"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config.get("debug") is True

    def test_remove_field(self):
        m = self._setup_migrator(
            MigrationRule(
                action=MigrationAction.REMOVE_FIELD,
                description="Remove old_setting",
                from_version="1.0",
                to_version="2.0",
                old_path="old_setting",
            )
        )
        result = m.migrate_config({"old_setting": 42, "name": "app"}, "1.0", "2.0")
        assert result.success
        assert "old_setting" not in result.migrated_config

    def test_rename_field(self):
        m = self._setup_migrator(
            MigrationRule(
                action=MigrationAction.RENAME_FIELD,
                description="Rename key",
                from_version="1.0",
                to_version="2.0",
                old_path="api_key",
                new_path="api_token",
            )
        )
        result = m.migrate_config({"api_key": "secret123"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config.get("api_token") == "secret123"
        assert "api_key" not in result.migrated_config

    def test_transform_value(self):
        m = self._setup_migrator(
            MigrationRule(
                action=MigrationAction.TRANSFORM_VALUE,
                description="Uppercase name",
                from_version="1.0",
                to_version="2.0",
                old_path="name",
                transform_func=lambda v: v.upper(),
            )
        )
        result = m.migrate_config({"name": "hello"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config["name"] == "HELLO"


# ---------------------------------------------------------------------------
# ConfigMigrator — Multi-Step
# ---------------------------------------------------------------------------


class TestConfigMigratorMultiStep:
    def test_multiple_rules_same_version(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Add debug",
                from_version="1.0",
                to_version="2.0",
                new_path="debug",
                new_value=False,
            )
        )
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.REMOVE_FIELD,
                description="Remove legacy",
                from_version="1.0",
                to_version="2.0",
                old_path="legacy",
            )
        )
        result = m.migrate_config({"legacy": True, "name": "app"}, "1.0", "2.0")
        assert result.success
        assert result.migrated_config.get("debug") is False
        assert "legacy" not in result.migrated_config

    def test_backup_config_preserved(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Add x",
                from_version="1.0",
                to_version="2.0",
                new_path="x",
                new_value=1,
            )
        )
        original = {"name": "app"}
        result = m.migrate_config(original, "1.0", "2.0")
        # Backup should be the original config
        assert result.backup_config is not None
        assert result.backup_config.get("name") == "app"


# ---------------------------------------------------------------------------
# ConfigMigrator — Custom Migrations
# ---------------------------------------------------------------------------


class TestConfigMigratorCustom:
    def test_register_custom_migration(self):
        m = ConfigMigrator()

        def custom_v2_to_v3(config):
            config["version"] = "3.0"
            return config

        m.register_migration("2.0", "3.0", custom_v2_to_v3)
        path = m.get_migration_path("2.0", "3.0")
        assert len(path) > 0


# ---------------------------------------------------------------------------
# ConfigMigrator — Validation
# ---------------------------------------------------------------------------


class TestConfigMigratorValidation:
    def test_validate_migration(self):
        m = ConfigMigrator()
        m.add_migration_rule(
            MigrationRule(
                action=MigrationAction.ADD_FIELD,
                description="Add required field",
                from_version="1.0",
                to_version="2.0",
                new_path="required_field",
                new_value="default",
            )
        )
        # Validate that config is compatible with target
        is_valid = m.validate_migration({"name": "app"}, target_version="2.0")
        assert isinstance(is_valid, bool)
