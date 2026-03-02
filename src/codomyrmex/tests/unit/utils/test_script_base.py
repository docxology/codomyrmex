"""Unit tests for codomyrmex.utils.process.script_base.

Tests ScriptConfig, ScriptResult, ScriptBase, ConfigurableScript, and run_script.
Zero-mock policy: all objects are real. Filesystem tests use tmp_path.
"""

import argparse
import json
import os
from typing import Any

import pytest
import yaml

from codomyrmex.utils.process.script_base import (
    ConfigurableScript,
    ScriptBase,
    ScriptConfig,
    ScriptResult,
    run_script,
)

# ---------------------------------------------------------------------------
# Concrete subclasses for testing the abstract ScriptBase
# ---------------------------------------------------------------------------


class SuccessScript(ScriptBase):
    """A minimal script that succeeds and returns data."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        return {"status": "ok", "items": [1, 2, 3]}


class FailingScript(ScriptBase):
    """A script whose run() raises a RuntimeError."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        raise RuntimeError("boom")


class TimeoutScript(ScriptBase):
    """A script whose run() raises TimeoutError."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        raise TimeoutError("took too long")


class KeyboardScript(ScriptBase):
    """A script whose run() raises KeyboardInterrupt."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        raise KeyboardInterrupt()


class CustomArgsScript(ScriptBase):
    """A script that adds custom CLI arguments."""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--custom-flag", action="store_true")
        parser.add_argument("--custom-value", type=int, default=42)

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        return {"custom_flag": args.custom_flag, "custom_value": args.custom_value}


class MetricsScript(ScriptBase):
    """A script that adds metrics and warnings during execution."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        self.add_metric("total_items", 100)
        self.add_metric("processed", 95)
        self.log_warning("5 items skipped")
        return {"result": "partial"}


class ConcreteConfigurableScript(ConfigurableScript):
    """Concrete subclass of ConfigurableScript for testing."""

    def run(self, args: argparse.Namespace, config: ScriptConfig) -> dict[str, Any]:
        return {"configured": True}


# ===========================================================================
# ScriptConfig tests
# ===========================================================================


@pytest.mark.unit
class TestScriptConfig:
    """Tests for the ScriptConfig dataclass."""

    def test_default_values(self):
        cfg = ScriptConfig()
        assert cfg.dry_run is False
        assert cfg.verbose is False
        assert cfg.quiet is False
        assert cfg.output_dir is None
        assert cfg.output_format == "json"
        assert cfg.save_output is True
        assert cfg.log_level == "INFO"
        assert cfg.log_file is None
        assert cfg.log_format == "text"
        assert cfg.timeout == 300
        assert cfg.max_retries == 3
        assert cfg.retry_delay == 1.0
        assert cfg.custom == {}

    def test_explicit_values(self):
        cfg = ScriptConfig(
            dry_run=True,
            verbose=True,
            output_format="yaml",
            timeout=60,
            max_retries=1,
        )
        assert cfg.dry_run is True
        assert cfg.verbose is True
        assert cfg.output_format == "yaml"
        assert cfg.timeout == 60
        assert cfg.max_retries == 1

    def test_from_dict_known_fields(self):
        data = {"dry_run": True, "verbose": True, "timeout": 120}
        cfg = ScriptConfig.from_dict(data)
        assert cfg.dry_run is True
        assert cfg.verbose is True
        assert cfg.timeout == 120

    def test_from_dict_unknown_fields_go_to_custom(self):
        data = {"dry_run": True, "my_special_key": "my_value", "another": 42}
        cfg = ScriptConfig.from_dict(data)
        assert cfg.dry_run is True
        assert cfg.custom["my_special_key"] == "my_value"
        assert cfg.custom["another"] == 42

    def test_from_dict_empty(self):
        cfg = ScriptConfig.from_dict({})
        assert cfg.dry_run is False
        assert cfg.custom == {}

    def test_to_dict_roundtrip(self):
        cfg = ScriptConfig(dry_run=True, timeout=99)
        d = cfg.to_dict()
        assert isinstance(d, dict)
        assert d["dry_run"] is True
        assert d["timeout"] == 99
        assert d["custom"] == {}

    def test_to_dict_includes_custom(self):
        cfg = ScriptConfig.from_dict({"extra_key": "extra_val"})
        d = cfg.to_dict()
        assert d["custom"]["extra_key"] == "extra_val"


# ===========================================================================
# ScriptResult tests
# ===========================================================================


@pytest.mark.unit
class TestScriptResult:
    """Tests for the ScriptResult dataclass."""

    def _make_result(self, **overrides) -> ScriptResult:
        defaults = dict(
            script_name="test_script",
            status="success",
            start_time="2026-01-01T00:00:00",
            end_time="2026-01-01T00:00:05",
            duration_seconds=5.0,
            exit_code=0,
        )
        defaults.update(overrides)
        return ScriptResult(**defaults)

    def test_default_collections(self):
        r = self._make_result()
        assert r.data == {}
        assert r.errors == []
        assert r.warnings == []
        assert r.metrics == {}
        assert r.config_used == {}

    def test_to_dict(self):
        r = self._make_result(data={"key": "val"}, errors=["err1"])
        d = r.to_dict()
        assert d["script_name"] == "test_script"
        assert d["data"] == {"key": "val"}
        assert d["errors"] == ["err1"]

    def test_to_json(self):
        r = self._make_result(data={"a": 1})
        j = r.to_json()
        parsed = json.loads(j)
        assert parsed["status"] == "success"
        assert parsed["data"]["a"] == 1

    def test_to_json_indent(self):
        r = self._make_result()
        j_4 = r.to_json(indent=4)
        # 4-space indent means lines start with "    " for nested keys
        assert "    " in j_4

    def test_status_variations(self):
        for status in ("success", "failed", "timeout", "error", "skipped"):
            r = self._make_result(status=status)
            assert r.status == status


# ===========================================================================
# ScriptBase tests
# ===========================================================================


@pytest.mark.unit
class TestScriptBaseInit:
    """Tests for ScriptBase initialization."""

    def test_basic_init(self):
        s = SuccessScript(name="test", description="A test script")
        assert s.name == "test"
        assert s.description == "A test script"
        assert s.version == "1.0.0"
        assert s.default_output_dir is None
        assert s.logger is None
        assert s.perf_logger is None
        assert s.config is None
        assert s.run_id is None
        assert s.output_path is None
        assert s._warnings == []
        assert s._errors == []
        assert s._metrics == {}

    def test_custom_version_and_output_dir(self, tmp_path):
        s = SuccessScript(
            name="s", description="d", version="2.3.4",
            default_output_dir=tmp_path,
        )
        assert s.version == "2.3.4"
        assert s.default_output_dir == tmp_path


@pytest.mark.unit
class TestScriptBaseParser:
    """Tests for create_parser and argument parsing."""

    def test_parser_prog_and_description(self):
        s = SuccessScript(name="my_script", description="My description")
        parser = s.create_parser()
        assert parser.prog == "my_script"
        assert "My description" in parser.description

    def test_standard_args_defaults(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args([])
        assert args.dry_run is False
        assert args.timeout == 300
        assert args.max_retries == 3
        assert args.output_format == "json"
        assert args.no_save is False
        assert args.log_level == "INFO"
        assert args.verbose is False
        assert args.quiet is False

    def test_dry_run_flag(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_dry_run_short_flag(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["-n"])
        assert args.dry_run is True

    def test_timeout_flag(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--timeout", "60"])
        assert args.timeout == 60

    def test_output_format_choices(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        for fmt in ("json", "yaml", "text"):
            args = parser.parse_args(["--output-format", fmt])
            assert args.output_format == fmt

    def test_verbose_flag(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["-v"])
        assert args.verbose is True

    def test_quiet_flag(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["-q"])
        assert args.quiet is True

    def test_custom_arguments(self):
        s = CustomArgsScript(name="c", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--custom-flag", "--custom-value", "99"])
        assert args.custom_flag is True
        assert args.custom_value == 99

    def test_log_level_choices(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        for level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            args = parser.parse_args(["--log-level", level])
            assert args.log_level == level

    def test_env_prefix_default(self):
        s = SuccessScript(name="my-script", description="d")
        parser = s.create_parser()
        args = parser.parse_args([])
        assert args.env_prefix == "MY_SCRIPT"


@pytest.mark.unit
class TestScriptBaseEpilog:
    """Tests for the generated epilog."""

    def test_epilog_contains_script_name(self):
        s = SuccessScript(name="cool_script", description="d")
        epilog = s._get_epilog()
        assert "cool_script" in epilog

    def test_epilog_contains_env_var_hint(self):
        s = SuccessScript(name="my-tool", description="d")
        epilog = s._get_epilog()
        assert "MY_TOOL_" in epilog


@pytest.mark.unit
class TestScriptBaseLoadConfig:
    """Tests for load_config and config file / env loading."""

    def test_load_config_defaults(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args([])
        config = s.load_config(args)
        assert isinstance(config, ScriptConfig)
        assert config.dry_run is False
        assert config.output_format == "json"

    def test_load_config_cli_overrides(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--dry-run", "--timeout", "10", "--output-format", "yaml"])
        config = s.load_config(args)
        assert config.dry_run is True
        assert config.timeout == 10
        assert config.output_format == "yaml"

    def test_load_config_verbose_sets_debug(self):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--verbose"])
        config = s.load_config(args)
        assert config.log_level == "DEBUG"
        assert config.verbose is True

    def test_load_config_from_json_file(self, tmp_path):
        # CLI defaults (timeout=300) override config file values because they
        # are never None. Custom keys still come through to config.custom.
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"extra_key": "hello"}))

        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(cfg_file)])
        config = s.load_config(args)
        assert config.custom.get("extra_key") == "hello"

    def test_load_config_from_json_file_cli_override(self, tmp_path):
        # When CLI explicitly sets a value, it wins over the file.
        cfg_file = tmp_path / "config.json"
        cfg_file.write_text(json.dumps({"timeout": 999}))

        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(cfg_file), "--timeout", "42"])
        config = s.load_config(args)
        assert config.timeout == 42

    def test_load_config_from_yaml_file(self, tmp_path):
        # CLI defaults override standard fields from YAML, but custom keys
        # pass through to config.custom.
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(yaml.dump({"custom_key": "world"}))

        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(cfg_file)])
        config = s.load_config(args)
        assert config.custom.get("custom_key") == "world"

    def test_load_config_unknown_format_returns_empty(self, tmp_path):
        cfg_file = tmp_path / "config.toml"
        cfg_file.write_text("key = 'value'")

        s = SuccessScript(name="t", description="d")
        # We need config set for log_warning to not crash on config.quiet access
        s.config = ScriptConfig()
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(cfg_file)])
        config = s.load_config(args)
        # The toml file is ignored; defaults apply
        assert config.timeout == 300

    def test_load_config_nonexistent_file_ignored(self, tmp_path):
        s = SuccessScript(name="t", description="d")
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(tmp_path / "nope.json")])
        config = s.load_config(args)
        assert config.timeout == 300

    def test_load_config_corrupt_file_ignored(self, tmp_path):
        cfg_file = tmp_path / "bad.json"
        cfg_file.write_text("{not valid json!!! }")

        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig()
        parser = s.create_parser()
        args = parser.parse_args(["--config", str(cfg_file)])
        config = s.load_config(args)
        # Gracefully degrades to defaults
        assert config.timeout == 300


@pytest.mark.unit
class TestScriptBaseEnvConfig:
    """Tests for _load_env_config."""

    def test_env_boolean_true_variants(self):
        s = SuccessScript(name="t", description="d")
        env_key = "MYPREFIX_DRY_RUN"
        for truthy in ("true", "True", "1", "yes"):
            os.environ[env_key] = truthy
            try:
                result = s._load_env_config("MYPREFIX")
                assert result["dry_run"] is True, f"Failed for {truthy}"
            finally:
                del os.environ[env_key]

    def test_env_boolean_false_variants(self):
        s = SuccessScript(name="t", description="d")
        env_key = "MYPREFIX_DRY_RUN"
        for falsy in ("false", "False", "0", "no"):
            os.environ[env_key] = falsy
            try:
                result = s._load_env_config("MYPREFIX")
                assert result["dry_run"] is False, f"Failed for {falsy}"
            finally:
                del os.environ[env_key]

    def test_env_integer_parsing(self):
        s = SuccessScript(name="t", description="d")
        os.environ["MYPREFIX_TIMEOUT"] = "120"
        try:
            result = s._load_env_config("MYPREFIX")
            assert result["timeout"] == 120
        finally:
            del os.environ["MYPREFIX_TIMEOUT"]

    def test_env_float_parsing(self):
        s = SuccessScript(name="t", description="d")
        os.environ["MYPREFIX_DELAY"] = "2.5"
        try:
            result = s._load_env_config("MYPREFIX")
            assert result["delay"] == 2.5
        finally:
            del os.environ["MYPREFIX_DELAY"]

    def test_env_string_passthrough(self):
        s = SuccessScript(name="t", description="d")
        os.environ["MYPREFIX_NAME"] = "hello_world"
        try:
            result = s._load_env_config("MYPREFIX")
            assert result["name"] == "hello_world"
        finally:
            del os.environ["MYPREFIX_NAME"]

    def test_env_unrelated_vars_ignored(self):
        s = SuccessScript(name="t", description="d")
        os.environ["UNRELATED_KEY"] = "ignored"
        try:
            result = s._load_env_config("MYPREFIX")
            assert "key" not in result
        finally:
            del os.environ["UNRELATED_KEY"]


@pytest.mark.unit
class TestScriptBaseOutputDirectory:
    """Tests for setup_output_directory."""

    def test_uses_config_output_dir(self, tmp_path):
        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig(output_dir=tmp_path / "custom_out")
        out = s.setup_output_directory()
        assert out.exists()
        assert tmp_path / "custom_out" in out.parents or str(tmp_path / "custom_out") in str(out)
        assert s.run_id is not None

    def test_uses_default_output_dir(self, tmp_path):
        s = SuccessScript(
            name="t", description="d", default_output_dir=tmp_path / "default_out"
        )
        s.config = ScriptConfig(output_dir=None)
        out = s.setup_output_directory()
        assert out.exists()
        assert "default_out" in str(out)

    def test_run_id_is_timestamp_format(self, tmp_path):
        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig(output_dir=tmp_path)
        s.setup_output_directory()
        # run_id should be YYYYMMDD_HHMMSS format
        assert len(s.run_id) == 15
        assert s.run_id[8] == "_"


@pytest.mark.unit
class TestScriptBaseLogging:
    """Tests for log_* methods and add_metric."""

    def _make_script_with_config(self, **config_kwargs) -> SuccessScript:
        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig(**config_kwargs)
        return s

    def test_log_warning_appends_to_warnings(self):
        s = self._make_script_with_config()
        s.log_warning("watch out")
        assert "watch out" in s._warnings

    def test_log_error_appends_to_errors(self):
        s = self._make_script_with_config()
        s.log_error("something broke")
        assert "something broke" in s._errors

    def test_add_metric(self):
        s = self._make_script_with_config()
        s.add_metric("total", 42)
        s.add_metric("rate", 3.14)
        assert s._metrics["total"] == 42
        assert s._metrics["rate"] == 3.14

    def test_log_info_quiet_suppressed(self, capsys):
        s = self._make_script_with_config(quiet=True)
        s.log_info("should not appear")
        captured = capsys.readouterr()
        assert "should not appear" not in captured.out

    def test_log_info_not_quiet(self, capsys):
        s = self._make_script_with_config(quiet=False)
        s.log_info("visible")
        captured = capsys.readouterr()
        assert "visible" in captured.out

    def test_log_success_always_prints(self, capsys):
        s = self._make_script_with_config(quiet=True)
        s.log_success("done!")
        captured = capsys.readouterr()
        assert "done!" in captured.out

    def test_log_error_always_prints(self, capsys):
        s = self._make_script_with_config(quiet=True)
        s.log_error("fail!")
        captured = capsys.readouterr()
        assert "fail!" in captured.out

    def test_log_debug_verbose(self, capsys):
        s = self._make_script_with_config(verbose=True)
        s.log_debug("debug msg")
        captured = capsys.readouterr()
        assert "debug msg" in captured.out

    def test_log_debug_not_verbose(self, capsys):
        s = self._make_script_with_config(verbose=False)
        s.log_debug("invisible debug")
        captured = capsys.readouterr()
        assert "invisible debug" not in captured.out


# ===========================================================================
# ScriptBase.execute() integration-style tests
# ===========================================================================


@pytest.mark.unit
class TestScriptBaseExecute:
    """Tests for the execute() lifecycle method."""

    def test_success_returns_zero(self, tmp_path):
        s = SuccessScript(name="exec_test", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet"])
        assert exit_code == 0

    def test_runtime_error_returns_one(self, tmp_path):
        s = FailingScript(name="fail_test", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet", "--no-save"])
        assert exit_code == 1

    def test_timeout_error_returns_124(self, tmp_path):
        s = TimeoutScript(name="timeout_test", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet", "--no-save"])
        assert exit_code == 124

    def test_keyboard_interrupt_returns_130(self, tmp_path):
        s = KeyboardScript(name="kb_test", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet", "--no-save"])
        assert exit_code == 130

    def test_dry_run_mode(self, tmp_path, capsys):
        s = SuccessScript(name="dry", description="d")
        exit_code = s.execute(["--dry-run", "--output-dir", str(tmp_path)])
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out

    def test_no_save_skips_output(self, tmp_path):
        s = SuccessScript(name="nosave", description="d")
        exit_code = s.execute(["--no-save", "--quiet"])
        assert exit_code == 0
        # No output_path should be set
        assert s.output_path is None

    def test_execute_with_custom_args(self, tmp_path):
        s = CustomArgsScript(name="custom", description="d")
        exit_code = s.execute([
            "--custom-flag", "--custom-value", "77",
            "--output-dir", str(tmp_path), "--quiet",
        ])
        assert exit_code == 0

    def test_metrics_script_collects_data(self, tmp_path):
        s = MetricsScript(name="metrics", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet"])
        assert exit_code == 0
        assert s._metrics["total_items"] == 100
        assert s._metrics["processed"] == 95
        assert len(s._warnings) == 1
        assert "5 items skipped" in s._warnings[0]


@pytest.mark.unit
class TestScriptBaseSaveResult:
    """Tests for save_result in different formats."""

    def _execute_and_get_output(self, tmp_path, fmt):
        s = SuccessScript(name="save_test", description="d")
        s.execute(["--output-dir", str(tmp_path), "--output-format", fmt, "--quiet"])
        return s.output_path

    def test_save_json_format(self, tmp_path):
        out = self._execute_and_get_output(tmp_path, "json")
        result_file = out / "result.json"
        assert result_file.exists()
        data = json.loads(result_file.read_text())
        assert data["status"] == "success"
        assert data["script_name"] == "save_test"

    def test_save_yaml_format(self, tmp_path):
        out = self._execute_and_get_output(tmp_path, "yaml")
        result_file = out / "result.yaml"
        assert result_file.exists()
        # yaml.dump serializes Path objects with Python-specific tags that
        # safe_load and full_load cannot parse on Python 3.13+.
        # Use unsafe_load which handles all Python object tags.
        data = yaml.unsafe_load(result_file.read_text())
        assert data["status"] == "success"
        assert data["script_name"] == "save_test"

    def test_save_text_format(self, tmp_path):
        out = self._execute_and_get_output(tmp_path, "text")
        result_file = out / "result.txt"
        assert result_file.exists()
        text = result_file.read_text()
        assert "Script: save_test" in text
        assert "Status: success" in text
        assert "Duration:" in text

    def test_save_result_no_output_returns_none(self):
        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig(save_output=False)
        s.output_path = None
        result = ScriptResult(
            script_name="t", status="success",
            start_time="x", end_time="y",
            duration_seconds=1.0, exit_code=0,
        )
        assert s.save_result(result) is None


@pytest.mark.unit
class TestFormatTextResult:
    """Tests for _format_text_result."""

    def test_basic_format(self):
        s = SuccessScript(name="t", description="d")
        r = ScriptResult(
            script_name="test_script", status="success",
            start_time="t0", end_time="t1",
            duration_seconds=2.5, exit_code=0,
            data={"key": "val"},
        )
        text = s._format_text_result(r)
        assert "Script: test_script" in text
        assert "Status: success" in text
        assert "Duration: 2.50s" in text
        assert "Exit Code: 0" in text
        assert '"key": "val"' in text

    def test_format_with_errors(self):
        s = SuccessScript(name="t", description="d")
        r = ScriptResult(
            script_name="t", status="error",
            start_time="t0", end_time="t1",
            duration_seconds=1.0, exit_code=1,
            errors=["err1", "err2"],
        )
        text = s._format_text_result(r)
        assert "Errors:" in text
        assert "err1" in text
        assert "err2" in text

    def test_format_with_warnings(self):
        s = SuccessScript(name="t", description="d")
        r = ScriptResult(
            script_name="t", status="success",
            start_time="t0", end_time="t1",
            duration_seconds=1.0, exit_code=0,
            warnings=["warn1"],
        )
        text = s._format_text_result(r)
        assert "Warnings:" in text
        assert "warn1" in text

    def test_format_with_metrics(self):
        s = SuccessScript(name="t", description="d")
        r = ScriptResult(
            script_name="t", status="success",
            start_time="t0", end_time="t1",
            duration_seconds=1.0, exit_code=0,
            metrics={"count": 10},
        )
        text = s._format_text_result(r)
        assert "Metrics:" in text
        assert "10" in text


# ===========================================================================
# ConfigurableScript tests
# ===========================================================================


@pytest.mark.unit
class TestConfigurableScript:
    """Tests for ConfigurableScript config helpers."""

    def _make_script(self, custom=None, **config_kwargs) -> ConcreteConfigurableScript:
        s = ConcreteConfigurableScript(name="cfg", description="d")
        cfg = ScriptConfig(**config_kwargs)
        if custom:
            cfg.custom.update(custom)
        s.config = cfg
        return s

    def test_get_config_value_standard_field(self):
        s = self._make_script(timeout=42)
        assert s.get_config_value("timeout") == 42

    def test_get_config_value_custom_field(self):
        s = self._make_script(custom={"my_key": "my_val"})
        assert s.get_config_value("my_key") == "my_val"

    def test_get_config_value_missing_returns_default(self):
        s = self._make_script()
        assert s.get_config_value("nonexistent", "fallback") == "fallback"

    def test_get_config_value_no_config_returns_default(self):
        s = ConcreteConfigurableScript(name="cfg", description="d")
        # config is None
        assert s.get_config_value("anything", 99) == 99

    def test_get_config_value_dot_notation(self):
        s = self._make_script(custom={"db": {"host": "localhost", "port": 5432}})
        assert s.get_config_value("db.host") == "localhost"
        assert s.get_config_value("db.port") == 5432

    def test_get_config_value_dot_notation_missing(self):
        s = self._make_script(custom={"db": {"host": "localhost"}})
        assert s.get_config_value("db.missing", "default") == "default"

    def test_get_config_value_custom_takes_priority_over_standard(self):
        # If "timeout" is in custom, custom should be returned
        s = self._make_script(timeout=300, custom={"timeout": 999})
        assert s.get_config_value("timeout") == 999

    def test_require_config_present(self):
        s = self._make_script(custom={"api_key": "secret123"})
        assert s.require_config("api_key") == "secret123"

    def test_require_config_missing_raises(self):
        s = self._make_script()
        with pytest.raises(ValueError, match="Required configuration missing"):
            s.require_config("nonexistent_key")

    def test_require_config_custom_message(self):
        s = self._make_script()
        with pytest.raises(ValueError, match="Need an API key"):
            s.require_config("api_key", message="Need an API key")

    def test_execute_lifecycle(self, tmp_path):
        s = ConcreteConfigurableScript(name="cfg_exec", description="d")
        exit_code = s.execute(["--output-dir", str(tmp_path), "--quiet"])
        assert exit_code == 0


# ===========================================================================
# run_script convenience function tests
# ===========================================================================


@pytest.mark.unit
class TestRunScript:
    """Tests for the run_script convenience function.

    run_script() calls execute() without argv, so argparse reads sys.argv.
    To test in isolation we replicate the internal SimpleScript pattern and
    call execute() with explicit argv, which tests the same code paths
    without sys.argv pollution.
    """

    def _run_script_with_argv(
        self,
        name,
        description,
        run_func,
        add_args_func=None,
        version="1.0.0",
        argv=None,
    ) -> int:
        """Replicate run_script but allow explicit argv."""

        class SimpleScript(ScriptBase):
            def add_arguments(self, parser):
                if add_args_func:
                    add_args_func(parser)

            def run(self, args, config):
                return run_func(args, config)

        script = SimpleScript(name=name, description=description, version=version)
        return script.execute(argv=argv if argv is not None else ["--no-save", "--quiet"])

    def test_basic_run_script(self):
        def my_run(args, config):
            return {"ran": True}

        exit_code = self._run_script_with_argv(
            name="simple",
            description="A simple script",
            run_func=my_run,
        )
        assert exit_code == 0

    def test_run_script_with_custom_args(self):
        results = {}

        def add_args(parser):
            parser.add_argument("--name", default="world")

        def my_run(args, config):
            results["name"] = args.name
            return {"greeting": f"hello {args.name}"}

        exit_code = self._run_script_with_argv(
            name="greet",
            description="Greeter",
            run_func=my_run,
            add_args_func=add_args,
            version="2.0.0",
            argv=["--name", "test_user", "--no-save", "--quiet"],
        )
        assert exit_code == 0
        assert results["name"] == "test_user"

    def test_run_script_failing(self):
        def failing_run(args, config):
            raise ValueError("intentional error")

        exit_code = self._run_script_with_argv(
            name="fail",
            description="fails",
            run_func=failing_run,
            argv=["--no-save", "--quiet"],
        )
        assert exit_code == 1

    def test_run_script_function_exists(self):
        """Verify run_script is callable and has expected signature."""
        import inspect
        sig = inspect.signature(run_script)
        params = list(sig.parameters.keys())
        assert "name" in params
        assert "description" in params
        assert "run_func" in params
        assert "add_args_func" in params
        assert "version" in params


# ===========================================================================
# Edge case tests
# ===========================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Edge cases and boundary conditions."""

    def test_script_name_with_hyphens(self):
        s = SuccessScript(name="my-hyphenated-script", description="d")
        parser = s.create_parser()
        args = parser.parse_args([])
        assert args.env_prefix == "MY_HYPHENATED_SCRIPT"

    def test_empty_config_file(self, tmp_path):
        cfg_file = tmp_path / "empty.yaml"
        cfg_file.write_text("")
        s = SuccessScript(name="t", description="d")
        result = s._load_config_file(cfg_file)
        assert result == {}

    def test_execute_with_verbose_shows_config(self, tmp_path, capsys):
        s = SuccessScript(name="verbose_test", description="d")
        s.execute(["--verbose", "--output-dir", str(tmp_path)])
        captured = capsys.readouterr()
        assert "Configuration:" in captured.out

    def test_multiple_warnings_and_errors(self, tmp_path):
        s = SuccessScript(name="t", description="d")
        s.config = ScriptConfig(quiet=True)
        s.log_warning("w1")
        s.log_warning("w2")
        s.log_error("e1")
        s.log_error("e2")
        assert len(s._warnings) == 2
        assert len(s._errors) == 2

    def test_add_metric_overwrites(self):
        s = SuccessScript(name="t", description="d")
        s.add_metric("count", 1)
        s.add_metric("count", 2)
        assert s._metrics["count"] == 2

    def test_yml_extension_loads_as_yaml(self, tmp_path):
        cfg_file = tmp_path / "config.yml"
        cfg_file.write_text(yaml.dump({"timeout": 555}))
        s = SuccessScript(name="t", description="d")
        result = s._load_config_file(cfg_file)
        assert result["timeout"] == 555
