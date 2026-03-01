"""
Comprehensive tests for database_management core: schema generation, DDL output,
column type mapping, primary/foreign keys, indexes, migration planning, schema
comparison, drift reports, and migration models/executor.

Covers:
1. Column SQL generation across dialects (sqlite, postgresql, mysql)
2. Column type mapping (string->VARCHAR, int->INTEGER, etc.)
3. Primary key and auto-increment handling
4. Foreign key relationship rendering
5. Unique / NOT NULL / DEFAULT / CHECK constraints
6. Index generation (regular, unique, partial/conditional)
7. SchemaTable CREATE TABLE statement format
8. SchemaDefinition full schema generation
9. SchemaGenerator create_table and create_table_from_dict
10. Migration generation (up + down SQL)
11. Schema comparison (diff two schemas)
12. Schema drift report
13. Migration models (MigrationStep, MigrationResult, Migration)
14. MigrationRunner execution (up, down, rollback)
15. DataMigrator with transformers (rename, type-convert, composite)
16. MigrationManager with in-memory SQLite (create, apply, rollback)
"""

import json
import sqlite3
from pathlib import Path

import pytest

from codomyrmex.database_management.schema_generator import (
    Column,
    Index,
    SchemaDefinition,
    SchemaGenerator,
    SchemaTable,
    SchemaMigration,
    TYPE_MAPPINGS,
    generate_schema_from_models,
)
from codomyrmex.database_management.migration.models import (
    CompositeTransformer,
    FieldRenameTransformer,
    FieldTypeTransformer,
    Migration as MigrationModel,
    MigrationResult as MigrationModelResult,
    MigrationStatus,
    MigrationStep,
)
from codomyrmex.database_management.migration.executor import (
    DataMigrator,
    MigrationRunner,
)
from codomyrmex.database_management.migration.migration_manager import (
    DatabaseConnector,
    MigrationManager,
)
from codomyrmex.exceptions import CodomyrmexError


# =============================================================================
# Column SQL Generation Tests
# =============================================================================

class TestColumnTypeMappingSQLite:
    """Test Column.to_sql() produces correct SQLite DDL fragments."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "data_type, expected_sql_type",
        [
            ("string", "TEXT"),
            ("text", "TEXT"),
            ("integer", "INTEGER"),
            ("float", "REAL"),
            ("boolean", "INTEGER"),
            ("datetime", "TEXT"),
            ("date", "TEXT"),
            ("binary", "BLOB"),
            ("json", "TEXT"),
            ("uuid", "TEXT"),
        ],
        ids=lambda v: v if isinstance(v, str) else None,
    )
    def test_sqlite_type_mapping(self, data_type, expected_sql_type):
        """Each Python-style type maps to correct SQLite type."""
        col = Column(name="col", data_type=data_type)
        sql = col.to_sql("sqlite")
        assert expected_sql_type in sql

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "data_type, expected_sql_type",
        [
            ("string", "VARCHAR"),
            ("text", "TEXT"),
            ("integer", "INTEGER"),
            ("float", "DOUBLE PRECISION"),
            ("boolean", "BOOLEAN"),
            ("datetime", "TIMESTAMP"),
            ("date", "DATE"),
            ("binary", "BYTEA"),
            ("json", "JSONB"),
            ("uuid", "UUID"),
        ],
        ids=lambda v: v if isinstance(v, str) else None,
    )
    def test_postgresql_type_mapping(self, data_type, expected_sql_type):
        """Each Python-style type maps to correct PostgreSQL type."""
        col = Column(name="col", data_type=data_type)
        sql = col.to_sql("postgresql")
        assert expected_sql_type in sql

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "data_type, expected_sql_type",
        [
            ("string", "VARCHAR"),
            ("text", "TEXT"),
            ("integer", "INT"),
            ("float", "DOUBLE"),
            ("boolean", "TINYINT(1)"),
            ("datetime", "DATETIME"),
            ("date", "DATE"),
            ("binary", "BLOB"),
            ("json", "JSON"),
            ("uuid", "CHAR(36)"),
        ],
        ids=lambda v: v if isinstance(v, str) else None,
    )
    def test_mysql_type_mapping(self, data_type, expected_sql_type):
        """Each Python-style type maps to correct MySQL type."""
        col = Column(name="col", data_type=data_type)
        sql = col.to_sql("mysql")
        assert expected_sql_type in sql


class TestColumnConstraints:
    """Test Column DDL constraint rendering."""

    @pytest.mark.unit
    def test_primary_key_sqlite(self):
        """PRIMARY KEY clause appears in SQLite column definition."""
        col = Column(name="id", data_type="integer", primary_key=True)
        sql = col.to_sql("sqlite")
        assert "PRIMARY KEY" in sql

    @pytest.mark.unit
    def test_primary_key_autoincrement_sqlite(self):
        """AUTOINCREMENT appears for SQLite primary key with auto_increment."""
        col = Column(name="id", data_type="integer", primary_key=True, auto_increment=True)
        sql = col.to_sql("sqlite")
        assert "AUTOINCREMENT" in sql

    @pytest.mark.unit
    def test_primary_key_auto_increment_mysql(self):
        """AUTO_INCREMENT appears for MySQL primary key with auto_increment."""
        col = Column(name="id", data_type="integer", primary_key=True, auto_increment=True)
        sql = col.to_sql("mysql")
        assert "AUTO_INCREMENT" in sql

    @pytest.mark.unit
    def test_not_null_constraint(self):
        """NOT NULL appears when nullable=False (non-PK column)."""
        col = Column(name="username", data_type="string", nullable=False)
        sql = col.to_sql("sqlite")
        assert "NOT NULL" in sql

    @pytest.mark.unit
    def test_primary_key_does_not_emit_not_null(self):
        """Primary key columns do not redundantly emit NOT NULL."""
        col = Column(name="id", data_type="integer", primary_key=True, nullable=False)
        sql = col.to_sql("sqlite")
        assert "PRIMARY KEY" in sql
        assert "NOT NULL" not in sql

    @pytest.mark.unit
    def test_unique_constraint(self):
        """UNIQUE appears on non-PK unique column."""
        col = Column(name="email", data_type="string", unique=True)
        sql = col.to_sql("sqlite")
        assert "UNIQUE" in sql

    @pytest.mark.unit
    def test_primary_key_does_not_emit_unique(self):
        """Primary key columns do not redundantly emit UNIQUE."""
        col = Column(name="id", data_type="integer", primary_key=True, unique=True)
        sql = col.to_sql("sqlite")
        assert "UNIQUE" not in sql

    @pytest.mark.unit
    def test_default_string_value(self):
        """DEFAULT with string value is single-quoted."""
        col = Column(name="status", data_type="string", default="active")
        sql = col.to_sql("sqlite")
        assert "DEFAULT 'active'" in sql

    @pytest.mark.unit
    def test_default_integer_value(self):
        """DEFAULT with integer value is unquoted."""
        col = Column(name="count", data_type="integer", default=0)
        sql = col.to_sql("sqlite")
        assert "DEFAULT 0" in sql

    @pytest.mark.unit
    def test_default_boolean_value(self):
        """DEFAULT with boolean maps to 1/0."""
        col = Column(name="active", data_type="boolean", default=True)
        sql = col.to_sql("sqlite")
        assert "DEFAULT 1" in sql

    @pytest.mark.unit
    def test_check_constraint(self):
        """CHECK clause appears when check is set."""
        col = Column(name="age", data_type="integer", check="age >= 0")
        sql = col.to_sql("sqlite")
        assert "CHECK (age >= 0)" in sql

    @pytest.mark.unit
    def test_string_length_varchar(self):
        """VARCHAR column with length renders as VARCHAR(N)."""
        col = Column(name="name", data_type="string", length=255)
        sql = col.to_sql("postgresql")
        assert "VARCHAR(255)" in sql

    @pytest.mark.unit
    def test_unknown_type_passes_through(self):
        """Unknown data_type is uppercased and passed through."""
        col = Column(name="special", data_type="BIGSERIAL")
        sql = col.to_sql("sqlite")
        assert "BIGSERIAL" in sql


# =============================================================================
# Index SQL Generation Tests
# =============================================================================

class TestIndexGeneration:
    """Test Index.to_sql() produces correct CREATE INDEX statements."""

    @pytest.mark.unit
    def test_simple_index(self):
        """Simple non-unique index creation."""
        idx = Index(name="idx_users_email", columns=["email"])
        sql = idx.to_sql("users", "sqlite")
        assert "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)" in sql

    @pytest.mark.unit
    def test_unique_index(self):
        """UNIQUE INDEX creation."""
        idx = Index(name="idx_unique_email", columns=["email"], unique=True)
        sql = idx.to_sql("users", "sqlite")
        assert "CREATE UNIQUE INDEX" in sql

    @pytest.mark.unit
    def test_composite_index(self):
        """Index on multiple columns."""
        idx = Index(name="idx_name_email", columns=["last_name", "first_name"])
        sql = idx.to_sql("users", "sqlite")
        assert "last_name, first_name" in sql

    @pytest.mark.unit
    def test_partial_index_sqlite(self):
        """Partial index with WHERE condition on SQLite."""
        idx = Index(name="idx_active", columns=["status"], condition="status = 'active'")
        sql = idx.to_sql("users", "sqlite")
        assert "WHERE status = 'active'" in sql

    @pytest.mark.unit
    def test_partial_index_postgresql(self):
        """Partial index with WHERE condition on PostgreSQL."""
        idx = Index(name="idx_active", columns=["status"], condition="status = 'active'")
        sql = idx.to_sql("users", "postgresql")
        assert "WHERE status = 'active'" in sql

    @pytest.mark.unit
    def test_partial_index_mysql_no_condition(self):
        """MySQL does not support partial indexes -- condition is omitted."""
        idx = Index(name="idx_active", columns=["status"], condition="status = 'active'")
        sql = idx.to_sql("users", "mysql")
        assert "WHERE" not in sql


# =============================================================================
# SchemaTable CREATE TABLE Tests
# =============================================================================

class TestSchemaTableDDL:
    """Test SchemaTable.to_sql() produces well-formed CREATE TABLE."""

    @pytest.mark.unit
    def test_create_table_basic(self):
        """Basic CREATE TABLE with two columns."""
        table = SchemaTable(
            name="users",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="name", data_type="string"),
            ],
        )
        sql = table.to_sql("sqlite")
        assert "CREATE TABLE IF NOT EXISTS users" in sql
        assert "id INTEGER PRIMARY KEY" in sql
        assert "name TEXT" in sql

    @pytest.mark.unit
    def test_create_table_with_foreign_key(self):
        """FOREIGN KEY constraint appears for column with foreign_key dict."""
        table = SchemaTable(
            name="orders",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(
                    name="user_id",
                    data_type="integer",
                    foreign_key={"table": "users", "column": "id"},
                ),
            ],
        )
        sql = table.to_sql("sqlite")
        assert "FOREIGN KEY (user_id) REFERENCES users(id)" in sql

    @pytest.mark.unit
    def test_create_table_with_extra_constraints(self):
        """Extra table-level constraints are rendered."""
        table = SchemaTable(
            name="items",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
            constraints=["CHECK (id > 0)"],
        )
        sql = table.to_sql("sqlite")
        assert "CHECK (id > 0)" in sql

    @pytest.mark.unit
    def test_table_to_dict_round_trip(self):
        """to_dict captures all column metadata."""
        table = SchemaTable(
            name="t",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="val", data_type="string", nullable=False, unique=True, default="x"),
            ],
            indexes=[Index(name="idx_val", columns=["val"], unique=True)],
            constraints=["CHECK (id > 0)"],
            description="test table",
        )
        d = table.to_dict()
        assert d["name"] == "t"
        assert len(d["columns"]) == 2
        assert d["columns"][1]["unique"] is True
        assert d["columns"][1]["default"] == "x"
        assert d["indexes"][0]["name"] == "idx_val"
        assert d["constraints"] == ["CHECK (id > 0)"]
        assert d["description"] == "test table"


# =============================================================================
# SchemaDefinition Full Schema Tests
# =============================================================================

class TestSchemaDefinitionSQL:
    """Test SchemaDefinition.to_sql() produces a full schema."""

    @pytest.mark.unit
    def test_full_schema_header(self):
        """Schema SQL contains header comment with name and version."""
        sd = SchemaDefinition(name="app", version="1.0.0", tables=[])
        sql = sd.to_sql("sqlite")
        assert "-- Schema: app v1.0.0" in sql

    @pytest.mark.unit
    def test_full_schema_includes_tables_and_indexes(self):
        """Schema SQL contains CREATE TABLE and CREATE INDEX for each table."""
        table = SchemaTable(
            name="users",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
            indexes=[Index(name="idx_id", columns=["id"])],
        )
        sd = SchemaDefinition(name="app", version="1.0.0", tables=[table])
        sql = sd.to_sql("sqlite")
        assert "CREATE TABLE IF NOT EXISTS users" in sql
        assert "CREATE INDEX IF NOT EXISTS idx_id ON users" in sql

    @pytest.mark.unit
    def test_schema_to_dict(self):
        """to_dict contains name, version, tables, created_at."""
        sd = SchemaDefinition(name="app", version="2.0.0", tables=[])
        d = sd.to_dict()
        assert d["name"] == "app"
        assert d["version"] == "2.0.0"
        assert "created_at" in d
        assert isinstance(d["tables"], list)


# =============================================================================
# SchemaGenerator Tests
# =============================================================================

class TestSchemaGenerator:
    """Test SchemaGenerator operations with tmp_path for filesystem isolation."""

    @pytest.mark.unit
    def test_create_table_stores_and_returns_id(self, tmp_path):
        """create_table stores table and returns an ID."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path), dialect="sqlite")
        table = SchemaTable(
            name="users",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        )
        table_id = gen.create_table(table)
        assert table_id == "table_users"
        assert table_id in gen._tables

    @pytest.mark.unit
    def test_create_table_saves_json(self, tmp_path):
        """create_table persists a JSON schema file."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        table = SchemaTable(
            name="items",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        )
        gen.create_table(table)
        schema_file = tmp_path / "database_schemas" / "table_items.json"
        assert schema_file.exists()
        data = json.loads(schema_file.read_text())
        assert data["name"] == "items"

    @pytest.mark.unit
    def test_create_table_from_dict(self, tmp_path):
        """create_table_from_dict builds a SchemaTable from dict."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        table_def = {
            "name": "products",
            "columns": [
                {"name": "id", "type": "integer", "primary_key": True},
                {"name": "name", "type": "string", "length": 100, "nullable": False},
                {"name": "price", "type": "float"},
            ],
            "indexes": [
                {"name": "idx_name", "columns": ["name"]},
            ],
            "description": "Product catalog",
        }
        table_id = gen.create_table_from_dict(table_def)
        assert table_id == "table_products"
        stored = gen._tables[table_id]
        assert len(stored.columns) == 3
        assert stored.columns[1].length == 100
        assert len(stored.indexes) == 1

    @pytest.mark.unit
    def test_generate_schema_sql(self, tmp_path):
        """generate_schema_sql produces SQL for all registered tables."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path), dialect="sqlite")
        gen.create_table(SchemaTable(
            name="a",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        ))
        gen.create_table(SchemaTable(
            name="b",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        ))
        sql = gen.generate_schema_sql("test_schema", "1.0.0")
        assert "CREATE TABLE IF NOT EXISTS a" in sql
        assert "CREATE TABLE IF NOT EXISTS b" in sql

    @pytest.mark.unit
    def test_export_schema_sql(self, tmp_path):
        """export_schema writes SQL file."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        gen.create_table(SchemaTable(
            name="t",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        ))
        out = tmp_path / "output.sql"
        result = gen.export_schema(str(out), format="sql")
        assert Path(result).exists()
        content = out.read_text()
        assert "CREATE TABLE" in content

    @pytest.mark.unit
    def test_export_schema_json(self, tmp_path):
        """export_schema writes JSON file."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        gen.create_table(SchemaTable(
            name="t",
            columns=[Column(name="id", data_type="integer", primary_key=True)],
        ))
        out = tmp_path / "output.json"
        gen.export_schema(str(out), format="json")
        data = json.loads(out.read_text())
        assert "tables" in data
        assert data["tables"][0]["name"] == "t"

    @pytest.mark.unit
    def test_export_schema_unsupported_format(self, tmp_path):
        """export_schema raises CodomyrmexError for unsupported format."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        with pytest.raises(CodomyrmexError, match="Unsupported format"):
            gen.export_schema(str(tmp_path / "out.xml"), format="xml")

    @pytest.mark.unit
    def test_list_migrations_empty(self, tmp_path):
        """list_migrations returns empty list initially."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        assert gen.list_migrations() == []


# =============================================================================
# Migration Generation (SchemaGenerator.generate_migration) Tests
# =============================================================================

class TestMigrationGeneration:
    """Test SchemaGenerator.generate_migration up/down SQL."""

    @pytest.mark.unit
    def test_generate_migration_create_table(self, tmp_path):
        """generate_migration with create_tables produces CREATE TABLE in up_sql."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path), dialect="sqlite")
        changes = {
            "name": "add_users",
            "create_tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer", "primary_key": True},
                        {"name": "name", "type": "string"},
                    ],
                }
            ],
        }
        migration = gen.generate_migration("add_users", "Add users table", changes)
        assert "CREATE TABLE IF NOT EXISTS users" in migration.up_sql
        assert "DROP TABLE IF EXISTS users" in migration.down_sql

    @pytest.mark.unit
    def test_generate_migration_add_columns(self, tmp_path):
        """generate_migration with add_columns produces ALTER TABLE ADD COLUMN."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "add_email",
            "add_columns": [
                {
                    "table": "users",
                    "columns": [{"name": "email", "data_type": "string"}],
                }
            ],
        }
        migration = gen.generate_migration("add_email", "Add email column", changes)
        assert "ALTER TABLE users ADD COLUMN" in migration.up_sql
        assert "email" in migration.up_sql
        # Down SQL drops the added column
        assert "ALTER TABLE users DROP COLUMN email" in migration.down_sql

    @pytest.mark.unit
    def test_generate_migration_drop_columns(self, tmp_path):
        """generate_migration with drop_columns produces ALTER TABLE DROP COLUMN."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "drop_cols",
            "drop_columns": [
                {"table": "users", "columns": ["email"]},
            ],
        }
        migration = gen.generate_migration("drop_cols", "Drop email", changes)
        assert "ALTER TABLE users DROP COLUMN email" in migration.up_sql

    @pytest.mark.unit
    def test_generate_migration_create_index(self, tmp_path):
        """generate_migration with create_indexes produces CREATE INDEX."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "add_idx",
            "create_indexes": [
                {"name": "idx_email", "columns": ["email"], "table": "users"},
            ],
        }
        migration = gen.generate_migration("add_idx", "Add email index", changes)
        assert "CREATE INDEX IF NOT EXISTS idx_email ON users" in migration.up_sql
        assert "DROP INDEX IF EXISTS idx_email" in migration.down_sql

    @pytest.mark.unit
    def test_generate_migration_drop_indexes(self, tmp_path):
        """generate_migration with drop_indexes produces DROP INDEX."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "drop_idx",
            "drop_indexes": ["idx_old"],
        }
        migration = gen.generate_migration("drop_idx", "Drop old index", changes)
        assert "DROP INDEX IF EXISTS idx_old" in migration.up_sql

    @pytest.mark.unit
    def test_generate_migration_drop_tables(self, tmp_path):
        """generate_migration with drop_tables produces DROP TABLE."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "cleanup",
            "drop_tables": ["old_table"],
        }
        migration = gen.generate_migration("cleanup", "Remove old table", changes)
        assert "DROP TABLE IF EXISTS old_table" in migration.up_sql

    @pytest.mark.unit
    def test_generate_migration_raw_sql(self, tmp_path):
        """generate_migration with raw_sql passes SQL through verbatim."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {
            "name": "custom",
            "raw_sql": ["INSERT INTO config VALUES ('key', 'value');"],
        }
        migration = gen.generate_migration("custom", "Custom SQL", changes)
        assert "INSERT INTO config VALUES ('key', 'value');" in migration.up_sql

    @pytest.mark.unit
    def test_migration_checksum_is_computed(self, tmp_path):
        """SchemaMigration computes a non-empty checksum from up_sql."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {"name": "test", "drop_tables": ["x"]}
        migration = gen.generate_migration("test", "test", changes)
        assert len(migration.checksum) == 16

    @pytest.mark.unit
    def test_migration_saved_to_files(self, tmp_path):
        """generate_migration saves JSON, up SQL, and down SQL files."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        changes = {"name": "test", "drop_tables": ["x"]}
        migration = gen.generate_migration("test", "test", changes)
        mid = migration.migration_id
        assert (tmp_path / "schema_migrations" / f"{mid}.json").exists()
        assert (tmp_path / "schema_migrations" / f"{mid}_up.sql").exists()
        assert (tmp_path / "schema_migrations" / f"{mid}_down.sql").exists()


# =============================================================================
# Schema Comparison Tests
# =============================================================================

class TestSchemaComparison:
    """Test SchemaGenerator.compare_schemas and drift reports."""

    @pytest.mark.unit
    def test_compare_identical_schemas(self, tmp_path):
        """Identical schemas produce no differences."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        schema = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "integer"}]},
            ]
        }
        diff = gen.compare_schemas(schema, schema)
        assert diff["tables_to_add"] == []
        assert diff["tables_to_remove"] == []
        assert diff["columns_to_add"] == []
        assert diff["columns_to_remove"] == []
        assert diff["columns_to_modify"] == []

    @pytest.mark.unit
    def test_compare_detects_new_table(self, tmp_path):
        """New table in target is listed in tables_to_add."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {"tables": []}
        target = {
            "tables": [
                {"name": "orders", "columns": [{"name": "id", "type": "integer"}]},
            ]
        }
        diff = gen.compare_schemas(current, target)
        assert len(diff["tables_to_add"]) == 1
        assert diff["tables_to_add"][0]["name"] == "orders"

    @pytest.mark.unit
    def test_compare_detects_removed_table(self, tmp_path):
        """Table in current but not target is listed in tables_to_remove."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {
            "tables": [
                {"name": "legacy", "columns": [{"name": "id", "type": "integer"}]},
            ]
        }
        target = {"tables": []}
        diff = gen.compare_schemas(current, target)
        assert "legacy" in diff["tables_to_remove"]

    @pytest.mark.unit
    def test_compare_detects_added_column(self, tmp_path):
        """New column in existing table is listed in columns_to_add."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "integer"}]},
            ]
        }
        target = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer"},
                        {"name": "email", "type": "string"},
                    ],
                },
            ]
        }
        diff = gen.compare_schemas(current, target)
        assert len(diff["columns_to_add"]) == 1
        assert diff["columns_to_add"][0]["table"] == "users"
        assert diff["columns_to_add"][0]["column"]["name"] == "email"

    @pytest.mark.unit
    def test_compare_detects_removed_column(self, tmp_path):
        """Column in current but not target is listed in columns_to_remove."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "integer"},
                        {"name": "old_col", "type": "string"},
                    ],
                },
            ]
        }
        target = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "integer"}]},
            ]
        }
        diff = gen.compare_schemas(current, target)
        assert len(diff["columns_to_remove"]) == 1
        assert diff["columns_to_remove"][0]["column"] == "old_col"

    @pytest.mark.unit
    def test_compare_detects_modified_column(self, tmp_path):
        """Column with changed type is listed in columns_to_modify."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {
            "tables": [
                {"name": "users", "columns": [{"name": "age", "type": "string"}]},
            ]
        }
        target = {
            "tables": [
                {"name": "users", "columns": [{"name": "age", "type": "integer"}]},
            ]
        }
        diff = gen.compare_schemas(current, target)
        assert len(diff["columns_to_modify"]) == 1
        assert diff["columns_to_modify"][0]["from"]["type"] == "string"
        assert diff["columns_to_modify"][0]["to"]["type"] == "integer"

    @pytest.mark.unit
    def test_drift_report_no_drift(self, tmp_path):
        """Drift report for identical schemas shows no drift."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        schema = {"tables": [{"name": "t", "columns": [{"name": "id", "type": "integer"}]}]}
        report = gen.get_schema_drift_report(schema, schema)
        assert report["drift_detected"] is False
        assert report["migration_needed"] is False
        assert "no changes needed" in report["recommendations"][0].lower()

    @pytest.mark.unit
    def test_drift_report_with_drift(self, tmp_path):
        """Drift report with changes shows drift_detected=True."""
        gen = SchemaGenerator(workspace_dir=str(tmp_path))
        current = {"tables": []}
        target = {"tables": [{"name": "new_t", "columns": [{"name": "id", "type": "integer"}]}]}
        report = gen.get_schema_drift_report(current, target)
        assert report["drift_detected"] is True
        assert report["migration_needed"] is True
        assert "new_t" in report["tables_added"]
        assert any("1 new table" in r for r in report["recommendations"])


# =============================================================================
# generate_schema_from_models Tests
# =============================================================================

class TestGenerateSchemaFromModels:
    """Test the module-level generate_schema_from_models function."""

    @pytest.mark.unit
    def test_generate_from_dict_models(self, tmp_path):
        """Dict-based models generate schema with correct table count."""
        models = [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "name", "type": "string"},
                ],
            },
            {
                "name": "posts",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "title", "type": "string"},
                ],
            },
        ]
        result = generate_schema_from_models(models, str(tmp_path))
        assert result["tables_generated"] == 2
        assert Path(result["schema_file"]).exists()


# =============================================================================
# Migration Models Tests (migration/models.py)
# =============================================================================

class TestMigrationModels:
    """Test MigrationStep, MigrationResult, Migration dataclasses."""

    @pytest.mark.unit
    def test_migration_step_run_up_with_fn(self):
        """MigrationStep.run_up calls up_fn and returns its result."""
        step = MigrationStep(id="s1", name="step1", up_fn=lambda: True)
        assert step.run_up() is True

    @pytest.mark.unit
    def test_migration_step_run_up_no_fn(self):
        """MigrationStep.run_up returns True when no up_fn is set."""
        step = MigrationStep(id="s1", name="step1")
        assert step.run_up() is True

    @pytest.mark.unit
    def test_migration_step_run_down_with_fn(self):
        """MigrationStep.run_down calls down_fn."""
        step = MigrationStep(id="s1", name="step1", down_fn=lambda: True)
        assert step.run_down() is True

    @pytest.mark.unit
    def test_migration_step_run_down_no_fn(self):
        """MigrationStep.run_down returns True when no down_fn is set."""
        step = MigrationStep(id="s1", name="step1")
        assert step.run_down() is True

    @pytest.mark.unit
    def test_migration_result_progress(self):
        """MigrationModelResult.progress computes fraction correctly."""
        r = MigrationModelResult(
            migration_id="m1",
            status=MigrationStatus.RUNNING,
            steps_completed=3,
            steps_total=10,
        )
        assert r.progress == pytest.approx(0.3)

    @pytest.mark.unit
    def test_migration_result_progress_zero_total(self):
        """MigrationModelResult.progress is 0.0 when steps_total is 0."""
        r = MigrationModelResult(
            migration_id="m1",
            status=MigrationStatus.PENDING,
            steps_total=0,
        )
        assert r.progress == 0.0

    @pytest.mark.unit
    def test_migration_result_to_dict(self):
        """MigrationModelResult.to_dict contains expected keys."""
        r = MigrationModelResult(
            migration_id="m1",
            status=MigrationStatus.COMPLETED,
            steps_completed=5,
            steps_total=5,
        )
        d = r.to_dict()
        assert d["migration_id"] == "m1"
        assert d["status"] == "completed"
        assert d["progress"] == 1.0
        assert "duration_seconds" in d

    @pytest.mark.unit
    def test_migration_add_step(self):
        """Migration.add_step appends and returns self for chaining."""
        m = MigrationModel(id="m1", name="test", version="1.0")
        step = MigrationStep(id="s1", name="step1")
        result = m.add_step(step)
        assert result is m
        assert len(m.steps) == 1

    @pytest.mark.unit
    def test_migration_add_simple_step(self):
        """Migration.add_simple_step creates and adds a step with functions."""
        m = MigrationModel(id="m1", name="test", version="1.0")
        m.add_simple_step(id="s1", name="step1", up_fn=lambda: True)
        assert len(m.steps) == 1
        assert m.steps[0].id == "s1"


# =============================================================================
# MigrationRunner Tests
# =============================================================================

class TestMigrationRunner:
    """Test MigrationRunner.run, rollback, and completed tracking."""

    @pytest.mark.unit
    def test_runner_run_up_success(self):
        """Runner executes all steps UP and marks completed."""
        runner = MigrationRunner()
        m = MigrationModel(id="m1", name="test", version="1.0")
        m.add_simple_step(id="s1", name="step1", up_fn=lambda: True)
        m.add_simple_step(id="s2", name="step2", up_fn=lambda: True)

        result = runner.run(m)
        assert result.status == MigrationStatus.COMPLETED
        assert result.steps_completed == 2
        assert runner.is_completed("m1")

    @pytest.mark.unit
    def test_runner_run_up_failure_stops(self):
        """Runner stops on first failing step."""
        runner = MigrationRunner()
        m = MigrationModel(id="m1", name="test", version="1.0")
        m.add_simple_step(id="s1", name="ok", up_fn=lambda: True)
        m.add_simple_step(id="s2", name="fail", up_fn=lambda: False)
        m.add_simple_step(id="s3", name="never", up_fn=lambda: True)

        result = runner.run(m)
        assert result.status == MigrationStatus.FAILED
        assert result.steps_completed == 1
        assert not runner.is_completed("m1")

    @pytest.mark.unit
    def test_runner_rollback(self):
        """Runner rollback runs steps in reverse and removes from completed."""
        runner = MigrationRunner()
        m = MigrationModel(id="m1", name="test", version="1.0")
        m.add_simple_step(id="s1", name="step1", up_fn=lambda: True, down_fn=lambda: True)
        m.add_simple_step(id="s2", name="step2", up_fn=lambda: True, down_fn=lambda: True)

        runner.run(m)
        assert runner.is_completed("m1")

        result = runner.rollback(m)
        assert result.status == MigrationStatus.COMPLETED
        assert not runner.is_completed("m1")

    @pytest.mark.unit
    def test_runner_get_completed(self):
        """get_completed returns list of all completed migration IDs."""
        runner = MigrationRunner()
        m1 = MigrationModel(id="m1", name="t1", version="1.0")
        m1.add_simple_step(id="s1", name="s", up_fn=lambda: True)
        m2 = MigrationModel(id="m2", name="t2", version="1.0")
        m2.add_simple_step(id="s2", name="s", up_fn=lambda: True)

        runner.run(m1)
        runner.run(m2)
        assert set(runner.get_completed()) == {"m1", "m2"}


# =============================================================================
# DataMigrator and Transformer Tests
# =============================================================================

class TestDataTransformers:
    """Test FieldRenameTransformer, FieldTypeTransformer, CompositeTransformer."""

    @pytest.mark.unit
    def test_field_rename_transformer(self):
        """FieldRenameTransformer renames keys according to mapping."""
        t = FieldRenameTransformer({"old_name": "new_name"})
        result = t.transform({"old_name": "value", "other": 42})
        assert "new_name" in result
        assert "old_name" not in result
        assert result["other"] == 42

    @pytest.mark.unit
    def test_field_type_transformer(self):
        """FieldTypeTransformer converts field types."""
        t = FieldTypeTransformer({"count": int, "ratio": float})
        result = t.transform({"count": "42", "ratio": "3.14", "name": "test"})
        assert result["count"] == 42
        assert result["ratio"] == pytest.approx(3.14)
        assert result["name"] == "test"

    @pytest.mark.unit
    def test_field_type_transformer_invalid_conversion(self):
        """FieldTypeTransformer silently skips unconvertible values."""
        t = FieldTypeTransformer({"count": int})
        result = t.transform({"count": "not_a_number"})
        # Original value preserved on failure
        assert result["count"] == "not_a_number"

    @pytest.mark.unit
    def test_composite_transformer(self):
        """CompositeTransformer applies transformers in sequence."""
        t1 = FieldRenameTransformer({"old": "new"})
        t2 = FieldTypeTransformer({"new": int})
        composite = CompositeTransformer([t1, t2])
        result = composite.transform({"old": "123"})
        assert result["new"] == 123

    @pytest.mark.unit
    def test_data_migrator_batch(self):
        """DataMigrator.migrate transforms a list of records."""
        migrator = DataMigrator()
        migrator.add_transformer(FieldRenameTransformer({"x": "y"}))
        records = [{"x": 1}, {"x": 2}, {"x": 3}]
        result = migrator.migrate(records)
        assert all("y" in r for r in result)
        assert [r["y"] for r in result] == [1, 2, 3]

    @pytest.mark.unit
    def test_data_migrator_single(self):
        """DataMigrator.migrate_single transforms one record."""
        migrator = DataMigrator()
        migrator.add_transformer(FieldTypeTransformer({"age": int}))
        result = migrator.migrate_single({"age": "25", "name": "test"})
        assert result["age"] == 25

    @pytest.mark.unit
    def test_data_migrator_chaining(self):
        """DataMigrator.add_transformer returns self for chaining."""
        migrator = DataMigrator()
        result = migrator.add_transformer(FieldRenameTransformer({}))
        assert result is migrator


# =============================================================================
# MigrationManager with In-Memory SQLite Tests
# =============================================================================

class TestMigrationManagerSQLite:
    """Test MigrationManager end-to-end with in-memory SQLite."""

    @pytest.mark.unit
    def test_create_migration(self, tmp_path):
        """create_migration stores migration and saves JSON file."""
        mm = MigrationManager(workspace_dir=str(tmp_path))
        m = mm.create_migration(
            name="create users",
            description="Create users table",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        assert m.id in mm._migrations
        assert m.name == "create users"
        assert m.checksum  # non-empty
        # JSON file saved
        json_files = list((tmp_path / "migrations").glob("*.json"))
        assert len(json_files) == 1

    @pytest.mark.unit
    def test_apply_migration_to_sqlite(self, tmp_path):
        """apply_migration executes SQL against in-memory SQLite via connector."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="Create users",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        result = mm.apply_migration(m.id)
        assert result.success is True
        assert result.statements_executed >= 1
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_dry_run(self, tmp_path):
        """apply_migration with dry_run=True does not execute SQL."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
        )
        result = mm.apply_migration(m.id, dry_run=True)
        assert result.success is True
        assert "Dry run" in (result.error_message or "")

        # Table should NOT exist
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is None
        conn.close()
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_idempotent(self, tmp_path):
        """Applying same migration twice returns already-applied result."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
        )
        mm.apply_migration(m.id)
        result = mm.apply_migration(m.id)
        assert result.success is True
        assert "Already applied" in (result.error_message or "")
        mm.close()

    @pytest.mark.unit
    def test_rollback_migration(self, tmp_path):
        """rollback_migration reverts a previously applied migration."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="create table",
            description="test",
            sql="CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);",
            rollback_sql="DROP TABLE users;",
        )
        mm.apply_migration(m.id)
        result = mm.rollback_migration(m.id)
        assert result.success is True

        # users table should be gone
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is None
        conn.close()
        mm.close()

    @pytest.mark.unit
    def test_dependency_check_blocks_migration(self, tmp_path):
        """Migration with unmet dependency raises CodomyrmexError."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="dependent",
            description="depends on missing",
            sql="SELECT 1;",
            dependencies=["nonexistent_migration"],
        )
        with pytest.raises(CodomyrmexError, match="Dependency migration not applied"):
            mm.apply_migration(m.id)
        mm.close()

    @pytest.mark.unit
    def test_apply_migration_not_found(self, tmp_path):
        """Applying a non-existent migration ID raises CodomyrmexError."""
        mm = MigrationManager(workspace_dir=str(tmp_path))
        with pytest.raises(CodomyrmexError, match="Migration not found"):
            mm.apply_migration("nonexistent")

    @pytest.mark.unit
    def test_rollback_not_applied_raises(self, tmp_path):
        """Rolling back a migration that was never applied raises error."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="not applied",
            description="test",
            sql="SELECT 1;",
            rollback_sql="SELECT 1;",
        )
        with pytest.raises(CodomyrmexError, match="Migration not applied"):
            mm.rollback_migration(m.id)
        mm.close()

    @pytest.mark.unit
    def test_rollback_no_rollback_sql_raises(self, tmp_path):
        """Rolling back a migration without rollback_sql raises error."""
        db_path = str(tmp_path / "test.db")
        mm = MigrationManager(
            workspace_dir=str(tmp_path),
            database_url=f"sqlite:///{db_path}",
        )
        m = mm.create_migration(
            name="no rollback",
            description="test",
            sql="CREATE TABLE t (id INTEGER);",
        )
        mm.apply_migration(m.id)
        with pytest.raises(CodomyrmexError, match="No rollback SQL defined"):
            mm.rollback_migration(m.id)
        mm.close()


# =============================================================================
# DatabaseConnector Tests
# =============================================================================

class TestDatabaseConnector:
    """Test DatabaseConnector URL parsing and SQLite operations."""

    @pytest.mark.unit
    def test_parse_sqlite_url(self, tmp_path):
        """SQLite URL is parsed correctly."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        assert connector._db_type == "sqlite"

    @pytest.mark.unit
    def test_parse_postgresql_url(self):
        """PostgreSQL URL is parsed correctly."""
        connector = DatabaseConnector("postgresql://user:pass@localhost:5432/mydb")
        assert connector._db_type == "postgresql"

    @pytest.mark.unit
    def test_parse_mysql_url(self):
        """MySQL URL is parsed correctly."""
        connector = DatabaseConnector("mysql://user:pass@localhost:3306/mydb")
        assert connector._db_type == "mysql"

    @pytest.mark.unit
    def test_parse_unsupported_url(self):
        """Unsupported URL scheme raises CodomyrmexError."""
        with pytest.raises(CodomyrmexError, match="Unsupported database URL"):
            DatabaseConnector("mongodb://localhost/db")

    @pytest.mark.unit
    def test_execute_without_connection_raises(self, tmp_path):
        """Execute without connecting raises CodomyrmexError."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        with pytest.raises(CodomyrmexError, match="Not connected"):
            connector.execute("SELECT 1")

    @pytest.mark.unit
    def test_connect_and_execute(self, tmp_path):
        """Connect to SQLite and execute a simple query."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        rows, cursor = connector.execute("SELECT 1 AS val")
        assert cursor.fetchone()[0] == 1
        connector.disconnect()

    @pytest.mark.unit
    def test_execute_script(self, tmp_path):
        """execute_script runs multiple statements and counts them."""
        db_path = str(tmp_path / "test.db")
        connector = DatabaseConnector(f"sqlite:///{db_path}")
        connector.connect()
        script = (
            "CREATE TABLE t (id INTEGER PRIMARY KEY);\n"
            "INSERT INTO t VALUES (1);\n"
            "INSERT INTO t VALUES (2);\n"
        )
        total_rows, stmts = connector.execute_script(script)
        connector.commit()
        assert stmts == 3

        _, cursor = connector.execute("SELECT COUNT(*) FROM t")
        assert cursor.fetchone()[0] == 2
        connector.disconnect()


# =============================================================================
# SchemaMigration Dataclass Tests
# =============================================================================

class TestSchemaMigrationDataclass:
    """Test the SchemaMigration dataclass from schema_generator."""

    @pytest.mark.unit
    def test_checksum_auto_computed(self):
        """Checksum is auto-computed from up_sql in __post_init__."""
        m = SchemaMigration(
            migration_id="m1",
            name="test",
            description="test migration",
            up_sql="CREATE TABLE t (id INT);",
            down_sql="DROP TABLE t;",
        )
        assert len(m.checksum) == 16

    @pytest.mark.unit
    def test_checksum_not_overwritten_if_provided(self):
        """Pre-supplied checksum is preserved."""
        m = SchemaMigration(
            migration_id="m1",
            name="test",
            description="test",
            up_sql="SELECT 1;",
            down_sql="SELECT 1;",
            checksum="custom_checksum_",
        )
        assert m.checksum == "custom_checksum_"

    @pytest.mark.unit
    def test_dependencies_default_empty(self):
        """Dependencies default to empty list."""
        m = SchemaMigration(
            migration_id="m1",
            name="test",
            description="test",
            up_sql="SELECT 1;",
            down_sql="SELECT 1;",
        )
        assert m.dependencies == []


# =============================================================================
# TYPE_MAPPINGS Coverage
# =============================================================================

class TestTypeMappings:
    """Verify TYPE_MAPPINGS contains all expected dialects and types."""

    @pytest.mark.unit
    def test_all_dialects_present(self):
        """All three dialects are defined."""
        assert "sqlite" in TYPE_MAPPINGS
        assert "postgresql" in TYPE_MAPPINGS
        assert "mysql" in TYPE_MAPPINGS

    @pytest.mark.unit
    @pytest.mark.parametrize("dialect", ["sqlite", "postgresql", "mysql"])
    def test_all_base_types_mapped(self, dialect):
        """All 10 base types are mapped for each dialect."""
        expected_types = {
            "string", "text", "integer", "float", "boolean",
            "datetime", "date", "binary", "json", "uuid",
        }
        assert expected_types.issubset(set(TYPE_MAPPINGS[dialect].keys()))
