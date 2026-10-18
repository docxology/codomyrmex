"""Offline, escaped, hash-bound visualization and companion report rendering."""

from __future__ import annotations

import hashlib
import html
import json
import math
import statistics
from pathlib import Path
from typing import Any

from .profiling import PROFILE_SCHEMA


def _validate_report(report: dict[str, Any]) -> None:
    """Reject unsupported schemas and invalid chart inputs before writing files."""
    if not isinstance(report, dict) or report.get("schema") != PROFILE_SCHEMA:
        raise ValueError("unsupported MLX configuration profile schema")
    if (
        report.get("native_inference") != "not_run"
        or report.get("metal_memory") != "not_measured"
    ):
        raise ValueError(
            "configuration profiles cannot claim native or Metal measurements"
        )
    scenarios = report.get("scenarios")
    if not isinstance(scenarios, list) or not 1 <= len(scenarios) <= 20:
        raise ValueError("report must contain between 1 and 20 scenarios")
    for key in ("environment", "provenance", "method"):
        if not isinstance(report.get(key), dict):
            raise ValueError(f"{key} must be an object")
    if not isinstance(report["environment"].get("python"), str):
        raise ValueError("environment.python must be a string")
    for key, minimum, maximum in (("iterations", 1, 1_000_000), ("repeats", 3, 100)):
        value = report["method"].get(key)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f"invalid method.{key}")
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("scenario must be an object")
        if not isinstance(scenario.get("name"), str):
            raise ValueError("scenario name must be a string")
        samples = scenario.get("timing_ns_per_operation")
        if not isinstance(samples, list) or len(samples) != report["method"]["repeats"]:
            raise ValueError("timing samples must match repeats")
        for key in (
            "median_ns_per_operation",
            "mad_ns_per_operation",
            "python_peak_bytes",
            "python_retained_bytes",
        ):
            value = scenario.get(key)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{key} must be a finite nonnegative number")
        for value in samples:
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("timing samples must be finite nonnegative numbers")
        median = statistics.median(samples)
        mad = statistics.median(abs(value - median) for value in samples)
        for key, calculated in (
            ("median_ns_per_operation", median),
            ("mad_ns_per_operation", mad),
        ):
            if not math.isfinite(calculated) or not math.isclose(
                scenario[key], calculated, rel_tol=1e-12, abs_tol=1e-9
            ):
                raise ValueError(f"{key} does not match raw samples")
        if not math.isfinite(median + mad) or not math.isfinite(
            scenario["median_ns_per_operation"] + scenario["mad_ns_per_operation"]
        ):
            raise ValueError("timing bounds must be finite")
        for key in ("python_peak_bytes", "python_retained_bytes"):
            if type(scenario[key]) is not int:
                raise ValueError(f"{key} must be an integer")
        if scenario["python_retained_bytes"] > scenario["python_peak_bytes"]:
            raise ValueError("retained allocations cannot exceed peak allocations")
        hotspots = scenario.get("hotspots")
        if not isinstance(hotspots, list) or len(hotspots) > 30:
            raise ValueError("hotspots must contain at most 30 rows")
        for hotspot in hotspots:
            if not isinstance(hotspot, dict):
                raise ValueError("hotspot must be an object")
            for key in ("file", "function"):
                if not isinstance(hotspot.get(key), str):
                    raise ValueError(f"hotspot {key} must be a string")
            for key in ("line", "primitive_calls", "total_calls"):
                if type(hotspot.get(key)) is not int or hotspot[key] < 0:
                    raise ValueError(f"hotspot {key} must be a nonnegative integer")
            for key in ("self_seconds", "cumulative_seconds"):
                value = hotspot.get(key)
                if (
                    type(value) not in (int, float)
                    or not math.isfinite(value)
                    or value < 0
                ):
                    raise ValueError(f"hotspot {key} must be finite and nonnegative")


def render_profile_svg(report: dict[str, Any]) -> str:
    """Render a scalable timing chart with accessible text and MAD whiskers."""
    _validate_report(report)
    scenarios = report["scenarios"]
    height = 95 + 52 * len(scenarios)
    scale = max(
        [1]
        + [
            item["median_ns_per_operation"] + item["mad_ns_per_operation"]
            for item in scenarios
        ],
    )
    bars = []
    for index, item in enumerate(scenarios):
        median = item["median_ns_per_operation"]
        mad = item["mad_ns_per_operation"]
        center = 190 + median / scale * 370
        lower = 190 + max(0, median - mad) / scale * 370
        upper = 190 + (median + mad) / scale * 370
        position = 72 + index * 52
        bars.append(
            f'<text x="0" y="{position + 17}">{html.escape(item["name"])}</text>'
            f'<rect x="190" y="{position}" width="{median / scale * 370:.2f}" height="25" rx="4" fill="#2563eb"/>'
            f'<path d="M{lower:.2f},{position + 12} H{upper:.2f} M{lower:.2f},{position + 7} v10 M{upper:.2f},{position + 7} v10" stroke="#111827" stroke-width="2"/>'
            f'<text x="575" y="{position + 17}">{median / 1000:.3f} µs</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 728 {height}" role="img" aria-labelledby="title desc">'
        '<title id="title">Python configuration setup time</title>'
        '<desc id="desc">Median microseconds per configuration operation. Whiskers show median absolute deviation, not confidence intervals. No inference or Metal memory was measured.</desc>'
        '<rect width="100%" height="100%" fill="#ffffff"/>'
        '<g font-family="system-ui,sans-serif" font-size="14" fill="#111827">'
        '<text x="0" y="23" font-size="20">Configuration setup · not inference</text>'
        '<text x="0" y="46">Median ± MAD, separate uninstrumented timing pass</text>'
        + "".join(bars)
        + "</g></svg>"
    )


def _markdown_text(value: str) -> str:
    """Normalize metadata and encode Markdown metacharacters as literal text."""
    return html.escape(" ".join(value.split())).translate(
        {ord(character): f"&#{ord(character)};" for character in "\\`*_{}[]()#+-.!|"}
    )


def render_profile_markdown(report: dict[str, Any]) -> str:
    """Create a data-derived engineering manuscript, not a published paper."""
    _validate_report(report)
    rows = "\n".join(
        f"| {_markdown_text(item['name'])} | {item['median_ns_per_operation'] / 1000:.3f} | {item['mad_ns_per_operation'] / 1000:.3f} | {item['python_peak_bytes']} |"
        for item in report["scenarios"]
    )
    return (
        "# MLX configuration profiling: engineering companion\n\n"
        "## Abstract\n\nThis exploratory, single-environment study measures Python configuration overhead only. "
        "It neither evaluates language-model quality nor establishes native backend compatibility.\n\n"
        "## Methods\n\n"
        f"Python {_markdown_text(report['environment']['python'])}; {report['method']['iterations']} operations per batch; "
        f"{report['method']['repeats']} repeats. Each operation constructs MLXConfig, serializes it, "
        "validates it, and resolves generation kwargs. Scenario order rotates per repeat. "
        "Timing, cProfile, and tracemalloc use separate passes. The dispersion statistic is median "
        "absolute deviation (MAD), not a confidence interval. Imports, model loading, tokenization, "
        "prefill, and decode are outside the timed operation.\n\n"
        "## Results\n\n| Configuration | Median µs/op | MAD µs/op | Python allocation peak bytes |\n"
        "|---|---:|---:|---:|\n" + rows + "\n\n"
        "![Configuration setup time, not inference](timings.svg)\n\n"
        "## Interpretation and limitations\n\n"
        "Scenario names describe requested configuration, not instantiated native caches. "
        "The allocation peak covers a separately instrumented Python workload batch; it is not "
        "RSS, Metal RAM, model-weight memory, or bytes per operation. These measurements cannot "
        "establish faster inference, reduced device memory, attention correctness, recall, or "
        "Python 3.15 native MLX support. No causal comparison across Python versions is made. "
        "Production-model long-context experiments remain not run.\n\n"
        "## Reproducibility\n\n"
        "Read profile.json for raw samples, effective configurations, dependency versions, source "
        "hashes, and profiler hotspots. Verify all bundle files against manifest.json. Source "
        "revision and dirty status are recorded separately; hashes identify the measured files.\n\n"
        "## Related work and provenance\n\n"
        "StreamingLLM provides background on attention sinks; KIVI studies KV-cache quantization. "
        "Neither validates this configuration benchmark or the Codomyrmex workaround. The upstream "
        "PR and benchmark report are implementation evidence, not peer-reviewed replication.\n\n"
        "- Xiao, Tian, Chen, Han, and Lewis. Efficient Streaming Language Models with Attention Sinks. ICLR 2024. https://arxiv.org/abs/2309.17453v4\n"
        "- Liu, Yuan, Jin, Zhong, Xu, Braverman, Chen, and Hu. KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache. ICML 2024. https://arxiv.org/abs/2402.02750v2\n"
        "- Upstream rotating-mask PR: https://github.com/ml-explore/mlx-lm/pull/1978\n"
        "- Original workload measurements: https://gist.github.com/robertcprice/88f542f29ec8b97f2a8b1edde3fdc903\n"
    )


def render_profile_html(report: dict[str, Any]) -> str:
    """Render an offline accessible dashboard without scripts or remote assets."""
    chart = render_profile_svg(report)
    timing_rows = "".join(
        f"<tr><th scope='row'>{html.escape(item['name'])}</th><td>{item['median_ns_per_operation'] / 1000:.3f}</td><td>{item['mad_ns_per_operation'] / 1000:.3f}</td></tr>"
        for item in report["scenarios"]
    )
    sections = []
    for scenario in report["scenarios"]:
        rows = "".join(
            f"<tr><td>{html.escape(item['file'])}:{item['line']} {html.escape(item['function'])}</td>"
            f"<td>{item['total_calls']}</td><td>{item['self_seconds']:.6f}</td><td>{item['cumulative_seconds']:.6f}</td></tr>"
            for item in scenario["hotspots"]
        )
        sections.append(
            f"<details><summary>{html.escape(scenario['name'])} · Python peak {scenario['python_peak_bytes']:,} bytes</summary>"
            '<div class="scroll"><table><caption>Separate cProfile pass; seconds include profiler overhead</caption>'
            '<thead><tr><th scope="col">Function</th><th scope="col">Calls</th><th scope="col">Self s</th><th scope="col">Cumulative s</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div></details>"
        )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>MLX portable configuration profile</title><style>"
        "body{font:16px/1.6 system-ui,sans-serif;color:#111827;background:#fff;max-width:960px;margin:32px auto;padding:0 20px}"
        "svg{width:100%;height:auto}figure{margin:16px 0}a{color:#1d4ed8}table{border-collapse:collapse;width:100%;font-size:14px}"
        "th,td{text-align:left;padding:8px;border-bottom:1px solid #d1d5db}.scroll{overflow:auto}"
        "details{margin:16px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere}"
        ".scope{border-left:4px solid #2563eb;padding:12px 18px;background:#eff6ff}</style><main>"
        '<h1>Portable MLX configuration profile</h1><p class="scope">Python configuration only. '
        "No model loading, inference, recall, or Metal memory measurements. Scenario names do not establish native backend support.</p>"
        "<figure>"
        + chart
        + "<figcaption>Uninstrumented batch timing; whiskers show MAD, not confidence intervals.</figcaption></figure>"
        "<div class='scroll'><table><caption>Python configuration setup timing</caption><thead><tr><th scope='col'>Configuration</th><th scope='col'>Median µs/op</th><th scope='col'>MAD µs/op</th></tr></thead><tbody>"
        + timing_rows
        + "</tbody></table></div>"
        "<h2>CPU and Python allocation evidence</h2>"
        + "".join(sections)
        + "<h2>Environment and provenance</h2><pre>"
        + html.escape(
            json.dumps(
                {key: report[key] for key in ("environment", "provenance", "method")},
                indent=2,
            )
        )
        + '</pre><p><a href="profile.json">Raw samples</a> · <a href="manuscript.md">Companion manuscript</a> · '
        '<a href="manifest.json">SHA-256 manifest</a></p></main></html>'
    )


def write_profile_bundle(
    report: dict[str, Any], output_dir: str | Path
) -> dict[str, str]:
    """Write a new offline artifact bundle, refusing to overwrite existing files.

    The manifest is written last; its absence identifies an incomplete bundle.
    Each file uses exclusive creation, including under concurrent writers.
    """
    _validate_report(report)
    contents = {
        "profile.json": json.dumps(report, indent=2, allow_nan=False) + "\n",
        "timings.svg": render_profile_svg(report),
        "report.html": render_profile_html(report),
        "manuscript.md": render_profile_markdown(report),
    }
    destination = Path(output_dir)
    if destination.is_symlink():
        raise ValueError("output directory must not be a symlink")
    for name in (*contents, "manifest.json"):
        if (destination / name).exists() or (destination / name).is_symlink():
            raise FileExistsError(f"refusing to overwrite profile artifact {name}")
    hashes = {
        name: hashlib.sha256(content.encode()).hexdigest()
        for name, content in contents.items()
    }
    contents["manifest.json"] = (
        json.dumps({"schema": PROFILE_SCHEMA, "sha256": hashes}, indent=2) + "\n"
    )
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in contents.items():
        with (destination / name).open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    return {name: str(destination / name) for name in contents}
