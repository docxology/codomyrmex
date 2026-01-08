from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import re
import time

from dataclasses import dataclass, field
import hashlib

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger






#!/usr/bin/env python3
"""
Schema Generator Module for Codomyrmex Database Management.

This module provides database schema generation, migration creation,
and schema comparison capabilities supporting SQLite, PostgreSQL, and MySQL.
"""



logger = get_logger(__name__)


# SQL type mappings for different databases
TYPE_MAPPINGS = {
    "sqlite": {
        "string": "TEXT",
        "text": "TEXT",
        "integer": "INTEGER",
        "float": "REAL",
        "boolean": "INTEGER",
        "datetime": "TEXT",
        "date": "TEXT",
        "binary": "BLOB",
        "json": "TEXT",
        "uuid": "TEXT",
    },
    "postgresql": {
        "string": "VARCHAR",
        "text": "TEXT",
        "integer": "INTEGER",
        "float": "DOUBLE PRECISION",
        "boolean": "BOOLEAN",
        "datetime": "TIMESTAMP",
        "date": "DATE",
        "binary": "BYTEA",
        "json": "JSONB",
        "uuid": "UUID",
    },
    "mysql": {
        "string": "VARCHAR",
        "text": "TEXT",
        "integer": "INT",
        "float": "DOUBLE",
        "boolean": "TINYINT(1)",
        "datetime": "DATETIME",
        "date": "DATE",
        "binary": "BLOB",
        "json": "JSON",
        "uuid": "CHAR(36)",
    }
}


@dataclass
class Column:
    """Database column definition."""
    name: str
    data_type: str
    length: Optional[int] = None
    nullable: bool = True
    primary_key: bool = False
    auto_increment: bool = False
    unique: bool = False
    default: Optional[Any] = None
    foreign_key: Optional[dict[str, str]] = None  # {"table": "users", "column": "id"}
    check: Optional[str] = None

    def to_sql(self, dialect: str = "sqlite") -> str:
        """Generate SQL column definition."""
        type_mapping = TYPE_MAPPINGS.get(dialect, TYPE_MAPPINGS["sqlite"])
        sql_type = type_mapping.get(self.data_type.lower(), self.data_type.upper())

        if self.length and self.data_type.lower() in ["string", "varchar"]:
            sql_type = f"{sql_type}({self.length})"

        parts = [self.name, sql_type]

        if self.primary_key:
            parts.append("PRIMARY KEY")
            if self.auto_increment:
                if dialect == "sqlite":
                    parts.append("AUTOINCREMENT")
                elif dialect == "mysql":
                    parts.append("AUTO_INCREMENT")
                # PostgreSQL uses SERIAL type instead

        if not self.nullable and not self.primary_key:
            parts.append("NOT NULL")

        if self.unique and not self.primary_key:
            parts.append("UNIQUE")

        if self.default is not None:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            elif isinstance(self.default, bool):
                parts.append(f"DEFAULT {1 if self.default else 0}")
            else:
                parts.append(f"DEFAULT {self.default}")

        if self.check:
            parts.append(f"CHECK ({self.check})")

        return " ".join(parts)


@dataclass
class Index:
    """Database index definition."""
    name: str
    columns: list[str]
    unique: bool = False
    condition: Optional[str] = None  # Partial index condition

    def to_sql(self, table_name: str, dialect: str = "sqlite") -> str:
        """Generate SQL index creation statement."""
        unique_str = "UNIQUE " if self.unique else ""
        columns_str = ", ".join(self.columns)

        sql = f"CREATE {unique_str}INDEX IF NOT EXISTS {self.name} ON {table_name} ({columns_str})"

        if self.condition and dialect in ["postgresql", "sqlite"]:
            sql += f" WHERE {self.condition}"

        return sql


@dataclass
class SchemaTable:
    """Database table schema definition."""
    name: str
    columns: list[Column] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    description: str = ""

    def to_sql(self, dialect: str = "sqlite") -> str:
        """Generate SQL CREATE TABLE statement."""
        column_defs = []

        for col in self.columns:
            col_sql = col.to_sql(dialect)
            column_defs.append(f"    {col_sql}")

            # Add foreign key constraint
            if col.foreign_key:
                fk_table = col.foreign_key["table"]
                fk_column = col.foreign_key.get("column", "id")
                constraint = f"    FOREIGN KEY ({col.name}) REFERENCES {fk_table}({fk_column})"
                column_defs.append(constraint)

        for constraint in self.constraints:
            column_defs.append(f"    {constraint}")

        columns_sql = ",\n".join(column_defs)

        return f"CREATE TABLE IF NOT EXISTS {self.name} (\n{columns_sql}\n)"

    def to_dict(self) -> dict[str, Any]:
        """Convert table to dictionary."""
        return {
            "name": self.name,
            "columns": [
                {
                    "name": c.name,
                    "type": c.data_type,
                    "length": c.length,
                    "nullable": c.nullable,
                    "primary_key": c.primary_key,
                    "unique": c.unique,
                    "default": c.default,
                    "foreign_key": c.foreign_key
                }
                for c in self.columns
            ],
            "indexes": [{"name": i.name, "columns": i.columns, "unique": i.unique} for i in self.indexes],
            "constraints": self.constraints,
            "description": self.description
        }


@dataclass
class SchemaMigration:
    """Database schema migration."""
    migration_id: str
    name: str
    description: str
    up_sql: str
    down_sql: str
    dependencies: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.sha256(self.up_sql.encode()).hexdigest()[:16]


@dataclass
class SchemaDefinition:
    """Complete database schema definition."""
    name: str
    version: str
    tables: list[SchemaTable] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def to_sql(self, dialect: str = "sqlite") -> str:
        """Generate complete SQL schema."""
        statements = [f"-- Schema: {self.name} v{self.version}"]
        statements.append(f"-- Generated: {self.created_at.isoformat()}\n")

        for table in self.tables:
            statements.append(table.to_sql(dialect) + ";\n")

            for index in table.indexes:
                statements.append(index.to_sql(table.name, dialect) + ";")

        return "\n".join(statements)

    def to_dict(self) -> dict[str, Any]:
        """Convert schema to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "tables": [t.to_dict() for t in self.tables],
            "created_at": self.created_at.isoformat()
        }


class SchemaGenerator:
    """Database schema generation and management system."""

    def __init__(self, workspace_dir: Optional[str] = None, dialect: str = "sqlite"):
        """Initialize schema generator.

        Args:
            workspace_dir: Directory for storing schema data
            dialect: SQL dialect ("sqlite", "postgresql", "mysql")
        """
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.schemas_dir = self.workspace_dir / "database_schemas"
        self.migrations_dir = self.workspace_dir / "schema_migrations"
        self.dialect = dialect
        self._ensure_directories()

        self._tables: dict[str, SchemaTable] = {}
        self._migrations: dict[str, SchemaMigration] = {}

    def _ensure_directories(self):
        """Ensure required directories exist."""
        self.schemas_dir.mkdir(parents=True, exist_ok=True)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

    def create_table(self, table: SchemaTable) -> str:
        """Create a table schema definition.

        Args:
            table: Table schema definition

        Returns:
            Table ID
        """
        table_id = f"table_{table.name}"
        self._tables[table_id] = table

        # Save table schema
        schema_file = self.schemas_dir / f"{table_id}.json"
        with open(schema_file, 'w') as f:
            json.dump(table.to_dict(), f, indent=2)

        logger.info(f"Created table schema: {table.name}")
        return table_id

    def create_table_from_dict(self, table_def: dict[str, Any]) -> str:
        """Create a table from a dictionary definition.

        Args:
            table_def: Table definition dictionary

        Returns:
            Table ID
        """
        columns = []
        for col_def in table_def.get("columns", []):
            columns.append(Column(
                name=col_def["name"],
                data_type=col_def.get("type", "string"),
                length=col_def.get("length"),
                nullable=col_def.get("nullable", True),
                primary_key=col_def.get("primary_key", False),
                auto_increment=col_def.get("auto_increment", False),
                unique=col_def.get("unique", False),
                default=col_def.get("default"),
                foreign_key=col_def.get("foreign_key")
            ))

        indexes = []
        for idx_def in table_def.get("indexes", []):
            indexes.append(Index(
                name=idx_def["name"],
                columns=idx_def["columns"],
                unique=idx_def.get("unique", False)
            ))

        table = SchemaTable(
            name=table_def["name"],
            columns=columns,
            indexes=indexes,
            constraints=table_def.get("constraints", []),
            description=table_def.get("description", "")
        )

        return self.create_table(table)

    def generate_migration(
        self,
        name: str,
        description: str,
        changes: dict[str, Any]
    ) -> SchemaMigration:
        """Generate a schema migration from changes.

        Args:
            name: Migration name
            description: Migration description
            changes: Schema changes to apply

        Returns:
            Generated migration
        """
        migration_id = f"migration_{int(time.time())}_{name.replace(' ', '_').lower()}"

        up_sql = self._generate_up_sql(changes)
        down_sql = self._generate_down_sql(changes)

        migration = SchemaMigration(
            migration_id=migration_id,
            name=name,
            description=description,
            up_sql=up_sql,
            down_sql=down_sql
        )

        self._migrations[migration_id] = migration

        # Save migration
        migration_file = self.migrations_dir / f"{migration_id}.json"
        with open(migration_file, 'w') as f:
            json.dump({
                "id": migration.migration_id,
                "name": migration.name,
                "description": migration.description,
                "up_sql": migration.up_sql,
                "down_sql": migration.down_sql,
                "dependencies": migration.dependencies,
                "created_at": migration.created_at.isoformat(),
                "checksum": migration.checksum
            }, f, indent=2)

        # Also save as SQL files
        up_file = self.migrations_dir / f"{migration_id}_up.sql"
        down_file = self.migrations_dir / f"{migration_id}_down.sql"
        up_file.write_text(up_sql)
        down_file.write_text(down_sql)

        logger.info(f"Generated migration: {migration_id}")
        return migration

    def _generate_up_sql(self, changes: dict[str, Any]) -> str:
        """Generate up migration SQL from changes."""
        statements = [f"-- Migration: {changes.get('name', 'unnamed')}"]

        # Create new tables
        for table_def in changes.get("create_tables", []):
            if isinstance(table_def, dict):
                table = self._dict_to_table(table_def)
                statements.append(table.to_sql(self.dialect) + ";")

        # Add columns
        for col_change in changes.get("add_columns", []):
            table_name = col_change["table"]
            for col_def in col_change.get("columns", []):
                col = Column(**col_def) if isinstance(col_def, dict) else col_def
                statements.append(f"ALTER TABLE {table_name} ADD COLUMN {col.to_sql(self.dialect)};")

        # Drop columns
        for col_change in changes.get("drop_columns", []):
            table_name = col_change["table"]
            for col_name in col_change.get("columns", []):
                statements.append(f"ALTER TABLE {table_name} DROP COLUMN {col_name};")

        # Modify columns
        for col_change in changes.get("modify_columns", []):
            table_name = col_change["table"]
            for col_def in col_change.get("columns", []):
                col = Column(**col_def) if isinstance(col_def, dict) else col_def
                if self.dialect == "postgresql":
                    statements.append(
                        f"ALTER TABLE {table_name} ALTER COLUMN {col.name} TYPE {col.data_type};"
                    )
                elif self.dialect == "mysql":
                    statements.append(
                        f"ALTER TABLE {table_name} MODIFY COLUMN {col.to_sql(self.dialect)};"
                    )

        # Create indexes
        for idx_def in changes.get("create_indexes", []):
            table_name = idx_def["table"]
            index = Index(**{k: v for k, v in idx_def.items() if k != "table"})
            statements.append(index.to_sql(table_name, self.dialect) + ";")

        # Drop indexes
        for idx_name in changes.get("drop_indexes", []):
            statements.append(f"DROP INDEX IF EXISTS {idx_name};")

        # Drop tables
        for table_name in changes.get("drop_tables", []):
            statements.append(f"DROP TABLE IF EXISTS {table_name};")

        # Raw SQL
        for sql in changes.get("raw_sql", []):
            statements.append(sql)

        return "\n".join(statements)

    def _generate_down_sql(self, changes: dict[str, Any]) -> str:
        """Generate down migration SQL (rollback) from changes."""
        statements = [f"-- Rollback migration: {changes.get('name', 'unnamed')}"]

        # Rollback table creations by dropping them
        for table_def in changes.get("create_tables", []):
            table_name = table_def["name"] if isinstance(table_def, dict) else table_def.name
            statements.append(f"DROP TABLE IF EXISTS {table_name};")

        # Rollback column additions by dropping them
        for col_change in changes.get("add_columns", []):
            table_name = col_change["table"]
            for col_def in col_change.get("columns", []):
                col_name = col_def["name"] if isinstance(col_def, dict) else col_def.name
                statements.append(f"ALTER TABLE {table_name} DROP COLUMN {col_name};")

        # Rollback index creations by dropping them
        for idx_def in changes.get("create_indexes", []):
            idx_name = idx_def["name"]
            statements.append(f"DROP INDEX IF EXISTS {idx_name};")

        # Note: Dropping columns and tables can't be easily reversed
        # Would need to store original schema

        return "\n".join(statements)

    def _dict_to_table(self, table_def: dict[str, Any]) -> SchemaTable:
        """Convert dictionary to SchemaTable."""
        columns = []
        for col_def in table_def.get("columns", []):
            columns.append(Column(
                name=col_def["name"],
                data_type=col_def.get("type", "string"),
                length=col_def.get("length"),
                nullable=col_def.get("nullable", True),
                primary_key=col_def.get("primary_key", False),
                auto_increment=col_def.get("auto_increment", False),
                unique=col_def.get("unique", False),
                default=col_def.get("default"),
                foreign_key=col_def.get("foreign_key")
            ))

        indexes = []
        for idx_def in table_def.get("indexes", []):
            indexes.append(Index(
                name=idx_def["name"],
                columns=idx_def["columns"],
                unique=idx_def.get("unique", False)
            ))

        return SchemaTable(
            name=table_def["name"],
            columns=columns,
            indexes=indexes,
            constraints=table_def.get("constraints", []),
            description=table_def.get("description", "")
        )

    def compare_schemas(
        self,
        current_schema: dict[str, Any],
        target_schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Compare two schemas and generate differences.

        Args:
            current_schema: Current database schema
            target_schema: Target schema

        Returns:
            Schema differences with migration recommendations
        """
        differences = {
            "tables_to_add": [],
            "tables_to_remove": [],
            "columns_to_add": [],
            "columns_to_remove": [],
            "columns_to_modify": [],
            "indexes_to_add": [],
            "indexes_to_remove": []
        }

        current_tables = {t["name"]: t for t in current_schema.get("tables", [])}
        target_tables = {t["name"]: t for t in target_schema.get("tables", [])}

        # Find new tables
        for table_name in target_tables:
            if table_name not in current_tables:
                differences["tables_to_add"].append(target_tables[table_name])

        # Find removed tables
        for table_name in current_tables:
            if table_name not in target_tables:
                differences["tables_to_remove"].append(table_name)

        # Compare columns in matching tables
        for table_name in current_tables:
            if table_name in target_tables:
                current_cols = {c["name"]: c for c in current_tables[table_name].get("columns", [])}
                target_cols = {c["name"]: c for c in target_tables[table_name].get("columns", [])}

                # New columns
                for col_name in target_cols:
                    if col_name not in current_cols:
                        differences["columns_to_add"].append({
                            "table": table_name,
                            "column": target_cols[col_name]
                        })

                # Removed columns
                for col_name in current_cols:
                    if col_name not in target_cols:
                        differences["columns_to_remove"].append({
                            "table": table_name,
                            "column": col_name
                        })

                # Modified columns
                for col_name in current_cols:
                    if col_name in target_cols:
                        if current_cols[col_name] != target_cols[col_name]:
                            differences["columns_to_modify"].append({
                                "table": table_name,
                                "from": current_cols[col_name],
                                "to": target_cols[col_name]
                            })

        return differences

    def get_schema_drift_report(
        self,
        current_schema: dict[str, Any],
        target_schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate schema drift report.

        Args:
            current_schema: Current database schema
            target_schema: Target schema

        Returns:
            Drift analysis report
        """
        differences = self.compare_schemas(current_schema, target_schema)

        has_drift = any(
            len(differences[key]) > 0
            for key in differences
        )

        recommendations = []
        if differences["tables_to_add"]:
            recommendations.append(f"Create {len(differences['tables_to_add'])} new table(s)")
        if differences["tables_to_remove"]:
            recommendations.append(f"Review {len(differences['tables_to_remove'])} table(s) for removal")
        if differences["columns_to_add"]:
            recommendations.append(f"Add {len(differences['columns_to_add'])} new column(s)")
        if differences["columns_to_remove"]:
            recommendations.append(f"Review {len(differences['columns_to_remove'])} column(s) for removal")
        if differences["columns_to_modify"]:
            recommendations.append(f"Modify {len(differences['columns_to_modify'])} column(s)")

        if not recommendations:
            recommendations.append("Schema is up to date - no changes needed")

        return {
            "drift_detected": has_drift,
            "tables_added": [t["name"] for t in differences["tables_to_add"]],
            "tables_removed": differences["tables_to_remove"],
            "columns_added": differences["columns_to_add"],
            "columns_removed": differences["columns_to_remove"],
            "columns_modified": differences["columns_to_modify"],
            "recommendations": recommendations,
            "migration_needed": has_drift
        }

    def generate_schema_sql(self, schema_name: str, version: str = "1.0.0") -> str:
        """Generate complete SQL schema from defined tables.

        Args:
            schema_name: Name for the schema
            version: Schema version

        Returns:
            Complete SQL schema
        """
        schema = SchemaDefinition(
            name=schema_name,
            version=version,
            tables=list(self._tables.values())
        )

        return schema.to_sql(self.dialect)

    def export_schema(self, output_path: str, format: str = "sql") -> str:
        """Export schema to file.

        Args:
            output_path: Output file path
            format: Output format ("sql", "json")

        Returns:
            Path to exported file
        """
        output = Path(output_path)

        if format == "sql":
            sql = self.generate_schema_sql("exported_schema")
            output.write_text(sql)
        elif format == "json":
            schema_data = {
                "tables": [t.to_dict() for t in self._tables.values()],
                "exported_at": datetime.now().isoformat()
            }
            with open(output, 'w') as f:
                json.dump(schema_data, f, indent=2)
        else:
            raise CodomyrmexError(f"Unsupported format: {format}")

        logger.info(f"Exported schema to {output}")
        return str(output)

    def list_migrations(self) -> list[dict[str, Any]]:
        """List all migrations."""
        return [
            {
                "id": m.migration_id,
                "name": m.name,
                "description": m.description,
                "dependencies": m.dependencies,
                "created_at": m.created_at.isoformat(),
                "checksum": m.checksum
            }
            for m in self._migrations.values()
        ]


def generate_schema(models: list[Any], output_dir: str) -> dict[str, Any]:
    """Generate database schema from models.

    Args:
        models: List of model definitions
        output_dir: Output directory for generated schema

    Returns:
        Generated schema information
    """
    return generate_schema_from_models(models, output_dir)


def generate_schema_from_models(models: list[Any], output_dir: str) -> dict[str, Any]:
    """Generate database schema from model definitions.

    Args:
        models: List of model classes or dictionaries
        output_dir: Output directory for generated schema

    Returns:
        Generated schema information
    """
    generator = SchemaGenerator(workspace_dir=output_dir)
    tables_generated = 0

    for model in models:
        if isinstance(model, dict):
            generator.create_table_from_dict(model)
            tables_generated += 1
        elif hasattr(model, "__table__"):
            # SQLAlchemy model - extract table info
            table_def = {
                "name": model.__tablename__,
                "columns": [],
                "description": model.__doc__ or ""
            }

            for column in model.__table__.columns:
                col_def = {
                    "name": column.name,
                    "type": str(column.type).lower(),
                    "nullable": column.nullable,
                    "primary_key": column.primary_key
                }
                table_def["columns"].append(col_def)

            generator.create_table_from_dict(table_def)
            tables_generated += 1

    # Export schema
    schema_file = Path(output_dir) / "generated_schema.sql"
    generator.export_schema(str(schema_file), format="sql")

    return {
        "tables_generated": tables_generated,
        "schema_file": str(schema_file),
        "message": f"Generated schema with {tables_generated} tables"
    }
