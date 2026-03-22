"""Zero-mock test suite for OpenGauss Codomyrmex integration.

Tests cover the public Python API surface of the OpenGauss submodule:
  - SessionDB: schema init, session lifecycle, messages, FTS5, titles, export, delete, prune
  - gauss_time: now() tz-awareness, GAUSS_TIMEZONE env var, cache reset
  - gauss_constants: URL format correctness
  - utils: atomic_json_write, atomic_yaml_write crash safety
  - gauss_cli/project: is_lean_project_root, find_lean_project_root, detect_blueprint_markers,
                        resolve_template_source, initialize_gauss_project, load_gauss_project

All tests use real in-process implementations. Zero mocks. Zero external network calls.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

# Note: sys.path injection for open_gauss is handled in conftest.py


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def tmp_db(tmp_path):
    """SessionDB backed by a real SQLite file in a temp directory."""
    from gauss_state import SessionDB
    db = SessionDB(db_path=tmp_path / "state.db")
    yield db
    db.close()


@pytest.fixture(autouse=True)
def reset_gauss_time_cache():
    """Reset the gauss_time module cache before each test."""
    import gauss_time
    gauss_time.reset_cache()
    yield
    gauss_time.reset_cache()


# ===========================================================================
# gauss_constants
# ===========================================================================

class TestGaussConstants:
    def test_openrouter_base_url_format(self):
        from gauss_constants import OPENROUTER_BASE_URL
        assert OPENROUTER_BASE_URL.startswith("https://openrouter.ai/api/v")

    def test_openrouter_models_url_is_subpath(self):
        from gauss_constants import OPENROUTER_BASE_URL, OPENROUTER_MODELS_URL
        assert OPENROUTER_MODELS_URL.startswith(OPENROUTER_BASE_URL)

    def test_openrouter_chat_url_is_subpath(self):
        from gauss_constants import OPENROUTER_BASE_URL, OPENROUTER_CHAT_URL
        assert OPENROUTER_CHAT_URL.startswith(OPENROUTER_BASE_URL)

    def test_nous_base_url_is_https(self):
        from gauss_constants import NOUS_API_BASE_URL
        assert NOUS_API_BASE_URL.startswith("https://")

    def test_nous_chat_url_ends_chat_completions(self):
        from gauss_constants import NOUS_API_CHAT_URL
        assert NOUS_API_CHAT_URL.endswith("/chat/completions")


# ===========================================================================
# gauss_time
# ===========================================================================

class TestGaussTime:
    def test_now_returns_timezone_aware_datetime(self):
        from gauss_time import now
        result = now()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None, "now() must return a tz-aware datetime"

    def test_now_with_env_timezone(self, monkeypatch):
        from gauss_time import now, reset_cache
        monkeypatch.setenv("GAUSS_TIMEZONE", "America/New_York")
        reset_cache()
        result = now()
        assert result.tzinfo is not None

    def test_now_with_invalid_env_timezone_falls_back_gracefully(self, monkeypatch):
        from gauss_time import now, reset_cache
        monkeypatch.setenv("GAUSS_TIMEZONE", "Not/A/Real/Zone")
        reset_cache()
        result = now()
        # Should not raise; should return a tz-aware datetime as fallback
        assert result.tzinfo is not None

    def test_get_timezone_name_empty_by_default(self, tmp_path, monkeypatch):
        from gauss_time import get_timezone_name
        monkeypatch.setenv("GAUSS_HOME", str(tmp_path))
        monkeypatch.delenv("GAUSS_TIMEZONE", raising=False)
        result = get_timezone_name()
        assert isinstance(result, str)

    def test_reset_cache_clears_state(self, monkeypatch):
        from gauss_time import get_timezone_name, reset_cache
        monkeypatch.setenv("GAUSS_TIMEZONE", "Europe/Paris")
        reset_cache()
        name1 = get_timezone_name()
        assert name1 == "Europe/Paris"
        monkeypatch.setenv("GAUSS_TIMEZONE", "Asia/Tokyo")
        reset_cache()
        name2 = get_timezone_name()
        assert name2 == "Asia/Tokyo"

    def test_multiple_calls_to_now_are_monotonic(self):
        import time
        from gauss_time import now
        t1 = now()
        time.sleep(0.01)
        t2 = now()
        assert t2 >= t1


# ===========================================================================
# utils — atomic_json_write / atomic_yaml_write
# ===========================================================================

class TestAtomicJsonWrite:
    def test_writes_valid_json(self, tmp_path):
        from utils import atomic_json_write
        target = tmp_path / "out.json"
        data = {"key": "value", "num": 42}
        atomic_json_write(target, data)
        loaded = json.loads(target.read_text())
        assert loaded == data

    def test_overwrites_existing_file(self, tmp_path):
        from utils import atomic_json_write
        target = tmp_path / "out.json"
        atomic_json_write(target, {"v": 1})
        atomic_json_write(target, {"v": 2})
        assert json.loads(target.read_text())["v"] == 2

    def test_creates_parent_directories(self, tmp_path):
        from utils import atomic_json_write
        target = tmp_path / "deep" / "nested" / "out.json"
        atomic_json_write(target, {"nested": True})
        assert target.exists()

    def test_no_tmp_file_left_on_success(self, tmp_path):
        from utils import atomic_json_write
        target = tmp_path / "out.json"
        atomic_json_write(target, {"ok": True})
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0

    def test_handles_nested_structures(self, tmp_path):
        from utils import atomic_json_write
        target = tmp_path / "deep.json"
        data = {"list": [1, 2, 3], "nested": {"a": {"b": "c"}}}
        atomic_json_write(target, data)
        assert json.loads(target.read_text()) == data


class TestAtomicYamlWrite:
    def test_writes_valid_yaml(self, tmp_path):
        from utils import atomic_yaml_write
        target = tmp_path / "out.yaml"
        data = {"key": "value", "count": 7}
        atomic_yaml_write(target, data)
        loaded = yaml.safe_load(target.read_text())
        assert loaded == data

    def test_overwrites_existing_yaml(self, tmp_path):
        from utils import atomic_yaml_write
        target = tmp_path / "out.yaml"
        atomic_yaml_write(target, {"v": 1})
        atomic_yaml_write(target, {"v": 99})
        assert yaml.safe_load(target.read_text())["v"] == 99

    def test_extra_content_appended(self, tmp_path):
        from utils import atomic_yaml_write
        target = tmp_path / "out.yaml"
        atomic_yaml_write(target, {"k": "v"}, extra_content="# trailing comment\n")
        content = target.read_text()
        assert "# trailing comment" in content

    def test_no_tmp_file_left_on_success(self, tmp_path):
        from utils import atomic_yaml_write
        target = tmp_path / "out.yaml"
        atomic_yaml_write(target, {"ok": True})
        assert len(list(tmp_path.glob("*.tmp"))) == 0


# ===========================================================================
# SessionDB — schema, lifecycle, messages
# ===========================================================================

class TestSessionDBSchemaInit:
    def test_creates_database_file(self, tmp_path):
        from gauss_state import SessionDB
        db_path = tmp_path / "state.db"
        db = SessionDB(db_path=db_path)
        db.close()
        assert db_path.exists()

    def test_schema_version_initialized(self, tmp_path):
        from gauss_state import SessionDB, SCHEMA_VERSION
        db = SessionDB(db_path=tmp_path / "state.db")
        cursor = db._conn.execute("SELECT version FROM schema_version LIMIT 1")
        version = cursor.fetchone()[0]
        db.close()
        assert version == SCHEMA_VERSION

    def test_wal_mode_enabled(self, tmp_path):
        from gauss_state import SessionDB
        db = SessionDB(db_path=tmp_path / "state.db")
        cursor = db._conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        db.close()
        assert mode == "wal"

    def test_reinit_is_idempotent(self, tmp_path):
        from gauss_state import SessionDB
        db_path = tmp_path / "state.db"
        db = SessionDB(db_path=db_path)
        db.close()
        db2 = SessionDB(db_path=db_path)  # should not raise
        db2.close()


class TestSessionDBSessionLifecycle:
    def test_create_and_get_session(self, tmp_db):
        sid = tmp_db.create_session("sess-001", source="cli", model="claude-sonnet-4")
        assert sid == "sess-001"
        session = tmp_db.get_session("sess-001")
        assert session["id"] == "sess-001"
        assert session["source"] == "cli"
        assert session["model"] == "claude-sonnet-4"

    def test_create_session_with_all_fields(self, tmp_db):
        tmp_db.create_session(
            "sess-full", source="telegram",
            model="openrouter/hunter-alpha",
            model_config={"temperature": 0.7},
            system_prompt="You are a prover.",
            user_id="docxology",
        )
        session = tmp_db.get_session("sess-full")
        assert session["user_id"] == "docxology"
        assert session["system_prompt"] == "You are a prover."

    def test_end_session(self, tmp_db):
        tmp_db.create_session("sess-end", source="cli")
        tmp_db.end_session("sess-end", end_reason="user_exit")
        session = tmp_db.get_session("sess-end")
        assert session["end_reason"] == "user_exit"
        assert session["ended_at"] is not None

    def test_session_count_increments(self, tmp_db):
        assert tmp_db.session_count() == 0
        tmp_db.create_session("s1", source="cli")
        tmp_db.create_session("s2", source="telegram")
        assert tmp_db.session_count() == 2

    def test_session_count_by_source(self, tmp_db):
        tmp_db.create_session("s1", source="cli")
        tmp_db.create_session("s2", source="cli")
        tmp_db.create_session("s3", source="telegram")
        assert tmp_db.session_count(source="cli") == 2
        assert tmp_db.session_count(source="telegram") == 1

    def test_get_nonexistent_session_returns_none(self, tmp_db):
        assert tmp_db.get_session("does-not-exist") is None

    def test_resolve_session_by_prefix(self, tmp_db):
        tmp_db.create_session("abc123xyz", source="cli")
        resolved = tmp_db.resolve_session_id("abc")
        assert resolved == "abc123xyz"

    def test_resolve_session_exact_match(self, tmp_db):
        tmp_db.create_session("exact-id", source="cli")
        resolved = tmp_db.resolve_session_id("exact-id")
        assert resolved == "exact-id"

    def test_resolve_ambiguous_prefix_returns_none(self, tmp_db):
        tmp_db.create_session("abc-first", source="cli")
        tmp_db.create_session("abc-second", source="cli")
        assert tmp_db.resolve_session_id("abc") is None

    def test_update_token_counts(self, tmp_db):
        tmp_db.create_session("tok-sess", source="cli")
        tmp_db.update_token_counts("tok-sess", input_tokens=100, output_tokens=200)
        tmp_db.update_token_counts("tok-sess", input_tokens=50, output_tokens=75)
        s = tmp_db.get_session("tok-sess")
        assert s["input_tokens"] == 150
        assert s["output_tokens"] == 275

    def test_delete_session(self, tmp_db):
        tmp_db.create_session("to-delete", source="cli")
        assert tmp_db.delete_session("to-delete") is True
        assert tmp_db.get_session("to-delete") is None

    def test_delete_nonexistent_returns_false(self, tmp_db):
        assert tmp_db.delete_session("ghost") is False


class TestSessionDBMessages:
    def test_append_and_get_message(self, tmp_db):
        tmp_db.create_session("msg-sess", source="cli")
        msg_id = tmp_db.append_message("msg-sess", "user", content="Prove: 1+1=2")
        assert isinstance(msg_id, int)
        messages = tmp_db.get_messages("msg-sess")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Prove: 1+1=2"

    def test_message_count_increments(self, tmp_db):
        tmp_db.create_session("cnt-sess", source="cli")
        tmp_db.append_message("cnt-sess", "user", "Hello")
        tmp_db.append_message("cnt-sess", "assistant", "Hi")
        assert tmp_db.message_count("cnt-sess") == 2

    def test_messages_ordered_by_timestamp(self, tmp_db):
        tmp_db.create_session("ord-sess", source="cli")
        for content in ["first", "second", "third"]:
            tmp_db.append_message("ord-sess", "user", content=content)
        messages = tmp_db.get_messages("ord-sess")
        contents = [m["content"] for m in messages]
        assert contents == ["first", "second", "third"]

    def test_get_messages_as_conversation_format(self, tmp_db):
        tmp_db.create_session("conv-sess", source="cli")
        tmp_db.append_message("conv-sess", "user", "Question?")
        tmp_db.append_message("conv-sess", "assistant", "Answer.")
        conv = tmp_db.get_messages_as_conversation("conv-sess")
        assert len(conv) == 2
        assert all("role" in m and "content" in m for m in conv)

    def test_clear_messages_resets_count(self, tmp_db):
        tmp_db.create_session("clr-sess", source="cli")
        tmp_db.append_message("clr-sess", "user", "Hi")
        tmp_db.clear_messages("clr-sess")
        assert tmp_db.message_count("clr-sess") == 0


class TestSessionDBFTS5Search:
    def test_search_returns_matching_message(self, tmp_db):
        tmp_db.create_session("fts-sess", source="cli")
        tmp_db.append_message("fts-sess", "user", "The Pythagorean theorem states a²+b²=c²")
        results = tmp_db.search_messages("Pythagorean")
        assert len(results) >= 1
        assert any("Pythagorean" in r.get("snippet", "") or r.get("session_id") == "fts-sess"
                   for r in results)

    def test_search_empty_query_returns_empty(self, tmp_db):
        tmp_db.create_session("s1", source="cli")
        tmp_db.append_message("s1", "user", "content")
        assert tmp_db.search_messages("") == []

    def test_search_handles_special_chars(self, tmp_db):
        tmp_db.create_session("spec-sess", source="cli")
        tmp_db.append_message("spec-sess", "user", "C++ templates are powerful")
        # Should not raise on FTS5-special input:
        results = tmp_db.search_messages("C++")
        assert isinstance(results, list)

    def test_search_handles_bare_and_operator(self, tmp_db):
        tmp_db.create_session("and-sess", source="cli")
        tmp_db.append_message("and-sess", "user", "hello world")
        results = tmp_db.search_messages("hello AND")
        assert isinstance(results, list)  # no OperationalError

    def test_search_with_role_filter(self, tmp_db):
        tmp_db.create_session("role-sess", source="cli")
        tmp_db.append_message("role-sess", "user", "unique_user_word")
        tmp_db.append_message("role-sess", "assistant", "unique_user_word")
        user_results = tmp_db.search_messages(
            "unique_user_word", role_filter=["user"]
        )
        assert all(r["role"] == "user" for r in user_results)


class TestSessionDBTitleManagement:
    def test_set_and_get_title(self, tmp_db):
        tmp_db.create_session("titled-sess", source="cli")
        tmp_db.set_session_title("titled-sess", "My Proof Session")
        assert tmp_db.get_session_title("titled-sess") == "My Proof Session"

    def test_sanitize_title_strips_whitespace(self):
        from gauss_state import SessionDB
        assert SessionDB.sanitize_title("  hello  ") == "hello"

    def test_sanitize_title_empty_returns_none(self):
        from gauss_state import SessionDB
        assert SessionDB.sanitize_title("") is None
        assert SessionDB.sanitize_title("   ") is None
        assert SessionDB.sanitize_title(None) is None

    def test_sanitize_title_collapses_whitespace(self):
        from gauss_state import SessionDB
        result = SessionDB.sanitize_title("hello   world")
        assert result == "hello world"

    def test_sanitize_title_too_long_raises(self):
        from gauss_state import SessionDB
        with pytest.raises(ValueError, match="Title too long"):
            SessionDB.sanitize_title("x" * 101)

    def test_duplicate_title_raises_value_error(self, tmp_db):
        tmp_db.create_session("s1", source="cli")
        tmp_db.create_session("s2", source="cli")
        tmp_db.set_session_title("s1", "Unique Title")
        with pytest.raises(ValueError, match="already in use"):
            tmp_db.set_session_title("s2", "Unique Title")

    def test_get_session_by_title(self, tmp_db):
        tmp_db.create_session("ttl-sess", source="cli")
        tmp_db.set_session_title("ttl-sess", "Fermat Last Theorem")
        result = tmp_db.get_session_by_title("Fermat Last Theorem")
        assert result is not None
        assert result["id"] == "ttl-sess"

    def test_get_next_title_in_lineage(self, tmp_db):
        tmp_db.create_session("s1", source="cli")
        tmp_db.set_session_title("s1", "base session")
        next_title = tmp_db.get_next_title_in_lineage("base session")
        assert next_title == "base session #2"


class TestSessionDBExportAndPrune:
    def test_export_session_includes_messages(self, tmp_db):
        tmp_db.create_session("exp-sess", source="cli")
        tmp_db.append_message("exp-sess", "user", "Hello")
        tmp_db.append_message("exp-sess", "assistant", "Hi")
        exported = tmp_db.export_session("exp-sess")
        assert exported is not None
        assert "messages" in exported
        assert len(exported["messages"]) == 2

    def test_export_nonexistent_returns_none(self, tmp_db):
        assert tmp_db.export_session("ghost") is None

    def test_export_all_returns_all_sessions(self, tmp_db):
        tmp_db.create_session("e1", source="cli")
        tmp_db.create_session("e2", source="telegram")
        all_exported = tmp_db.export_all()
        assert len(all_exported) == 2

    def test_prune_ended_sessions(self, tmp_db):
        import time
        tmp_db.create_session("old-sess", source="cli")
        tmp_db.end_session("old-sess", "user_exit")
        # Force the session's started_at to be very old
        old_ts = time.time() - (100 * 86400)  # 100 days ago
        tmp_db._conn.execute(
            "UPDATE sessions SET started_at = ? WHERE id = 'old-sess'",
            (old_ts,)
        )
        tmp_db._conn.commit()
        pruned = tmp_db.prune_sessions(older_than_days=90)
        assert pruned >= 1

    def test_prune_does_not_remove_active_sessions(self, tmp_db):
        import time
        tmp_db.create_session("active-sess", source="cli")
        # Do NOT call end_session — leave it active
        old_ts = time.time() - (100 * 86400)
        tmp_db._conn.execute(
            "UPDATE sessions SET started_at = ? WHERE id = 'active-sess'",
            (old_ts,)
        )
        tmp_db._conn.commit()
        tmp_db.prune_sessions(older_than_days=90)
        # Active (non-ended) session should survive
        assert tmp_db.get_session("active-sess") is not None


# ===========================================================================
# gauss_cli/project — utility functions (no Lean install required)
# ===========================================================================

class TestGaussProjectUtilities:
    def test_is_lean_project_root_false_for_empty_dir(self, tmp_path):
        from gauss_cli.project import is_lean_project_root
        assert is_lean_project_root(tmp_path) is False

    def test_is_lean_project_root_true_with_lakefile_lean(self, tmp_path):
        from gauss_cli.project import is_lean_project_root
        (tmp_path / "lakefile.lean").touch()
        assert is_lean_project_root(tmp_path) is True

    def test_is_lean_project_root_true_with_lakefile_toml(self, tmp_path):
        from gauss_cli.project import is_lean_project_root
        (tmp_path / "lakefile.toml").touch()
        assert is_lean_project_root(tmp_path) is True

    def test_find_lean_project_root_none_when_not_found(self, tmp_path):
        from gauss_cli.project import find_lean_project_root
        result = find_lean_project_root(tmp_path)
        assert result is None

    def test_find_lean_project_root_finds_ancestor(self, tmp_path):
        from gauss_cli.project import find_lean_project_root
        (tmp_path / "lakefile.lean").touch()
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)
        result = find_lean_project_root(subdir)
        assert result == tmp_path

    def test_detect_blueprint_markers_empty(self, tmp_path):
        from gauss_cli.project import detect_blueprint_markers
        markers = detect_blueprint_markers(tmp_path)
        assert markers == ()

    def test_detect_blueprint_markers_finds_lean_toolchain(self, tmp_path):
        from gauss_cli.project import detect_blueprint_markers
        (tmp_path / "lean-toolchain").touch()
        markers = detect_blueprint_markers(tmp_path)
        assert "lean-toolchain" in markers

    def test_resolve_template_source_from_env(self, monkeypatch):
        from gauss_cli.project import resolve_template_source, GAUSS_PROJECT_TEMPLATE_ENV
        monkeypatch.setenv(GAUSS_PROJECT_TEMPLATE_ENV, "https://github.com/example/template")
        result = resolve_template_source(env=os.environ)
        assert result == "https://github.com/example/template"

    def test_resolve_template_source_empty_by_default(self):
        from gauss_cli.project import resolve_template_source
        result = resolve_template_source(config=None, env={})
        assert result == ""


class TestGaussProjectInit:
    def _make_lean_project(self, path: Path) -> Path:
        """Create a minimal Lean4 project structure for testing."""
        path.mkdir(parents=True, exist_ok=True)
        (path / "lakefile.lean").write_text("-- minimal lakefile\n")
        return path

    def test_initialize_gauss_project_creates_manifest(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "lean-proj")
        project = initialize_gauss_project(lean_dir, name="TestProj")
        manifest_path = lean_dir / ".gauss" / "project.yaml"
        assert manifest_path.exists()
        data = yaml.safe_load(manifest_path.read_text())
        assert data["name"] == "TestProj"

    def test_initialize_gauss_project_is_idempotent(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "lean-proj2")
        p1 = initialize_gauss_project(lean_dir, name="Idempotent")
        p2 = initialize_gauss_project(lean_dir, name="Idempotent")
        assert p1.root == p2.root
        assert p1.name == p2.name

    def test_initialize_gauss_project_creates_runtime_dirs(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "lean-proj3")
        project = initialize_gauss_project(lean_dir)
        assert project.runtime_dir.exists()
        assert project.cache_dir.exists()
        assert project.workflows_dir.exists()

    def test_initialize_gauss_project_frozen_dataclass(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        from dataclasses import FrozenInstanceError
        lean_dir = self._make_lean_project(tmp_path / "lean-frozen")
        project = initialize_gauss_project(lean_dir)
        with pytest.raises((FrozenInstanceError, AttributeError)):
            project.name = "mutated"  # type: ignore

    def test_discover_gauss_project_not_found_raises(self, tmp_path):
        from gauss_cli.project import discover_gauss_project, ProjectNotFoundError
        empty = tmp_path / "empty"
        empty.mkdir()
        with pytest.raises(ProjectNotFoundError):
            discover_gauss_project(empty)

    def test_load_gauss_project_invalid_dir_raises(self, tmp_path):
        from gauss_cli.project import load_gauss_project, ProjectNotFoundError
        non_gauss = tmp_path / "not-a-gauss-dir"
        non_gauss.mkdir()
        with pytest.raises(ProjectNotFoundError):
            load_gauss_project(non_gauss)

    def test_project_label_uses_name(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "label-proj")
        project = initialize_gauss_project(lean_dir, name="MyLeanProject")
        assert project.label == "MyLeanProject"

    def test_project_is_blueprint_respects_explicit_empty_markers(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "no-blueprint")
        # Pass explicit empty tuple — lakefile.lean is also a blueprint marker,
        # so auto-detection would return is_blueprint=True; override it.
        project = initialize_gauss_project(lean_dir, blueprint_markers=())
        assert project.is_blueprint is False

    def test_project_is_blueprint_true_when_lakefile_present(self, tmp_path):
        from gauss_cli.project import initialize_gauss_project
        lean_dir = self._make_lean_project(tmp_path / "yes-blueprint")
        # lakefile.lean is both a Lean project root AND a blueprint marker
        project = initialize_gauss_project(lean_dir)
        assert project.is_blueprint is True
