"""Tests for generic agent infrastructure: CLIAgentBase, retry_on_failure, AgentOrchestrator, MessageBus, TaskPlanner."""

import os
import platform
import time

import pytest

from codomyrmex.agents.core.base import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
    BaseAgent,
)
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.generic.cli_agent_base import CLIAgentBase, retry_on_failure
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
from codomyrmex.agents.generic.message_bus import Message, MessageBus
from codomyrmex.agents.generic.task_planner import Task, TaskPlanner, TaskStatus


# ---------------------------------------------------------------------------
# Concrete subclass helpers (real objects, zero mocks)
# ---------------------------------------------------------------------------

class EchoCLI(CLIAgentBase):
    """CLI agent wrapping the real `echo` command."""

    def __init__(self):
        super().__init__(
            name="echo_cli",
            command="echo",
            capabilities=[AgentCapabilities.TEXT_COMPLETION],
        )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        result = self._execute_command(args=[request.prompt])
        return AgentResponse(content=result.get("stdout", "").strip())

    def _stream_impl(self, request):
        for line in self._stream_command(args=[request.prompt]):
            yield line


class SuccessAgent(BaseAgent):
    def __init__(self, name="success"):
        super().__init__(name=name, capabilities=[AgentCapabilities.TEXT_COMPLETION])

    def _execute_impl(self, request):
        return AgentResponse(content=f"ok:{request.prompt}")

    def _stream_impl(self, request):
        yield "ok"


class FailAgent(BaseAgent):
    def __init__(self, name="fail"):
        super().__init__(name=name, capabilities=[AgentCapabilities.TEXT_COMPLETION])

    def _execute_impl(self, request):
        raise AgentError("boom")

    def _stream_impl(self, request):
        raise AgentError("boom")


# ── CLIAgentBase ──────────────────────────────────────────────────────────


class TestCLIAgentBase:
    def test_init(self):
        agent = EchoCLI()
        assert agent.name == "echo_cli"
        assert agent.command == "echo"

    def test_check_command_available(self):
        agent = EchoCLI()
        assert agent._check_command_available()

    def test_execute_echo(self):
        agent = EchoCLI()
        result = agent._execute_command(args=["hello world"])
        assert "hello world" in result.get("stdout", "")

    def test_stream_echo(self):
        agent = EchoCLI()
        lines = list(agent._stream_command(args=["streaming test"]))
        assert any("streaming test" in line for line in lines)

    def test_execute_impl(self):
        agent = EchoCLI()
        resp = agent.execute(AgentRequest(prompt="test123"))
        assert resp.is_success()
        assert "test123" in resp.content

    def test_health_check(self):
        agent = EchoCLI()
        health = agent.health_check()
        assert isinstance(health, dict)
        assert "available" in health

    def test_command_not_found(self):
        agent = CLIAgentBase(
            name="bad",
            command="__nonexistent_command_xyz__",
            capabilities=[],
        )
        assert not agent._check_command_available()


# ── retry_on_failure ──────────────────────────────────────────────────────


class TestRetryOnFailure:
    def test_succeeds_on_first_try(self):
        call_count = 0

        @retry_on_failure(max_retries=3)
        def always_ok():
            nonlocal call_count
            call_count += 1
            return "ok"

        assert always_ok() == "ok"
        assert call_count == 1

    def test_retries_then_succeeds(self):
        call_count = 0

        @retry_on_failure(max_retries=3, backoff_factor=0.01)
        def fail_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise AgentError("temporary")
            return "recovered"

        assert fail_twice() == "recovered"
        assert call_count == 3

    def test_exhausts_retries(self):
        @retry_on_failure(max_retries=1, backoff_factor=0.01)
        def always_fail():
            raise AgentError("permanent")

        with pytest.raises(AgentError, match="permanent"):
            always_fail()


# ── AgentOrchestrator ─────────────────────────────────────────────────────


class TestAgentOrchestrator:
    def test_sequential(self):
        agents = [SuccessAgent("a1"), SuccessAgent("a2")]
        orch = AgentOrchestrator(agents)
        results = orch.execute_sequential(AgentRequest(prompt="go"))
        assert len(results) == 2
        assert all(r.is_success() for r in results)

    def test_fallback_on_first_failure(self):
        agents = [FailAgent("x"), SuccessAgent("y")]
        orch = AgentOrchestrator(agents)
        result = orch.execute_with_fallback(AgentRequest(prompt="try"))
        assert result.is_success()
        assert "ok:" in result.content


# ── MessageBus ────────────────────────────────────────────────────────────


class TestMessageBus:
    def test_pub_sub(self):
        bus = MessageBus()
        received = []
        bus.subscribe("test", lambda msg: received.append(msg.content))
        bus.send(sender="s", recipient="r", message_type="test", content="hello")
        assert len(received) == 1
        assert received[0] == "hello"

    def test_unsubscribe(self):
        bus = MessageBus()
        received = []
        handler = lambda msg: received.append(msg.content)
        bus.subscribe("evt", handler)
        bus.unsubscribe("evt", handler)
        bus.send(sender="s", recipient="r", message_type="evt", content="nope")
        assert len(received) == 0

    def test_broadcast(self):
        bus = MessageBus()
        received = []
        bus.subscribe("bcast", lambda msg: received.append(1))
        msg = bus.broadcast(sender="s", message_type="bcast", content="hi")
        assert msg.recipient is None
        assert len(received) == 1

    def test_history(self):
        bus = MessageBus()
        bus.send(sender="a", recipient="b", message_type="t1", content="1")
        bus.send(sender="a", recipient="b", message_type="t2", content="2")
        all_msgs = bus.get_message_history()
        assert len(all_msgs) == 2
        t1 = bus.get_message_history(message_type="t1")
        assert len(t1) == 1


# ── TaskPlanner ───────────────────────────────────────────────────────────


class TestTaskPlanner:
    def test_create_task(self):
        tp = TaskPlanner()
        task = tp.create_task("Build feature")
        assert task.status == TaskStatus.PENDING
        assert task.id.startswith("task_")

    def test_update_status(self):
        tp = TaskPlanner()
        t = tp.create_task("Do something")
        tp.update_task_status(t.id, TaskStatus.IN_PROGRESS)
        assert tp.get_task(t.id).status == TaskStatus.IN_PROGRESS
        tp.update_task_status(t.id, TaskStatus.COMPLETED, result="done")
        assert tp.get_task(t.id).result == "done"

    def test_decompose(self):
        tp = TaskPlanner()
        main = tp.create_task("Main")
        subs = tp.decompose_task(main, ["Sub A", "Sub B"])
        assert len(subs) == 2
        assert all(s.metadata.get("parent_task") == main.id for s in subs)

    def test_ready_tasks(self):
        tp = TaskPlanner()
        t1 = tp.create_task("First")
        t2 = tp.create_task("Second", dependencies=[t1.id])
        ready = tp.get_ready_tasks()
        assert t1 in ready
        assert t2 not in ready
        tp.update_task_status(t1.id, TaskStatus.COMPLETED)
        ready2 = tp.get_ready_tasks()
        assert t2 in ready2

    def test_execution_order(self):
        tp = TaskPlanner()
        t1 = tp.create_task("A")
        t2 = tp.create_task("B", dependencies=[t1.id])
        t3 = tp.create_task("C", dependencies=[t2.id])
        order = tp.get_task_execution_order()
        ids = [t.id for t in order]
        assert ids.index(t1.id) < ids.index(t2.id) < ids.index(t3.id)
