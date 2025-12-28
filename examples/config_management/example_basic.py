#!/usr/bin/env python3
"""
Example: Config Management - Configuration Loading and Validation

This example demonstrates:
- Loading configuration from multiple sources
- Validating configurations against schemas
- Merging configuration overrides
- Managing configuration secrets

Tested Methods:
- load_configuration() - Verified in test_config_management.py::TestConfigManagement::test_load_configuration
- validate_configuration() - Verified in test_config_management.py::TestConfigManagement::test_validate_configuration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.config_management.config_loader import Configuration
from codomyrmex.config_management.config_validator import ConfigSchema
from codomyrmex.config_management.config_migrator import ConfigMigrator
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results

def main():
    """Run the config management example."""
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Config Management Example")

        # Get config management settings
        mgmt_config = config.get('config_management', {})

        results = {
            'configurations_loaded': 0,
            'validations_performed': 0,
            'migrations_applied': 0,
            'secrets_managed': 0
        }

        # Load configuration from multiple sources
        print("Loading configuration from multiple sources...")
        config_sources = mgmt_config.get('config_sources', ['config.yaml'])

        merged_config = {}
        for source in config_sources:
            source_path = Path(__file__).parent / source
            if source_path.exists():
                source_config = load_config(source_path)
                merged_config.update(source_config)
                results['configurations_loaded'] += 1

        print(f"✓ Loaded {results['configurations_loaded']} configuration sources")

        # Create configuration object
        configuration = Configuration(
            data=merged_config,
            source='example_merged',
            environment='development'
        )

        # Validate configuration
        print("\nValidating configuration...")
        schema_def = mgmt_config.get('schema', {})
        if schema_def:
            schema = ConfigSchema()
            # Add schema rules
            for field, rules in schema_def.items():
                schema.add_field(field, rules)

            validation_errors = configuration.validate()
            results['validations_performed'] = 1

            if validation_errors:
                print(f"✗ Configuration validation failed: {validation_errors}")
                results['validation_errors'] = validation_errors
            else:
                print("✓ Configuration validation passed")
                results['validation_status'] = 'valid'

        # Test configuration migration
        print("\nTesting configuration migration...")
        migrator = ConfigMigrator()
        current_version = configuration.version

        # Add a migration rule (example)
        migrator.add_migration_rule(
            from_version=current_version,
            to_version="2.0.0",
            migration_func=lambda config: {**config, 'migrated': True}
        )

        # Apply migration
        if migrator.can_migrate(current_version, "2.0.0"):
            migrated_config = migrator.migrate(configuration.data, current_version, "2.0.0")
            results['migrations_applied'] = 1
            results['migration_result'] = migrated_config.get('migrated', False)
            print("✓ Configuration migration successful")

        # Demonstrate configuration access
        print("\nDemonstrating configuration access...")
        config_access_examples = mgmt_config.get('access_examples', [])

        access_results = {}
        for example in config_access_examples:
            key = example.get('key')
            default = example.get('default', 'not found')
            value = configuration.get_value(key, default)
            access_results[key] = value
            print(f"  {key} -> {value}")

        results['config_access_examples'] = access_results

        # Generate summary
        results['summary'] = {
            'total_operations': (results['configurations_loaded'] +
                               results['validations_performed'] +
                               results['migrations_applied']),
            'configuration_size': len(str(merged_config)),
            'environment': configuration.environment,
            'config_keys': list(merged_config.keys())
        }

        print_section("Config Management Results")
        print_results(results['summary'], "Configuration Management Summary")

        runner.validate_results(results)
        runner.save_results(results)

        runner.complete("Config management example completed successfully")

    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

