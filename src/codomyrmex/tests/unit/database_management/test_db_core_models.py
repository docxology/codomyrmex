"""
Tests for database_management schema models: column SQL generation, DDL output,
column type mapping, primary/foreign keys, indexes, schema tables, schema
definitions, schema generator, generate_schema_from_models, SchemaMigration
dataclass, and TYPE_MAPPINGS coverage.

Split from test_database_core.py to reduce file size.
"""

import json
from pathlib import Path

import pytest

from codomyrmex.database_management.schema_generator import (
    TYPE_MAPPINGS,
    Column,
    Index,
    SchemaDefinition,
    SchemaGenerator,
    SchemaMigration,
    SchemaTable,
    generate_schema_from_models,
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
