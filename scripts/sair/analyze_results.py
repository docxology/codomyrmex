"""
Post-hoc analysis of SAIR evaluation runs.

Loads one or more run JSON files and produces:
- Overall and per-type (TRUE/FALSE) accuracy breakdown
- Latency percentile report using codomyrmex.performance.BenchmarkResult
- Token usage statistics
- Failure pattern identification
- Side-by-side run comparison via --compare

Usage:
    python scripts/sair/analyze_results.py --run-dir data/sair/runs/
    python scripts/sair/analyze_results.py --run-file data/sair/runs/run_ABC.json
    python scripts/sair/analyze_results.py --compare run_A.json run_B.json
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
from pathlib import Path
from typing import Any, Optional

import matplotlib as mpl

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.performance.profiling.benchmark import BenchmarkResult
from scripts.sair.utils import (
    compare_runs,
    ensure_dir,
    load_json,
    load_run_history,
    summarize_results,
)

mpl.use("Agg")
import matplotlib.pyplot as plt

logger = get_logger(__name__)

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VIS_DIR = os.path.join(MODULE_DIR, "output", "visualizations")


# -------------------------------------------------------------------
# Latency report using codomyrmex BenchmarkResult
# -------------------------------------------------------------------

def latency_report_from_results(results: list[dict[str, Any]], name: str = "evaluation") -> str:
    """Build a latency report using BenchmarkResult from codomyrmex.performance."""
    latencies = [r["latency"] for r in results if "latency" in r and "error" not in r]
    if not latencies:
        return "No latency data available."

    bench = BenchmarkResult(
        name=name,
        iterations=len(latencies),
        times=latencies,
    )
    lines = [
        f"  Calls      : {bench.iterations}",
        f"  Average    : {bench.average_time:.3f}s",
        f"  Median     : {bench.median:.3f}s",
        f"  Min        : {bench.min_time:.3f}s",
        f"  Max        : {bench.max_time:.3f}s",
        f"  StdDev     : {bench.stdev:.3f}s",
        f"  P95        : {bench.percentile(95):.3f}s",
        f"  P99        : {bench.percentile(99):.3f}s",
        f"  Total      : {bench.total_time:.2f}s",
    ]
    return "\n".join(lines)


# -------------------------------------------------------------------
# Visualizations
# -------------------------------------------------------------------

def generate_run_visualizations(run_data: dict[str, Any], out_dir: str = DEFAULT_VIS_DIR) -> None:
    """Generate and save visualizations for a single run."""
    ensure_dir(out_dir)
    results = run_data.get("results", [])
    summary = run_data.get("summary", {})
    run_id = summary.get("run_id", "unknown")

    # Latency Distribution
    latencies = [r["latency"] for r in results if "latency" in r and "error" not in r]
    if latencies:
        plt.figure(figsize=(8, 5))
        plt.hist(latencies, bins=15, color="skyblue", edgecolor="black")
        plt.title(f"Latency Distribution (Run {run_id})")
        plt.xlabel("Latency (seconds)")
        plt.ylabel("Frequency")
        plt.grid(axis="y", alpha=0.75)
        path = os.path.join(out_dir, f"latency_dist_{run_id}.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved run visualization → {path}")

def generate_trend_visualizations(runs: list[dict[str, Any]], out_dir: str = DEFAULT_VIS_DIR) -> None:
    """Generate and save visualizations across multiple runs (trend)."""
    if len(runs) < 2:
        return
    ensure_dir(out_dir)

    run_ids = []
    accuracies = []
    avg_latencies = []

    for rd in runs:
        s = rd.get("summary", {})
        run_ids.append(s.get("run_id", "unknown")[:8])
        accuracies.append(s.get("accuracy", 0.0) * 100)
        avg_latencies.append(s.get("avg_latency_sec", 0.0))

    # Accuracy/Latency Trend
    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = "tab:blue"
    ax1.set_xlabel("Run ID")
    ax1.set_ylabel("Accuracy (%)", color=color)
    ax1.plot(run_ids, accuracies, marker="o", color=color, linewidth=2)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_ylim(-5, 105)

    ax2 = ax1.twinx()
    color = "tab:red"
    ax2.set_ylabel("Avg Latency (s)", color=color)
    ax2.plot(run_ids, avg_latencies, marker="x", linestyle="--", color=color, linewidth=1)
    ax2.tick_params(axis="y", labelcolor=color)

    plt.title("SAIR Evaluation Trend (Accuracy vs Latency)")
    plt.grid(alpha=0.3)

    path = os.path.join(out_dir, "accuracy_latency_trend.png")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    logger.info(f"Saved trend visualization → {path}")



# -------------------------------------------------------------------
# Main analysis function
# -------------------------------------------------------------------

def analyze_run(run_data: dict[str, Any], verbose: bool = False) -> str:
    """Produce a human-readable analysis report for a single run."""
    summary = run_data.get("summary", {})
    results = run_data.get("results", [])
    s = summarize_results(results)

    lines: list[str] = []
    run_id = summary.get("run_id", "unknown")
    lines.append("╔══════════════════════════════════════════════════════╗")
    lines.append(f"  SAIR Run Analysis  run_id={run_id}")
    lines.append("╚══════════════════════════════════════════════════════╝")
    lines.append(f"  Model      : {summary.get('model', 'unknown')}")
    lines.append(f"  Dataset    : {summary.get('dataset', 'unknown')}")
    cs_hash = summary.get("cheatsheet_hash")
    lines.append(f"  Cheatsheet : {cs_hash or 'none (baseline)'}")
    lines.append(f"  Start      : {summary.get('timestamp_start', '-')}")
    lines.append("")
    lines.append("── Accuracy ─────────────────────────────────────────")
    lines.append(f"  Overall    : {s['accuracy']:.1%}  ({s['correct']}/{s['evaluated']})")
    if s["true_total"] > 0:
        lines.append(f"  TRUE probs : {s['true_accuracy']:.1%}  ({s['true_correct']}/{s['true_total']})")
    if s["false_total"] > 0:
        lines.append(f"  FALSE probs: {s['false_accuracy']:.1%}  ({s['false_correct']}/{s['false_total']})")
    lines.append(f"  Errors     : {s['errors']}  |  Unknown verdicts: {s['unknown_verdicts']}")
    if summary.get("stage2"):
        ll = summary.get("avg_log_loss")
        lines.append(f"  Avg LogLoss: {ll if ll is not None else 'N/A'} (Stage 2)")
    lines.append("")
    lines.append("── Latency (codomyrmex.performance.BenchmarkResult) ──")
    lines.append(latency_report_from_results(results, name=f"run_{run_id}"))
    lines.append("")
    lines.append("── Token Usage ──────────────────────────────────────")
    total_tokens = s["total_tokens"]
    avg_tokens = total_tokens / max(s["evaluated"], 1)
    lines.append(f"  Total      : {total_tokens:,}")
    lines.append(f"  Avg/call   : {avg_tokens:.0f}")
    lines.append("")

    if s["missed_problems"]:
        lines.append("── Missed Problems ──────────────────────────────────")
        for pid in s["missed_problems"][:10]:
            lines.append(f"  • {pid}")
        if len(s["missed_problems"]) > 10:
            lines.append(f"  … and {len(s['missed_problems']) - 10} more")
        lines.append("")
        lines.append("── Refinement Suggestions ───────────────────────────")
        if s["true_correct"] < s["true_total"]:
            lines.append("  → Add 'substitution_chain', 'singleton_magma' to cheatsheet for TRUE misses.")
        if s["false_correct"] < s["false_total"]:
            lines.append("  → Add 'counterexample_small_magma', 'left_zero_magma' for FALSE misses.")
        lines.append("  → Run: python scripts/sair/generate_cheatsheet.py --refine-from <run_file>")

    if verbose:
        lines.append("")
        lines.append("── Per-Problem Results ──────────────────────────────")
        for r in results:
            if "error" in r:
                lines.append(f"  [ERROR] {r.get('problem_id','?')}: {r['error']}")
            else:
                correct_sym = "✓" if r.get("is_correct") else "✗" if r.get("is_correct") is False else "?"
                lines.append(
                    f"  [{correct_sym}] {r.get('problem_id','?')}"
                    f" | GT={r.get('ground_truth','?')} verdict={r.get('verdict','?')}"
                    f" | {r.get('latency',0):.2f}s"
                )

    # Generate offline visual artifacts
    generate_run_visualizations(run_data)

    return "\n".join(lines)


def analyze_trend(runs: list[dict[str, Any]]) -> str:
    """Summarise accuracy/latency trend across multiple runs."""
    if not runs:
        return "No runs found."
    lines = ["── Run Trend ────────────────────────────────────────────────────────────"]
    lines.append(f"  {'run_id':<12} {'model':<26} {'accuracy':>8} {'logloss':>8} {'latency':>8} {'tokens':>8}  cheatsheet")
    lines.append("  " + "-" * 88)
    for rd in runs:
        s = rd.get("summary", {})
        run_id = s.get("run_id", rd.get("_filepath", "?"))[:10]
        model = (s.get("model") or "?")[:24]
        acc = f"{s.get('accuracy', 0):.1%}"
        ll = s.get("avg_log_loss")
        ll_str = f"{ll:.4f}" if ll is not None else "N/A"
        lat = f"{s.get('avg_latency_sec', 0):.2f}s"
        tokens = str(s.get("total_tokens", 0))
        cs = s.get("cheatsheet_hash") or "base"
        lines.append(f"  {run_id:<12} {model:<26} {acc:>8} {ll_str:>8} {lat:>8} {tokens:>8}  {cs}")

    generate_trend_visualizations(runs)

    return "\n".join(lines)


def compare_two_runs(path_a: str, path_b: str) -> str:
    """Side-by-side comparison of two run files."""
    run_a = load_json(path_a)
    run_b = load_json(path_b)
    delta = compare_runs(run_a, run_b)
    sign = "+" if delta["accuracy_delta"] >= 0 else ""
    lines = [
        "── Run Comparison ───────────────────────────────────────",
        f"  Run A : {Path(path_a).stem}  (model={delta['model_a']}, cs={delta['cheatsheet_a'] or 'none'})",
        f"  Run B : {Path(path_b).stem}  (model={delta['model_b']}, cs={delta['cheatsheet_b'] or 'none'})",
        f"  Δ Accuracy : {sign}{delta['accuracy_delta']:.1%}  "
        f"({delta['accuracy_a']:.1%} → {delta['accuracy_b']:.1%})",
        f"  Δ Latency  : {delta['latency_delta_sec']:+.2f}s",
        f"  Improved   : {'YES ✓' if delta['improved'] else 'NO ✗'}",
    ]
    return "\n".join(lines)


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze SAIR evaluation run results.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-file", help="Path to a single run JSON file.")
    group.add_argument("--run-dir", help="Directory of run JSON files for trend analysis.")
    group.add_argument("--compare", nargs=2, metavar=("RUN_A", "RUN_B"),
                       help="Compare two run JSON files side-by-side.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show per-problem breakdown.")
    args = parser.parse_args()

    if args.compare:
        print(compare_two_runs(args.compare[0], args.compare[1]))
    elif args.run_file:
        run_data = load_json(args.run_file)
        print(analyze_run(run_data, verbose=args.verbose))
    else:
        runs = load_run_history(args.run_dir)
        if not runs:
            print(f"No runs found in {args.run_dir}")
        else:
            print(analyze_trend(runs))
            print()
            print(analyze_run(runs[-1], verbose=args.verbose))
