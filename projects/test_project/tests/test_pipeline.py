"""Tests for the pipeline module."""

import pytest
from pathlib import Path

from src.pipeline import AnalysisPipeline, PipelineStep, PipelineResult, PipelineStatus


class TestPipelineStatus:
    """Tests for PipelineStatus enum."""
    
    def test_values(self):
        """Test status values."""
        assert PipelineStatus.PENDING.value == "pending"
        assert PipelineStatus.RUNNING.value == "running"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.FAILED.value == "failed"


class TestPipelineStep:
    """Tests for PipelineStep dataclass."""
    
    def test_creation(self):
        """Test step creation."""
        def handler(ctx):
            return "result"
            
        step = PipelineStep(name="test", handler=handler)
        
        assert step.name == "test"
        assert step.status == PipelineStatus.PENDING
        assert step.result is None
        assert step.error is None
        
    def test_execute_success(self):
        """Test successful step execution."""
        def handler(ctx):
            return {"data": "test"}
            
        step = PipelineStep(name="test", handler=handler)
        result = step.execute({})
        
        assert step.status == PipelineStatus.COMPLETED
        assert result == {"data": "test"}
        assert step.result == {"data": "test"}
        assert step.error is None
        
    def test_execute_failure(self):
        """Test failed step execution."""
        def handler(ctx):
            raise ValueError("Test error")
            
        step = PipelineStep(name="test", handler=handler)
        
        with pytest.raises(ValueError):
            step.execute({})
            
        assert step.status == PipelineStatus.FAILED
        assert step.error == "Test error"


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""
    
    def test_is_success(self):
        """Test success detection."""
        from datetime import datetime
        
        success = PipelineResult(
            status=PipelineStatus.COMPLETED,
            started_at=datetime.now()
        )
        failure = PipelineResult(
            status=PipelineStatus.FAILED,
            started_at=datetime.now()
        )
        
        assert success.is_success is True
        assert failure.is_success is False
        
    def test_duration_calculation(self):
        """Test duration calculation."""
        from datetime import datetime, timedelta
        
        start = datetime.now()
        end = start + timedelta(seconds=5)
        
        result = PipelineResult(
            status=PipelineStatus.COMPLETED,
            started_at=start,
            completed_at=end
        )
        
        assert result.duration_seconds == pytest.approx(5.0, rel=0.1)


class TestAnalysisPipeline:
    """Tests for AnalysisPipeline class."""
    
    def test_initialization(self):
        """Test pipeline initialization with default steps."""
        pipeline = AnalysisPipeline()
        
        assert len(pipeline.steps) >= 5  # Default pipeline has 5 steps
        assert "load_config" in pipeline.steps
        assert "validate" in pipeline.steps
        assert "analyze" in pipeline.steps
        
    def test_add_step(self):
        """Test adding custom steps."""
        pipeline = AnalysisPipeline()
        initial_count = len(pipeline.steps)
        
        def custom_handler(ctx):
            return "custom"
            
        pipeline.add_step(
            name="custom_step",
            handler=custom_handler,
            dependencies=["analyze"]
        )
        
        assert len(pipeline.steps) == initial_count + 1
        assert "custom_step" in pipeline.steps
        
    def test_add_duplicate_step_raises(self):
        """Test that adding duplicate step raises error."""
        pipeline = AnalysisPipeline()
        
        with pytest.raises(ValueError):
            pipeline.add_step(
                name="validate",  # Already exists
                handler=lambda ctx: None
            )
            
    def test_execute_success(self, sample_directory: Path):
        """Test successful pipeline execution."""
        pipeline = AnalysisPipeline()
        
        result = pipeline.execute(sample_directory)
        
        assert result.status == PipelineStatus.COMPLETED
        assert result.is_success is True
        assert result.steps_completed == result.total_steps
        assert result.duration_seconds > 0
        
    def test_execute_with_invalid_target(self):
        """Test pipeline with invalid target path."""
        pipeline = AnalysisPipeline()
        
        result = pipeline.execute(Path("/nonexistent/path"))
        
        assert result.status == PipelineStatus.FAILED
        assert result.is_success is False
        assert len(result.errors) > 0
        
    def test_step_order_respects_dependencies(self):
        """Test that execution order respects dependencies."""
        pipeline = AnalysisPipeline()
        
        order = pipeline._get_execution_order()
        
        # validate depends on load_config, so load_config must come first
        assert order.index("load_config") < order.index("validate")
        
        # analyze depends on validate
        assert order.index("validate") < order.index("analyze")
        
    def test_result_contains_step_outputs(self, sample_directory: Path):
        """Test that result contains outputs from each step."""
        pipeline = AnalysisPipeline()
        
        result = pipeline.execute(sample_directory)
        
        assert "load_config" in result.results
        assert "validate" in result.results
        assert "analyze" in result.results
        
    def test_result_to_dict(self, sample_directory: Path):
        """Test result serialization to dict."""
        pipeline = AnalysisPipeline()
        result = pipeline.execute(sample_directory)
        
        d = result.to_dict()
        
        assert "status" in d
        assert "duration_seconds" in d
        assert "steps_completed" in d
        assert "total_steps" in d
