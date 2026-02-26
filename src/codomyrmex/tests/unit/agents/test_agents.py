"""Tests for agents module — ConversationOrchestrator, data structures, helpers.

Covers: ConversationTurn, AgentSpec, FileContext, ConversationLog,
extract_todo_items, ConversationOrchestrator constructor/lifecycle.

Zero-mock policy: all tests use real instances, tmpfiles, and real constructors.
Tests requiring LLM connectivity use @pytest.mark.skipif guards.
"""

import json
import os
import tempfile
import urllib.request
from dataclasses import asdict
from pathlib import Path

import pytest

from codomyrmex.agents.orchestrator import (
    AgentSpec,
    ConversationLog,
    ConversationOrchestrator,
    ConversationTurn,
    FileContext,
    extract_todo_items,
)


# ── Helpers ──────────────────────────────────────────────────────────

def _ollama_reachable() -> bool:
    """Check whether a local Ollama instance is responding."""
    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=2.0) as resp:
            return resp.status == 200
    except (OSError, ValueError, urllib.error.URLError):
        return False


OLLAMA_AVAILABLE = _ollama_reachable()
SKIP_NO_OLLAMA = pytest.mark.skipif(
    not OLLAMA_AVAILABLE,
    reason="Ollama not reachable at localhost:11434",
)


# ── ConversationTurn tests ───────────────────────────────────────────

class TestConversationTurn:
    """Tests for the ConversationTurn dataclass."""

    @pytest.mark.unit
    def test_construction_with_all_fields(self):
        turn = ConversationTurn(
            turn_number=1,
            speaker="agent-a",
            provider="ollama",
            model="llama3.2:1b",
            content="Hello, world.",
            timestamp="2026-02-26T00:00:00+00:00",
            elapsed_seconds=1.23,
            token_estimate=3,
        )
        assert turn.turn_number == 1
        assert turn.speaker == "agent-a"
        assert turn.provider == "ollama"
        assert turn.model == "llama3.2:1b"
        assert turn.content == "Hello, world."
        assert turn.elapsed_seconds == 1.23
        assert turn.token_estimate == 3

    @pytest.mark.unit
    def test_default_token_estimate_is_zero(self):
        turn = ConversationTurn(
            turn_number=0,
            speaker="x",
            provider="ollama",
            model="m",
            content="c",
            timestamp="t",
            elapsed_seconds=0.0,
        )
        assert turn.token_estimate == 0

    @pytest.mark.unit
    def test_asdict_roundtrip(self):
        turn = ConversationTurn(
            turn_number=5,
            speaker="bob",
            provider="ollama",
            model="llama3",
            content="test content",
            timestamp="2026-01-01T00:00:00Z",
            elapsed_seconds=2.5,
            token_estimate=2,
        )
        d = asdict(turn)
        reconstructed = ConversationTurn(**d)
        assert reconstructed == turn


# ── AgentSpec tests ──────────────────────────────────────────────────

class TestAgentSpec:
    """Tests for the AgentSpec dataclass and its __post_init__ defaults."""

    @pytest.mark.unit
    def test_default_provider_is_ollama(self):
        spec = AgentSpec(identity="agent-1", persona="tester")
        assert spec.provider == "ollama"

    @pytest.mark.unit
    def test_ollama_default_model_from_env(self):
        """When provider is ollama and no model given, falls back to env or llama3.2:1b."""
        spec = AgentSpec(identity="agent-1", persona="tester", provider="ollama")
        expected = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
        assert spec.model == expected

    @pytest.mark.unit
    def test_non_ollama_default_model(self):
        spec = AgentSpec(identity="agent-1", persona="tester", provider="claude")
        assert spec.model == "claude-3-haiku-20240307"

    @pytest.mark.unit
    def test_explicit_model_overrides_default(self):
        spec = AgentSpec(
            identity="agent-1",
            persona="tester",
            provider="ollama",
            model="custom-model:7b",
        )
        assert spec.model == "custom-model:7b"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "provider,expected_model",
        [
            ("claude", "claude-3-haiku-20240307"),
            ("claude_code", "claude-3-haiku-20240307"),
            ("antigravity", "claude-3-haiku-20240307"),
        ],
    )
    def test_non_ollama_providers_default_to_claude_model(self, provider, expected_model):
        spec = AgentSpec(identity="a", persona="p", provider=provider)
        assert spec.model == expected_model


# ── FileContext tests ────────────────────────────────────────────────

class TestFileContext:
    """Tests for FileContext — reads real files, clips to max_lines."""

    @pytest.mark.unit
    def test_reads_real_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("line 1\nline 2\nline 3\n")
            f.flush()
            path = f.name
        try:
            fc = FileContext(path=Path(path))
            assert "line 1" in fc.content
            assert "line 2" in fc.content
            assert "line 3" in fc.content
        finally:
            os.unlink(path)

    @pytest.mark.unit
    def test_clips_to_max_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for i in range(300):
                f.write(f"line {i}\n")
            f.flush()
            path = f.name
        try:
            fc = FileContext(path=Path(path), max_lines=10)
            assert "line 0" in fc.content
            assert "line 9" in fc.content
            assert "more lines" in fc.content
        finally:
            os.unlink(path)

    @pytest.mark.unit
    def test_nonexistent_file_produces_empty_content(self):
        fc = FileContext(path=Path("/nonexistent/file/abc123.txt"))
        assert fc.content == ""

    @pytest.mark.unit
    def test_name_property_returns_filename(self):
        fc = FileContext(path=Path("/some/dir/myfile.py"))
        assert fc.name == "myfile.py"

    @pytest.mark.unit
    def test_token_estimate_is_word_count(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("one two three four five")
            f.flush()
            path = f.name
        try:
            fc = FileContext(path=Path(path))
            assert fc.token_estimate == 5
        finally:
            os.unlink(path)


# ── extract_todo_items tests ─────────────────────────────────────────

class TestExtractTodoItems:
    """Tests for the extract_todo_items helper function."""

    @pytest.mark.unit
    def test_extracts_unchecked_items(self):
        text = "- [ ] First task\n- [ ] Second task\n- [x] Done task\n"
        items = extract_todo_items(text)
        assert items == ["First task", "Second task"]

    @pytest.mark.unit
    def test_extracts_in_progress_items(self):
        text = "- [/] Partial task\n"
        items = extract_todo_items(text)
        assert len(items) == 1
        assert "Partial task" in items[0]
        assert "(in progress)" in items[0]

    @pytest.mark.unit
    def test_empty_text_returns_empty_list(self):
        assert extract_todo_items("") == []

    @pytest.mark.unit
    def test_no_checkboxes_returns_empty_list(self):
        text = "Just some text\n- A bullet\n## A heading\n"
        assert extract_todo_items(text) == []

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "line,expected_count",
        [
            ("- [ ] task", 1),
            ("  - [ ] indented task", 1),
            ("- [x] completed", 0),
            ("- [X] also completed", 0),
            ("- [/] in progress", 1),
            ("random text", 0),
        ],
    )
    def test_single_line_extraction(self, line, expected_count):
        items = extract_todo_items(line)
        assert len(items) == expected_count


# ── ConversationLog tests ────────────────────────────────────────────

class TestConversationLog:
    """Tests for ConversationLog — summary, export, serialization."""

    @pytest.mark.unit
    def test_summary_returns_expected_keys(self):
        log = ConversationLog(
            channel_id="test-channel",
            started_at="2026-02-26T00:00:00Z",
            agents=["a1", "a2"],
        )
        summary = log.summary()
        assert summary["channel_id"] == "test-channel"
        assert summary["agents"] == ["a1", "a2"]
        assert summary["total_turns"] == 0
        assert summary["status"] == "running"

    @pytest.mark.unit
    def test_summary_reflects_added_turns(self):
        log = ConversationLog(
            channel_id="ch1",
            started_at="2026-01-01T00:00:00Z",
        )
        log.turns.append(
            ConversationTurn(
                turn_number=1,
                speaker="agent-a",
                provider="ollama",
                model="m",
                content="hello",
                timestamp="t",
                elapsed_seconds=0.1,
            )
        )
        assert log.summary()["total_turns"] == 1

    @pytest.mark.unit
    def test_export_creates_jsonl_file(self):
        log = ConversationLog(
            channel_id="export-test",
            started_at="2026-02-26T00:00:00Z",
            agents=["a1"],
        )
        log.turns.append(
            ConversationTurn(
                turn_number=1,
                speaker="a1",
                provider="ollama",
                model="llama3",
                content="exported turn",
                timestamp="2026-02-26T00:01:00Z",
                elapsed_seconds=0.5,
                token_estimate=2,
            )
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "conv.jsonl"
            result = log.export(export_path)
            assert result.exists()
            lines = result.read_text().splitlines()
            # First line is summary metadata, second is the turn
            assert len(lines) == 2
            meta = json.loads(lines[0])
            assert meta["channel_id"] == "export-test"
            turn_data = json.loads(lines[1])
            assert turn_data["speaker"] == "a1"
            assert turn_data["content"] == "exported turn"

    @pytest.mark.unit
    def test_export_creates_parent_directories(self):
        log = ConversationLog(
            channel_id="nested-export",
            started_at="2026-02-26T00:00:00Z",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "deep" / "nested" / "conv.jsonl"
            result = log.export(export_path)
            assert result.exists()


# ── ConversationOrchestrator tests (require Ollama) ──────────────────

class TestConversationOrchestratorConstruction:
    """Tests for ConversationOrchestrator constructor and configuration."""

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_with_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(relay_dir=tmpdir)
            assert orch.channel_id.startswith("conv-")
            assert len(orch.agents) == 2  # default agents
            assert orch.seed_prompt != ""
            assert orch.max_retries == 2
            assert orch._running is False

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_with_custom_channel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(
                channel="my-custom-channel",
                relay_dir=tmpdir,
            )
            assert orch.channel_id == "my-custom-channel"

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_with_explicit_agents(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = [
                {"identity": "analyst", "persona": "data analyst", "provider": "ollama"},
                {"identity": "reviewer", "persona": "code reviewer", "provider": "ollama"},
                {"identity": "writer", "persona": "tech writer", "provider": "ollama"},
            ]
            orch = ConversationOrchestrator(
                agents=agents,
                relay_dir=tmpdir,
            )
            assert len(orch.agents) == 3
            identities = [a.identity for a in orch.agents]
            assert "analyst" in identities
            assert "reviewer" in identities
            assert "writer" in identities

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_accepts_agentspec_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            specs = [
                AgentSpec(identity="spec-agent", persona="test persona", provider="ollama"),
            ]
            orch = ConversationOrchestrator(
                agents=specs,
                relay_dir=tmpdir,
            )
            assert len(orch.agents) == 1
            assert orch.agents[0].identity == "spec-agent"

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_creates_llm_clients_for_each_agent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = [
                {"identity": "a1", "persona": "p1", "provider": "ollama"},
                {"identity": "a2", "persona": "p2", "provider": "ollama"},
            ]
            orch = ConversationOrchestrator(agents=agents, relay_dir=tmpdir)
            assert "a1" in orch.clients
            assert "a2" in orch.clients

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_unknown_provider_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = [
                {"identity": "bad-agent", "persona": "test", "provider": "nonexistent_provider_xyz"},
            ]
            with pytest.raises(RuntimeError, match="Unknown provider"):
                ConversationOrchestrator(agents=agents, relay_dir=tmpdir)

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_with_context_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a real context file
            ctx_file = Path(tmpdir) / "context.txt"
            ctx_file.write_text("This is context content for agents.")
            orch = ConversationOrchestrator(
                context_files=[str(ctx_file)],
                relay_dir=tmpdir,
            )
            assert len(orch.context_files) == 1
            assert "context content" in orch.context_files[0].content

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_constructor_with_todo_path_extracts_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            todo_file = Path(tmpdir) / "TODO.md"
            todo_file.write_text(
                "# Tasks\n"
                "- [ ] Implement feature A\n"
                "- [x] Already done\n"
                "- [ ] Write tests for B\n"
                "- [/] In progress C\n"
            )
            orch = ConversationOrchestrator(
                todo_path=str(todo_file),
                relay_dir=tmpdir,
            )
            assert len(orch.todo_items) == 3
            assert "Implement feature A" in orch.todo_items[0]
            assert "Write tests for B" in orch.todo_items[1]
            assert "(in progress)" in orch.todo_items[2]

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_log_initialized_with_agent_identities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            agents = [
                {"identity": "x1", "persona": "p1", "provider": "ollama"},
                {"identity": "x2", "persona": "p2", "provider": "ollama"},
            ]
            orch = ConversationOrchestrator(agents=agents, relay_dir=tmpdir)
            assert orch.log.agents == ["x1", "x2"]
            assert orch.log.status == "running"
            assert orch.log.channel_id == orch.channel_id


class TestConversationOrchestratorLifecycle:
    """Tests for orchestrator methods that don't execute LLM calls."""

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_get_transcript_initially_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(relay_dir=tmpdir)
            assert orch.get_transcript() == []

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_get_log_returns_conversation_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(relay_dir=tmpdir)
            log = orch.get_log()
            assert isinstance(log, ConversationLog)
            assert log.channel_id == orch.channel_id

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_stop_sets_running_to_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(relay_dir=tmpdir)
            orch._running = True
            orch.stop()
            assert orch._running is False

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_load_export_roundtrip(self):
        """Export a log, then load it back into a fresh orchestrator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create orchestrator and manually add turns to its log
            orch = ConversationOrchestrator(
                channel="roundtrip-test",
                relay_dir=tmpdir,
            )
            orch.log.turns.append(
                ConversationTurn(
                    turn_number=1,
                    speaker="agent-a",
                    provider="ollama",
                    model="llama3",
                    content="Hello from agent A",
                    timestamp="2026-02-26T00:00:00Z",
                    elapsed_seconds=0.5,
                    token_estimate=4,
                )
            )
            orch.log.turns.append(
                ConversationTurn(
                    turn_number=2,
                    speaker="agent-b",
                    provider="ollama",
                    model="llama3",
                    content="Response from agent B",
                    timestamp="2026-02-26T00:00:01Z",
                    elapsed_seconds=0.8,
                    token_estimate=4,
                )
            )
            export_path = Path(tmpdir) / "export.jsonl"
            orch.log.export(export_path)

            # Create a new orchestrator and load the export
            orch2 = ConversationOrchestrator(
                channel="fresh-channel",
                relay_dir=tmpdir,
            )
            orch2.load_export(export_path)
            assert orch2.channel_id == "roundtrip-test"
            assert len(orch2.log.turns) == 2
            assert orch2.log.turns[0].speaker == "agent-a"
            assert orch2.log.turns[1].content == "Response from agent B"

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_load_export_nonexistent_file_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(relay_dir=tmpdir)
            with pytest.raises(FileNotFoundError, match="Export not found"):
                orch.load_export("/nonexistent/path/export.jsonl")

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_dev_loop_classmethod_creates_orchestrator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            todo_file = Path(tmpdir) / "TODO.md"
            todo_file.write_text("- [ ] Task one\n- [ ] Task two\n")
            orch = ConversationOrchestrator.dev_loop(
                todo_path=str(todo_file),
                relay_dir=tmpdir,
            )
            assert isinstance(orch, ConversationOrchestrator)
            assert len(orch.agents) == 3  # architect, developer, reviewer
            assert len(orch.todo_items) == 2
            assert orch.channel_id.startswith("devloop-")

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_max_retries_configurable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(
                max_retries=5,
                relay_dir=tmpdir,
            )
            assert orch.max_retries == 5

    @pytest.mark.unit
    @SKIP_NO_OLLAMA
    def test_custom_seed_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = ConversationOrchestrator(
                seed_prompt="Custom seed for testing.",
                relay_dir=tmpdir,
            )
            assert orch.seed_prompt == "Custom seed for testing."
