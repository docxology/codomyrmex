"""Unit tests for migration module."""
import pytest


@pytest.mark.unit
class TestMigrationImports:
    """Test suite for migration module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import migration
        assert migration is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.migration import __all__
        expected_exports = [
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
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestMigrationStatus:
    """Test suite for MigrationStatus enum."""

    def test_migration_status_values(self):
        """Verify all migration statuses are available."""
        from codomyrmex.migration import MigrationStatus

        assert MigrationStatus.PENDING.value == "pending"
        assert MigrationStatus.RUNNING.value == "running"
        assert MigrationStatus.COMPLETED.value == "completed"
        assert MigrationStatus.FAILED.value == "failed"
        assert MigrationStatus.ROLLED_BACK.value == "rolled_back"


@pytest.mark.unit
class TestMigrationDirection:
    """Test suite for MigrationDirection enum."""

    def test_migration_direction_values(self):
        """Verify all migration directions are available."""
        from codomyrmex.migration import MigrationDirection

        assert MigrationDirection.UP.value == "up"
        assert MigrationDirection.DOWN.value == "down"


@pytest.mark.unit
class TestMigrationStep:
    """Test suite for MigrationStep dataclass."""

    def test_step_creation(self):
        """Verify MigrationStep can be created."""
        from codomyrmex.migration import MigrationStep

        step = MigrationStep(
            id="add_column",
            name="Add email column",
            description="Adds email column to users table",
        )

        assert step.id == "add_column"
        assert step.name == "Add email column"

    def test_step_run_up(self):
        """Verify step up execution."""
        from codomyrmex.migration import MigrationStep

        executed = [False]

        def up_fn():
            executed[0] = True
            return True

        step = MigrationStep(id="test", name="Test", up_fn=up_fn)
        result = step.run_up()

        assert result is True
        assert executed[0] is True

    def test_step_run_down(self):
        """Verify step down execution."""
        from codomyrmex.migration import MigrationStep

        executed = [False]

        def down_fn():
            executed[0] = True
            return True

        step = MigrationStep(id="test", name="Test", down_fn=down_fn)
        result = step.run_down()

        assert result is True
        assert executed[0] is True

    def test_step_without_functions(self):
        """Verify step without functions returns True."""
        from codomyrmex.migration import MigrationStep

        step = MigrationStep(id="empty", name="Empty Step")

        assert step.run_up() is True
        assert step.run_down() is True


@pytest.mark.unit
class TestMigrationResult:
    """Test suite for MigrationResult dataclass."""

    def test_result_creation(self):
        """Verify MigrationResult can be created."""
        from codomyrmex.migration import MigrationResult, MigrationStatus

        result = MigrationResult(
            migration_id="v1_to_v2",
            status=MigrationStatus.COMPLETED,
            steps_completed=5,
            steps_total=5,
        )

        assert result.migration_id == "v1_to_v2"
        assert result.status == MigrationStatus.COMPLETED

    def test_result_progress(self):
        """Verify progress calculation."""
        from codomyrmex.migration import MigrationResult, MigrationStatus

        result = MigrationResult(
            migration_id="test",
            status=MigrationStatus.RUNNING,
            steps_completed=3,
            steps_total=10,
        )

        assert result.progress == 0.3

    def test_result_to_dict(self):
        """Verify result serialization."""
        from codomyrmex.migration import MigrationResult, MigrationStatus

        result = MigrationResult(
            migration_id="test",
            status=MigrationStatus.COMPLETED,
            steps_completed=2,
            steps_total=2,
        )

        data = result.to_dict()
        assert data["migration_id"] == "test"
        assert data["status"] == "completed"
        assert data["progress"] == 1.0


@pytest.mark.unit
class TestMigration:
    """Test suite for Migration dataclass."""

    def test_migration_creation(self):
        """Verify Migration can be created."""
        from codomyrmex.migration import Migration

        migration = Migration(
            id="v1_to_v2",
            name="Upgrade to V2",
            version="2.0",
            description="Major version upgrade",
        )

        assert migration.id == "v1_to_v2"
        assert migration.version == "2.0"
        assert len(migration.steps) == 0

    def test_migration_add_step(self):
        """Verify step addition."""
        from codomyrmex.migration import Migration, MigrationStep

        migration = Migration(id="test", name="Test", version="1.0")

        step = MigrationStep(id="s1", name="Step 1")
        migration.add_step(step)

        assert len(migration.steps) == 1

    def test_migration_add_simple_step(self):
        """Verify simple step addition."""
        from codomyrmex.migration import Migration

        migration = Migration(id="test", name="Test", version="1.0")

        migration.add_simple_step(
            id="simple",
            name="Simple Step",
            up_fn=lambda: True,
            down_fn=lambda: True,
        )

        assert len(migration.steps) == 1
        assert migration.steps[0].id == "simple"

    def test_migration_chaining(self):
        """Verify method chaining works."""
        from codomyrmex.migration import Migration, MigrationStep

        migration = (
            Migration(id="test", name="Test", version="1.0")
            .add_step(MigrationStep(id="s1", name="S1"))
            .add_step(MigrationStep(id="s2", name="S2"))
            .add_simple_step(id="s3", name="S3", up_fn=lambda: True)
        )

        assert len(migration.steps) == 3


@pytest.mark.unit
class TestFieldRenameTransformer:
    """Test suite for FieldRenameTransformer."""

    def test_field_rename(self):
        """Verify field renaming."""
        from codomyrmex.migration import FieldRenameTransformer

        transformer = FieldRenameTransformer({
            "old_name": "new_name",
            "email": "email_address",
        })

        data = {"old_name": "value1", "email": "test@example.com", "other": "unchanged"}
        result = transformer.transform(data)

        assert result["new_name"] == "value1"
        assert result["email_address"] == "test@example.com"
        assert result["other"] == "unchanged"
        assert "old_name" not in result


@pytest.mark.unit
class TestFieldTypeTransformer:
    """Test suite for FieldTypeTransformer."""

    def test_field_type_conversion(self):
        """Verify field type conversion."""
        from codomyrmex.migration import FieldTypeTransformer

        transformer = FieldTypeTransformer({
            "age": int,
            "score": float,
        })

        data = {"age": "25", "score": "0.95", "name": "Alice"}
        result = transformer.transform(data)

        assert result["age"] == 25
        assert isinstance(result["age"], int)
        assert result["score"] == 0.95
        assert isinstance(result["score"], float)
        assert result["name"] == "Alice"

    def test_field_type_handles_errors(self):
        """Verify type conversion handles errors gracefully."""
        from codomyrmex.migration import FieldTypeTransformer

        transformer = FieldTypeTransformer({"value": int})

        data = {"value": "not_a_number"}
        result = transformer.transform(data)

        # Should keep original value on error
        assert result["value"] == "not_a_number"


@pytest.mark.unit
class TestCompositeTransformer:
    """Test suite for CompositeTransformer."""

    def test_composite_applies_all(self):
        """Verify composite transformer applies all transformers."""
        from codomyrmex.migration import (
            CompositeTransformer, FieldRenameTransformer, FieldTypeTransformer
        )

        transformer = CompositeTransformer([
            FieldRenameTransformer({"old_age": "age"}),
            FieldTypeTransformer({"age": int}),
        ])

        data = {"old_age": "30"}
        result = transformer.transform(data)

        assert result["age"] == 30
        assert "old_age" not in result


@pytest.mark.unit
class TestMigrationRunner:
    """Test suite for MigrationRunner."""

    def test_runner_run_migration(self):
        """Verify migration execution."""
        from codomyrmex.migration import (
            MigrationRunner, Migration, MigrationStatus
        )

        runner = MigrationRunner()

        executed_steps = []

        migration = Migration(id="test", name="Test", version="1.0")
        migration.add_simple_step(
            id="s1",
            name="Step 1",
            up_fn=lambda: executed_steps.append("s1") or True,
        )
        migration.add_simple_step(
            id="s2",
            name="Step 2",
            up_fn=lambda: executed_steps.append("s2") or True,
        )

        result = runner.run(migration)

        assert result.status == MigrationStatus.COMPLETED
        assert result.steps_completed == 2
        assert executed_steps == ["s1", "s2"]

    def test_runner_handles_failure(self):
        """Verify failure handling."""
        from codomyrmex.migration import (
            MigrationRunner, Migration, MigrationStatus
        )

        runner = MigrationRunner()

        migration = Migration(id="test", name="Test", version="1.0")
        migration.add_simple_step(id="ok", name="OK", up_fn=lambda: True)
        migration.add_simple_step(id="fail", name="Fail", up_fn=lambda: False)
        migration.add_simple_step(id="skip", name="Skip", up_fn=lambda: True)

        result = runner.run(migration)

        assert result.status == MigrationStatus.FAILED
        assert result.steps_completed == 1
        assert "fail" in result.error

    def test_runner_rollback(self):
        """Verify rollback execution."""
        from codomyrmex.migration import (
            MigrationRunner, Migration, MigrationDirection, MigrationStatus
        )

        runner = MigrationRunner()

        rollback_executed = []

        migration = Migration(id="test", name="Test", version="1.0")
        migration.add_simple_step(
            id="s1",
            name="Step 1",
            up_fn=lambda: True,
            down_fn=lambda: rollback_executed.append("s1") or True,
        )
        migration.add_simple_step(
            id="s2",
            name="Step 2",
            up_fn=lambda: True,
            down_fn=lambda: rollback_executed.append("s2") or True,
        )

        result = runner.rollback(migration)

        assert result.status == MigrationStatus.COMPLETED
        # Steps should be rolled back in reverse order
        assert rollback_executed == ["s2", "s1"]

    def test_runner_is_completed(self):
        """Verify completion tracking."""
        from codomyrmex.migration import MigrationRunner, Migration

        runner = MigrationRunner()
        migration = Migration(id="tracked", name="Test", version="1.0")

        assert runner.is_completed("tracked") is False

        runner.run(migration)

        assert runner.is_completed("tracked") is True
        assert "tracked" in runner.get_completed()


@pytest.mark.unit
class TestDataMigrator:
    """Test suite for DataMigrator."""

    def test_migrator_migrate(self):
        """Verify data migration."""
        from codomyrmex.migration import DataMigrator, FieldRenameTransformer

        migrator = DataMigrator()
        migrator.add_transformer(FieldRenameTransformer({"old": "new"}))

        data = [
            {"old": "value1"},
            {"old": "value2"},
        ]

        result = migrator.migrate(data)

        assert len(result) == 2
        assert result[0]["new"] == "value1"
        assert "old" not in result[0]

    def test_migrator_migrate_single(self):
        """Verify single record migration."""
        from codomyrmex.migration import DataMigrator, FieldTypeTransformer

        migrator = DataMigrator()
        migrator.add_transformer(FieldTypeTransformer({"count": int}))

        result = migrator.migrate_single({"count": "42"})

        assert result["count"] == 42

    def test_migrator_chaining(self):
        """Verify transformer chaining."""
        from codomyrmex.migration import (
            DataMigrator, FieldRenameTransformer, FieldTypeTransformer
        )

        migrator = (
            DataMigrator()
            .add_transformer(FieldRenameTransformer({"user_age": "age"}))
            .add_transformer(FieldTypeTransformer({"age": int}))
        )

        result = migrator.migrate_single({"user_age": "25"})

        assert result["age"] == 25
