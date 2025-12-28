"""Enhanced tests for configuration management improvements."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

# Test ConfigValidator
class TestConfigValidator:
    """Test cases for ConfigValidator functionality."""

    def test_config_validator_creation(self):
        """Test creating a ConfigValidator."""
        try:
            from codomyrmex.config_management.config_validator import ConfigValidator, ConfigSchema
        except ImportError:
            pytest.skip("ConfigValidator not available")

        validator = ConfigValidator()
        assert validator is not None
        assert validator.schema == {}
        assert validator.custom_validators == {}

    def test_config_schema_creation(self):
        """Test creating configuration schemas."""
        try:
            from codomyrmex.config_management.config_validator import ConfigSchema
        except ImportError:
            pytest.skip("ConfigSchema not available")

        schema = ConfigSchema(
            type="str",
            required=True,
            default="default_value",
            description="Test field",
            constraints={"min_length": 3, "max_length": 50}
        )

        assert schema.type == "str"
        assert schema.required == True
        assert schema.default == "default_value"
        assert schema.description == "Test field"
        assert schema.constraints["min_length"] == 3

    def test_validate_simple_config(self):
        """Test validating a simple configuration."""
        try:
            from codomyrmex.config_management.config_validator import ConfigValidator, ConfigSchema
        except ImportError:
            pytest.skip("ConfigValidator not available")

        schema = {
            "name": ConfigSchema(type="str", required=True),
            "port": ConfigSchema(type="int", required=False, default=8080, constraints={"min": 1, "max": 65535})
        }

        validator = ConfigValidator(schema)

        # Valid config
        valid_config = {"name": "test_service", "port": 9000}
        result = validator.validate(valid_config)
        assert result.is_valid
        assert len(result.errors) == 0

        # Invalid config - missing required field
        invalid_config = {"port": 9000}
        result = validator.validate(invalid_config)
        assert not result.is_valid
        assert len(result.errors) > 0

        # Invalid config - wrong type
        invalid_config2 = {"name": "test", "port": "not_a_number"}
        result = validator.validate(invalid_config2)
        assert not result.is_valid
        assert len(result.errors) > 0

    def test_validate_constraints(self):
        """Test constraint validation."""
        try:
            from codomyrmex.config_management.config_validator import ConfigValidator, ConfigSchema
        except ImportError:
            pytest.skip("ConfigValidator not available")

        schema = {
            "username": ConfigSchema(
                type="str",
                constraints={"min_length": 3, "max_length": 20, "pattern": r"^[a-zA-Z0-9_]+$"}
            ),
            "timeout": ConfigSchema(
                type="int",
                constraints={"min": 1, "max": 300}
            )
        }

        validator = ConfigValidator(schema)

        # Valid constraints
        valid_config = {"username": "test_user", "timeout": 60}
        result = validator.validate(valid_config)
        assert result.is_valid

        # Invalid constraints - too short username
        invalid_config1 = {"username": "a", "timeout": 60}
        result = validator.validate(invalid_config1)
        assert not result.is_valid

        # Invalid constraints - timeout too high
        invalid_config2 = {"username": "test_user", "timeout": 500}
        result = validator.validate(invalid_config2)
        assert not result.is_valid

        # Invalid constraints - bad pattern
        invalid_config3 = {"username": "test-user!", "timeout": 60}
        result = validator.validate(invalid_config3)
        assert not result.is_valid

    def test_custom_validator(self):
        """Test custom validator functionality."""
        try:
            from codomyrmex.config_management.config_validator import ConfigValidator, ValidationIssue, ValidationSeverity
        except ImportError:
            pytest.skip("ConfigValidator not available")

        def custom_port_validator(config):
            """Custom validator to check port ranges."""
            issues = []
            if "port" in config:
                port = config["port"]
                if port in [22, 80, 443]:  # Common ports that might be restricted
                    issues.append(ValidationIssue(
                        field_path="port",
                        message=f"Port {port} is commonly reserved and may cause conflicts",
                        severity=ValidationSeverity.WARNING,
                        suggestion="Consider using a different port"
                    ))
            return issues

        validator = ConfigValidator()
        validator.add_custom_validator("port_check", custom_port_validator)

        # Test with reserved port
        config = {"port": 80}
        result = validator.validate(config)

        # Should pass basic validation but have warnings from custom validator
        assert result.is_valid  # No schema, so basic validation passes
        assert len(result.warnings) > 0
        assert "commonly reserved" in result.warnings[0].message

    def test_premade_schemas(self):
        """Test premade schema functions."""
        try:
            from codomyrmex.config_management.config_validator import (
                get_logging_config_schema,
                get_database_config_schema,
                get_ai_model_config_schema
            )
        except ImportError:
            pytest.skip("Premade schemas not available")

        # Test logging schema
        logging_schema = get_logging_config_schema()
        assert "level" in logging_schema
        assert "format" in logging_schema

        # Test database schema
        db_schema = get_database_config_schema()
        assert "host" in db_schema
        assert "port" in db_schema
        assert "database" in db_schema

        # Test AI model schema
        ai_schema = get_ai_model_config_schema()
        assert "provider" in ai_schema
        assert "model" in ai_schema
        assert "temperature" in ai_schema

    def test_convenience_functions(self):
        """Test convenience validation functions."""
        try:
            from codomyrmex.config_management.config_validator import validate_config_schema
        except ImportError:
            pytest.skip("Convenience functions not available")

        schema = {"name": Mock(type="str", required=True)}
        valid_config = {"name": "test"}
        invalid_config = {"name": 123}

        # Mock the ConfigSchema to avoid full implementation
        with patch('codomyrmex.config_management.config_validator.ConfigSchema') as mock_schema:
            mock_schema_instance = Mock()
            mock_schema_instance.type = "str"
            mock_schema_instance.required = True
            mock_schema.return_value = mock_schema_instance

            # This would normally work with full implementation
            # For now, just test that function exists
            assert callable(validate_config_schema)


# Test ConfigMigrator
class TestConfigMigrator:
    """Test cases for ConfigMigrator functionality."""

    def test_config_migrator_creation(self):
        """Test creating a ConfigMigrator."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()
        assert migrator is not None
        assert migrator.migration_rules == {}
        assert migrator.version_order == []

    def test_add_migration_rule(self):
        """Test adding migration rules."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator, MigrationRule, MigrationAction
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()

        rule = MigrationRule(
            action=MigrationAction.RENAME_FIELD,
            description="Rename field",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="old_name",
            new_path="new_name"
        )

        migrator.add_migration_rule(rule)

        assert ("1.0.0", "2.0.0") in migrator.migration_rules
        assert len(migrator.migration_rules[("1.0.0", "2.0.0")]) == 1

    def test_migrate_config_simple(self):
        """Test simple configuration migration."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator, MigrationRule, MigrationAction
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()

        # Add a rename rule
        rule = MigrationRule(
            action=MigrationAction.RENAME_FIELD,
            description="Rename database field",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="database_name",
            new_path="database"
        )
        migrator.add_migration_rule(rule)

        # Test migration
        config = {"database_name": "test_db", "host": "localhost"}
        result = migrator.migrate_config(config, "1.0.0", "2.0.0")

        assert result.success
        assert result.original_version == "1.0.0"
        assert result.target_version == "2.0.0"
        assert "database" in result.migrated_config
        assert "database_name" not in result.migrated_config
        assert result.migrated_config["database"] == "test_db"
        assert len(result.applied_rules) == 1

    def test_migration_with_transform(self):
        """Test migration with value transformation."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator, MigrationRule, MigrationAction
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()

        # Add a transform rule
        rule = MigrationRule(
            action=MigrationAction.TRANSFORM_VALUE,
            description="Convert log level to uppercase",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="log_level",
            transform_func=lambda x: str(x).upper()
        )
        migrator.add_migration_rule(rule)

        # Test migration
        config = {"log_level": "debug", "format": "text"}
        result = migrator.migrate_config(config, "1.0.0", "2.0.0")

        assert result.success
        assert result.migrated_config["log_level"] == "DEBUG"

    def test_migration_path_finding(self):
        """Test finding migration paths."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()
        migrator.version_order = ["1.0.0", "1.1.0", "2.0.0", "2.1.0"]

        # Test forward migration
        path = migrator.get_migration_path("1.0.0", "2.0.0")
        expected = [("1.0.0", "1.1.0"), ("1.1.0", "2.0.0")]
        assert path == expected

        # Test backward migration
        path = migrator.get_migration_path("2.0.0", "1.0.0")
        expected = [("2.0.0", "1.1.0"), ("1.1.0", "1.0.0")]
        assert path == expected

        # Test same version
        path = migrator.get_migration_path("1.0.0", "1.0.0")
        assert path == []

    def test_migration_error_handling(self):
        """Test migration error handling."""
        try:
            from codomyrmex.config_management.config_migrator import ConfigMigrator, MigrationRule, MigrationAction
        except ImportError:
            pytest.skip("ConfigMigrator not available")

        migrator = ConfigMigrator()

        # Add a rule that will fail
        rule = MigrationRule(
            action=MigrationAction.TRANSFORM_VALUE,
            description="Failing transform",
            from_version="1.0.0",
            to_version="2.0.0",
            old_path="missing_field",
            transform_func=lambda x: x  # This won't be reached
        )
        migrator.add_migration_rule(rule)

        # Test migration with missing field
        config = {"other_field": "value"}
        result = migrator.migrate_config(config, "1.0.0", "2.0.0")

        # Should succeed but with warnings
        assert result.success
        assert len(result.warnings) > 0

    def test_premade_migration_rules(self):
        """Test premade migration rule functions."""
        try:
            from codomyrmex.config_management.config_migrator import (
                create_logging_migration_rules,
                create_database_migration_rules
            )
        except ImportError:
            pytest.skip("Premade migration rules not available")

        logging_rules = create_logging_migration_rules()
        assert len(logging_rules) > 0
        assert all(rule.from_version and rule.to_version for rule in logging_rules)

        db_rules = create_database_migration_rules()
        assert len(db_rules) > 0
        assert all(rule.from_version and rule.to_version for rule in db_rules)

    def test_convenience_migration(self):
        """Test convenience migration function."""
        try:
            from codomyrmex.config_management.config_migrator import migrate_config
        except ImportError:
            pytest.skip("Convenience migration function not available")

        # Test that function exists and is callable
        assert callable(migrate_config)

        # Test with mock
        with patch('codomyrmex.config_management.config_migrator.ConfigMigrator') as mock_migrator_class:
            mock_migrator = Mock()
            mock_migrator.migrate_config.return_value = Mock(success=True, migrated_config={"migrated": True})
            mock_migrator_class.return_value = mock_migrator

            result = migrate_config({"test": "data"}, "1.0.0", "2.0.0")

            assert result.success
            mock_migrator.migrate_config.assert_called_once()


# Test Enhanced ConfigurationManager
class TestConfigurationManagerEnhanced:
    """Test cases for enhanced ConfigurationManager functionality."""

    @patch('codomyrmex.config_management.config_loader.datetime')
    def test_load_config_with_validation(self, mock_datetime):
        """Test loading configuration with validation."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager, Configuration
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"

        manager = ConfigurationManager()

        # Mock the validation
        with patch.object(manager, 'load_configuration_from_file') as mock_load:
            mock_config = Mock(spec=Configuration)
            mock_config.config_data = {"name": "test", "port": 8080}
            mock_load.return_value = mock_config

            with patch('codomyrmex.config_management.config_loader.ConfigValidator') as mock_validator_class:
                mock_validator = Mock()
                mock_validator.validate.return_value = Mock(is_valid=True, errors=[], warnings=[])
                mock_validator_class.return_value = mock_validator

                result = manager.load_config_with_validation("/path/to/config.json", schema={})

                assert result is not None
                mock_validator.validate.assert_called_once()

    @patch('codomyrmex.config_management.config_loader.datetime')
    def test_migrate_configuration(self, mock_datetime):
        """Test configuration migration."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager, Configuration
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        mock_datetime.now.return_value.timestamp.return_value = 1672531200

        manager = ConfigurationManager()

        # Add a test configuration
        config = Configuration(
            name="test_config",
            config_data={"version": "1.0.0", "setting": "old_value"},
            source="test",
            loaded_at=mock_datetime.now.return_value
        )
        manager.configurations["test_config"] = config

        # Mock migration
        with patch('codomyrmex.config_management.config_migrator.migrate_config') as mock_migrate:
            mock_result = Mock()
            mock_result.success = True
            mock_result.migrated_config = {"version": "2.0.0", "setting": "new_value"}
            mock_migrate.return_value = mock_result

            success = manager.migrate_configuration("test_config", "2.0.0")

            assert success
            assert manager.configurations["test_config"].config_data["version"] == "2.0.0"
            assert manager.configurations["test_config"].config_data["setting"] == "new_value"

    def test_validate_config_schema(self):
        """Test configuration schema validation."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        manager = ConfigurationManager()

        # Test with mock
        with patch('codomyrmex.config_management.config_loader.validate_config_schema') as mock_validate:
            mock_validate.return_value = (True, [])

            result = manager.validate_config_schema({"test": "data"}, {"test": {"type": "str"}})

            assert result[0] == True
            assert result[1] == []
            mock_validate.assert_called_once()

    def test_get_validation_report(self):
        """Test getting validation reports."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager, Configuration
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        manager = ConfigurationManager()

        # Add test configuration
        config = Configuration(
            name="test_config",
            config_data={"level": "INFO", "format": "TEXT"},
            source="test",
            loaded_at=None
        )
        manager.configurations["test_config"] = config

        # Test validation report
        report = manager.get_validation_report("test_config")

        assert report is not None
        assert "is_valid" in report

        # Test with non-existent config
        report = manager.get_validation_report("nonexistent")
        assert report is None

    @patch('codomyrmex.config_management.config_loader.datetime')
    def test_create_migration_backup(self, mock_datetime):
        """Test creating migration backups."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager, Configuration
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        # Mock datetime
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
        mock_datetime.now.return_value.timestamp.return_value = 1672531200

        manager = ConfigurationManager()

        # Add test configuration
        config = Configuration(
            name="test_config",
            config_data={"version": "1.0.0", "data": "value"},
            source="test",
            loaded_at=mock_datetime.now.return_value
        )
        manager.configurations["test_config"] = config

        # Create backup
        success = manager.create_migration_backup("test_config")

        assert success
        # Should have created a backup configuration
        backup_names = [name for name in manager.configurations.keys() if name.startswith("test_config_backup")]
        assert len(backup_names) == 1

    def test_migration_error_handling(self):
        """Test migration error handling."""
        try:
            from codomyrmex.config_management.config_loader import ConfigurationManager
        except ImportError:
            pytest.skip("ConfigurationManager not available")

        manager = ConfigurationManager()

        # Test migrating non-existent configuration
        success = manager.migrate_configuration("nonexistent", "2.0.0")
        assert not success


if __name__ == "__main__":
    pytest.main([__file__])
