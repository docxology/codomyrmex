"""
Tests for Migration Module
"""

import pytest
from codomyrmex.migration import (
    MigrationStatus,
    MigrationDirection,
    MigrationStep,
    MigrationResult,
    Migration,
    FieldRenameTransformer,
    FieldTypeTransformer,
    CompositeTransformer,
    MigrationRunner,
    DataMigrator,
)


class TestMigrationStep:
    """Tests for MigrationStep."""
    
    def test_run_up(self):
        """Should run up migration."""
        step = MigrationStep(
            id="s1",
            name="Test",
            up_fn=lambda: True,
        )
        assert step.run_up() is True
    
    def test_run_down(self):
        """Should run down migration."""
        step = MigrationStep(
            id="s1",
            name="Test",
            down_fn=lambda: True,
        )
        assert step.run_down() is True
    
    def test_default_up(self):
        """Should default to True."""
        step = MigrationStep(id="s1", name="Test")
        assert step.run_up() is True


class TestMigration:
    """Tests for Migration."""
    
    def test_add_step(self):
        """Should add step."""
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_step(MigrationStep(id="s1", name="Step 1"))
        
        assert len(m.steps) == 1
    
    def test_add_simple_step(self):
        """Should add simple step."""
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_simple_step(
            id="s1",
            name="Step 1",
            up_fn=lambda: True,
        )
        
        assert len(m.steps) == 1


class TestMigrationResult:
    """Tests for MigrationResult."""
    
    def test_progress(self):
        """Should calculate progress."""
        r = MigrationResult(
            migration_id="m1",
            status=MigrationStatus.RUNNING,
            steps_completed=3,
            steps_total=10,
        )
        assert r.progress == 0.3
    
    def test_duration(self):
        """Should calculate duration."""
        r = MigrationResult(migration_id="m1", status=MigrationStatus.RUNNING)
        assert r.duration_seconds >= 0


class TestMigrationRunner:
    """Tests for MigrationRunner."""
    
    def test_run_success(self):
        """Should run migration successfully."""
        runner = MigrationRunner()
        
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_simple_step("s1", "Step 1", lambda: True)
        m.add_simple_step("s2", "Step 2", lambda: True)
        
        result = runner.run(m)
        
        assert result.status == MigrationStatus.COMPLETED
        assert result.steps_completed == 2
    
    def test_run_failure(self):
        """Should handle failure."""
        runner = MigrationRunner()
        
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_simple_step("s1", "Step 1", lambda: True)
        m.add_simple_step("s2", "Step 2", lambda: False)  # Fails
        m.add_simple_step("s3", "Step 3", lambda: True)
        
        result = runner.run(m)
        
        assert result.status == MigrationStatus.FAILED
        assert result.steps_completed == 1
    
    def test_rollback(self):
        """Should rollback migration."""
        runner = MigrationRunner()
        
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_simple_step("s1", "Step 1", lambda: True, lambda: True)
        
        runner.run(m)
        result = runner.rollback(m)
        
        assert result.status == MigrationStatus.COMPLETED
    
    def test_is_completed(self):
        """Should track completed migrations."""
        runner = MigrationRunner()
        
        m = Migration(id="m1", name="Test", version="1.0")
        m.add_simple_step("s1", "Step 1", lambda: True)
        
        runner.run(m)
        
        assert runner.is_completed("m1") is True


class TestFieldRenameTransformer:
    """Tests for FieldRenameTransformer."""
    
    def test_rename(self):
        """Should rename fields."""
        t = FieldRenameTransformer({"old_name": "new_name"})
        
        result = t.transform({"old_name": "value", "other": 123})
        
        assert "new_name" in result
        assert "old_name" not in result
        assert result["other"] == 123


class TestFieldTypeTransformer:
    """Tests for FieldTypeTransformer."""
    
    def test_convert_types(self):
        """Should convert field types."""
        t = FieldTypeTransformer({"age": int, "score": float})
        
        result = t.transform({"age": "25", "score": "3.14"})
        
        assert result["age"] == 25
        assert result["score"] == 3.14


class TestCompositeTransformer:
    """Tests for CompositeTransformer."""
    
    def test_chain_transformers(self):
        """Should chain transformers."""
        t1 = FieldRenameTransformer({"old": "new"})
        t2 = FieldTypeTransformer({"new": int})
        
        composite = CompositeTransformer([t1, t2])
        result = composite.transform({"old": "42"})
        
        assert result["new"] == 42


class TestDataMigrator:
    """Tests for DataMigrator."""
    
    def test_migrate(self):
        """Should migrate data."""
        migrator = DataMigrator()
        migrator.add_transformer(FieldRenameTransformer({"x": "y"}))
        
        data = [{"x": 1}, {"x": 2}]
        result = migrator.migrate(data)
        
        assert all("y" in r for r in result)
    
    def test_migrate_single(self):
        """Should migrate single record."""
        migrator = DataMigrator()
        migrator.add_transformer(FieldRenameTransformer({"a": "b"}))
        
        result = migrator.migrate_single({"a": "value"})
        
        assert result["b"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
