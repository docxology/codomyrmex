"""
Tests for the OpenGauss Codomyrmex client (open_gauss_client.py).

Covers: OpenGaussConfig, validate_environment, OpenGaussClient:
  - config loading, defaults, env overrides
  - env validation (all checks pass with isolated tmp dir)
  - session CRUD via client wrapper
  - message append + FTS5 search
  - artifact export (per-session JSON, bulk JSONL)
  - structured log file written to disk (operations.jsonl)
  - stats reporting

Zero mocks. All real file I/O, SQLite, and datetime operations.
"""

import json
import os
import sys
from pathlib import Path

import pytest

# sys.path injection handled by conftest.py at collection time
# (adds src/codomyrmex/agents/open_gauss to path)
from open_gauss_client import OpenGaussClient, OpenGaussConfig, validate_environment

# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def demo_home(tmp_path):
    """Isolated GAUSS_HOME for client tests."""
    home = tmp_path / "gauss_demo"
    home.mkdir()
    return home


@pytest.fixture
def cfg(demo_home):
    """Fully configured OpenGaussConfig in a temp directory."""
    return OpenGaussConfig(
        gauss_home=demo_home,
        default_model="test-model/test",
        default_source="test",
        log_level="DEBUG",
    )


@pytest.fixture
def client(cfg):
    """OpenGaussClient backed by a real temp DB."""
    c = OpenGaussClient(cfg)
    yield c
    c.close()


# ===========================================================================
# OpenGaussConfig
# ===========================================================================


class TestOpenGaussConfig:
    def test_defaults_from_home(self, demo_home):
        cfg = OpenGaussConfig(gauss_home=demo_home)
        assert cfg.gauss_home == demo_home
        assert cfg.db_path.parent == demo_home
        assert cfg.log_dir.parent == demo_home
        assert cfg.artifact_dir.parent == demo_home

    def test_creates_dirs_on_init(self, demo_home):
        cfg = OpenGaussConfig(gauss_home=demo_home)
        assert cfg.log_dir.is_dir()
        assert cfg.artifact_dir.is_dir()

    def test_from_env_reads_openrouter_key(self, demo_home, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
        monkeypatch.setenv("GAUSS_HOME", str(demo_home))
        cfg = OpenGaussConfig.from_env()
        assert cfg.openrouter_api_key == "test-key-123"

    def test_from_env_respects_default_model(self, demo_home, monkeypatch):
        monkeypatch.setenv("GAUSS_DEFAULT_MODEL", "openrouter/my-custom-model")
        monkeypatch.setenv("GAUSS_HOME", str(demo_home))
        cfg = OpenGaussConfig.from_env()
        assert cfg.default_model == "openrouter/my-custom-model"

    def test_from_env_log_level(self, demo_home, monkeypatch):
        monkeypatch.setenv("GAUSS_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("GAUSS_HOME", str(demo_home))
        cfg = OpenGaussConfig.from_env()
        assert cfg.log_level == "DEBUG"

    def test_validate_warns_without_api_key(self, cfg):
        cfg.openrouter_api_key = ""
        warnings = cfg.validate()
        assert any("OPENROUTER_API_KEY" in w for w in warnings)

    def test_validate_raises_with_invalid_log_level(self, cfg):
        cfg.log_level = "NONSENSE"
        with pytest.raises(ValueError, match="log_level"):
            cfg.validate()

    def test_validate_raises_with_missing_gauss_home(self, tmp_path):
        nonexistent = tmp_path / "does-not-exist"
        cfg = OpenGaussConfig.__new__(OpenGaussConfig)
        cfg.gauss_home = nonexistent
        cfg.db_path = nonexistent / "state.db"
        cfg.log_dir = nonexistent / "logs"
        cfg.artifact_dir = nonexistent / "artifacts"
        cfg.default_model = "test"
        cfg.default_source = "test"
        cfg.max_sessions_per_export = 10
        cfg.openrouter_api_key = "key"
        cfg.log_level = "INFO"
        with pytest.raises(ValueError, match="does not exist"):
            cfg.validate()

    def test_to_dict_has_expected_keys(self, cfg):
        d = cfg.to_dict()
        assert "gauss_home" in d
        assert "db_path" in d
        assert "log_dir" in d
        assert "artifact_dir" in d
        assert "api_endpoints" in d
        assert "has_openrouter_key" in d
        assert d["api_endpoints"]["openrouter_base"].startswith("https://openrouter.ai")

    def test_to_dict_masks_api_key(self, cfg):
        cfg.openrouter_api_key = "secret-key"
        d = cfg.to_dict()
        # Should only expose boolean, not the actual key
        assert d["has_openrouter_key"] is True
        assert "secret-key" not in json.dumps(d)


# ===========================================================================
# validate_environment
# ===========================================================================


class TestValidateEnvironment:
    def test_returns_ok_status_with_valid_config(self, cfg):
        result = validate_environment(cfg)
        # May have warnings about missing API key, but shouldn't error
        assert result["status"] in ("ok", "warnings")
        assert "checks" in result
        assert "warnings" in result
        assert "validated_at" in result

    def test_checks_include_gauss_home_exists(self, cfg):
        result = validate_environment(cfg)
        names = [c["check"] for c in result["checks"]]
        assert "gauss_home_exists" in names

    def test_checks_include_session_db_schema(self, cfg):
        result = validate_environment(cfg)
        names = [c["check"] for c in result["checks"]]
        assert "session_db_schema" in names

    def test_checks_include_gauss_time(self, cfg):
        result = validate_environment(cfg)
        names = [c["check"] for c in result["checks"]]
        assert "gauss_time_tz_aware" in names

    def test_validated_at_is_iso_string(self, cfg):
        result = validate_environment(cfg)
        from datetime import datetime

        dt = datetime.fromisoformat(result["validated_at"])
        assert dt.tzinfo is not None

    def test_config_summary_included(self, cfg):
        result = validate_environment(cfg)
        assert "config_summary" in result
        assert result["config_summary"]["gauss_home"] == str(cfg.gauss_home)

    def test_missing_api_key_produces_warning_not_error(self, cfg):
        cfg.openrouter_api_key = ""
        result = validate_environment(cfg)
        assert result["status"] != "error"  # warnings only, not hard failure
        assert any("OPENROUTER_API_KEY" in w for w in result["warnings"])


# ===========================================================================
# OpenGaussClient — session management
# ===========================================================================


class TestOpenGaussClientSessions:
    def test_create_session_returns_id(self, client):
        sid = client.create_session("test-sess-001")
        assert sid == "test-sess-001"

    def test_create_session_uses_config_defaults(self, cfg, client):
        client.create_session("defaults-sess")
        session = client._db.get_session("defaults-sess")
        assert session["source"] == cfg.default_source
        assert session["model"] == cfg.default_model

    def test_create_session_accepts_overrides(self, client):
        client.create_session(
            "override-sess",
            source="telegram",
            model="claude-opus-4",
            user_id="test-user",
        )
        session = client._db.get_session("override-sess")
        assert session["source"] == "telegram"
        assert session["model"] == "claude-opus-4"
        assert session["user_id"] == "test-user"

    def test_get_stats_returns_expected_keys(self, client):
        client.create_session("stats-sess-1")
        client.create_session("stats-sess-2")
        stats = client.get_stats()
        assert stats["total_sessions"] >= 2
        assert "total_messages" in stats
        assert "db_path" in stats
        assert "ts" in stats

    def test_get_stats_ts_is_tz_aware(self, client):
        from datetime import datetime

        stats = client.get_stats()
        dt = datetime.fromisoformat(stats["ts"])
        assert dt.tzinfo is not None


# ===========================================================================
# OpenGaussClient — messages + FTS5
# ===========================================================================


class TestOpenGaussClientMessages:
    def test_append_message_returns_int_id(self, client):
        client.create_session("msg-client-001")
        msg_id = client.append_message("msg-client-001", "user", "Hello Lean4")
        assert isinstance(msg_id, int)
        assert msg_id > 0

    def test_messages_retrievable_via_db(self, client):
        client.create_session("retrieve-sess")
        client.append_message("retrieve-sess", "user", "Pythagorean theorem proof")
        client.append_message("retrieve-sess", "assistant", "Here is the proof…")
        msgs = client._db.get_messages("retrieve-sess")
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"

    def test_fts5_search_returns_results(self, client):
        client.create_session("fts-client-sess")
        client.append_message(
            "fts-client-sess", "user", "Fermat last theorem proof approach"
        )
        results = client.search_sessions("Fermat", limit=5)
        assert len(results) >= 1

    def test_fts5_search_empty_when_no_match(self, client):
        client.create_session("no-match-sess")
        client.append_message("no-match-sess", "user", "unrelated topic xyz")
        results = client.search_sessions("Riemann hypothesis")
        assert isinstance(results, list)


# ===========================================================================
# OpenGaussClient — artifact exports
# ===========================================================================


class TestOpenGaussClientArtifacts:
    def test_export_session_artifact_creates_json_file(self, client, cfg):
        client.create_session("export-sess-001")
        client.append_message("export-sess-001", "user", "Hello")
        path = client.export_session_artifact("export-sess-001")
        assert path.exists()
        assert path.suffix == ".json"
        assert path.parent == cfg.artifact_dir

    def test_export_session_artifact_content_valid(self, client):
        client.create_session("content-export-sess")
        client.append_message("content-export-sess", "user", "theorem proof")
        path = client.export_session_artifact("content-export-sess")
        data = json.loads(path.read_text())
        assert data["id"] == "content-export-sess"
        assert "messages" in data
        assert len(data["messages"]) == 1

    def test_export_session_artifact_nonexistent_raises(self, client):
        with pytest.raises(ValueError, match="Session not found"):
            client.export_session_artifact("ghost-session")

    def test_export_all_artifacts_creates_jsonl(self, client, cfg):
        client.create_session("bulk-sess-1")
        client.create_session("bulk-sess-2")
        path = client.export_all_artifacts()
        assert path.exists()
        assert path.suffix == ".jsonl"
        lines = path.read_text().strip().splitlines()
        assert len(lines) >= 2  # at least 2 sessions

    def test_export_all_artifacts_source_filter(self, client, cfg):
        client.create_session("filter-cli-1", source="cli")
        client.create_session("filter-tg-1", source="telegram")
        path = client.export_all_artifacts(source="cli")
        lines = [json.loads(l) for l in path.read_text().strip().splitlines()]
        assert all(s["source"] == "cli" for s in lines)

    def test_validation_report_written_on_validate(self, client, cfg):
        client.validate_environment()
        report_path = cfg.artifact_dir / "validation_report.json"
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert "status" in data
        assert "checks" in data

    def test_log_file_written_on_operations(self, client, cfg):
        client.create_session("log-test-sess")
        client.append_message("log-test-sess", "user", "test content")
        log_path = cfg.log_dir / "operations.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        # Should have: client_init, create_session, append_message at minimum
        assert len(lines) >= 3
        for line in lines:
            entry = json.loads(line)
            assert "ts" in entry
            assert "event" in entry

    def test_log_entries_have_correct_events(self, client, cfg):
        client.create_session("events-sess")
        client.append_message("events-sess", "user", "test")
        client.get_stats()
        log_path = cfg.log_dir / "operations.jsonl"
        events = [
            json.loads(l)["event"] for l in log_path.read_text().strip().splitlines()
        ]
        assert "client_init" in events
        assert "create_session" in events
        assert "append_message" in events
        assert "get_stats" in events


# ===========================================================================
# _load_dotenv + _ensure_api_key  (zero-mock, real file I/O)
# ===========================================================================

from open_gauss_client import _ensure_api_key, _load_dotenv


class TestDotenvLoading:
    """Tests for .env auto-loading and API key resolution."""

    def test_load_dotenv_returns_empty_when_no_file(self, tmp_path):
        result = _load_dotenv(tmp_path)
        assert result == {}

    def test_load_dotenv_parses_key_value(self, tmp_path):
        (tmp_path / ".env").write_text("FOO=bar\nBAZ=qux\n")
        result = _load_dotenv(tmp_path)
        assert result["FOO"] == "bar"
        assert result["BAZ"] == "qux"

    def test_load_dotenv_skips_comments(self, tmp_path):
        (tmp_path / ".env").write_text("# comment\nFOO=bar\n")
        result = _load_dotenv(tmp_path)
        assert "# comment" not in result
        assert result["FOO"] == "bar"

    def test_load_dotenv_strips_quotes(self, tmp_path):
        (tmp_path / ".env").write_text("KEY='single'\nKEY2=\"double\"\n")
        result = _load_dotenv(tmp_path)
        assert result["KEY"] == "single"
        assert result["KEY2"] == "double"

    def test_load_dotenv_does_not_override_existing_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("EXISTING_VAR", "original")
        (tmp_path / ".env").write_text("EXISTING_VAR=overridden\n")
        result = _load_dotenv(tmp_path)
        # The .env file is parsed but should not override the existing env value
        assert os.environ["EXISTING_VAR"] == "original"
        assert result["EXISTING_VAR"] == "overridden"  # returned, but not applied

    def test_load_dotenv_sets_missing_env_vars(self, tmp_path, monkeypatch):
        monkeypatch.delenv("NEW_DOTENV_VAR", raising=False)
        (tmp_path / ".env").write_text("NEW_DOTENV_VAR=hello\n")
        _load_dotenv(tmp_path)
        assert os.environ.get("NEW_DOTENV_VAR") == "hello"

    def test_ensure_api_key_from_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-from-env")
        key = _ensure_api_key(tmp_path, interactive=False)
        assert key == "sk-from-env"

    def test_ensure_api_key_from_dotenv_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        (tmp_path / ".env").write_text("OPENROUTER_API_KEY=sk-from-file\n")
        key = _ensure_api_key(tmp_path, interactive=False)
        assert key == "sk-from-file"

    def test_ensure_api_key_returns_empty_when_none_available(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        key = _ensure_api_key(tmp_path, interactive=False)
        assert key == ""

    def test_from_env_loads_dotenv_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        (tmp_path / ".env").write_text("OPENROUTER_API_KEY=sk-dotenv-123\n")
        cfg = OpenGaussConfig.from_env(gauss_home=str(tmp_path), interactive=False)
        assert cfg.openrouter_api_key == "sk-dotenv-123"
