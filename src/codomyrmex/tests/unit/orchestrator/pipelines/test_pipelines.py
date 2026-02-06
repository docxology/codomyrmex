"""
Tests for Orchestrator Pipelines Module
"""

import pytest

from codomyrmex.orchestrator.pipelines import (
    ConditionalStage,
    FunctionStage,
    ParallelStage,
    Pipeline,
    PipelineBuilder,
    PipelineStatus,
)


class TestFunctionStage:
    """Tests for FunctionStage."""

    def test_execute(self):
        """Should execute function."""
        stage = FunctionStage("test", lambda ctx: ctx.get("value", 0) * 2)

        result = stage.execute({"value": 5})
        assert result == 10

    def test_with_context(self):
        """Should access context."""
        stage = FunctionStage("test", lambda ctx: f"Hello {ctx['name']}")

        result = stage.execute({"name": "World"})
        assert result == "Hello World"


class TestPipeline:
    """Tests for Pipeline."""

    def test_simple_pipeline(self):
        """Should execute simple pipeline."""
        pipeline = Pipeline("test")
        pipeline.add_stage(FunctionStage("step1", lambda ctx: "result1"))
        pipeline.add_stage(FunctionStage("step2", lambda ctx: "result2"))

        result = pipeline.run()

        assert result.status == PipelineStatus.SUCCESS
        assert len(result.stages) == 2
        assert result.successful_stages == 2

    def test_with_dependencies(self):
        """Should respect dependencies."""
        pipeline = Pipeline("test")

        pipeline.add_stage(FunctionStage("first", lambda ctx: "first_result"))
        pipeline.add_stage(FunctionStage(
            "second",
            lambda ctx: ctx.get("stage_first_output", "missing") + "_modified",
            depends_on=["first"],
        ))

        result = pipeline.run()

        assert result.status == PipelineStatus.SUCCESS
        assert result.stages[1].output == "first_result_modified"

    def test_fail_fast(self):
        """Should stop on failure when fail_fast is True."""
        pipeline = Pipeline("test", fail_fast=True)

        pipeline.add_stage(FunctionStage("pass", lambda ctx: "ok"))
        pipeline.add_stage(FunctionStage("fail", lambda ctx: 1/0))  # Will fail
        pipeline.add_stage(FunctionStage("never", lambda ctx: "never"))

        result = pipeline.run()

        assert result.status == PipelineStatus.FAILED
        assert result.failed_stages == 1

    def test_initial_context(self):
        """Should use initial context."""
        pipeline = Pipeline("test")
        pipeline.add_stage(FunctionStage("step", lambda ctx: ctx["input"] * 2))

        result = pipeline.run(initial_context={"input": 5})

        assert result.stages[0].output == 10

    def test_duration(self):
        """Should track duration."""
        pipeline = Pipeline("test")
        pipeline.add_stage(FunctionStage("step", lambda ctx: "done"))

        result = pipeline.run()

        assert result.duration_ms >= 0


class TestConditionalStage:
    """Tests for ConditionalStage."""

    def test_condition_true(self):
        """Should execute when condition is true."""
        inner = FunctionStage("inner", lambda ctx: "executed")
        stage = ConditionalStage("cond", lambda ctx: True, inner)

        result = stage.execute({})
        assert result == "executed"

    def test_condition_false(self):
        """Should skip when condition is false."""
        inner = FunctionStage("inner", lambda ctx: "executed")
        stage = ConditionalStage("cond", lambda ctx: False, inner)

        result = stage.execute({})
        assert result is None


class TestParallelStage:
    """Tests for ParallelStage."""

    def test_parallel_execution(self):
        """Should execute stages in parallel."""
        stages = [
            FunctionStage("a", lambda ctx: "result_a"),
            FunctionStage("b", lambda ctx: "result_b"),
        ]
        parallel = ParallelStage("parallel", stages)

        result = parallel.execute({})

        assert result["a"] == "result_a"
        assert result["b"] == "result_b"


class TestPipelineBuilder:
    """Tests for PipelineBuilder."""

    def test_builder(self):
        """Should build pipeline fluently."""
        pipeline = (PipelineBuilder("my_pipeline")
            .stage("step1", lambda ctx: "r1")
            .stage("step2", lambda ctx: "r2", depends_on=["step1"])
            .context("key", "value")
            .build())

        result = pipeline.run()

        assert result.status == PipelineStatus.SUCCESS
        assert len(result.stages) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
