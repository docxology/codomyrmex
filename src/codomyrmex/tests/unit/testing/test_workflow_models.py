"""Tests for testing.workflow.models."""

from codomyrmex.testing.workflow.models import (
    StepResult,
    StepStatus,
    Workflow,
    WorkflowResult,
    WorkflowStep,
    WorkflowStepType,
)


class TestWorkflowStepType:
    def test_all_values(self):
        values = {t.value for t in WorkflowStepType}
        assert "http_request" in values
        assert "assertion" in values
        assert "wait" in values
        assert "script" in values
        assert "conditional" in values

    def test_construction(self):
        assert WorkflowStepType("wait") == WorkflowStepType.WAIT


class TestStepStatus:
    def test_all_values(self):
        values = {s.value for s in StepStatus}
        assert "pending" in values
        assert "running" in values
        assert "passed" in values
        assert "failed" in values
        assert "skipped" in values
        assert "error" in values


class TestWorkflowStep:
    def test_construction(self):
        step = WorkflowStep(
            id="s1", name="Login", step_type=WorkflowStepType.HTTP_REQUEST
        )
        assert step.id == "s1"
        assert step.name == "Login"
        assert step.step_type == WorkflowStepType.HTTP_REQUEST
        assert step.retry_count == 0
        assert step.timeout_seconds == 30.0

    def test_to_dict(self):
        step = WorkflowStep(
            id="s1",
            name="Check",
            step_type=WorkflowStepType.ASSERTION,
            config={"expected": 200},
        )
        d = step.to_dict()
        assert d["id"] == "s1"
        assert d["name"] == "Check"
        assert d["type"] == "assertion"
        assert d["config"] == {"expected": 200}

    def test_independent_default_lists(self):
        s1 = WorkflowStep(id="a", name="a", step_type=WorkflowStepType.WAIT)
        s2 = WorkflowStep(id="b", name="b", step_type=WorkflowStepType.WAIT)
        s1.dependencies.append("x")
        assert s2.dependencies == []


class TestStepResult:
    def test_passed_property_true(self):
        r = StepResult(step_id="s1", status=StepStatus.PASSED)
        assert r.passed is True

    def test_passed_property_false(self):
        for status in [
            StepStatus.FAILED,
            StepStatus.SKIPPED,
            StepStatus.ERROR,
            StepStatus.PENDING,
        ]:
            r = StepResult(step_id="s1", status=status)
            assert r.passed is False

    def test_to_dict_basic(self):
        r = StepResult(step_id="s1", status=StepStatus.PASSED, duration_ms=150.0)
        d = r.to_dict()
        assert d["step_id"] == "s1"
        assert d["status"] == "passed"
        assert d["duration_ms"] == 150.0

    def test_to_dict_with_error(self):
        r = StepResult(step_id="s1", status=StepStatus.FAILED, error="timeout")
        d = r.to_dict()
        assert d["error"] == "timeout"

    def test_to_dict_output_stringified(self):
        r = StepResult(step_id="s1", status=StepStatus.PASSED, output={"key": "val"})
        d = r.to_dict()
        assert isinstance(d["output"], str)

    def test_to_dict_output_none(self):
        r = StepResult(step_id="s1", status=StepStatus.PASSED, output=None)
        d = r.to_dict()
        assert d["output"] is None

    def test_defaults(self):
        r = StepResult(step_id="s1", status=StepStatus.RUNNING)
        assert r.duration_ms == 0.0
        assert r.retries == 0
        assert r.error is None


class TestWorkflowResult:
    def _make_result(self, status: StepStatus) -> StepResult:
        return StepResult(step_id="x", status=status)

    def test_empty_result(self):
        wr = WorkflowResult(workflow_id="w1", status=StepStatus.PASSED)
        assert wr.total_steps == 0
        assert wr.passed_steps == 0
        assert wr.pass_rate == 0.0
        assert wr.duration_ms == 0.0

    def test_total_steps(self):
        wr = WorkflowResult(
            workflow_id="w1",
            status=StepStatus.PASSED,
            step_results=[
                self._make_result(StepStatus.PASSED),
                self._make_result(StepStatus.FAILED),
            ],
        )
        assert wr.total_steps == 2

    def test_passed_steps(self):
        wr = WorkflowResult(
            workflow_id="w1",
            status=StepStatus.PASSED,
            step_results=[
                self._make_result(StepStatus.PASSED),
                self._make_result(StepStatus.PASSED),
                self._make_result(StepStatus.FAILED),
            ],
        )
        assert wr.passed_steps == 2

    def test_pass_rate(self):
        wr = WorkflowResult(
            workflow_id="w1",
            status=StepStatus.PASSED,
            step_results=[
                self._make_result(StepStatus.PASSED),
                self._make_result(StepStatus.FAILED),
            ],
        )
        assert wr.pass_rate == 0.5

    def test_duration_ms_sums_steps(self):
        r1 = StepResult(step_id="s1", status=StepStatus.PASSED, duration_ms=100.0)
        r2 = StepResult(step_id="s2", status=StepStatus.PASSED, duration_ms=200.0)
        wr = WorkflowResult(
            workflow_id="w1", status=StepStatus.PASSED, step_results=[r1, r2]
        )
        assert wr.duration_ms == 300.0

    def test_to_dict(self):
        wr = WorkflowResult(workflow_id="w1", status=StepStatus.PASSED)
        d = wr.to_dict()
        assert d["workflow_id"] == "w1"
        assert d["status"] == "passed"
        assert d["total_steps"] == 0
        assert d["pass_rate"] == 0.0


class TestWorkflow:
    def test_construction(self):
        wf = Workflow(id="wf1", name="Login Flow")
        assert wf.id == "wf1"
        assert wf.name == "Login Flow"
        assert wf.steps == []

    def test_add_step_chainable(self):
        wf = Workflow(id="wf1", name="Flow")
        step = WorkflowStep(id="s1", name="Step 1", step_type=WorkflowStepType.SCRIPT)
        result = wf.add_step(step)
        assert result is wf  # chainable
        assert len(wf.steps) == 1

    def test_add_assertion(self):
        wf = Workflow(id="wf1", name="Flow")
        wf.add_assertion(
            id="a1", name="Check status", assertion_type="equals", expected=200
        )
        assert len(wf.steps) == 1
        step = wf.steps[0]
        assert step.step_type == WorkflowStepType.ASSERTION
        assert step.config["type"] == "equals"
        assert step.config["expected"] == 200

    def test_add_wait(self):
        wf = Workflow(id="wf1", name="Flow")
        wf.add_wait(id="w1", seconds=2.5)
        assert len(wf.steps) == 1
        step = wf.steps[0]
        assert step.step_type == WorkflowStepType.WAIT
        assert step.config["seconds"] == 2.5

    def test_chain_multiple_steps(self):
        wf = Workflow(id="wf1", name="Flow")
        wf.add_wait(id="w1", seconds=1.0).add_assertion(
            id="a1", name="Check", assertion_type="equals", expected=True
        )
        assert len(wf.steps) == 2

    def test_independent_default_lists(self):
        wf1 = Workflow(id="a", name="a")
        wf2 = Workflow(id="b", name="b")
        step = WorkflowStep(id="s1", name="s1", step_type=WorkflowStepType.WAIT)
        wf1.add_step(step)
        assert len(wf2.steps) == 0
