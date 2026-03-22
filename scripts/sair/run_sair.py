"""
Unified SAIR orchestrator — replaces ad-hoc script calls.

Modes:
    evaluate  — Run LLM evaluation on a dataset, auto-save results & telemetry.
    generate  — Generate/refine a cheat sheet (optionally from previous run).
    analyze   — Analyze and compare run result files.
    full      — download → generate baseline cheatsheet → evaluate → analyze (all-in-one).

Usage examples:
    python scripts/sair/run_sair.py evaluate \\
        --dataset data/sair/public/data/normal.jsonl --limit 20 --model gemini-2.5-flash

    python scripts/sair/run_sair.py generate \\
        --bundle baseline structural --output cheatsheets/v1.txt

    python scripts/sair/run_sair.py generate \\
        --refine-from data/sair/runs/run_XYZ.json --output cheatsheets/v2.txt

    python scripts/sair/run_sair.py analyze --run-dir data/sair/runs/

    python scripts/sair/run_sair.py full \\
        --dataset data/sair/public/data/normal.jsonl --limit 20

    python scripts/sair/run_sair.py compare \\
        data/sair/runs/run_A.json data/sair/runs/run_B.json
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from codomyrmex.logging_monitoring import get_logger, setup_logging

logger = get_logger(__name__)

# Canonical default paths
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_DIR = os.path.join(MODULE_DIR, "data")
DEFAULT_PUBLIC_DIR = os.path.join(MODULE_DIR, "data", "public")
DEFAULT_NORMAL = os.path.join(DEFAULT_PUBLIC_DIR, "data", "normal.jsonl")
DEFAULT_HARD = os.path.join(DEFAULT_PUBLIC_DIR, "data", "hard.jsonl")
DEFAULT_RUNS_DIR = os.path.join(MODULE_DIR, "output", "runs")
DEFAULT_LOGS_DIR = os.path.join(MODULE_DIR, "output", "logs")
DEFAULT_CS_DIR = os.path.join(MODULE_DIR, "output", "cheatsheets")
DEFAULT_MODEL = "gemini-2.5-flash"


def _ensure_dataset(dataset_path: str, pub_dir: str) -> None:
    """Auto-download datasets if they don't exist yet."""
    if os.path.exists(dataset_path):
        return
    logger.warning("Dataset '%s' not found — attempting auto-download.", dataset_path)
    from scripts.sair.download_data import download_sair_datasets
    download_sair_datasets(pub_dir)
    if not os.path.exists(dataset_path):
        logger.error("Auto-download failed. Run: python scripts/sair/download_data.py --type public")
        sys.exit(1)


def cmd_evaluate(args: argparse.Namespace) -> str:
    """Run LLM evaluation on a SAIR dataset."""
    _ensure_dataset(args.dataset, DEFAULT_PUBLIC_DIR)
    from scripts.sair.evaluate import run_evaluation
    run_data = run_evaluation(
        dataset_path=args.dataset,
        model=args.model,
        cheatsheet_path=args.cheatsheet,
        limit=args.limit,
        output_file=getattr(args, "output", None),
        runs_dir=args.runs_dir,
        logs_dir=args.logs_dir,
        stage2=getattr(args, "stage2", False),
    )
    s = run_data["summary"]
    msg = (
        f"\n✓ Evaluation complete  run_id={s['run_id']}"
        f"  accuracy={s['accuracy']:.1%} ({s['correct']}/{s['evaluated']})"
        f"  avg_latency={s['avg_latency_sec']:.2f}s"
    )
    if s.get("stage2"):
        msg += f"  avg_log_loss={s.get('avg_log_loss', 'N/A')}"
    print(msg)
    # Return path to the auto-saved run
    import glob
    runs = sorted(glob.glob(os.path.join(args.runs_dir, f"*{s['run_id']}*")))
    return runs[-1] if runs else ""


def cmd_generate(args: argparse.Namespace) -> None:
    """Generate or refine a cheatsheet."""
    from scripts.sair.generate_cheatsheet import (
        MAX_BYTES,
        STRATEGY_BUNDLES,
        TECHNIQUE_LIBRARY,
        build_cheatsheet,
        refine_from_results,
        save_cheatsheet,
    )

    output = getattr(args, "output", "cheatsheets/default_cs.txt")

    if getattr(args, "refine_from", None):
        print(f"Refining from previous run: {args.refine_from}")
        content = refine_from_results(
            results_file=args.refine_from,
            base_bundles=getattr(args, "bundle", ["baseline"]),
            base_techniques=getattr(args, "technique", []),
        )
    else:
        content = build_cheatsheet(
            techniques=getattr(args, "technique", []),
            bundles=getattr(args, "bundle", ["baseline"]),
            rules=["Magma: a set with one binary operation (no other axioms)."],
        )

    meta = save_cheatsheet(content, output)
    print(f"Budget usage: {meta['size_bytes']}/{MAX_BYTES} bytes ({meta['size_bytes']/MAX_BYTES*100:.1f}%)")


def cmd_analyze(args: argparse.Namespace) -> None:
    """Analyze run results."""
    from scripts.sair.analyze_results import (
        analyze_run,
        analyze_trend,
        compare_two_runs,
        load_run_history,
    )
    from scripts.sair.utils import load_json

    if getattr(args, "compare", None):
        print(compare_two_runs(args.compare[0], args.compare[1]))
    elif getattr(args, "run_file", None):
        print(analyze_run(load_json(args.run_file), verbose=getattr(args, "verbose", False)))
    else:
        run_dir = getattr(args, "run_dir", DEFAULT_RUNS_DIR)
        runs = load_run_history(run_dir)
        if not runs:
            print(f"No runs found in {run_dir}")
        else:
            print(analyze_trend(runs))
            print()
            print(analyze_run(runs[-1], verbose=getattr(args, "verbose", False)))


def cmd_full(args: argparse.Namespace) -> None:
    """Full pipeline: ensure data → generate baseline cheatsheet → evaluate → analyze."""
    logger.info("Starting SAIR full pipeline.")

    # 1. Ensure data
    _ensure_dataset(args.dataset, DEFAULT_PUBLIC_DIR)

    # 2. Generate baseline cheatsheet
    cs_path = os.path.join(DEFAULT_CS_DIR, "baseline.txt")
    from scripts.sair.generate_cheatsheet import build_cheatsheet, save_cheatsheet
    cs_content = build_cheatsheet(bundles=["baseline", "structural"])
    save_cheatsheet(cs_content, cs_path)
    print(f"✓ Baseline cheatsheet generated → {cs_path}")

    # 3. Evaluate
    from scripts.sair.evaluate import run_evaluation
    run_data = run_evaluation(
        dataset_path=args.dataset,
        model=args.model,
        cheatsheet_path=cs_path,
        limit=args.limit,
        runs_dir=args.runs_dir,
        logs_dir=args.logs_dir,
        stage2=getattr(args, "stage2", False),
    )

    # 4. Analyze
    from scripts.sair.analyze_results import analyze_run
    print(analyze_run(run_data, verbose=getattr(args, "verbose", False)))

    s = run_data["summary"]
    if s.get("missed_problems"):
        print("\n💡 Tip: Refine the cheatsheet for the next run:")
        import glob
        runs = sorted(glob.glob(os.path.join(args.runs_dir, f"*{s['run_id']}*")))
        if runs:
            print(f"   python scripts/sair/run_sair.py generate --refine-from {runs[-1]}")


def cmd_compare(args: argparse.Namespace) -> None:
    """Compare two run files."""
    from scripts.sair.analyze_results import compare_two_runs
    print(compare_two_runs(args.run_a, args.run_b))


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SAIR Mathematics Distillation — unified orchestrator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ---- evaluate ----
    ev = sub.add_parser("evaluate", help="Run LLM evaluation on a SAIR dataset.")
    ev.add_argument("--dataset", default=DEFAULT_NORMAL, help="Path to JSONL dataset.")
    ev.add_argument("--model", default=DEFAULT_MODEL, help="LLM model name.")
    ev.add_argument("--cheatsheet", default=None, help="Path to cheatsheet file.")
    ev.add_argument("--limit", type=int, default=None, help="Max problems to evaluate.")
    ev.add_argument("--output", default=None, help="Explicit output JSON path.")
    ev.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    ev.add_argument("--logs-dir", default=DEFAULT_LOGS_DIR)
    ev.add_argument("--stage2", action="store_true", help="Enable Stage 2 log-loss confidence scoring.")

    # ---- generate ----
    gen = sub.add_parser("generate", help="Generate or refine a cheatsheet.")
    gen.add_argument("--output", default=f"{DEFAULT_CS_DIR}/default_cs.txt")
    gen.add_argument("--bundle", nargs="*", default=["baseline"])
    gen.add_argument("--technique", nargs="*", default=[])
    gen.add_argument("--rule", nargs="*", default=[])
    gen.add_argument("--refine-from", dest="refine_from", default=None,
                     help="Previous run JSON file to refine from.")

    # ---- analyze ----
    an = sub.add_parser("analyze", help="Analyze saved run results.")
    an_group = an.add_mutually_exclusive_group(required=True)
    an_group.add_argument("--run-file", help="Single run JSON file.")
    an_group.add_argument("--run-dir", help="Directory of run JSON files.")
    an.add_argument("--verbose", "-v", action="store_true")

    # ---- full ----
    fl = sub.add_parser("full", help="Full pipeline: data → generate → evaluate → analyze.")
    fl.add_argument("--dataset", default=DEFAULT_NORMAL)
    fl.add_argument("--model", default=DEFAULT_MODEL)
    fl.add_argument("--limit", type=int, default=None)
    fl.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    fl.add_argument("--logs-dir", default=DEFAULT_LOGS_DIR)
    fl.add_argument("--stage2", action="store_true", help="Enable Stage 2 log-loss scoring.")
    fl.add_argument("--verbose", "-v", action="store_true")

    # ---- compare ----
    cmp = sub.add_parser("compare", help="Compare two run JSON files.")
    cmp.add_argument("run_a", help="Path to run A JSON file.")
    cmp.add_argument("run_b", help="Path to run B JSON file.")

    return parser


if __name__ == "__main__":
    setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "evaluate": cmd_evaluate,
        "generate": cmd_generate,
        "analyze": cmd_analyze,
        "full": cmd_full,
        "compare": cmd_compare,
    }
    dispatch[args.command](args)
