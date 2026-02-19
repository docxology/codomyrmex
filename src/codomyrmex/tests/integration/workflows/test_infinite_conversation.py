"""Integration test: Infinite conversation orchestration.

Validates that Ollama, Claude Code, and Antigravity can engage in
sustained, multi-turn conversations using REAL LLM inference.

All tests use actual Ollama models — zero mocks. Skipped if Ollama
is offline or no models are available.
"""

import json
import os
import shutil
import tempfile
import time
import threading
import urllib.request
import urllib.error

import pytest


# ── Skip entire module if Ollama is unreachable ─────────────────────

def _ollama_available() -> bool:
    """Check if Ollama is running and has at least one model."""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return len(data.get("models", [])) > 0
    except Exception:
        return False


def _get_smallest_model() -> str:
    """Get the smallest available Ollama model for fast testing."""
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            if not models:
                return "llama3.2:1b"
            # Prefer 1b models for speed.
            for m in models:
                name = m.get("name", "")
                if "1b" in name:
                    return name
            return models[0]["name"]
    except Exception:
        return "llama3.2:1b"


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _ollama_available(),
        reason="Ollama not running or no models available"
    ),
]


@pytest.fixture
def relay_dir(tmp_path):
    """Temporary relay directory for test isolation."""
    d = tmp_path / "relay"
    d.mkdir()
    return str(d)


@pytest.fixture
def model_name():
    """The smallest available Ollama model."""
    return _get_smallest_model()


class TestInfiniteConversation:
    """Real-LLM tests for the ConversationOrchestrator."""

    def test_ollama_reachable(self):
        """Ollama is running and has models."""
        assert _ollama_available(), "Ollama should be reachable"
        model = _get_smallest_model()
        assert model, "At least one model should be available"

    def test_single_turn_ollama_conversation(self, relay_dir, model_name):
        """Single turn produces a non-empty response from real Ollama."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-single-turn",
            agents=[
                {"identity": "agent-alpha", "persona": "helpful assistant",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Say hello in one sentence.",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=1)

        assert len(transcript) == 1
        turn = transcript[0]
        assert turn.speaker == "agent-alpha"
        assert len(turn.content) > 0, "Response should be non-empty"
        assert "[Error" not in turn.content, f"LLM error: {turn.content}"
        assert turn.elapsed_seconds > 0

    def test_multi_turn_conversation(self, relay_dir, model_name):
        """3 rounds with 2 agents = 6 turns, all with real content."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-multi-turn",
            agents=[
                {"identity": "analyst", "persona": "data analyst who asks questions",
                 "provider": "ollama", "model": model_name},
                {"identity": "reviewer", "persona": "code reviewer who gives feedback",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="What makes a good code review?",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=3)

        assert len(transcript) == 6, f"Expected 6 turns, got {len(transcript)}"

        # Every turn should have real content.
        for turn in transcript:
            assert len(turn.content) > 0
            assert "[Error" not in turn.content

        # Verify alternating speakers.
        speakers = [t.speaker for t in transcript]
        assert speakers == ["analyst", "reviewer"] * 3

    def test_multi_agent_relay_persistence(self, relay_dir, model_name):
        """Messages are persisted in the relay JSONL file."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator
        from codomyrmex.ide.antigravity.agent_relay import AgentRelay

        orch = ConversationOrchestrator(
            channel="test-relay-persist",
            agents=[
                {"identity": "writer", "persona": "creative writer",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Write one sentence about the ocean.",
            relay_dir=relay_dir,
        )

        orch.run(rounds=2)

        # Read persisted messages from the relay.
        relay = AgentRelay("test-relay-persist", relay_dir=relay_dir)
        messages = relay.poll_messages(since_cursor=0)

        # Should have: 1 seed message + 2 agent responses = 3 chat messages.
        chat_messages = [m for m in messages if m.is_chat]
        assert len(chat_messages) >= 3, (
            f"Expected ≥3 persisted messages, got {len(chat_messages)}"
        )

    def test_conversation_log_structure(self, relay_dir, model_name):
        """ConversationLog has correct metadata."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-log-structure",
            agents=[
                {"identity": "bot-a", "persona": "assistant",
                 "provider": "ollama", "model": model_name},
                {"identity": "bot-b", "persona": "reviewer",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Hi",
            relay_dir=relay_dir,
        )

        orch.run(rounds=1)
        log = orch.get_log()

        assert log.channel_id == "test-log-structure"
        assert log.status == "completed"
        assert len(log.agents) == 2
        assert "bot-a" in log.agents
        assert "bot-b" in log.agents
        assert log.started_at != ""
        assert log.ended_at != ""
        assert log.total_rounds == 1

        summary = log.summary()
        assert summary["total_turns"] == 2
        assert summary["status"] == "completed"

    def test_graceful_shutdown(self, relay_dir, model_name):
        """Orchestrator stops gracefully when stop() is called."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-shutdown",
            agents=[
                {"identity": "infinite-bot", "persona": "chatbot",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Count from 1 to infinity.",
            relay_dir=relay_dir,
        )

        results: list = []

        def run_conversation():
            # Run with rounds=0 (infinite).
            transcript = orch.run(rounds=0)
            results.extend(transcript)

        thread = threading.Thread(target=run_conversation, daemon=True)
        thread.start()

        # Let it run for a few seconds (at least 1 turn).
        time.sleep(8)
        orch.stop()
        thread.join(timeout=30)

        assert not thread.is_alive(), "Thread should have stopped"
        assert len(results) >= 1, "Should have completed at least 1 turn"

    def test_three_agent_conversation(self, relay_dir, model_name):
        """Three agents can converse in round-robin."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-three-agents",
            agents=[
                {"identity": "planner", "persona": "project planner",
                 "provider": "ollama", "model": model_name},
                {"identity": "developer", "persona": "software developer",
                 "provider": "ollama", "model": model_name},
                {"identity": "tester", "persona": "QA tester",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="How should we build a login page?",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=2)

        assert len(transcript) == 6, f"Expected 6 turns (3 agents × 2 rounds), got {len(transcript)}"
        speakers = [t.speaker for t in transcript]
        assert speakers == ["planner", "developer", "tester"] * 2

        # All turns should have real LLM responses.
        for turn in transcript:
            assert len(turn.content) > 5, f"Turn too short: {turn.content!r}"
            assert turn.provider == "ollama"
            assert turn.model == model_name
