"""Unit tests for workflow_testing module."""
import time

import pytest


@pytest.mark.unit
class TestWorkflowTestingImports:
    """Test suite for workflow_testing module imports."""

    def test_module_imports(self):
        """Verify module can be imported without errors."""
        from codomyrmex import workflow_testing
        assert workflow_testing is not None

    def test_public_api_exists(self):
        """Verify expected public API is available."""
        from codomyrmex.workflow_testing import __all__
        expected_exports = [
            "WorkflowStepType",
            "StepStatus",
            "WorkflowStep",
            "StepResult",
            "WorkflowResult",
            "Workflow",
            "StepExecutor",
            "AssertionExecutor",
            "WaitExecutor",
            "ScriptExecutor",
            "WorkflowRunner",
        ]
        for export in expected_exports:
            assert export in __all__, f"Missing export: {export}"


@pytest.mark.unit
class TestWorkflowStepType:
    """Test suite for WorkflowStepType enum."""

    def test_step_type_values(self):
        """Verify all step types are available."""
        from codomyrmex.workflow_testing import WorkflowStepType

        assert WorkflowStepType.HTTP_REQUEST.value == "http_request"
        assert WorkflowStepType.ASSERTION.value == "assertion"
        assert WorkflowStepType.WAIT.value == "wait"
        assert WorkflowStepType.SCRIPT.value == "script"
        assert WorkflowStepType.CONDITIONAL.value == "conditional"


@pytest.mark.unit
class TestStepStatus:
    """Test suite for StepStatus enum."""

    def test_status_values(self):
        """Verify all step statuses are available."""
        from codomyrmex.workflow_testing import StepStatus

        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.PASSED.value == "passed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.ERROR.value == "error"


@pytest.mark.unit
class TestWorkflowStep:
    """Test suite for WorkflowStep dataclass."""

    def test_step_creation(self):
        """Verify WorkflowStep can be created."""
        from codomyrmex.workflow_testing import WorkflowStep, WorkflowStepType

        step = WorkflowStep(
            id="step_1",
            name="Verify Response",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "expected": 200},
        )

        assert step.id == "step_1"
        assert step.step_type == WorkflowStepType.ASSERTION

    def test_step_to_dict(self):
        """Verify step serialization."""
        from codomyrmex.workflow_testing import WorkflowStep, WorkflowStepType

        step = WorkflowStep(
            id="test",
            name="Test Step",
            step_type=WorkflowStepType.WAIT,
            config={"seconds": 5},
        )

        result = step.to_dict()
        assert result["id"] == "test"
        assert result["type"] == "wait"


@pytest.mark.unit
class TestStepResult:
    """Test suite for StepResult dataclass."""

    def test_result_creation(self):
        """Verify StepResult can be created."""
        from codomyrmex.workflow_testing import StepResult, StepStatus

        result = StepResult(
            step_id="step_1",
            status=StepStatus.PASSED,
            output={"data": "test"},
            duration_ms=150.0,
        )

        assert result.step_id == "step_1"
        assert result.passed is True

    def test_result_passed_property(self):
        """Verify passed property."""
        from codomyrmex.workflow_testing import StepResult, StepStatus

        passed = StepResult(step_id="1", status=StepStatus.PASSED)
        assert passed.passed is True

        failed = StepResult(step_id="2", status=StepStatus.FAILED)
        assert failed.passed is False

    def test_result_to_dict(self):
        """Verify result serialization."""
        from codomyrmex.workflow_testing import StepResult, StepStatus

        result = StepResult(
            step_id="test",
            status=StepStatus.PASSED,
            duration_ms=100.0,
        )

        data = result.to_dict()
        assert data["step_id"] == "test"
        assert data["status"] == "passed"


@pytest.mark.unit
class TestWorkflowResult:
    """Test suite for WorkflowResult dataclass."""

    def test_result_creation(self):
        """Verify WorkflowResult can be created."""
        from codomyrmex.workflow_testing import StepStatus, WorkflowResult

        result = WorkflowResult(
            workflow_id="wf_1",
            status=StepStatus.PASSED,
        )

        assert result.workflow_id == "wf_1"
        assert result.total_steps == 0

    def test_result_metrics(self):
        """Verify workflow result metrics."""
        from codomyrmex.workflow_testing import StepResult, StepStatus, WorkflowResult

        result = WorkflowResult(workflow_id="test", status=StepStatus.PASSED)
        result.step_results = [
            StepResult(step_id="1", status=StepStatus.PASSED, duration_ms=100),
            StepResult(step_id="2", status=StepStatus.PASSED, duration_ms=200),
            StepResult(step_id="3", status=StepStatus.FAILED, duration_ms=50),
        ]

        assert result.total_steps == 3
        assert result.passed_steps == 2
        assert result.duration_ms == 350.0
        assert result.pass_rate == 2/3

    def test_result_to_dict(self):
        """Verify result serialization."""
        from codomyrmex.workflow_testing import StepStatus, WorkflowResult

        result = WorkflowResult(workflow_id="test", status=StepStatus.PASSED)

        data = result.to_dict()
        assert data["workflow_id"] == "test"
        assert data["status"] == "passed"


@pytest.mark.unit
class TestWorkflow:
    """Test suite for Workflow dataclass."""

    def test_workflow_creation(self):
        """Verify Workflow can be created."""
        from codomyrmex.workflow_testing import Workflow

        workflow = Workflow(
            id="api_test",
            name="API Integration Test",
            description="Tests API endpoints",
            tags=["api", "integration"],
        )

        assert workflow.id == "api_test"
        assert len(workflow.steps) == 0

    def test_workflow_add_step(self):
        """Verify step addition."""
        from codomyrmex.workflow_testing import Workflow, WorkflowStep, WorkflowStepType

        workflow = Workflow(id="test", name="Test")
        step = WorkflowStep(id="s1", name="Step 1", step_type=WorkflowStepType.WAIT)

        workflow.add_step(step)

        assert len(workflow.steps) == 1

    def test_workflow_add_assertion(self):
        """Verify assertion step addition."""
        from codomyrmex.workflow_testing import Workflow

        workflow = Workflow(id="test", name="Test")
        workflow.add_assertion(
            id="assert_status",
            name="Check Status",
            assertion_type="equals",
            expected=200,
            actual_key="status_code",
        )

        assert len(workflow.steps) == 1
        assert workflow.steps[0].config["type"] == "equals"

    def test_workflow_add_wait(self):
        """Verify wait step addition."""
        from codomyrmex.workflow_testing import Workflow, WorkflowStepType

        workflow = Workflow(id="test", name="Test")
        workflow.add_wait(id="pause", seconds=2.0)

        assert len(workflow.steps) == 1
        assert workflow.steps[0].step_type == WorkflowStepType.WAIT
        assert workflow.steps[0].config["seconds"] == 2.0

    def test_workflow_chaining(self):
        """Verify method chaining."""
        from codomyrmex.workflow_testing import Workflow, WorkflowStep, WorkflowStepType

        workflow = (
            Workflow(id="test", name="Test")
            .add_step(WorkflowStep(id="s1", name="S1", step_type=WorkflowStepType.SCRIPT))
            .add_assertion(id="a1", name="Assert", assertion_type="equals", expected=True)
            .add_wait(id="w1", seconds=1.0)
        )

        assert len(workflow.steps) == 3


@pytest.mark.unit
class TestAssertionExecutor:
    """Test suite for AssertionExecutor."""

    def test_executor_equals_pass(self):
        """Verify equals assertion passes."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 200, "expected": 200},
        )

        result = executor.execute(step, {})
        assert result.status == StepStatus.PASSED

    def test_executor_equals_fail(self):
        """Verify equals assertion fails."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual": 404, "expected": 200},
        )

        result = executor.execute(step, {})
        assert result.status == StepStatus.FAILED

    def test_executor_contains(self):
        """Verify contains assertion."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "contains", "actual": "hello world", "expected": "world"},
        )

        result = executor.execute(step, {})
        assert result.status == StepStatus.PASSED

    def test_executor_not_null(self):
        """Verify not_null assertion."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "not_null", "actual": "value", "expected": None},
        )

        result = executor.execute(step, {})
        assert result.status == StepStatus.PASSED

    def test_executor_from_context(self):
        """Verify assertion using context value."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "equals", "actual_key": "status", "expected": 200},
        )

        context = {"status": 200}
        result = executor.execute(step, context)
        assert result.status == StepStatus.PASSED

    def test_executor_greater_than(self):
        """Verify greater_than assertion."""
        from codomyrmex.workflow_testing import (
            AssertionExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = AssertionExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.ASSERTION,
            config={"type": "greater_than", "actual": 10, "expected": 5},
        )

        result = executor.execute(step, {})
        assert result.status == StepStatus.PASSED


@pytest.mark.unit
class TestWaitExecutor:
    """Test suite for WaitExecutor."""

    def test_executor_wait(self):
        """Verify wait execution."""
        from codomyrmex.workflow_testing import (
            StepStatus,
            WaitExecutor,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = WaitExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.WAIT,
            config={"seconds": 0.01},  # Short wait for test
        )

        start = time.time()
        result = executor.execute(step, {})
        elapsed = time.time() - start

        assert result.status == StepStatus.PASSED
        assert elapsed >= 0.01


@pytest.mark.unit
class TestScriptExecutor:
    """Test suite for ScriptExecutor."""

    def test_executor_with_function(self):
        """Verify script execution with function."""
        from codomyrmex.workflow_testing import (
            ScriptExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = ScriptExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.SCRIPT,
            config={"function": lambda ctx: ctx.get("value", 0) * 2},
        )

        result = executor.execute(step, {"value": 21})
        assert result.status == StepStatus.PASSED
        assert result.output == 42

    def test_executor_with_expression(self):
        """Verify script execution with expression."""
        from codomyrmex.workflow_testing import (
            ScriptExecutor,
            StepStatus,
            WorkflowStep,
            WorkflowStepType,
        )

        executor = ScriptExecutor()
        step = WorkflowStep(
            id="test",
            name="Test",
            step_type=WorkflowStepType.SCRIPT,
            config={"expression": "ctx.get('x', 0) + ctx.get('y', 0)"},
        )

        result = executor.execute(step, {"x": 10, "y": 20})
        assert result.status == StepStatus.PASSED
        assert result.output == 30


@pytest.mark.unit
class TestWorkflowRunner:
    """Test suite for WorkflowRunner."""

    def test_runner_run_workflow(self):
        """Verify workflow execution."""
        from codomyrmex.workflow_testing import StepStatus, Workflow, WorkflowRunner

        runner = WorkflowRunner()

        workflow = (
            Workflow(id="test", name="Test")
            .add_assertion(id="a1", name="Check True", assertion_type="equals",
                          expected=True, actual_key="flag")
        )

        result = runner.run(workflow, initial_context={"flag": True})

        assert result.status == StepStatus.PASSED
        assert result.passed_steps == 1

    def test_runner_workflow_with_variables(self):
        """Verify workflow variables are available."""
        from codomyrmex.workflow_testing import StepStatus, Workflow, WorkflowRunner

        runner = WorkflowRunner()

        workflow = Workflow(
            id="test",
            name="Test",
            variables={"expected_value": 42},
        )
        workflow.add_assertion(
            id="check",
            name="Check Variable",
            assertion_type="equals",
            expected=42,
            actual_key="expected_value",
        )

        result = runner.run(workflow)

        assert result.status == StepStatus.PASSED

    def test_runner_step_output_in_context(self):
        """Verify step output is stored in context."""
        from codomyrmex.workflow_testing import (
            StepStatus,
            Workflow,
            WorkflowRunner,
            WorkflowStep,
            WorkflowStepType,
        )

        runner = WorkflowRunner()

        workflow = Workflow(id="test", name="Test")
        workflow.add_step(WorkflowStep(
            id="compute",
            name="Compute",
            step_type=WorkflowStepType.SCRIPT,
            config={"function": lambda ctx: 100},
        ))
        workflow.add_assertion(
            id="check",
            name="Check Output",
            assertion_type="not_null",
            expected=None,
            actual_key="step_compute",
        )

        result = runner.run(workflow)

        assert result.status == StepStatus.PASSED

    def test_runner_stops_on_error(self):
        """Verify runner stops on error."""
        from codomyrmex.workflow_testing import (
            StepStatus,
            Workflow,
            WorkflowRunner,
            WorkflowStep,
            WorkflowStepType,
        )

        runner = WorkflowRunner()

        workflow = Workflow(id="test", name="Test")
        workflow.add_step(WorkflowStep(
            id="error",
            name="Error Step",
            step_type=WorkflowStepType.SCRIPT,
            config={"function": lambda ctx: 1/0},  # Will raise error
        ))
        workflow.add_assertion(
            id="should_not_run",
            name="Should Not Run",
            assertion_type="equals",
            expected=True,
            actual_key="unreachable",
        )

        result = runner.run(workflow)

        assert result.status == StepStatus.FAILED
        # Only first step should have run
        assert len([r for r in result.step_results if r.status != StepStatus.PENDING]) <= 1

    def test_runner_register_executor(self):
        """Verify custom executor registration."""
        from codomyrmex.workflow_testing import (
            StepExecutor,
            StepResult,
            StepStatus,
            Workflow,
            WorkflowRunner,
            WorkflowStep,
            WorkflowStepType,
        )

        class CustomExecutor(StepExecutor):
            def execute(self, step, context):
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.PASSED,
                    output="custom",
                )

        runner = WorkflowRunner()
        runner.register_executor(WorkflowStepType.CONDITIONAL, CustomExecutor())

        workflow = Workflow(id="test", name="Test")
        workflow.add_step(WorkflowStep(
            id="custom",
            name="Custom Step",
            step_type=WorkflowStepType.CONDITIONAL,
        ))

        result = runner.run(workflow)

        assert result.status == StepStatus.PASSED
        assert result.step_results[0].output == "custom"

    def test_runner_retry_support(self):
        """Verify retry functionality."""
        from codomyrmex.workflow_testing import (
            StepStatus,
            Workflow,
            WorkflowRunner,
            WorkflowStep,
            WorkflowStepType,
        )

        attempt_count = [0]

        def flaky_function(ctx):
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        runner = WorkflowRunner()

        workflow = Workflow(id="test", name="Test")
        workflow.add_step(WorkflowStep(
            id="flaky",
            name="Flaky Step",
            step_type=WorkflowStepType.SCRIPT,
            config={"function": flaky_function},
            retry_count=5,
        ))

        result = runner.run(workflow)

        assert result.status == StepStatus.PASSED
        assert attempt_count[0] == 3  # Succeeded on 3rd attempt
