"""
Migration Module

Data migration with versioned steps, rollbacks, and transformers.
"""

from .models import (
    CompositeTransformer,
    DataTransformer,
    FieldRenameTransformer,
    FieldTypeTransformer,
    Migration,
    MigrationDirection,
    MigrationResult,
    MigrationStatus,
    MigrationStep,
)
from .executor import DataMigrator, MigrationRunner

# Shared schemas for cross-module interop
try:
    from codomyrmex.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the migration module."""
    return {
        "pending": lambda: print(
            "Pending Migrations\n"
            "  Migration statuses: " + ", ".join(ms.value for ms in MigrationStatus) + "\n"
            "  Directions: " + ", ".join(md.value for md in MigrationDirection) + "\n"
            "  Use MigrationRunner to check for and list pending migrations."
        ),
        "run": lambda: print(
            "Run Migrations\n"
            "  Use MigrationRunner.run() to execute pending migrations.\n"
            "  Use DataMigrator for data-level transformations.\n"
            "  Available transformers: FieldRenameTransformer, FieldTypeTransformer, CompositeTransformer"
        ),
    }


__all__ = [
    "MigrationStatus",
    "MigrationDirection",
    "MigrationStep",
    "MigrationResult",
    "Migration",
    "DataTransformer",
    "FieldRenameTransformer",
    "FieldTypeTransformer",
    "CompositeTransformer",
    "MigrationRunner",
    "DataMigrator",
    # CLI
    "cli_commands",
]
