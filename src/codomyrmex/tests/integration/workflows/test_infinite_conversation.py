"""Integration test: Infinite conversation orchestration.

Validates that Ollama, Claude Code, and Antigravity can engage in
sustained, multi-turn conversations using REAL LLM inference.

All tests use actual Ollama models — zero mocks. Skipped if Ollama
is offline or no models are available.
"""

import json
import os
import threading
import time
import urllib.error
import urllib.request

import pytest

_OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ── Skip entire module if Ollama is unreachable ─────────────────────

def _ollama_available() -> bool:
    """Check if Ollama is running and has at least one model."""
    try:
        with urllib.request.urlopen(f"{_OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return len(data.get("models", [])) > 0
    except Exception:
        return False


def _get_smallest_model() -> str:
    """Get the smallest available Ollama model for fast testing."""
    try:
        with urllib.request.urlopen(f"{_OLLAMA_BASE_URL}/api/tags", timeout=3) as resp:
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

    def test_conversation_export_to_jsonl(self, relay_dir, model_name, tmp_path):
        """Conversation can be exported to JSONL and imported back."""
        import json

        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-export",
            agents=[
                {"identity": "exporter", "persona": "assistant",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Say one word.",
            relay_dir=relay_dir,
        )

        orch.run(rounds=1)
        export_path = tmp_path / "conv.jsonl"
        result_path = orch.get_log().export(export_path)

        assert result_path.exists()
        lines = result_path.read_text().strip().split("\n")
        assert len(lines) >= 2  # header + at least 1 turn

        # First line is summary, rest are turns.
        summary = json.loads(lines[0])
        assert summary["channel_id"] == "test-export"
        assert summary["status"] == "completed"

        turn_data = json.loads(lines[1])
        assert turn_data["speaker"] == "exporter"
        assert len(turn_data["content"]) > 0

    def test_correlation_id_threaded(self, relay_dir, model_name):
        """Each conversation gets a unique correlation ID in its log."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-cid",
            agents=[
                {"identity": "cid-bot", "persona": "assistant",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Hi",
            relay_dir=relay_dir,
        )

        orch.run(rounds=1)
        log = orch.get_log()

        assert log.correlation_id != "", "Should have a correlation ID"
        assert log.correlation_id.startswith("conv-test-cid-")
        assert log.summary()["correlation_id"] == log.correlation_id

    def test_antigravity_agent_identity(self, relay_dir, model_name):
        """Agent configured as 'antigravity' provider uses a real LLM."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-antigravity",
            agents=[
                {"identity": "antigravity-coder", "persona": "Antigravity code agent",
                 "provider": "antigravity", "model": model_name},
            ],
            seed_prompt="Respond with one word.",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=1)
        assert len(transcript) == 1
        assert transcript[0].speaker == "antigravity-coder"
        assert len(transcript[0].content) > 0
        assert "[Error" not in transcript[0].content

    def test_agent_specific_system_prompts(self, relay_dir, model_name):
        """Different personas produce different response styles."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-personas",
            agents=[
                {"identity": "poet", "persona": "a poet who speaks in metaphors",
                 "provider": "ollama", "model": model_name},
                {"identity": "engineer", "persona": "a systems engineer who is precise",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Describe the sunrise in one sentence.",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=1)
        assert len(transcript) == 2
        # Both produce real content (different due to different personas).
        assert transcript[0].content != transcript[1].content
        assert len(transcript[0].content) > 5
        assert len(transcript[1].content) > 5

    def test_multi_provider_identity(self, relay_dir, model_name):
        """Agents report correct provider identity in turns."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        orch = ConversationOrchestrator(
            channel="test-providers",
            agents=[
                {"identity": "o-bot", "persona": "assistant",
                 "provider": "ollama", "model": model_name},
                {"identity": "a-bot", "persona": "reviewer",
                 "provider": "antigravity", "model": model_name},
            ],
            seed_prompt="Hi",
            relay_dir=relay_dir,
        )

        transcript = orch.run(rounds=1)
        assert len(transcript) == 2
        assert transcript[0].provider == "ollama"
        assert transcript[1].provider == "antigravity"
        for t in transcript:
            assert "[Error" not in t.content


class TestFileInjection:
    """Tests for file-injection and TO-DO scaffolding features."""

    def test_file_context_reads_real_file(self, tmp_path):
        """FileContext reads a real file from disk."""
        from codomyrmex.agents.orchestrator import FileContext

        f = tmp_path / "sample.md"
        f.write_text("# Title\n\nSome content here.\n- item 1\n- item 2\n")

        fc = FileContext(path=f)
        assert fc.name == "sample.md"
        assert "# Title" in fc.content
        assert fc.token_estimate > 0

    def test_file_context_clips_long_files(self, tmp_path):
        """FileContext clips files exceeding max_lines."""
        from codomyrmex.agents.orchestrator import FileContext

        f = tmp_path / "long.txt"
        f.write_text("\n".join(f"Line {i}" for i in range(500)))

        fc = FileContext(path=f, max_lines=50)
        assert "Line 0" in fc.content
        assert "Line 49" in fc.content
        assert "450 more lines" in fc.content

    def test_extract_todo_items(self):
        """extract_todo_items parses unchecked and in-progress checkboxes."""
        from codomyrmex.agents.orchestrator import extract_todo_items

        text = """\
# TO-DO
- [x] Done item
- [ ] Unchecked item 1
- [/] In progress item
- [ ] Unchecked item 2
- Some other line
"""
        items = extract_todo_items(text)
        assert len(items) == 3
        assert items[0] == "Unchecked item 1"
        assert items[1] == "In progress item (in progress)"
        assert items[2] == "Unchecked item 2"

    def test_context_files_injected_into_prompt(self, relay_dir, model_name, tmp_path):
        """Files passed via context_files appear in LLM-generated responses."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        ctx_file = tmp_path / "project_info.md"
        ctx_file.write_text("# Project Zephyr\n\nA wind simulation engine.\n")

        orch = ConversationOrchestrator(
            channel="test-ctx-inject",
            agents=[
                {"identity": "bot", "persona": "assistant who references project files",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Summarize the project described in the attached files.",
            context_files=[str(ctx_file)],
            relay_dir=relay_dir,
        )

        assert len(orch.context_files) == 1
        assert orch.context_files[0].name == "project_info.md"

        transcript = orch.run(rounds=1)
        assert len(transcript) == 1
        assert "[Error" not in transcript[0].content

    def test_todo_scaffolding_cycles_items(self, relay_dir, model_name, tmp_path):
        """TO-DO items cycle per round in the development focus."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        todo = tmp_path / "TODO.md"
        todo.write_text("# Tasks\n- [ ] Build API\n- [ ] Add tests\n- [ ] Write docs\n")

        orch = ConversationOrchestrator(
            channel="test-todo-cycle",
            agents=[
                {"identity": "dev", "persona": "developer",
                 "provider": "ollama", "model": model_name},
            ],
            seed_prompt="Work through each TO-DO item.",
            todo_path=str(todo),
            relay_dir=relay_dir,
        )

        assert len(orch.todo_items) == 3
        assert orch.todo_items[0] == "Build API"
        assert orch.todo_items[1] == "Add tests"
        assert orch.todo_items[2] == "Write docs"

        transcript = orch.run(rounds=2)
        assert len(transcript) == 2
        for t in transcript:
            assert "[Error" not in t.content

    def test_dev_loop_constructor(self, relay_dir, tmp_path, model_name):
        """dev_loop() creates a pre-configured orchestrator with file context."""
        from codomyrmex.agents.orchestrator import ConversationOrchestrator

        todo = tmp_path / "TO-DO.md"
        todo.write_text("# v1.0\n- [ ] Implement feature A\n- [ ] Write tests\n")

        extra = tmp_path / "README.md"
        extra.write_text("# My Project\n\nA sample project.\n")

        orch = ConversationOrchestrator.dev_loop(
            todo_path=str(todo),
            extra_files=[str(extra)],
            agents=[
                {"identity": "arch", "persona": "architect",
                 "provider": "ollama", "model": model_name},
                {"identity": "dev", "persona": "developer",
                 "provider": "ollama", "model": model_name},
            ],
            relay_dir=relay_dir,
        )

        assert len(orch.agents) == 2
        assert len(orch.todo_items) == 2
        # Extra file + TO-DO file = 2 context files.
        assert len(orch.context_files) == 2

        transcript = orch.run(rounds=1)
        assert len(transcript) == 2
        for t in transcript:
            assert "[Error" not in t.content
