"""Comprehensive tests for database_management.schema_generator — zero-mock.

Covers: Column, Index, SchemaTable, SchemaMigration, SchemaDefinition (SQL generation
for sqlite/postgresql/mysql), and SchemaGenerator (table creation, migration generation).
"""

import tempfile


from codomyrmex.database_management.schema_generator import (
    Column,
    Index,
    SchemaDefinition,
    SchemaGenerator,
    SchemaMigration,
    SchemaTable,
    TYPE_MAPPINGS,
)


# ---------------------------------------------------------------------------
# TYPE_MAPPINGS
# ---------------------------------------------------------------------------


class TestTypeMappings:
    def test_sqlite_has_all_types(self):
        assert "string" in TYPE_MAPPINGS["sqlite"]
        assert "integer" in TYPE_MAPPINGS["sqlite"]
        assert "boolean" in TYPE_MAPPINGS["sqlite"]

    def test_postgresql_has_all_types(self):
        assert "string" in TYPE_MAPPINGS["postgresql"]
        assert "uuid" in TYPE_MAPPINGS["postgresql"]

    def test_mysql_has_all_types(self):
        assert "string" in TYPE_MAPPINGS["mysql"]
        assert "json" in TYPE_MAPPINGS["mysql"]


# ---------------------------------------------------------------------------
# Column
# ---------------------------------------------------------------------------


class TestColumn:
    def test_basic_column(self):
        col = Column(name="id", data_type="integer", primary_key=True)
        assert col.name == "id"
        assert col.primary_key is True

    def test_to_sql_sqlite(self):
        col = Column(name="name", data_type="string", nullable=False)
        sql = col.to_sql(dialect="sqlite")
        assert "name" in sql
        assert "TEXT" in sql
        assert "NOT NULL" in sql

    def test_to_sql_postgresql(self):
        col = Column(name="email", data_type="string", unique=True)
        sql = col.to_sql(dialect="postgresql")
        assert "VARCHAR" in sql or "TEXT" in sql
        assert "UNIQUE" in sql

    def test_primary_key_in_sql(self):
        col = Column(name="id", data_type="integer", primary_key=True, auto_increment=True)
        sql = col.to_sql(dialect="sqlite")
        assert "PRIMARY KEY" in sql

    def test_foreign_key(self):
        col = Column(
            name="user_id",
            data_type="integer",
            foreign_key={"table": "users", "column": "id"},
        )
        sql = col.to_sql(dialect="sqlite")
        assert "user_id" in sql

    def test_default_value(self):
        col = Column(name="active", data_type="boolean", default=True)
        sql = col.to_sql(dialect="sqlite")
        assert "DEFAULT" in sql or "active" in sql

    def test_nullable_column(self):
        col = Column(name="bio", data_type="text", nullable=True)
        sql = col.to_sql(dialect="sqlite")
        assert "NOT NULL" not in sql


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------


class TestIndex:
    def test_basic_index(self):
        idx = Index(name="idx_email", columns=["email"])
        sql = idx.to_sql(table_name="users")
        assert "idx_email" in sql
        assert "email" in sql

    def test_unique_index(self):
        idx = Index(name="idx_unique_email", columns=["email"], unique=True)
        sql = idx.to_sql(table_name="users")
        assert "UNIQUE" in sql

    def test_multi_column_index(self):
        idx = Index(name="idx_name_email", columns=["first_name", "last_name"])
        sql = idx.to_sql(table_name="users")
        assert "first_name" in sql
        assert "last_name" in sql


# ---------------------------------------------------------------------------
# SchemaTable
# ---------------------------------------------------------------------------


class TestSchemaTable:
    def test_create_table(self):
        table = SchemaTable(
            name="users",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="name", data_type="string", nullable=False),
            ],
        )
        assert table.name == "users"
        assert len(table.columns) == 2

    def test_to_sql(self):
        table = SchemaTable(
            name="products",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="title", data_type="string"),
                Column(name="price", data_type="float"),
            ],
        )
        sql = table.to_sql(dialect="sqlite")
        assert "CREATE TABLE" in sql
        assert "products" in sql

    def test_to_sql_postgresql(self):
        table = SchemaTable(
            name="events",
            columns=[
                Column(name="id", data_type="uuid", primary_key=True),
                Column(name="data", data_type="json"),
            ],
        )
        sql = table.to_sql(dialect="postgresql")
        assert "events" in sql

    def test_to_dict(self):
        table = SchemaTable(
            name="items",
            columns=[Column(name="id", data_type="integer")],
            description="Item table",
        )
        d = table.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "items"
        assert "columns" in d

    def test_with_indexes(self):
        table = SchemaTable(
            name="users",
            columns=[
                Column(name="id", data_type="integer", primary_key=True),
                Column(name="email", data_type="string"),
            ],
            indexes=[Index(name="idx_email", columns=["email"], unique=True)],
        )
        sql = table.to_sql()
        assert "users" in sql


# ---------------------------------------------------------------------------
# SchemaMigration
# ---------------------------------------------------------------------------


class TestSchemaMigration:
    def test_create_migration(self):
        m = SchemaMigration(
            migration_id="001",
            name="add_users",
            description="Create users table",
            up_sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
            down_sql="DROP TABLE users;",
        )
        assert m.migration_id == "001"
        assert m.checksum  # auto-calculated

    def test_checksum_changes_with_sql(self):
        m1 = SchemaMigration(
            migration_id="001",
            name="a",
            description="d",
            up_sql="CREATE TABLE a (id INT);",
            down_sql="DROP TABLE a;",
        )
        m2 = SchemaMigration(
            migration_id="001",
            name="a",
            description="d",
            up_sql="CREATE TABLE b (id INT);",
            down_sql="DROP TABLE b;",
        )
        assert m1.checksum != m2.checksum


# ---------------------------------------------------------------------------
# SchemaDefinition
# ---------------------------------------------------------------------------


class TestSchemaDefinition:
    def test_create_schema(self):
        schema = SchemaDefinition(name="mydb", version="1.0")
        assert schema.name == "mydb"
        assert len(schema.tables) == 0

    def test_to_sql(self):
        schema = SchemaDefinition(
            name="mydb",
            version="1.0",
            tables=[
                SchemaTable(
                    name="users",
                    columns=[Column(name="id", data_type="integer", primary_key=True)],
                ),
            ],
        )
        sql = schema.to_sql(dialect="sqlite")
        assert "CREATE TABLE" in sql
        assert "users" in sql

    def test_to_dict(self):
        schema = SchemaDefinition(name="testdb", version="2.0")
        d = schema.to_dict()
        assert d["name"] == "testdb"
        assert d["version"] == "2.0"


# ---------------------------------------------------------------------------
# SchemaGenerator
# ---------------------------------------------------------------------------


class TestSchemaGenerator:
    def test_init_with_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir)
            assert gen.dialect == "sqlite"

    def test_init_with_dialect(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir, dialect="postgresql")
            assert gen.dialect == "postgresql"

    def test_create_table(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir)
            table = SchemaTable(
                name="test_table",
                columns=[
                    Column(name="id", data_type="integer", primary_key=True),
                    Column(name="value", data_type="string"),
                ],
            )
            table_id = gen.create_table(table)
            assert table_id is not None

    def test_create_table_from_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir)
            table_def = {
                "name": "products",
                "columns": [
                    {"name": "id", "data_type": "integer", "primary_key": True},
                    {"name": "title", "data_type": "string"},
                    {"name": "price", "data_type": "float", "nullable": False},
                ],
            }
            table_id = gen.create_table_from_dict(table_def)
            assert table_id is not None

    def test_generate_migration(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir)
            changes = {
                "add_tables": [
                    {
                        "name": "logs",
                        "columns": [
                            {"name": "id", "data_type": "integer", "primary_key": True},
                            {"name": "message", "data_type": "text"},
                        ],
                    }
                ]
            }
            migration = gen.generate_migration(
                name="add_logs", description="Add logs table", changes=changes
            )
            assert migration is not None
            assert migration.name == "add_logs"
            assert len(migration.up_sql) > 0

    def test_list_migrations(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = SchemaGenerator(workspace_dir=tmpdir)
            migrations = gen.list_migrations()
            assert isinstance(migrations, list)
