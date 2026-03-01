"""
Tests for database_management operations: migration generation (up/down SQL),
schema comparison, schema drift reports, migration models (MigrationStep,
MigrationResult, Migration), MigrationRunner execution, and DataMigrator
with transformers (rename, type-convert, composite).

Split from test_database_core.py to reduce file size.
"""

import json

import pytest

from codomyrmex.database_management.schema_generator import (
    Column,
    Index,
    SchemaGenerator,
    SchemaTable,
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
