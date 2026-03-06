"""Unit tests for agent telemetry hooks."""

import time

import pytest

from codomyrmex.telemetry.agent_hooks import AgentTelemetryHooks
from codomyrmex.telemetry.metrics import MetricsRegistry, get_metrics
from codomyrmex.telemetry.tracing import InMemoryExporter, SpanStatus, get_tracer


@pytest.fixture
def exporter():
    """Create an in-memory exporter."""
    exporter = InMemoryExporter()
    return exporter

@pytest.fixture
def hooks(exporter):
    """Create agent telemetry hooks with a custom tracer and exporter."""
    agent_name = "test_agent"
    # Re-initialize tracer with InMemoryExporter for testing
    tracer = get_tracer(f"agent.{agent_name}", exporter=exporter)
    # Ensure it uses the exporter we want
    tracer.exporter = exporter

    hooks = AgentTelemetryHooks(agent_name)
    hooks.tracer = tracer
    # Use a fresh MetricsRegistry for tests
    hooks.metrics = MetricsRegistry()
    return hooks

def test_track_phase_success(hooks, exporter):
    """Test tracking a successful phase."""
    with hooks.track_phase("test_phase", attributes={"attr1": "val1"}):
        time.sleep(0.01)

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "agent.test_agent.test_phase"
    assert span.attributes["attr1"] == "val1"
    assert span.status == SpanStatus.OK

    # Check metrics
    metrics = hooks.metrics

    executions = metrics.get("agent_phase_executions_total")
    assert executions is not None
    assert executions.get_value(labels={"agent": "test_agent", "phase": "test_phase"}) == 1

    errors = metrics.get("agent_phase_errors_total")
    # If no errors, it might not have been created or value is 0
    if errors:
        assert errors.get_value(labels={"agent": "test_agent", "phase": "test_phase"}) == 0

    latency_metric = metrics.get("agent_phase_latency_seconds")
    assert latency_metric is not None
    stats = latency_metric.get_value(labels={"agent": "test_agent", "phase": "test_phase"})
    assert stats["count"] == 1
    assert stats["sum"] >= 0.01

def test_track_phase_error(hooks, exporter):
    """Test tracking a phase that raises an error."""
    with pytest.raises(ValueError, match="test error"):
        with hooks.track_phase("error_phase"):
            raise ValueError("test error")

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert len(spans) == 1
    span = spans[0]
    assert span.name == "agent.test_agent.error_phase"
    assert span.status == SpanStatus.ERROR

    # Check metrics
    metrics = hooks.metrics
    executions = metrics.get("agent_phase_executions_total")
    assert executions.get_value(labels={"agent": "test_agent", "phase": "error_phase"}) == 1

    errors = metrics.get("agent_phase_errors_total")
    assert errors.get_value(labels={"agent": "test_agent", "phase": "error_phase"}) == 1

def test_track_plan(hooks, exporter):
    """Test track_plan helper."""
    with hooks.track_plan(goal="test_goal"):
        pass

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert spans[0].name == "agent.test_agent.plan"
    assert spans[0].attributes["goal"] == "test_goal"

    metrics = hooks.metrics
    executions = metrics.get("agent_phase_executions_total")
    assert executions.get_value(labels={"agent": "test_agent", "phase": "plan"}) == 1

def test_track_act(hooks, exporter):
    """Test track_act helper."""
    with hooks.track_act("shell_command", command="ls"):
        pass

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert spans[0].name == "agent.test_agent.act"
    assert spans[0].attributes["action_type"] == "shell_command"
    assert spans[0].attributes["command"] == "ls"

    metrics = hooks.metrics
    executions = metrics.get("agent_phase_executions_total")
    assert executions.get_value(labels={"agent": "test_agent", "phase": "act", "action_type": "shell_command"}) == 1

def test_track_observe(hooks, exporter):
    """Test track_observe helper."""
    with hooks.track_observe(result="success"):
        pass

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert spans[0].name == "agent.test_agent.observe"
    assert spans[0].attributes["result"] == "success"

    metrics = hooks.metrics
    executions = metrics.get("agent_phase_executions_total")
    assert executions.get_value(labels={"agent": "test_agent", "phase": "observe"}) == 1

def test_track_task(hooks, exporter):
    """Test track_task helper."""
    with hooks.track_task("task-123"):
        pass

    hooks.tracer.flush()
    spans = exporter.get_spans()
    assert spans[0].name == "agent.test_agent.task"
    assert spans[0].attributes["task_id"] == "task-123"

    metrics = hooks.metrics
    executions = metrics.get("agent_phase_executions_total")
    assert executions.get_value(labels={"agent": "test_agent", "phase": "task", "task_id": "task-123"}) == 1
