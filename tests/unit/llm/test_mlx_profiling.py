"""Real portable workload, offline artifact, and CLI regression tests."""

import copy
import cProfile
import hashlib
import json
import os
import subprocess
import sys
import tracemalloc
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from codomyrmex.llm.mlx.profile_report import (
    render_profile_html,
    render_profile_markdown,
    render_profile_svg,
    write_profile_bundle,
)
from codomyrmex.llm.mlx.profiling import PROFILE_SCHEMA, profile_cache_configuration

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/llm/mlx_profile.py"


@pytest.fixture
def report(monkeypatch):
    for key in ("MLX_MAX_KV_SIZE", "MLX_KV_BITS", "MLX_PREFILL_STEP_SIZE"):
        monkeypatch.delenv(key, raising=False)
    code = (
        "import json; from codomyrmex.llm.mlx.profiling import profile_cache_configuration; "
        "print(json.dumps(profile_cache_configuration(iterations=2,repeats=3)))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def test_real_configuration_profile(report):
    assert json.loads(json.dumps(report)) == report
    assert report["schema"] == PROFILE_SCHEMA
    assert report["native_inference"] == "not_run"
    assert report["metal_memory"] == "not_measured"
    assert [
        item["cache_kwargs"]["prefill_step_size"] for item in report["scenarios"]
    ] == [2048, 1, 512, 512]
    for scenario in report["scenarios"]:
        assert len(scenario["timing_ns_per_operation"]) == 3
        assert scenario["median_ns_per_operation"] > 0
        assert scenario["python_peak_bytes"] >= scenario["python_retained_bytes"]
        assert any(
            item["function"] == "get_generation_kwargs" for item in scenario["hotspots"]
        )
    assert not tracemalloc.is_tracing()


@pytest.mark.parametrize(
    "options",
    [
        {"iterations": 0},
        {"iterations": True},
        {"iterations": 1.5},
        {"iterations": 1000001},
        {"repeats": 2},
        {"repeats": 101},
        {"repeats": False},
    ],
)
def test_invalid_workload(options):
    with pytest.raises(ValueError):
        profile_cache_configuration(**options)


@pytest.mark.parametrize(
    "key", ["MLX_MAX_KV_SIZE", "MLX_KV_BITS", "MLX_PREFILL_STEP_SIZE"]
)
def test_reject_ambient_cache_overrides(key, monkeypatch):
    monkeypatch.setenv(key, "invalid")
    with pytest.raises(ValueError, match="environment overrides"):
        profile_cache_configuration(1, 3)


def test_preserve_caller_tracing():
    tracemalloc.start()
    try:
        with pytest.raises(RuntimeError, match="already active"):
            profile_cache_configuration(1, 3)
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()


def test_preserve_caller_cpu_profiler():
    with cProfile.Profile():
        original = sys.getprofile()
        with pytest.raises(RuntimeError, match="CPU profiler"):
            profile_cache_configuration(1, 3)
        assert sys.getprofile() is original


def test_bundle_roundtrip_and_integrity(report, tmp_path):
    paths = write_profile_bundle(report, tmp_path / "evidence")
    assert len(paths) == 5
    assert json.loads(Path(paths["profile.json"]).read_text()) == report
    manifest = json.loads(Path(paths["manifest.json"]).read_text())
    for name, digest in manifest["sha256"].items():
        assert hashlib.sha256(Path(paths[name]).read_bytes()).hexdigest() == digest
    with pytest.raises(FileExistsError, match="overwrite"):
        write_profile_bundle(report, tmp_path / "evidence")


def test_reject_symlink_output(report, tmp_path):
    (tmp_path / "target").mkdir()
    (tmp_path / "link").symlink_to(tmp_path / "target", target_is_directory=True)
    with pytest.raises(ValueError, match="symlink"):
        write_profile_bundle(report, tmp_path / "link")


def test_renderers_escape_and_remain_offline(report):
    report["scenarios"][0]["name"] = '<script>alert("x")</script>|'
    report["scenarios"][0]["hotspots"][0]["function"] = "<img src=x onerror=alert(1)>"
    svg = render_profile_svg(report)
    assert ET.fromstring(svg).attrib["role"] == "img"
    html = render_profile_html(report)
    assert "<script" not in html and "<img" not in html
    assert "&lt;script&gt;" in html and "&lt;img" in html
    assert 'src="http' not in html and "<script" not in html
    markdown = render_profile_markdown(report)
    assert "&#124;" in markdown
    assert "2309.17453v4" in markdown and "2402.02750v2" in markdown


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("median_ns_per_operation", float("nan")),
        ("mad_ns_per_operation", -1),
        ("python_peak_bytes", True),
        ("hotspots", [None]),
        ("timing_ns_per_operation", [1]),
    ],
)
def test_invalid_reports_fail_before_writes(report, key, value, tmp_path):
    broken = copy.deepcopy(report)
    broken["scenarios"][0][key] = value
    with pytest.raises(ValueError):
        write_profile_bundle(broken, tmp_path / "invalid")
    assert not (tmp_path / "invalid").exists()


@pytest.mark.parametrize(("arguments", "returncode"), [(["--help"], 0), ([], 2)])
def test_cli_readonly_without_output(arguments, returncode, tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == returncode
    assert list(tmp_path.iterdir()) == []


def test_cli_bundle_without_native_imports(tmp_path):
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("MLX_")
    }
    code = (
        "import runpy,sys; "
        f"sys.argv=[{str(SCRIPT)!r},'--output-dir',{str(tmp_path / 'bundle')!r},'--iterations','2','--repeats','3']; "
        f"runpy.run_path({str(SCRIPT)!r},run_name='__main__'); "
        "assert not any(name == 'mlx' or name.startswith('mlx.') or name == 'mlx_lm' or name.startswith('mlx_lm.') for name in sys.modules)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "bundle/manifest.json").exists()


def test_preserve_caller_trace_function():
    events = []

    def trace_function(frame, event, argument):
        events.append(event)
        return trace_function

    original = sys.gettrace()
    sys.settrace(trace_function)
    try:
        with pytest.raises(RuntimeError, match="no active tracing"):
            profile_cache_configuration(1, 3)
        assert sys.gettrace() is trace_function
    finally:
        sys.settrace(original)
    assert events


@pytest.mark.skipif(
    not hasattr(sys, "monitoring"), reason="requires Python 3.12 monitoring"
)
def test_reject_monitoring_tool():
    tool_id = 5
    monitoring = sys.monitoring
    if monitoring.get_tool(tool_id) is not None:
        pytest.skip("monitoring test slot already owned")
    monitoring.use_tool_id(tool_id, "configuration-profile-test")
    try:
        with pytest.raises(RuntimeError, match="no active tracing"):
            profile_cache_configuration(1, 3)
        assert monitoring.get_tool(tool_id) == "configuration-profile-test"
    finally:
        monitoring.free_tool_id(tool_id)


@pytest.mark.parametrize(
    "changes",
    [
        {"median_ns_per_operation": 9e9},
        {"mad_ns_per_operation": 8e9},
        {"python_retained_bytes": 999999999},
        {"python_peak_bytes": 2.5},
        {
            "timing_ns_per_operation": [1e308, 1e308, 1e308],
            "median_ns_per_operation": 1e308,
            "mad_ns_per_operation": 1e308,
        },
    ],
)
def test_reject_inconsistent_evidence(report, changes, tmp_path):
    report["scenarios"][0].update(changes)
    with pytest.raises(ValueError):
        write_profile_bundle(report, tmp_path / "inconsistent")
    assert not (tmp_path / "inconsistent").exists()


def test_markdown_metadata_is_literal(report):
    report["environment"]["python"] = (
        "<script>alert(1)</script>\n\n[link](javascript:alert(1))"
    )
    result = render_profile_markdown(report)
    assert "<script>" not in result
    assert "[link]" not in result
    assert "&lt;script&gt;" in result


def test_reject_overflow_with_tolerated_statistic_roundoff(report, tmp_path):
    scenario = report["scenarios"][0]
    scenario["timing_ns_per_operation"] = [0.0, 1e308, 1.7976931348623155e308]
    scenario["median_ns_per_operation"] = 1e308 * (1 + 1e-13)
    scenario["mad_ns_per_operation"] = 1.7976931348623155e308 - 1e308
    with pytest.raises(ValueError, match="bounds must be finite"):
        write_profile_bundle(report, tmp_path / "overflow")
    assert not (tmp_path / "overflow").exists()
