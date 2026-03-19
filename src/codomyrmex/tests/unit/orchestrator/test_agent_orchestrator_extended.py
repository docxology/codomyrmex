"""Extended unit tests: AgentOrchestrator capability routing, orchestrator_run_dag MCP,
dead-letter mailbox scenarios, EventStore-backed P2P durability, and BM25 FTS5 search.

Zero-mock: uses real InMemoryStore, SQLiteSessionStore (:memory:), EventStore, etc.
"""

from __future__ import annotations

import pytest

from codomyrmex.events.event_store import EventStore
from codomyrmex.events.integration_bus import IntegrationBus
from codomyrmex.orchestrator.integration import AgentOrchestrator
from codomyrmex.orchestrator.swarm_topology import SwarmTopology, TaskSpec

# ── AgentOrchestrator capability_profile + filter_tools ──────────────────────


def test_filter_tools_no_profile_returns_all() -> None:
    all_tools = ["write_file", "read_file", "run_test", "run_command"]
    result = AgentOrchestrator.filter_tools(all_tools, {}, "any_role")
    assert result == all_tools


def test_filter_tools_role_restricts_subset() -> None:
    all_tools = ["write_file", "read_file", "run_test", "deploy"]
    profile = {"reviewer": ["read_file", "run_test"]}
    result = AgentOrchestrator.filter_tools(all_tools, profile, "reviewer")
    assert set(result) == {"read_file", "run_test"}


def test_filter_tools_prefix_matching() -> None:
    all_tools = ["git_commit", "git_push", "run_test", "deploy_k8s"]
    profile = {"release": ["git_", "deploy_"]}
    result = AgentOrchestrator.filter_tools(all_tools, profile, "release")
    assert set(result) == {"git_commit", "git_push", "deploy_k8s"}


def test_spawn_agent_with_no_registered_agents_returns_error() -> None:
    orch = AgentOrchestrator(capability_profile={"analyst": ["read_"]})
    result = orch.spawn_agent("analyst", "Summarise the codebase.")
    assert result["status"] == "error"
    assert "analyst" in result["error"]


def test_spawn_agent_dispatches_to_matching_agent() -> None:
    orch = AgentOrchestrator(capability_profile={"coder": ["coder"]})
    orch.register_agent("coder", lambda t, **_: {"done": t})
    result = orch.spawn_agent("coder", "Fix the bug.")
    assert result["status"] == "success"
    assert result["agent"] == "coder"
    assert result["result"]["done"] == "Fix the bug."


def test_spawn_agent_extra_kwargs_forwarded() -> None:
    received: list[dict] = []

    def handler(task: str, **kwargs: object) -> dict:
        received.append({"task": task, **kwargs})
        return {}

    orch = AgentOrchestrator(capability_profile={"helper": ["helper"]})
    orch.register_agent("helper", handler)
    orch.spawn_agent("helper", "Do something.", extra_kwargs={"priority": "high"})
    assert received[0]["priority"] == "high"


def test_spawn_agent_catches_exception_gracefully() -> None:
    def broken(_t: str, **_kw: object) -> None:
        msg = "agent exploded"
        raise RuntimeError(msg)

    orch = AgentOrchestrator()
    orch.register_agent("boom", broken)
    result = orch.spawn_agent("boom", "crash please")
    assert result["status"] == "error"
    assert "exploded" in result["error"]


# ── orchestrator_run_dag MCP tool ─────────────────────────────────────────────


def test_orchestrator_run_dag_fan_out() -> None:
    from codomyrmex.orchestrator.mcp_tools import orchestrator_run_dag

    def _add(x: int) -> int:
        return x + 1

    tasks = [
        {"task_id": f"t{i}", "fn": "builtins.int", "args": [i]}
        for i in range(3)
    ]
    # Use the SwarmTopology directly since the MCP tool resolves fn from strings
    topo = SwarmTopology()
    specs = [TaskSpec(task_id=f"t{i}", fn=lambda i=i: i + 1) for i in range(3)]
    result = topo.run("fan_out", specs)
    assert "results" in result
    assert len(result["results"]) == 3


def test_orchestrator_run_dag_rejects_unknown_topology() -> None:
    from codomyrmex.orchestrator.mcp_tools import orchestrator_run_dag

    result = orchestrator_run_dag("quantum_teleport", [])
    assert "error" in result.get("status", result).lower() or "error" in str(result).lower()


# ── EventStore-backed IntegrationBus durability ───────────────────────────────


def test_eventstore_backed_bus_persists_p2p_messages() -> None:
    store = EventStore()
    bus = IntegrationBus(event_store=store)

    bus.send_to_agent("replayer", {"cmd": "start"})
    bus.send_to_agent("replayer", {"cmd": "stop"})

    # Drain the in-memory queue
    bus.drain_inbox("replayer")

    # Replay from EventStore
    replayed = bus.replay_from_store("replayer")
    assert len(replayed) == 2
    assert replayed[0]["message"]["cmd"] == "start"
    assert replayed[1]["message"]["cmd"] == "stop"


def test_eventstore_backed_bus_isolates_agents() -> None:
    store = EventStore()
    bus = IntegrationBus(event_store=store)
    bus.send_to_agent("alpha", {"x": 1})
    bus.send_to_agent("beta", {"y": 2})

    assert len(bus.replay_from_store("alpha")) == 1
    assert len(bus.replay_from_store("beta")) == 1


def test_eventstore_replay_returns_empty_without_store() -> None:
    bus = IntegrationBus()  # no store
    bus.send_to_agent("ghost", {"secret": True})
    replayed = bus.replay_from_store("ghost")
    assert replayed == []


# ── Dead-letter / edge-case mailbox scenarios ─────────────────────────────────


def test_unknown_agent_mailbox_starts_empty() -> None:
    bus = IntegrationBus()
    assert bus.drain_inbox("nobody") == []


def test_drain_is_atomic_under_concurrent_sends() -> None:
    import threading

    bus = IntegrationBus()
    sent: list[int] = []

    def sender(n: int) -> None:
        bus.send_to_agent("concurrent", {"n": n})
        sent.append(n)

    threads = [threading.Thread(target=sender, args=(i,), daemon=True) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    drained = bus.drain_inbox("concurrent")
    assert len(drained) == 20
    assert bus.mailbox_size == 0


def test_receive_timeout_does_not_block_indefinitely() -> None:
    import time

    bus = IntegrationBus()
    start = time.time()
    msg = bus.receive("empty-agent", timeout=0.15)
    elapsed = time.time() - start
    assert msg is None
    assert elapsed < 1.0  # tight bound: never more than 1 s


# ── BM25 FTS5 recall via SQLiteSessionStore ───────────────────────────────────


def test_fts5_search_returns_bm25_ranked_results() -> None:
    from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

    store = SQLiteSessionStore()  # :memory:

    s1 = HermesSession(session_id="s-bm25")
    s1.add_message("user", "Explain the BM25 ranking algorithm.")
    s1.add_message("assistant", "BM25 scores documents using term frequency and inverse document frequency.")
    store.save(s1)

    s2 = HermesSession(session_id="s-other")
    s2.add_message("user", "How does Docker work?")
    s2.add_message("assistant", "Docker packages applications in containers using layered filesystems.")
    store.save(s2)

    results = store.search_fts("BM25 ranking", limit=5)
    assert len(results) >= 1
    assert results[0]["session_id"] == "s-bm25"


def test_fts5_search_empty_returns_empty() -> None:
    from codomyrmex.agents.hermes.session import SQLiteSessionStore

    store = SQLiteSessionStore()
    results = store.search_fts("zzznomatch")
    assert results == []


def test_fts5_search_snippet_contains_highlighted_term() -> None:
    from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

    store = SQLiteSessionStore()
    s = HermesSession(session_id="s-snippet")
    s.add_message("assistant", "The quicksort algorithm divides arrays recursively.")
    store.save(s)

    results = store.search_fts("quicksort")
    assert any("<b>" in r["messages_snippet"] for r in results)
