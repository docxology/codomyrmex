"""
Local evaluation engine for SAIR Mathematics Distillation Challenge.

Replicates the official playground using the Jinja2 template from SPEC.md.
Integrates:
- codomyrmex.llm for provider management (Gemini / OpenRouter)
- codomyrmex.logging_monitoring for structured, correlated logging
- codomyrmex.performance for per-call latency profiling
- Full persistent telemetry: every run auto-saved to data/sair/runs/<run_id>.json
"""

from __future__ import annotations

import os
import argparse
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Template

from codomyrmex.llm.providers import get_provider, ProviderType, Message
from codomyrmex.logging_monitoring import get_logger, new_correlation_id, set_correlation_id
from codomyrmex.performance import profile_function
from scripts.sair.utils import (
    compute_hash,
    ensure_dir,
    format_timestamp,
    load_jsonl,
    save_json,
    summarize_results,
)

logger = get_logger(__name__)

# -------------------------------------------------------------------
# Competition constants (SAIR Stage 1)
# -------------------------------------------------------------------
COMPETITION_URL = "https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/overview"
PLAYGROUND_URL = "https://playground.sair.foundation/playground/mathematics-distillation-challenge-equational-theories-stage1"
BENCHMARK_URL = "https://benchmark.sair.foundation/benchmarks/mathematics-distillation-challenge-equational-theories-stage1"
SUBMISSION_DEADLINE = "2026-04-20"
CHEATSHEET_MAX_BYTES = 10_240  # Official: ≤10KB UTF-8
DATASET_REPO_ID = "SAIRfoundation/equational-theories-selected-problems"

# Official SAIR Jinja2 evaluation template (verbatim from SPEC.md)
# Cheatsheet is injected as USER CONTENT (not system prompt)
# Source: https://terrytao.wordpress.com/2026/03/13/mathematics-distillation-challenge-equational-theories/
OFFICIAL_TEMPLATE = """\
You are a mathematician specializing in equational theories of magmas.
Your task is to determine whether Equation 1 ({{ equation1 }}) implies Equation 2 ({{ equation2 }}) over all magmas.
{% if cheatsheet is defined and cheatsheet %}
{{ cheatsheet }}
{% endif %}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.\
"""

# Stage 2 extended template (adds confidence probability for log-loss scoring)
STAGE2_TEMPLATE = """\
You are a mathematician specializing in equational theories of magmas.
Your task is to determine whether Equation 1 ({{ equation1 }}) implies Equation 2 ({{ equation2 }}) over all magmas.
{% if cheatsheet is defined and cheatsheet %}
{{ cheatsheet }}
{% endif %}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
CONFIDENCE: a probability between 0.0 and 1.0 that VERDICT is TRUE (for log-loss scoring).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise.\
"""

# Default paths
import os
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RUNS_DIR = os.path.join(MODULE_DIR, "output", "runs")
DEFAULT_LOGS_DIR = os.path.join(MODULE_DIR, "output", "logs")


# -------------------------------------------------------------------
# Parsing
# -------------------------------------------------------------------

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """Parse the structured LLM response based on the official SAIR headers.

    Handles multiline REASONING/PROOF/COUNTEREXAMPLE sections.
    Stage 2 CONFIDENCE field parsed as float string if present.
    """
    lines = response_text.strip().split("\n")
    result: Dict[str, str] = {
        "VERDICT": "UNKNOWN",
        "CONFIDENCE": "",
        "REASONING": "",
        "PROOF": "",
        "COUNTEREXAMPLE": "",
    }
    current_key: Optional[str] = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("VERDICT:"):
            result["VERDICT"] = stripped.replace("VERDICT:", "").strip().upper()
            current_key = None
        elif stripped.startswith("CONFIDENCE:"):
            result["CONFIDENCE"] = stripped.replace("CONFIDENCE:", "").strip()
            current_key = None
        elif stripped.startswith("REASONING:"):
            current_key = "REASONING"
            result["REASONING"] = stripped.replace("REASONING:", "").strip()
        elif stripped.startswith("PROOF:"):
            current_key = "PROOF"
            result["PROOF"] = stripped.replace("PROOF:", "").strip()
        elif stripped.startswith("COUNTEREXAMPLE:"):
            current_key = "COUNTEREXAMPLE"
            result["COUNTEREXAMPLE"] = stripped.replace("COUNTEREXAMPLE:", "").strip()
        elif current_key:
            result[current_key] += "\n" + line
    return result


def extract_confidence(parsed: Dict[str, str]) -> Optional[float]:
    """Extract confidence probability from parsed response (Stage 2 log-loss support).

    Returns float in [0, 1] or None if not parseable.
    """
    raw = parsed.get("CONFIDENCE", "").strip()
    if not raw:
        # Infer from verdict: 0.9 for TRUE, 0.1 for FALSE (conservative baseline)
        verdict = parsed.get("VERDICT", "UNKNOWN")
        if verdict == "TRUE":
            return 0.9
        elif verdict == "FALSE":
            return 0.1
        return None
    try:
        val = float(raw)
        return max(0.0, min(1.0, val))  # Clamp to [0, 1]
    except ValueError:
        return None


def compute_log_loss(ground_truth: str, confidence: Optional[float]) -> Optional[float]:
    """Compute log-loss for a single prediction (Stage 2 scoring).

    Args:
        ground_truth: "TRUE" or "FALSE"
        confidence: P(TRUE) in [0, 1], or None

    Returns:
        log-loss float or None
    """
    import math
    if confidence is None or ground_truth not in ("TRUE", "FALSE"):
        return None
    # Clamp to avoid log(0)
    p = max(1e-7, min(1 - 1e-7, confidence))
    label = 1 if ground_truth == "TRUE" else 0
    return -(label * math.log(p) + (1 - label) * math.log(1 - p))

# -------------------------------------------------------------------
# Single problem evaluation
# -------------------------------------------------------------------

def evaluate_problem(
    provider: Any,
    model_name: str,
    problem: Dict[str, Any],
    cheatsheet: Optional[str] = None,
    cheatsheet_hash: Optional[str] = None,
    max_retries: int = 3,
    stage2: bool = False,
) -> Dict[str, Any]:
    """Run evaluation for a single SAIR problem with retries and full telemetry.

    Returns a result dict containing all fields required for structured logging.
    If stage2=True, includes CONFIDENCE parsing and log-loss computation.
    """
    template = Template(STAGE2_TEMPLATE if stage2 else OFFICIAL_TEMPLATE)
    prompt = template.render(
        equation1=problem.get("equation1", "Unknown"),
        equation2=problem.get("equation2", "Unknown"),
        cheatsheet=cheatsheet,
    )
    messages = [Message(role="user", content=prompt)]

    ground_truth_raw = str(
        problem.get("answer", problem.get("expected_verdict", problem.get("is_true", "")))
    ).upper()
    ground_truth = ground_truth_raw if ground_truth_raw in ("TRUE", "FALSE") else None

    last_error: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            # Use performance.profile_function to capture execution time + memory
            result_holder: Dict[str, Any] = {}

            def _call() -> None:
                completion = provider.complete(messages=messages, model=model_name)
                result_holder["completion"] = completion

            profile_result = profile_function(_call)
            completion = result_holder["completion"]
            latency = profile_result["execution_time"]

            raw_content = completion.content
            parsed = parse_llm_response(raw_content)
            verdict = parsed["VERDICT"]
            confidence = extract_confidence(parsed) if stage2 else None

            is_correct: Optional[bool] = None
            log_loss: Optional[float] = None
            if ground_truth is not None:
                is_correct = verdict == ground_truth
                if stage2:
                    log_loss = compute_log_loss(ground_truth, confidence)

            return {
                "problem_id": problem.get("id"),
                "equation1": problem.get("equation1"),
                "equation2": problem.get("equation2"),
                "ground_truth": ground_truth,
                "verdict": verdict,
                "confidence": confidence,
                "is_correct": is_correct,
                "log_loss": log_loss,
                "parsed": parsed,
                "raw_response": raw_content,
                "latency": round(latency, 4),
                "memory_delta_mb": round(profile_result.get("memory_usage", 0.0), 3),
                "usage": completion.usage,
                "model": model_name,
                "cheatsheet_hash": cheatsheet_hash,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "attempts": attempt + 1,
            }
        except Exception as e:
            last_error = e
            logger.warning(
                "Attempt %d/%d failed for problem %s: %s",
                attempt + 1,
                max_retries,
                problem.get("id"),
                e,
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

    logger.error(
        "Problem %s failed after %d attempts: %s",
        problem.get("id"),
        max_retries,
        last_error,
    )
    return {
        "problem_id": problem.get("id"),
        "equation1": problem.get("equation1"),
        "equation2": problem.get("equation2"),
        "ground_truth": ground_truth,
        "error": str(last_error),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# -------------------------------------------------------------------
# Batch evaluation
# -------------------------------------------------------------------

def run_evaluation(
    dataset_path: str,
    model: str,
    cheatsheet_path: Optional[str] = None,
    limit: Optional[int] = None,
    output_file: Optional[str] = None,
    run_id: Optional[str] = None,
    runs_dir: str = DEFAULT_RUNS_DIR,
    logs_dir: str = DEFAULT_LOGS_DIR,
    stage2: bool = False,
) -> Dict[str, Any]:
    """Run a full batch evaluation and persist all structured telemetry.

    Args:
        dataset_path: Path to a JSONL problem file.
        model: Model name (Gemini or OpenRouter format).
        cheatsheet_path: Optional path to a ≤10KB cheatsheet text file.
        limit: Maximum number of problems to evaluate.
        output_file: Explicit output path (auto-generated if None).
        run_id: Pre-generated run UUID (auto-generated if None).
        runs_dir: Directory for auto-saving run JSON files.
        logs_dir: Directory for structured telemetry NDJSON log.
        stage2: If True, uses Stage 2 templates and logs log-loss scores.

    Returns:
        The full run result dict (summary + results list).
    """
    run_id = run_id or str(uuid.uuid4())[:8]
    correlation_id = new_correlation_id()
    set_correlation_id(correlation_id)
    timestamp_start = datetime.utcnow().isoformat() + "Z"

    logger.info("Starting SAIR evaluation run %s (corr=%s)", run_id, correlation_id)

    # Load cheatsheet -------------------------------------------------------
    cheatsheet: Optional[str] = None
    cheatsheet_hash: Optional[str] = None
    if cheatsheet_path and os.path.exists(cheatsheet_path):
        with open(cheatsheet_path, "r", encoding="utf-8") as f:
            cheatsheet = f.read()
        size_bytes = len(cheatsheet.encode("utf-8"))
        cheatsheet_hash = compute_hash(cheatsheet)
        if size_bytes > 10_240:
            logger.warning(
                "Cheatsheet '%s' is %d bytes — exceeds 10KB limit!", cheatsheet_path, size_bytes
            )
        logger.info("Loaded cheatsheet %s (%d bytes, hash=%s)", cheatsheet_path, size_bytes, cheatsheet_hash)

    # Load problems ---------------------------------------------------------
    problems = load_jsonl(dataset_path)
    if limit:
        problems = problems[:limit]
    logger.info("Loaded %d problems from %s", len(problems), dataset_path)

    # Initialise LLM provider -----------------------------------------------
    api_key_openrouter = os.getenv("OPENROUTER_API_KEY")
    api_key_gemini = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if api_key_openrouter:
        logger.info("Using OpenRouter provider")
        provider = get_provider(ProviderType.OPENROUTER, api_key=api_key_openrouter)
    elif api_key_gemini:
        logger.info("Using Google Gemini provider")
        provider = get_provider(ProviderType.GOOGLE, api_key=api_key_gemini)
    else:
        logger.error("No API key found. Set OPENROUTER_API_KEY or GEMINI_API_KEY.")
        raise RuntimeError("Missing API key for LLM provider.")

    # Run evaluation --------------------------------------------------------
    results: List[Dict[str, Any]] = []
    for i, problem in enumerate(problems):
        logger.info(
            "[%d/%d] Evaluating '%s'", i + 1, len(problems), problem.get("id", "?")
        )
        res = evaluate_problem(
            provider=provider,
            model_name=model,
            problem=problem,
            cheatsheet=cheatsheet,
            cheatsheet_hash=cheatsheet_hash,
        )
        results.append(res)

    # Compute summary -------------------------------------------------------
    summary_stats = summarize_results(results)
    timestamp_end = datetime.utcnow().isoformat() + "Z"
    wall_time = sum(r.get("latency", 0.0) for r in results if "error" not in r)

    summary = {
        "run_id": run_id,
        "correlation_id": correlation_id,
        "model": model,
        "dataset": dataset_path,
        "cheatsheet_path": cheatsheet_path,
        "cheatsheet_hash": cheatsheet_hash,
        "timestamp_start": timestamp_start,
        "timestamp_end": timestamp_end,
        "wall_time_sec": round(wall_time, 3),
        **summary_stats,
    }

    logger.info(
        "Run %s complete — accuracy=%.2f%% (%d/%d) | avg_latency=%.2fs | tokens=%d",
        run_id,
        summary["accuracy"] * 100,
        summary["correct"],
        summary["evaluated"],
        summary["avg_latency_sec"],
        summary["total_tokens"],
    )

    run_data: Dict[str, Any] = {"summary": summary, "results": results}

    # Persist run -----------------------------------------------------------
    ensure_dir(runs_dir)
    ensure_dir(logs_dir)

    auto_path = os.path.join(runs_dir, f"run_{format_timestamp()}_{run_id}.json")
    save_path = output_file or auto_path
    save_json(run_data, save_path)
    logger.info("Run saved → %s", save_path)

    # Append structured telemetry log line ----------------------------------
    import json as _json
    log_line = _json.dumps(
        {
            "type": "sair_run",
            "run_id": run_id,
            "correlation_id": correlation_id,
            "model": model,
            "dataset": dataset_path,
            "accuracy": summary["accuracy"],
            "correct": summary["correct"],
            "evaluated": summary["evaluated"],
            "total_tokens": summary["total_tokens"],
            "avg_latency_sec": summary["avg_latency_sec"],
            "cheatsheet_hash": cheatsheet_hash,
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end,
        }
    )
    tel_log_path = os.path.join(logs_dir, "telemetry.ndjson")
    with open(tel_log_path, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")
    logger.info("Telemetry appended → %s", tel_log_path)

    return run_data


# -------------------------------------------------------------------
# CLI entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local SAIR evaluation.")
    parser.add_argument("--cheatsheet", help="Path to the cheat sheet text file.")
    parser.add_argument("--dataset", required=True, help="Path to the JSONL dataset.")
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Model to use (Gemini or OpenRouter format).",
    )
    parser.add_argument("--limit", type=int, help="Limit the number of problems evaluated.")
    parser.add_argument("--output", help="Explicit path to save evaluation JSON results.")
    parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR, help="Directory for auto-saved runs.")
    parser.add_argument("--logs-dir", default=DEFAULT_LOGS_DIR, help="Directory for telemetry log.")

    args = parser.parse_args()

    run_evaluation(
        dataset_path=args.dataset,
        model=args.model,
        cheatsheet_path=args.cheatsheet,
        limit=args.limit,
        output_file=args.output,
        runs_dir=args.runs_dir,
        logs_dir=args.logs_dir,
    )
