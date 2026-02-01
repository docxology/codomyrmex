"""
Tests for Workflow Testing Module
"""

import pytest
from codomyrmex.workflow_testing import (
    WorkflowStepType,
    StepStatus,
    WorkflowStep,
    StepResult,
    WorkflowResult,
    Workflow,
    AssertionExecutor,
    WaitExecutor,
    ScriptExecutor,
    WorkflowRunner,
)


class TestWorkflowStep:
    """Tests for WorkflowStep."""
    
    def test_create(self):
        """Should create step."""
        step = WorkflowStep(id="s1", name="Test", step_type=WorkflowStepType.ASSERTION)
        assert step.id == "s1"
    
    def test_to_dict(self):
        """Should convert to dict."""
        step = WorkflowStep(id="s1", name="Test", step_type=WorkflowStepType.WAIT)
        d = step.to_dict()
        assert d["id"] == "s1"


class TestAssertionExecutor:
    """Tests for AssertionExecutor."""
    
    def test_equals_pass(self):
        """Should pass equal assertion."""
        executor = AssertionExecutor()
        step = WorkflowStep(
            id="s1", name="Test", step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 200},
        )
        
        result = executor.execute(step, {})
        assert result.passed
    
    def test_equals_fail(self):
        """Should fail unequal assertion."""
        executor = AssertionExecutor()
        step = WorkflowStep(
            id="s1", name="Test", step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 201},
        )
        
        result = executor.execute(step, {})
        assert not result.passed
    
    def test_contains(self):
        """Should evaluate contains."""
        executor = AssertionExecutor()
        step = WorkflowStep(
            id="s1", name="Test", step_type=WorkflowStepType.ASSERTION,
            config={"type": "contains", "actual": "hello world", "expected": "hello"},
        )
        
        result = executor.execute(step, {})
        assert result.passed
    
    def test_from_context(self):
        """Should read from context."""
        executor = AssertionExecutor()
        step = WorkflowStep(
            id="s1", name="Test", step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual_key": "status", "expected": 200},
        )
        
        result = executor.execute(step, {"status": 200})
        assert result.passed


class TestWaitExecutor:
    """Tests for WaitExecutor."""
    
    def test_wait(self):
        """Should wait specified time."""
        executor = WaitExecutor()
        step = WorkflowStep(
            id="s1", name="Wait", step_type=WorkflowStepType.WAIT,
            config={"seconds": 0.1},
        )
        
        result = executor.execute(step, {})
        assert result.passed
        assert result.duration_ms >= 100


class TestScriptExecutor:
    """Tests for ScriptExecutor."""
    
    def test_execute_function(self):
        """Should execute function."""
        executor = ScriptExecutor()
        step = WorkflowStep(
            id="s1", name="Script", step_type=WorkflowStepType.SCRIPT,
            config={"function": lambda ctx: ctx.get("x", 0) * 2},
        )
        
        result = executor.execute(step, {"x": 5})
        assert result.output == 10


class TestWorkflow:
    """Tests for Workflow."""
    
    def test_add_step(self):
        """Should add step."""
        workflow = Workflow(id="w1", name="Test")
        workflow.add_step(WorkflowStep(id="s1", name="Step 1", step_type=WorkflowStepType.WAIT))
        
        assert len(workflow.steps) == 1
    
    def test_add_assertion(self):
        """Should add assertion step."""
        workflow = Workflow(id="w1", name="Test")
        workflow.add_assertion("a1", "Check value", "equals", 100, actual_key="value")
        
        assert len(workflow.steps) == 1
        assert workflow.steps[0].step_type == WorkflowStepType.ASSERTION
    
    def test_add_wait(self):
        """Should add wait step."""
        workflow = Workflow(id="w1", name="Test")
        workflow.add_wait("w1", 0.5)
        
        assert workflow.steps[0].config["seconds"] == 0.5


class TestWorkflowResult:
    """Tests for WorkflowResult."""
    
    def test_metrics(self):
        """Should calculate metrics."""
        result = WorkflowResult(workflow_id="w1", status=StepStatus.PASSED)
        result.step_results.append(StepResult("s1", StepStatus.PASSED, duration_ms=100))
        result.step_results.append(StepResult("s2", StepStatus.FAILED, duration_ms=50))
        
        assert result.total_steps == 2
        assert result.passed_steps == 1
        assert result.pass_rate == 0.5
        assert result.duration_ms == 150


class TestWorkflowRunner:
    """Tests for WorkflowRunner."""
    
    def test_run_passing(self):
        """Should run passing workflow."""
        runner = WorkflowRunner()
        workflow = Workflow(id="w1", name="Test")
        workflow.add_step(WorkflowStep(
            id="check",
            name="Check",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 200},
        ))
        
        result = runner.run(workflow)
        assert result.status == StepStatus.PASSED
    
    def test_run_failing(self):
        """Should run failing workflow."""
        runner = WorkflowRunner()
        workflow = Workflow(id="w1", name="Test")
        workflow.add_step(WorkflowStep(
            id="check",
            name="Check",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 500},
        ))
        
        result = runner.run(workflow)
        assert result.status == StepStatus.FAILED
    
    def test_context_propagation(self):
        """Should propagate context between steps."""
        runner = WorkflowRunner()
        workflow = Workflow(id="w1", name="Test", variables={"value": 100})
        workflow.add_assertion("check", "Check value", "equals", 100, actual_key="value")
        
        result = runner.run(workflow)
        assert result.status == StepStatus.PASSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
