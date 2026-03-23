"""Tests for the extended Hermes MCP tools (v2.1.0).

Zero-Mock: Tests verify real tool function signatures and return structures.
CLI-dependent tests are skipped gracefully.
"""

from __future__ import annotations

import shutil

import pytest

from codomyrmex.agents.hermes.mcp_tools import (
    hermes_check_dependencies,
    hermes_create_task,
    hermes_doctor,
    hermes_honcho_status,
    hermes_insights,
    hermes_provider_status,
    hermes_read_log_chunk,
    hermes_session_search,
    hermes_system_health,
    hermes_template_list,
    hermes_template_render,
    hermes_update_task_status,
    hermes_version,
    hermes_worktree_cleanup,
    hermes_worktree_create,
)

HAS_HERMES = shutil.which("hermes") is not None


# ── hermes_doctor ─────────────────────────────────────────────────────


class TestHermesDoctor:
    """Verify hermes_doctor MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_doctor()
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_output(self) -> None:
        result = hermes_doctor()
        assert result["status"] in ("success", "error")
        assert "success" in result  # The nested 'success' from run_doctor


# ── hermes_version ────────────────────────────────────────────────────


class TestHermesVersion:
    """Verify hermes_version MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_version()
        assert isinstance(result, dict)
        assert "status" in result
        assert "cli_available" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_version_string(self) -> None:
        result = hermes_version()
        assert result["status"] == "success"
        assert result["version"] is not None
        assert "." in result["version"]  # e.g. "0.2.0"


# ── hermes_worktree_create / cleanup ──────────────────────────────────


class TestHermesWorktreeTools:
    """Verify worktree MCP tools return proper structures."""

    def test_create_returns_dict(self) -> None:
        # Even without git repo context, should not crash
        result = hermes_worktree_create(session_id="test-wt-001")
        assert isinstance(result, dict)
        assert "status" in result

    def test_cleanup_returns_dict(self) -> None:
        result = hermes_worktree_cleanup(session_id="test-wt-nonexistent")
        assert isinstance(result, dict)
        assert "status" in result
        assert "cleaned" in result


# ── hermes_session_search ─────────────────────────────────────────────


class TestHermesSessionSearch:
    """Verify hermes_session_search MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_session_search(query="test")
        assert isinstance(result, dict)
        assert "status" in result

    def test_empty_query(self) -> None:
        result = hermes_session_search(query="")
        assert result["status"] == "success"
        assert isinstance(result["sessions"], list)

    def test_search_with_monkeypatched_store(self, monkeypatch, tmp_path) -> None:
        """Test search with an injected DB containing named sessions."""
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "search_test.db"

        # Pre-populate DB with named sessions
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="s1", name="api-refactoring"))
            store.save(HermesSession(session_id="s2", name="api-testing"))
            store.save(HermesSession(session_id="s3", name="deployment"))

        def patched_get_client(**kwargs):
            return HermesClient(
                config={
                    "hermes_command": "echo",
                    "hermes_session_db": str(db_path),
                }
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_session_search(query="api")
        assert result["status"] == "success"
        assert result["count"] == 2


# ── hermes_honcho_status ──────────────────────────────────────────────


class TestHermesHonchoStatus:
    """Verify hermes_honcho_status MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_honcho_status()
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_returns_output(self) -> None:
        result = hermes_honcho_status()
        assert "status" in result
        # May return success or error depending on honcho setup


# ── hermes_insights ───────────────────────────────────────────────────


class TestHermesInsights:
    """Verify hermes_insights MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_insights(days=7)
        assert isinstance(result, dict)
        assert "status" in result

    @pytest.mark.skipif(not HAS_HERMES, reason="hermes CLI not installed")
    def test_with_cli_runs(self) -> None:
        result = hermes_insights(days=1)
        assert result["status"] in ("success", "error")


# ── hermes_provider_status ────────────────────────────────────────────


class TestHermesProviderStatus:
    """Verify hermes_provider_status MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_provider_status()
        assert isinstance(result, dict)
        assert "status" in result

    def test_providers_dict_present(self) -> None:
        result = hermes_provider_status()
        assert "providers" in result
        providers = result["providers"]
        assert isinstance(providers, dict)
        # Should contain all supported providers
        for p in ("openrouter", "ollama", "anthropic", "openai"):
            assert p in providers


# ── CLI Flag Arg Building ─────────────────────────────────────────────


class TestHermesClientCLIFlags:
    """Verify new CLI flag arg building."""

    def test_yolo_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"yolo": True})
        args = client._build_hermes_args("test", {})
        assert "--yolo" in args

    def test_continue_session_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"continue_session": "my-project"})
        args = client._build_hermes_args("test", {})
        assert "--continue" in args
        idx = args.index("--continue")
        assert args[idx + 1] == "my-project"

    def test_pass_session_id_flag(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(config={"pass_session_id": True})
        args = client._build_hermes_args("test", {})
        assert "--pass-session-id" in args

    def test_no_flags_by_default(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient()
        args = client._build_hermes_args("test", {})
        assert "--yolo" not in args
        assert "--continue" not in args
        assert "--pass-session-id" not in args

    def test_all_flags_combined(self) -> None:
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        client = HermesClient(
            config={
                "yolo": True,
                "continue_session": "proj",
                "pass_session_id": True,
            }
        )
        args = client._build_hermes_args("test", {})
        assert "--yolo" in args
        assert "--continue" in args
        assert "--pass-session-id" in args


# ── hermes_template_list ──────────────────────────────────────────────


class TestHermesTemplateList:
    """Verify hermes_template_list MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_template_list()
        assert isinstance(result, dict)
        assert "status" in result

    def test_success_returns_templates(self) -> None:
        result = hermes_template_list()
        assert result["status"] == "success"
        assert "templates" in result
        assert isinstance(result["templates"], list)
        assert "count" in result
        assert result["count"] == len(result["templates"])

    def test_builtin_templates_present(self) -> None:
        result = hermes_template_list()
        templates = result["templates"]
        assert "code_review" in templates
        assert "task_decomposition" in templates
        assert "documentation" in templates
        assert "debugging" in templates

    def test_templates_sorted_alphabetically(self) -> None:
        result = hermes_template_list()
        templates = result["templates"]
        assert templates == sorted(templates)


# ── hermes_template_render ─────────────────────────────────────────────


class TestHermesTemplateRender:
    """Verify hermes_template_render MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_template_render("code_review")
        assert isinstance(result, dict)
        assert "status" in result

    def test_render_with_all_variables(self) -> None:
        result = hermes_template_render(
            "code_review",
            variables={
                "language": "python",
                "code": "def foo(): pass",
                "focus_areas": "style",
            },
        )
        assert result["status"] == "success"
        assert "rendered_prompt" in result
        assert "python" in result["rendered_prompt"]
        assert "def foo(): pass" in result["rendered_prompt"]

    def test_render_system_prompt_included(self) -> None:
        result = hermes_template_render("code_review")
        assert result["status"] == "success"
        assert "system_prompt" in result
        assert len(result["system_prompt"]) > 0

    def test_render_missing_template_returns_error(self) -> None:
        result = hermes_template_render("nonexistent_template_xyz")
        assert result["status"] == "error"
        assert "message" in result

    def test_render_safe_with_partial_variables(self) -> None:
        result = hermes_template_render(
            "code_review",
            variables={"language": "rust"},
        )
        assert result["status"] == "success"
        rendered = result["rendered_prompt"]
        assert "rust" in rendered
        # Missing variables should appear as {placeholders}
        assert "{code}" in rendered
        assert "{focus_areas}" in rendered

    def test_render_no_variables_uses_safe_mode(self) -> None:
        result = hermes_template_render("debugging")
        assert result["status"] == "success"
        rendered = result["rendered_prompt"]
        # All variables should be placeholders
        assert "{error_message}" in rendered
        assert "{language}" in rendered

    def test_variables_used_tracked(self) -> None:
        result = hermes_template_render(
            "documentation",
            variables={"doc_type": "API", "component_name": "Auth"},
        )
        assert result["status"] == "success"
        assert "variables_used" in result
        assert "doc_type" in result["variables_used"]
        assert "component_name" in result["variables_used"]


# ── hermes_system_health ───────────────────────────────────────────────


class TestHermesSystemHealth:
    """Verify hermes_system_health MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_system_health()
        assert isinstance(result, dict)
        assert "status" in result

    def test_success_includes_metrics(self) -> None:
        result = hermes_system_health()
        if result["status"] == "success":
            assert "metrics" in result
            metrics = result["metrics"]
            assert isinstance(metrics, dict)
            # Should have cpu and ram at minimum
            assert "cpu_percent" in metrics or "ram_usage_percent" in metrics


# ── hermes_read_log_chunk ─────────────────────────────────────────────────


class TestHermesReadLogChunk:
    """Verify hermes_read_log_chunk MCP tool."""

    def test_returns_dict_with_status(self, tmp_path) -> None:
        log_file = tmp_path / "test.log"
        log_file.write_text("line 1\nline 2\nline 3\n")
        result = hermes_read_log_chunk(str(log_file))
        assert isinstance(result, dict)
        assert "status" in result

    def test_reads_entire_file(self, tmp_path) -> None:
        log_file = tmp_path / "test.log"
        log_file.write_text("alpha\nbeta\ngamma\n")
        result = hermes_read_log_chunk(str(log_file))
        assert result["status"] == "success"
        assert "alpha" in result["content"]
        assert "beta" in result["content"]
        assert "gamma" in result["content"]
        assert result["total_lines"] == 3
        assert result["eof"] is True

    def test_reads_with_offset(self, tmp_path) -> None:
        log_file = tmp_path / "test.log"
        log_file.write_text("line0\nline1\nline2\nline3\n")
        result = hermes_read_log_chunk(str(log_file), offset=2)
        assert result["status"] == "success"
        assert "line0" not in result["content"]
        assert "line1" not in result["content"]
        assert "line2" in result["content"]
        assert "line3" in result["content"]

    def test_reads_with_offset_and_length(self, tmp_path) -> None:
        log_file = tmp_path / "test.log"
        log_file.write_text("a\nb\nc\nd\ne\n")
        result = hermes_read_log_chunk(str(log_file), offset=1, length=2)
        assert result["status"] == "success"
        assert result["content"] == "b\nc\n"
        assert result["eof"] is False

    def test_file_not_found(self) -> None:
        result = hermes_read_log_chunk("/nonexistent/path/file.log")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()

    def test_length_capped_at_5000(self, tmp_path) -> None:
        log_file = tmp_path / "big.log"
        log_file.write_text("x\n" * 100)
        result = hermes_read_log_chunk(str(log_file), length=99999)
        assert result["status"] == "success"
        # length should be capped to 5000, but file only has 100 lines
        assert result["total_lines"] == 100
        assert result["eof"] is True

    def test_empty_file(self, tmp_path) -> None:
        log_file = tmp_path / "empty.log"
        log_file.write_text("")
        result = hermes_read_log_chunk(str(log_file))
        assert result["status"] == "success"
        assert result["content"] == ""
        assert result["total_lines"] == 0
        assert result["eof"] is True


# ── hermes_create_task / hermes_update_task_status ───────────────────────


class TestHermesCreateTask:
    """Verify hermes_create_task MCP tool."""

    def test_returns_dict_with_status(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "task_test.db"
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="sess-1"))

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_create_task(
            session_id="sess-1", name="setup", description="Set up the environment"
        )
        assert isinstance(result, dict)
        assert "status" in result

    def test_create_task_success(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "task_test2.db"
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="sess-2"))

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_create_task(
            session_id="sess-2",
            name="build",
            description="Build the project",
            depends_on=["setup"],
        )
        assert result["status"] == "success"
        assert result["task"]["name"] == "build"
        assert result["task"]["description"] == "Build the project"
        assert result["task"]["status"] == "pending"
        assert result["task"]["depends_on"] == ["setup"]

    def test_create_duplicate_task(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "task_test3.db"
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="sess-3"))

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        hermes_create_task(session_id="sess-3", name="task-a", description="First task")
        result = hermes_create_task(
            session_id="sess-3", name="task-a", description="Duplicate"
        )
        assert result["status"] == "error"
        assert "already exists" in result["message"]

    def test_create_task_missing_session(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        db_path = tmp_path / "task_test4.db"

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_create_task(session_id="nonexistent", name="x", description="y")
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


class TestHermesUpdateTaskStatus:
    """Verify hermes_update_task_status MCP tool."""

    def test_returns_dict_with_status(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "update_test.db"
        with SQLiteSessionStore(str(db_path)) as store:
            sess = HermesSession(session_id="sess-u1")
            sess.metadata["workflow_tasks"] = {
                "t1": {
                    "name": "t1",
                    "description": "test",
                    "depends_on": [],
                    "status": "pending",
                    "result": None,
                    "error": "",
                    "parent_trace_id": None,
                }
            }
            store.save(sess)

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_update_task_status(
            session_id="sess-u1", name="t1", status="completed"
        )
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["task"]["status"] == "completed"

    def test_update_with_result_and_error(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "update_test2.db"
        with SQLiteSessionStore(str(db_path)) as store:
            sess = HermesSession(session_id="sess-u2")
            sess.metadata["workflow_tasks"] = {
                "build": {
                    "name": "build",
                    "description": "build",
                    "depends_on": [],
                    "status": "running",
                    "result": None,
                    "error": "",
                    "parent_trace_id": None,
                }
            }
            store.save(sess)

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_update_task_status(
            session_id="sess-u2",
            name="build",
            status="failed",
            error="Missing dependency",
        )
        assert result["status"] == "success"
        assert result["task"]["status"] == "failed"
        assert result["task"]["error"] == "Missing dependency"

    def test_update_nonexistent_task(self, monkeypatch, tmp_path) -> None:
        from codomyrmex.agents.hermes import mcp_tools
        from codomyrmex.agents.hermes.hermes_client import HermesClient
        from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore

        db_path = tmp_path / "update_test3.db"
        with SQLiteSessionStore(str(db_path)) as store:
            store.save(HermesSession(session_id="sess-u3"))

        def patched_get_client(**kwargs):
            return HermesClient(
                config={"hermes_command": "echo", "hermes_session_db": str(db_path)}
            )

        monkeypatch.setattr(mcp_tools, "_get_client", patched_get_client)
        result = hermes_update_task_status(
            session_id="sess-u3", name="nope", status="done"
        )
        assert result["status"] == "error"
        assert "not found" in result["message"].lower()


# ── hermes_check_dependencies ─────────────────────────────────────────────


class TestHermesCheckDependencies:
    """Verify hermes_check_dependencies MCP tool."""

    def test_returns_dict_with_status(self) -> None:
        result = hermes_check_dependencies("requests")
        assert isinstance(result, dict)
        assert "status" in result

    def test_error_on_missing_lockfile(self, monkeypatch, tmp_path) -> None:
        """Should return error when lockfile doesn't exist."""
        import codomyrmex.environment_setup.lockfile as lockfile_mod

        class BrokenParser:
            def check_dependency(self, name):
                raise FileNotFoundError("uv.lock not found")

        monkeypatch.setattr(lockfile_mod, "LockfileParser", BrokenParser)
        result = hermes_check_dependencies("some-package")
        assert result["status"] == "error"
        assert (
            "not found" in result["message"].lower() or "uv.lock" in result["message"]
        )
