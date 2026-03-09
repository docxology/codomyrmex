"""Tests for database_management.migration.models."""

from codomyrmex.database_management.migration.models import (
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


class TestMigrationStatus:
    def test_all_values(self):
        values = {s.value for s in MigrationStatus}
        assert "pending" in values
        assert "running" in values
        assert "completed" in values
        assert "failed" in values
        assert "rolled_back" in values


class TestMigrationDirection:
    def test_values(self):
        assert MigrationDirection.UP.value == "up"
        assert MigrationDirection.DOWN.value == "down"


class TestMigrationStep:
    def test_defaults(self):
        step = MigrationStep(id="s1", name="Create users table")
        assert step.id == "s1"
        assert step.up_fn is None
        assert step.down_fn is None
        assert step.dependencies == []

    def test_run_up_no_fn_returns_true(self):
        step = MigrationStep(id="s1", name="step")
        assert step.run_up() is True

    def test_run_down_no_fn_returns_true(self):
        step = MigrationStep(id="s1", name="step")
        assert step.run_down() is True

    def test_run_up_with_fn(self):
        called = []
        step = MigrationStep(
            id="s1", name="step", up_fn=lambda: called.append(1) or True
        )
        result = step.run_up()
        assert result is True
        assert len(called) == 1

    def test_run_down_with_fn(self):
        results = []
        step = MigrationStep(
            id="s1", name="step", down_fn=lambda: results.append(1) or False
        )
        result = step.run_down()
        assert result is False

    def test_independent_default_dependencies(self):
        s1 = MigrationStep(id="a", name="a")
        s2 = MigrationStep(id="b", name="b")
        s1.dependencies.append("x")
        assert s2.dependencies == []


class TestMigrationResult:
    def test_construction(self):
        r = MigrationResult(migration_id="m1", status=MigrationStatus.PENDING)
        assert r.migration_id == "m1"
        assert r.steps_completed == 0
        assert r.steps_total == 0
        assert r.error is None

    def test_progress_zero_total(self):
        r = MigrationResult(
            migration_id="m1", status=MigrationStatus.PENDING, steps_total=0
        )
        assert r.progress == 0.0

    def test_progress_calculation(self):
        r = MigrationResult(
            migration_id="m1",
            status=MigrationStatus.RUNNING,
            steps_completed=3,
            steps_total=10,
        )
        assert r.progress == 0.3

    def test_progress_complete(self):
        r = MigrationResult(
            migration_id="m1",
            status=MigrationStatus.COMPLETED,
            steps_completed=5,
            steps_total=5,
        )
        assert r.progress == 1.0

    def test_duration_seconds_positive(self):
        r = MigrationResult(migration_id="m1", status=MigrationStatus.RUNNING)
        import time

        time.sleep(0.01)
        assert r.duration_seconds > 0

    def test_to_dict_keys(self):
        r = MigrationResult(
            migration_id="m1",
            status=MigrationStatus.COMPLETED,
            steps_completed=4,
            steps_total=4,
        )
        d = r.to_dict()
        assert d["migration_id"] == "m1"
        assert d["status"] == "completed"
        assert d["progress"] == 1.0
        assert d["steps_completed"] == 4
        assert d["steps_total"] == 4
        assert "duration_seconds" in d


class TestMigration:
    def test_construction(self):
        m = Migration(id="m1", name="Initial schema", version="1.0.0")
        assert m.id == "m1"
        assert m.version == "1.0.0"
        assert m.steps == []

    def test_add_step_chainable(self):
        m = Migration(id="m1", name="test", version="1.0")
        step = MigrationStep(id="s1", name="step")
        result = m.add_step(step)
        assert result is m
        assert len(m.steps) == 1

    def test_add_simple_step(self):
        m = Migration(id="m1", name="test", version="1.0")
        m.add_simple_step(id="s1", name="step", up_fn=lambda: True)
        assert len(m.steps) == 1
        assert m.steps[0].up_fn() is True

    def test_add_simple_step_chainable(self):
        m = Migration(id="m1", name="test", version="1.0")
        result = m.add_simple_step(
            id="s1", name="step1", up_fn=lambda: True
        ).add_simple_step(id="s2", name="step2", up_fn=lambda: True)
        assert result is m
        assert len(m.steps) == 2

    def test_independent_default_steps(self):
        m1 = Migration(id="a", name="a", version="1.0")
        m2 = Migration(id="b", name="b", version="1.0")
        m1.steps.append(MigrationStep(id="s1", name="s1"))
        assert len(m2.steps) == 0


class TestFieldRenameTransformer:
    def test_renames_field(self):
        t = FieldRenameTransformer({"old_name": "new_name"})
        result = t.transform({"old_name": "value", "other": "x"})
        assert "new_name" in result
        assert "old_name" not in result
        assert result["new_name"] == "value"
        assert result["other"] == "x"

    def test_no_mapping_passthrough(self):
        t = FieldRenameTransformer({})
        data = {"key": "val"}
        result = t.transform(data)
        assert result == data

    def test_multiple_renames(self):
        t = FieldRenameTransformer({"a": "x", "b": "y"})
        result = t.transform({"a": 1, "b": 2})
        assert result == {"x": 1, "y": 2}


class TestFieldTypeTransformer:
    def test_converts_int(self):
        t = FieldTypeTransformer({"age": int})
        result = t.transform({"age": "42", "name": "Alice"})
        assert result["age"] == 42
        assert isinstance(result["age"], int)

    def test_converts_float(self):
        t = FieldTypeTransformer({"score": float})
        result = t.transform({"score": "3.14"})
        assert result["score"] == 3.14

    def test_skips_missing_field(self):
        t = FieldTypeTransformer({"missing": int})
        result = t.transform({"other": "val"})
        assert result == {"other": "val"}

    def test_handles_conversion_error_gracefully(self):
        t = FieldTypeTransformer({"val": int})
        result = t.transform({"val": "not-a-number"})
        # Should not raise; logs warning and leaves original or skips
        assert "val" in result


class TestCompositeTransformer:
    def test_applies_in_sequence(self):
        rename = FieldRenameTransformer({"old": "new"})
        convert = FieldTypeTransformer({"new": int})
        composite = CompositeTransformer([rename, convert])
        result = composite.transform({"old": "42"})
        assert result["new"] == 42

    def test_empty_transformers_passthrough(self):
        composite = CompositeTransformer([])
        data = {"key": "val"}
        result = composite.transform(data)
        assert result == data

    def test_is_data_transformer(self):
        composite = CompositeTransformer([])
        assert isinstance(composite, DataTransformer)
