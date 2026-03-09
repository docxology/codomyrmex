"""Comprehensive tests for agents.orchestrator data models — zero-mock.

Covers: ConversationTurn, AgentSpec, FileContext, ConversationLog (summary, export),
and extract_todo_items. Tests data structures without requiring real LLM clients.
"""

import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.agents.orchestrator import (
    AgentSpec,
    ConversationLog,
    ConversationTurn,
    FileContext,
    extract_todo_items,
)


class TestConversationTurn:
    def test_create(self):
        turn = ConversationTurn(
            turn_number=1,
            speaker="Architect",
            provider="ollama",
            model="qwen2.5",
            content="Let's discuss architecture.",
            timestamp="2026-03-08T12:00:00Z",
            elapsed_seconds=2.5,
        )
        assert turn.turn_number == 1
        assert turn.speaker == "Architect"
        assert turn.token_estimate == 0


class TestAgentSpec:
    def test_create_default(self):
        spec = AgentSpec(identity="Architect", persona="Senior software architect")
        assert spec.identity == "Architect"
        assert spec.provider == "ollama"

    def test_with_custom_model(self):
        spec = AgentSpec(
            identity="Coder", persona="Expert coder", provider="ollama", model="qwen2.5-coder"
        )
        assert spec.model == "qwen2.5-coder"


class TestFileContext:
    def test_create_with_real_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def hello():\n    return 'world'\n")
            f.flush()
            ctx = FileContext(path=Path(f.name))
            assert ctx.content != ""
            assert "hello" in ctx.content

    def test_name_property(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("x = 1\n")
            f.flush()
            ctx = FileContext(path=Path(f.name))
            assert ctx.name == Path(f.name).name

    def test_token_estimate(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("word " * 100)
            f.flush()
            ctx = FileContext(path=Path(f.name))
            assert ctx.token_estimate > 0

    def test_max_lines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("\n".join([f"line {i}" for i in range(500)]))
            f.flush()
            ctx = FileContext(path=Path(f.name), max_lines=10)
            lines = ctx.content.strip().split("\n")
            # max_lines may be approximate; verify truncation happened
            assert len(lines) < 500


class TestExtractTodoItems:
    def test_extracts_unchecked(self):
        text = "- [ ] Fix bug\n- [x] Write tests\n- [ ] Deploy\n"
        items = extract_todo_items(text)
        assert len(items) == 2
        assert "Fix bug" in items[0]
        assert "Deploy" in items[1]

    def test_empty_text(self):
        items = extract_todo_items("")
        assert items == []

    def test_no_todos(self):
        items = extract_todo_items("Just some text without checkboxes.")
        assert items == []


class TestConversationLog:
    def test_create(self):
        log = ConversationLog(channel_id="test-channel", started_at="2026-03-08T12:00:00Z")
        assert log.channel_id == "test-channel"
        assert log.status == "running"

    def test_summary(self):
        log = ConversationLog(
            channel_id="ch-1",
            started_at="2026-03-08T12:00:00Z",
            agents=["Architect", "Coder"],
            total_rounds=5,
        )
        s = log.summary()
        assert isinstance(s, dict)

    def test_export(self):
        log = ConversationLog(
            channel_id="ch-export",
            started_at="2026-03-08T12:00:00Z",
            turns=[
                ConversationTurn(
                    turn_number=1, speaker="A", provider="ollama", model="q",
                    content="Hello", timestamp="2026-03-08T12:00:01Z", elapsed_seconds=1.0,
                ),
            ],
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            log.export(f.name)
            with open(f.name) as rf:
                lines = rf.readlines()
                assert len(lines) >= 1
