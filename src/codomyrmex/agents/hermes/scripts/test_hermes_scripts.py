"""Comprehensive test suite for Hermes orchestration scripts.

Zero-mock policy: all tests use real ``HermesClient`` instantiation, real
``SQLiteSessionStore`` (in-memory mode), and real ``TemplateLibrary``.

Tests requiring Ollama are gated with ``pytest.mark.skipif``.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

# Ensure the evolution submodule is importable
_evo_path = Path(__file__).resolve().parent.parent / "evolution"
if _evo_path.exists() and str(_evo_path) not in sys.path:
    sys.path.insert(0, str(_evo_path))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_OLLAMA_AVAILABLE = bool(shutil.which("ollama"))
_HERMES_CLI_AVAILABLE = bool(shutil.which("hermes"))
_ANY_BACKEND = _OLLAMA_AVAILABLE or _HERMES_CLI_AVAILABLE

requires_backend = pytest.mark.skipif(
    not _ANY_BACKEND,
    reason="Neither ollama nor hermes CLI available",
)


# ═══════════════════════════════════════════════════════════════════════
# 1. Status
# ═══════════════════════════════════════════════════════════════════════


class TestRunStatus:
    """Tests for ``run_status``."""

    def test_returns_dict_with_required_keys(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_status import run_status

        result = run_status()
        assert isinstance(result, dict)
        assert "active_backend" in result
        assert "cli_available" in result
        assert "ollama_available" in result
        assert "ollama_model" in result
        assert "success" in result

    def test_active_backend_is_string(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_status import run_status

        result = run_status()
        assert result["active_backend"] in ("cli", "ollama", "none")


# ═══════════════════════════════════════════════════════════════════════
# 2. Chat
# ═══════════════════════════════════════════════════════════════════════


class TestRunChat:
    """Tests for ``run_chat``."""

    @requires_backend
    def test_chat_returns_structured_result(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_chat import run_chat

        result = run_chat("Say the word 'hello'", timeout=30)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result
        assert "elapsed_s" in result
        assert "backend" in result

    @requires_backend
    def test_chat_content_not_empty_on_success(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_chat import run_chat

        result = run_chat("Say the word 'hello'", timeout=30)
        if result["status"] == "success":
            assert len(result["content"]) > 0

    def test_chat_graceful_error_without_backend(self) -> None:
        """Even without a backend, run_chat should return a dict, not raise."""
        from codomyrmex.agents.hermes.scripts.run_chat import run_chat

        result = run_chat("test", backend="nonexistent", timeout=5)
        assert isinstance(result, dict)
        assert "status" in result


# ═══════════════════════════════════════════════════════════════════════
# 3. Stream
# ═══════════════════════════════════════════════════════════════════════


class TestRunStream:
    """Tests for ``run_stream``."""

    @requires_backend
    def test_stream_returns_lines(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_stream import run_stream

        result = run_stream("Count to 3", timeout=30)
        assert isinstance(result, dict)
        assert "lines" in result
        assert isinstance(result["lines"], list)
        assert "line_count" in result


# ═══════════════════════════════════════════════════════════════════════
# 4. Session
# ═══════════════════════════════════════════════════════════════════════


class TestRunSession:
    """Tests for ``run_session`` — uses in-memory SQLite."""

    def test_session_persistence_roundtrip(self) -> None:
        """Session must persist and reload from SQLite (in-memory)."""
        from codomyrmex.agents.hermes.session import (
            HermesSession,
            SQLiteSessionStore,
        )

        store = SQLiteSessionStore(db_path=":memory:")
        session = HermesSession(session_id="test-001")
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        store.save(session)

        reloaded = store.load("test-001")
        assert reloaded is not None
        assert reloaded.session_id == "test-001"
        assert reloaded.message_count == 2
        assert reloaded.messages[0]["role"] == "user"
        assert reloaded.messages[1]["content"] == "Hi there!"
        store.close()

    def test_session_list_and_delete(self) -> None:
        from codomyrmex.agents.hermes.session import (
            HermesSession,
            SQLiteSessionStore,
        )

        store = SQLiteSessionStore(db_path=":memory:")
        s1 = HermesSession(session_id="s1")
        s2 = HermesSession(session_id="s2")
        store.save(s1)
        store.save(s2)

        ids = store.list_sessions()
        assert "s1" in ids
        assert "s2" in ids

        deleted = store.delete("s1")
        assert deleted is True

        remaining = store.list_sessions()
        assert "s1" not in remaining
        assert "s2" in remaining
        store.close()

    def test_in_memory_session_store(self) -> None:
        from codomyrmex.agents.hermes.session import (
            HermesSession,
            InMemorySessionStore,
        )

        store = InMemorySessionStore()
        session = HermesSession(session_id="mem-01")
        session.add_message("user", "test")
        store.save(session)

        loaded = store.load("mem-01")
        assert loaded is not None
        assert loaded.session_id == "mem-01"
        assert loaded.message_count == 1

        assert store.delete("mem-01") is True
        assert store.load("mem-01") is None
        assert store.delete("nonexistent") is False

    def test_session_properties(self) -> None:
        from codomyrmex.agents.hermes.session import HermesSession

        s = HermesSession()
        assert s.message_count == 0
        assert s.last_message is None

        s.add_message("user", "hi")
        assert s.message_count == 1
        assert s.last_message == {"role": "user", "content": "hi"}


# ═══════════════════════════════════════════════════════════════════════
# 5. Templates
# ═══════════════════════════════════════════════════════════════════════


class TestTemplates:
    """Tests for template rendering and the TemplateLibrary."""

    def test_all_builtin_templates_render(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_template import render_template

        for name in ("code_review", "task_decomposition", "documentation", "debugging"):
            result = render_template(name)
            assert result["template_name"] == name
            assert len(result["rendered_prompt"]) > 0
            assert len(result["system_prompt"]) > 0

    def test_template_library_registration(self) -> None:
        from codomyrmex.agents.hermes.templates import TemplateLibrary
        from codomyrmex.agents.hermes.templates.models import PromptTemplate

        lib = TemplateLibrary()
        assert lib.has("code_review")
        assert not lib.has("custom_template")

        custom = PromptTemplate(
            name="custom_template",
            system_prompt="You are custom.",
            user_template="Do {action}.",
            variables=["action"],
        )
        lib.register(custom)
        assert lib.has("custom_template")
        assert "custom_template" in lib.list_templates()

        got = lib.get("custom_template")
        assert got.render(action="something") == "Do something."

    def test_template_render_raises_on_missing_vars(self) -> None:
        from codomyrmex.agents.hermes.templates.models import PromptTemplate

        t = PromptTemplate(
            name="strict",
            user_template="{a} and {b}",
            variables=["a", "b"],
        )
        with pytest.raises(KeyError):
            t.render(a="x")  # missing b

    def test_template_render_safe_with_missing_vars(self) -> None:
        from codomyrmex.agents.hermes.templates.models import PromptTemplate

        t = PromptTemplate(
            name="safe",
            user_template="{a} and {b}",
            variables=["a", "b"],
        )
        rendered = t.render_safe(a="x")
        assert "x" in rendered
        assert "{b}" in rendered

    def test_list_available_templates(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_template import (
            list_available_templates,
        )

        templates = list_available_templates()
        assert isinstance(templates, list)
        assert len(templates) >= 4
        assert "code_review" in templates

    @requires_backend
    def test_template_execution(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_template import run_template

        result = run_template("code_review")
        assert isinstance(result, dict)
        assert "status" in result
        assert "template" in result


# ═══════════════════════════════════════════════════════════════════════
# 6. Pipeline
# ═══════════════════════════════════════════════════════════════════════


class TestRunPipeline:
    """Tests for ``run_pipeline``."""

    @requires_backend
    def test_pipeline_returns_all_stages(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_pipeline import run_pipeline

        result = run_pipeline(db_path=":memory:")
        assert isinstance(result, dict)
        assert "stages" in result
        assert "status" in result["stages"]
        assert "templates" in result["stages"]
        assert "chat" in result["stages"]
        assert "session" in result["stages"]
        assert "pipeline_status" in result
        assert "total_elapsed_s" in result


# ═══════════════════════════════════════════════════════════════════════
# 7. Evolution Bridge
# ═══════════════════════════════════════════════════════════════════════


class TestRunEvolutionBridge:
    """Tests for ``run_evolution_bridge``."""

    def test_evolution_config(self) -> None:
        """EvolutionConfig instantiation with custom values."""
        try:
            from evolution.core.config import EvolutionConfig

            config = EvolutionConfig(
                iterations=3,
                population_size=2,
                hermes_agent_path=Path("/tmp"),
            )
            assert config.iterations == 3
            assert config.population_size == 2
            assert config.max_skill_size == 15_000
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_constraint_validator_size(self) -> None:
        """ConstraintValidator correctly validates size limits."""
        try:
            from evolution.core.config import EvolutionConfig
            from evolution.core.constraints import ConstraintValidator

            config = EvolutionConfig(max_skill_size=50, hermes_agent_path=Path("/tmp"))
            validator = ConstraintValidator(config)

            # Passing size — "short" is under 50 chars
            results = validator.validate_all("short", "skill")
            size_result = next(r for r in results if r.constraint_name == "size_limit")
            assert size_result.passed

            # Failing size — 100 chars > 50 limit
            results = validator.validate_all("x" * 100, "skill")
            size_result = next(r for r in results if r.constraint_name == "size_limit")
            assert not size_result.passed
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_fitness_score_composite(self) -> None:
        """FitnessScore composite calculation is correct."""
        try:
            from evolution.core.fitness import FitnessScore

            score = FitnessScore(
                correctness=1.0,
                procedure_following=1.0,
                conciseness=1.0,
                length_penalty=0.0,
            )
            # 0.5*1 + 0.3*1 + 0.2*1 - 0 = 1.0
            assert abs(score.composite - 1.0) < 1e-6

            score2 = FitnessScore(
                correctness=0.0,
                procedure_following=0.0,
                conciseness=0.0,
                length_penalty=0.1,
            )
            assert score2.composite == 0.0  # max(0, 0 - 0.1) = 0
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_eval_example_roundtrip(self) -> None:
        """EvalExample serialization round-trip."""
        try:
            from evolution.core.dataset_builder import EvalExample

            ex = EvalExample(
                task_input="test input",
                expected_behavior="test behavior",
                difficulty="hard",
            )
            restored = EvalExample.from_dict(ex.to_dict())
            assert restored.task_input == ex.task_input
            assert restored.difficulty == "hard"
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_skill_reassemble(self) -> None:
        """reassemble_skill produces valid YAML-fronted markdown."""
        try:
            from evolution.skills.skill_module import reassemble_skill

            result = reassemble_skill("name: demo\ndescription: test", "# Body")
            assert result.startswith("---")
            assert "name: demo" in result
            assert "# Body" in result
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_constraint_growth_and_structure(self) -> None:
        """Growth limits and skill structure validation."""
        try:
            from evolution.core.config import EvolutionConfig
            from evolution.core.constraints import ConstraintValidator

            config = EvolutionConfig(
                max_skill_size=10_000,
                max_prompt_growth=0.1,
                hermes_agent_path=Path("/tmp"),
            )
            validator = ConstraintValidator(config)

            # Growth too large (>10%)
            baseline = "hello"
            grown = "hello" + " world" * 50
            results = validator.validate_all(grown, "skill", baseline_text=baseline)
            growth_r = next(r for r in results if r.constraint_name == "growth_limit")
            assert not growth_r.passed

            # Valid skill structure
            valid = "---\nname: x\ndescription: y\n---\n\nBody"
            results = validator.validate_all(valid, "skill")
            struct_r = next(
                r for r in results if r.constraint_name == "skill_structure"
            )
            assert struct_r.passed

            # Invalid structure (no frontmatter)
            invalid = "Just a body with no frontmatter"
            results = validator.validate_all(invalid, "skill")
            struct_r = next(
                r for r in results if r.constraint_name == "skill_structure"
            )
            assert not struct_r.passed
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_parse_score_edge_cases(self) -> None:
        """_parse_score handles edge cases."""
        try:
            from evolution.core.fitness import _parse_score

            assert _parse_score(0.5) == 0.5
            assert _parse_score(2.0) == 1.0
            assert _parse_score(-1.0) == 0.0
            assert _parse_score("0.75") == 0.75
            assert _parse_score("garbage") == 0.5
            assert _parse_score(None) == 0.5
        except ImportError:
            pytest.skip("evolution submodule not available")

    def test_eval_dataset_splits(self) -> None:
        """EvalDataset correctly aggregates splits."""
        try:
            from evolution.core.dataset_builder import EvalDataset, EvalExample

            dataset = EvalDataset(
                train=[EvalExample(task_input="t1", expected_behavior="e1")],
                val=[EvalExample(task_input="t2", expected_behavior="e2")],
                holdout=[],
            )
            assert len(dataset.all_examples) == 2
            assert len(dataset.train) == 1
            assert len(dataset.holdout) == 0
        except ImportError:
            pytest.skip("evolution submodule not available")


# ═══════════════════════════════════════════════════════════════════════
# 8. MCP Tools
# ═══════════════════════════════════════════════════════════════════════


class TestRunMCPTools:
    """Tests for ``run_mcp_tools``."""

    def test_mcp_status_returns_dict(self) -> None:
        from codomyrmex.agents.hermes.mcp_tools import hermes_status

        result = hermes_status()
        assert isinstance(result, dict)
        assert "status" in result

    @requires_backend
    def test_mcp_execute_returns_dict(self) -> None:
        from codomyrmex.agents.hermes.mcp_tools import hermes_execute

        result = hermes_execute(prompt="Say hello", timeout=30)
        assert isinstance(result, dict)
        assert "status" in result
        assert "content" in result

    def test_mcp_skills_returns_dict(self) -> None:
        from codomyrmex.agents.hermes.mcp_tools import hermes_skills_list

        result = hermes_skills_list()
        assert isinstance(result, dict)
        assert "status" in result

    def test_run_mcp_tools_consolidated(self) -> None:
        from codomyrmex.agents.hermes.scripts.run_mcp_tools import run_mcp_tools

        result = run_mcp_tools()
        assert isinstance(result, dict)
        for key in (
            "status_tool",
            "execute_tool",
            "skills_tool",
            "template_list_tool",
            "template_render_tool",
            "stream_tool",
        ):
            assert key in result, f"missing key: {key}"
        assert result["all_have_status_key"] is True
        assert "total_elapsed_s" in result


# ═══════════════════════════════════════════════════════════════════════
# 9. HermesClient Direct
# ═══════════════════════════════════════════════════════════════════════


class TestHermesClientDirect:
    """Direct tests for HermesClient construction and properties."""

    def test_client_instantiation(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient()
        assert client.active_backend in ("cli", "ollama", "none")
        assert isinstance(client.ollama_model, str)

    def test_client_backend_override(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(
            config={"hermes_backend": "ollama", "hermes_model": "test-model"}
        )
        assert client.ollama_model == "test-model"

    def test_hermes_error_has_command(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesError

        err = HermesError("test failure", command="hermes chat")
        assert "test failure" in str(err)
        assert err.command == "hermes chat"

    def test_get_hermes_status(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient()
        status = client.get_hermes_status()
        assert isinstance(status, dict)
        assert "active_backend" in status
        assert "cli_available" in status
        assert "ollama_available" in status


# ═══════════════════════════════════════════════════════════════════════
# 10. New MCP Tools
# ═══════════════════════════════════════════════════════════════════════


class TestNewMCPTools:
    """Tests for hermes_template_list, hermes_template_render, hermes_stream."""

    def test_template_list_returns_names(self) -> None:
        """hermes_template_list requires no backend and returns builtin names."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_template_list

        result = hermes_template_list()
        assert result["status"] == "success"
        assert isinstance(result["templates"], list)
        assert result["count"] >= 4
        assert "code_review" in result["templates"]
        assert "debugging" in result["templates"]

    def test_template_render_code_review(self) -> None:
        """hermes_template_render renders code_review with safe substitution."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_template_render

        result = hermes_template_render(
            template_name="code_review",
            variables={
                "language": "python",
                "code": "x = 1",
                "focus_areas": "correctness",
            },
        )
        assert result["status"] == "success"
        assert result["template_name"] == "code_review"
        assert "python" in result["rendered_prompt"]
        assert "x = 1" in result["rendered_prompt"]
        assert isinstance(result["system_prompt"], str)
        assert len(result["system_prompt"]) > 0
        assert "language" in result["variables_used"]

    def test_template_render_partial_vars_safe(self) -> None:
        """hermes_template_render leaves unresolved placeholders intact."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_template_render

        result = hermes_template_render(
            template_name="code_review",
            variables={"language": "go"},
        )
        assert result["status"] == "success"
        # Unreplaced variables stay as {placeholder}
        assert (
            "{code}" in result["rendered_prompt"]
            or "{focus_areas}" in result["rendered_prompt"]
        )

    def test_template_render_unknown_returns_error(self) -> None:
        """hermes_template_render returns error status for unknown template."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_template_render

        result = hermes_template_render(template_name="nonexistent_template_xyz")
        assert result["status"] == "error"
        assert "message" in result
        assert "nonexistent_template_xyz" in result["message"]

    def test_template_render_no_variables(self) -> None:
        """hermes_template_render works with no variables provided."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_template_render

        result = hermes_template_render(template_name="task_decomposition")
        assert result["status"] == "success"
        assert result["template_name"] == "task_decomposition"
        assert isinstance(result["rendered_prompt"], str)

    def test_stream_returns_expected_keys(self) -> None:
        """hermes_stream always returns status/lines/line_count regardless of backend."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_stream

        result = hermes_stream(prompt="hello", backend="cli", timeout=5)
        assert isinstance(result, dict)
        assert "status" in result
        assert "lines" in result
        assert "line_count" in result

    @requires_backend
    def test_stream_with_backend_returns_lines(self) -> None:
        """hermes_stream collects lines when a backend is available."""
        from codomyrmex.agents.hermes.mcp_tools import hermes_stream

        result = hermes_stream(prompt="Say the word 'hello'", timeout=30)
        assert result["status"] == "success"
        assert isinstance(result["lines"], list)
        assert result["line_count"] == len(result["lines"])
        assert "backend" in result

    def test_context_manager_sqlite_store(self) -> None:
        """SQLiteSessionStore works as a context manager."""
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        with SQLiteSessionStore(":memory:") as store:
            sess = HermesSession(session_id="ctx-test")
            sess.add_message("user", "hello")
            store.save(sess)
            loaded = store.load("ctx-test")
            assert loaded is not None
            assert loaded.message_count == 1

    def test_session_store_exported_from_package(self) -> None:
        """SessionStore protocol is importable from the hermes package."""
        from codomyrmex.agents.hermes import SessionStore, SQLiteSessionStore

        store = SQLiteSessionStore(":memory:")
        assert isinstance(store, SessionStore)
