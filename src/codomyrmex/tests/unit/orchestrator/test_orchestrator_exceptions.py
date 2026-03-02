"""
Unit tests for orchestrator.exceptions — Zero-Mock compliant.

Covers: StepError (step_name/step_index/workflow_name context injection),
OrchestratorTimeoutError (timeout_seconds/operation),
StateError (current_state/expected_state/workflow_id),
DependencyResolutionError (task_name/missing_dependencies),
ConcurrencyError (resource_name/max_workers).
Also verifies re-exported WorkflowError, CycleError, TaskFailedError.
"""

import pytest

from codomyrmex.orchestrator.exceptions import (
    ConcurrencyError,
    CycleError,
    DependencyResolutionError,
    OrchestratorTimeoutError,
    StateError,
    StepError,
    TaskFailedError,
    WorkflowError,
)


# ── StepError ─────────────────────────────────────────────────────────


@pytest.mark.unit
class TestStepError:
    def test_is_exception(self):
        assert isinstance(StepError("step failed"), Exception)

    def test_message_stored(self):
        e = StepError("step failed")
        assert "step failed" in str(e)

    def test_step_name_in_context(self):
        e = StepError("err", step_name="build")
        assert e.context.get("step_name") == "build"

    def test_step_index_in_context(self):
        e = StepError("err", step_index=2)
        assert e.context.get("step_index") == 2

    def test_step_index_zero_stored(self):
        """step_index=0 is falsy but should still be stored (not None check)."""
        e = StepError("err", step_index=0)
        assert e.context.get("step_index") == 0

    def test_workflow_name_in_context(self):
        e = StepError("err", workflow_name="deploy-pipeline")
        assert e.context.get("workflow_name") == "deploy-pipeline"

    def test_all_fields_stored(self):
        e = StepError("err", step_name="test", step_index=3, workflow_name="wf")
        assert e.context["step_name"] == "test"
        assert e.context["step_index"] == 3
        assert e.context["workflow_name"] == "wf"

    def test_no_optional_fields_absent(self):
        e = StepError("err")
        assert "step_name" not in e.context
        assert "step_index" not in e.context
        assert "workflow_name" not in e.context

    def test_raise_and_catch(self):
        with pytest.raises(StepError):
            raise StepError("failed at step 2")


# ── OrchestratorTimeoutError ──────────────────────────────────────────


@pytest.mark.unit
class TestOrchestratorTimeoutError:
    def test_is_exception(self):
        assert isinstance(OrchestratorTimeoutError("timed out"), Exception)

    def test_message_stored(self):
        e = OrchestratorTimeoutError("execution timed out")
        assert "execution timed out" in str(e)

    def test_timeout_seconds_in_context(self):
        e = OrchestratorTimeoutError("err", timeout_seconds=30.0)
        assert e.context.get("timeout_seconds") == pytest.approx(30.0)

    def test_timeout_seconds_zero_stored(self):
        e = OrchestratorTimeoutError("err", timeout_seconds=0.0)
        assert e.context.get("timeout_seconds") == pytest.approx(0.0)

    def test_operation_in_context(self):
        e = OrchestratorTimeoutError("err", operation="run_workflow")
        assert e.context.get("operation") == "run_workflow"

    def test_both_fields(self):
        e = OrchestratorTimeoutError("err", timeout_seconds=5.0, operation="step_run")
        assert e.context["timeout_seconds"] == pytest.approx(5.0)
        assert e.context["operation"] == "step_run"

    def test_no_optional_fields_absent(self):
        e = OrchestratorTimeoutError("err")
        assert "timeout_seconds" not in e.context
        assert "operation" not in e.context


# ── StateError ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestStateError:
    def test_is_exception(self):
        assert isinstance(StateError("bad state"), Exception)

    def test_message_stored(self):
        e = StateError("unexpected state transition")
        assert "unexpected state transition" in str(e)

    def test_current_state_in_context(self):
        e = StateError("err", current_state="running")
        assert e.context.get("current_state") == "running"

    def test_expected_state_in_context(self):
        e = StateError("err", expected_state="idle")
        assert e.context.get("expected_state") == "idle"

    def test_workflow_id_in_context(self):
        e = StateError("err", workflow_id="wf-123")
        assert e.context.get("workflow_id") == "wf-123"

    def test_all_fields(self):
        e = StateError("err", current_state="paused",
                       expected_state="running", workflow_id="wf-abc")
        assert e.context["current_state"] == "paused"
        assert e.context["expected_state"] == "running"
        assert e.context["workflow_id"] == "wf-abc"

    def test_no_optional_fields_absent(self):
        e = StateError("err")
        assert "current_state" not in e.context
        assert "expected_state" not in e.context
        assert "workflow_id" not in e.context


# ── DependencyResolutionError ─────────────────────────────────────────


@pytest.mark.unit
class TestDependencyResolutionError:
    def test_is_exception(self):
        assert isinstance(DependencyResolutionError("unresolved"), Exception)

    def test_message_stored(self):
        e = DependencyResolutionError("missing deps")
        assert "missing deps" in str(e)

    def test_task_name_in_context(self):
        e = DependencyResolutionError("err", task_name="build_step")
        assert e.context.get("task_name") == "build_step"

    def test_missing_dependencies_in_context(self):
        e = DependencyResolutionError("err", missing_dependencies=["dep1", "dep2"])
        assert e.context.get("missing_dependencies") == ["dep1", "dep2"]

    def test_empty_missing_dependencies_not_stored(self):
        """Empty list is falsy — not stored in context."""
        e = DependencyResolutionError("err", missing_dependencies=[])
        assert "missing_dependencies" not in e.context

    def test_both_fields(self):
        e = DependencyResolutionError(
            "err", task_name="t", missing_dependencies=["x"]
        )
        assert e.context["task_name"] == "t"
        assert e.context["missing_dependencies"] == ["x"]


# ── ConcurrencyError ──────────────────────────────────────────────────


@pytest.mark.unit
class TestConcurrencyError:
    def test_is_exception(self):
        assert isinstance(ConcurrencyError("deadlock"), Exception)

    def test_message_stored(self):
        e = ConcurrencyError("resource contention")
        assert "resource contention" in str(e)

    def test_resource_name_in_context(self):
        e = ConcurrencyError("err", resource_name="db-connection-pool")
        assert e.context.get("resource_name") == "db-connection-pool"

    def test_max_workers_in_context(self):
        e = ConcurrencyError("err", max_workers=4)
        assert e.context.get("max_workers") == 4

    def test_max_workers_zero_stored(self):
        e = ConcurrencyError("err", max_workers=0)
        assert e.context.get("max_workers") == 0

    def test_both_fields(self):
        e = ConcurrencyError("err", resource_name="queue", max_workers=8)
        assert e.context["resource_name"] == "queue"
        assert e.context["max_workers"] == 8

    def test_no_optional_fields_absent(self):
        e = ConcurrencyError("err")
        assert "resource_name" not in e.context
        assert "max_workers" not in e.context


# ── Re-exported exceptions ─────────────────────────────────────────────


@pytest.mark.unit
class TestReExportedExceptions:
    def test_workflow_error_importable(self):
        assert issubclass(WorkflowError, Exception)

    def test_cycle_error_importable(self):
        assert issubclass(CycleError, Exception)

    def test_task_failed_error_importable(self):
        assert issubclass(TaskFailedError, Exception)

    def test_raise_workflow_error(self):
        with pytest.raises(WorkflowError):
            raise WorkflowError("cycle detected")
