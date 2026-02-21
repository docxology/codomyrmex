"""Tests for Sprint 34: Multi-Process Agent Orchestration.

Covers HeartbeatMonitor (registration, beats, status detection),
AgentSupervisor (restart strategies, escalation), and
ProcessOrchestrator (spawn, shutdown, crash recovery, health).
"""

import time
import pytest

from codomyrmex.orchestrator.heartbeat import AgentStatus, HeartbeatMonitor
from codomyrmex.orchestrator.agent_supervisor import (
    AgentSupervisor,
    RestartStrategy,
    SupervisorAction,
)
from codomyrmex.orchestrator.process_orchestrator import ProcessOrchestrator, ProcessState


# ─── HeartbeatMonitor ────────────────────────────────────────────────

class TestHeartbeatMonitor:

    def test_healthy_after_beat(self):
        monitor = HeartbeatMonitor(timeout_seconds=10.0)
        monitor.register("a1")
        monitor.beat("a1")
        assert monitor.check("a1") == AgentStatus.HEALTHY

    def test_unknown_agent(self):
        monitor = HeartbeatMonitor()
        assert monitor.check("nonexistent") == AgentStatus.UNKNOWN

    def test_check_all(self):
        monitor = HeartbeatMonitor(timeout_seconds=10.0)
        monitor.register("a1")
        monitor.register("a2")
        monitor.beat("a1")
        monitor.beat("a2")
        statuses = monitor.check_all()
        assert all(s == AgentStatus.HEALTHY for s in statuses.values())

    def test_auto_register_on_beat(self):
        monitor = HeartbeatMonitor()
        monitor.beat("new-agent")
        assert monitor.agent_count == 1


# ─── AgentSupervisor ─────────────────────────────────────────────────

class TestAgentSupervisor:

    def test_restart_on_crash(self):
        supervisor = AgentSupervisor(max_restarts=3)
        supervisor.register("a1")
        action = supervisor.on_agent_crash("a1", "OOM")
        assert action == SupervisorAction.RESTART

    def test_escalate_after_max_restarts(self):
        supervisor = AgentSupervisor(max_restarts=2, restart_window=60.0)
        supervisor.register("a1")
        supervisor.on_agent_crash("a1", "err1")
        supervisor.on_agent_crash("a1", "err2")
        action = supervisor.on_agent_crash("a1", "err3")
        assert action == SupervisorAction.ESCALATE

    def test_one_for_one_strategy(self):
        supervisor = AgentSupervisor(strategy=RestartStrategy.ONE_FOR_ONE)
        supervisor.register("a1")
        supervisor.register("a2")
        to_restart = supervisor.agents_to_restart("a1")
        assert to_restart == ["a1"]

    def test_one_for_all_strategy(self):
        supervisor = AgentSupervisor(strategy=RestartStrategy.ONE_FOR_ALL)
        supervisor.register("a1")
        supervisor.register("a2")
        to_restart = supervisor.agents_to_restart("a1")
        assert set(to_restart) == {"a1", "a2"}

    def test_rest_for_one_strategy(self):
        supervisor = AgentSupervisor(strategy=RestartStrategy.REST_FOR_ONE)
        supervisor.register("a1")
        supervisor.register("a2")
        supervisor.register("a3")
        to_restart = supervisor.agents_to_restart("a2")
        assert to_restart == ["a2", "a3"]


# ─── ProcessOrchestrator ─────────────────────────────────────────────

class TestProcessOrchestrator:

    def test_spawn_and_health(self):
        orch = ProcessOrchestrator()
        agent_id = orch.spawn("ThinkingAgent", {"depth": 3})
        health = orch.health()
        assert health.total_agents == 1
        assert health.running == 1

    def test_shutdown(self):
        orch = ProcessOrchestrator()
        aid = orch.spawn("Agent")
        orch.shutdown(aid)
        health = orch.health()
        assert health.stopped == 1

    def test_crash_and_auto_restart(self):
        orch = ProcessOrchestrator()
        aid = orch.spawn("Agent")
        action = orch.report_crash(aid, "segfault")
        assert action == SupervisorAction.RESTART
        health = orch.health()
        assert health.running == 1  # Restarted


__all__: list[str] = []
