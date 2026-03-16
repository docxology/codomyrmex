"""
Shared utilities for the SAIR Mathematics Distillation module.

Includes helpers for:
- File I/O (JSONL, JSON)
- Run history management
- Cheatsheet fingerprinting
- Performance result summarization & comparison
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------

def ensure_dir(path: str) -> None:
    """Ensure that a directory exists, creating it if necessary."""
    os.makedirs(path, exist_ok=True)


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load a JSONL file into a list of dictionaries."""
    data: List[Dict[str, Any]] = []
    if not os.path.exists(filepath):
        return data
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def save_jsonl(data: List[Dict[str, Any]], filepath: str) -> None:
    """Save a list of dictionaries to a JSONL file."""
    ensure_dir(os.path.dirname(filepath) or ".")
    with open(filepath, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")


def load_json(filepath: str) -> Dict[str, Any]:
    """Load a JSON file into a dictionary."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """Save a dictionary to a JSON file with pretty-printing."""
    ensure_dir(os.path.dirname(filepath) or ".")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)


# ---------------------------------------------------------------------------
# Cheatsheet Fingerprinting
# ---------------------------------------------------------------------------

def compute_hash(content: str) -> str:
    """Compute a SHA-256 hex-digest of the given string (for cheatsheet fingerprinting)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def format_equation(law_data: Dict[str, Any]) -> str:
    """Format equational law data into a human-readable string."""
    return law_data.get("equation", "Unknown")


# ---------------------------------------------------------------------------
# Run History & Analysis
# ---------------------------------------------------------------------------

def load_run_history(run_dir: str) -> List[Dict[str, Any]]:
    """Load all saved evaluation runs from a directory.

    Returns a list of run dicts, each containing 'summary' and 'results' keys,
    plus a '_filepath' metadata key.
    """
    run_dir_path = Path(run_dir)
    if not run_dir_path.exists():
        return []
    runs = []
    for fp in sorted(run_dir_path.glob("*.json")):
        try:
            data = load_json(str(fp))
            data["_filepath"] = str(fp)
            runs.append(data)
        except Exception:
            pass
    return runs


def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute a rich accuracy summary from a list of per-problem result dicts.

    Returns a dict with:
    - total, evaluated, errors
    - correct, accuracy
    - true_correct / true_total (accuracy on ground-truth TRUE problems)
    - false_correct / false_total (accuracy on ground-truth FALSE problems)
    - unknown_verdicts (LLM returned neither TRUE nor FALSE)
    - avg_latency, total_tokens
    - missed_problems: list of problem_ids answered incorrectly
    """
    total = len(results)
    errors = sum(1 for r in results if "error" in r)
    evaluated = total - errors

    correct = 0
    true_correct = 0
    true_total = 0
    false_correct = 0
    false_total = 0
    unknown_verdicts = 0
    missed_problems: List[str] = []
    latencies: List[float] = []
    total_tokens = 0
    total_log_loss = 0.0
    valid_log_loss_count = 0

    for r in results:
        if "error" in r:
            continue
        verdict = (r.get("parsed") or {}).get("VERDICT", "UNKNOWN")
        if verdict not in ("TRUE", "FALSE"):
            unknown_verdicts += 1

        is_correct = r.get("is_correct")
        gt = str(r.get("ground_truth", "")).upper()

        if gt == "TRUE":
            true_total += 1
            if is_correct is True:
                true_correct += 1
                correct += 1
            elif is_correct is False:
                missed_problems.append(r.get("problem_id", "?"))
        elif gt == "FALSE":
            false_total += 1
            if is_correct is True:
                false_correct += 1
                correct += 1
            elif is_correct is False:
                missed_problems.append(r.get("problem_id", "?"))
        elif is_correct is True:
            correct += 1

        if lat := r.get("latency"):
            latencies.append(lat)
        usage = r.get("usage") or {}
        total_tokens += usage.get("total_tokens", 0)
        
        if "log_loss" in r and r["log_loss"] is not None:
            total_log_loss += r["log_loss"]
            valid_log_loss_count += 1

    accuracy = correct / evaluated if evaluated > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    ans: Dict[str, Any] = {
        "total": total,
        "evaluated": evaluated,
        "errors": errors,
        "correct": correct,
        "accuracy": round(accuracy, 4),
        "true_correct": true_correct,
        "true_total": true_total,
        "true_accuracy": round(true_correct / true_total, 4) if true_total > 0 else None,
        "false_correct": false_correct,
        "false_total": false_total,
        "false_accuracy": round(false_correct / false_total, 4) if false_total > 0 else None,
        "unknown_verdicts": unknown_verdicts,
        "avg_latency_sec": round(avg_latency, 3),
        "total_tokens": total_tokens,
        "missed_problems": missed_problems,
    }
    if valid_log_loss_count > 0:
        ans["stage2"] = True
        ans["avg_log_loss"] = round(total_log_loss / valid_log_loss_count, 4)
    return ans


def compare_runs(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compute performance delta between two evaluation runs.

    Args:
        run_a: Earlier run dict (with 'summary' key).
        run_b: Later run dict (with 'summary' key).

    Returns:
        Delta dict showing improvements or regressions.
    """
    sa = run_a.get("summary", {})
    sb = run_b.get("summary", {})
    acc_a = sa.get("accuracy", 0.0)
    acc_b = sb.get("accuracy", 0.0)
    lat_a = sa.get("avg_latency_sec", 0.0)
    lat_b = sb.get("avg_latency_sec", 0.0)
    return {
        "accuracy_delta": round(acc_b - acc_a, 4),
        "accuracy_a": acc_a,
        "accuracy_b": acc_b,
        "improved": acc_b > acc_a,
        "latency_delta_sec": round(lat_b - lat_a, 3),
        "model_a": sa.get("model"),
        "model_b": sb.get("model"),
        "cheatsheet_a": sa.get("cheatsheet_hash"),
        "cheatsheet_b": sb.get("cheatsheet_hash"),
    }


def format_timestamp() -> str:
    """Return a filesystem-safe ISO-8601 timestamp string."""
    return datetime.now().strftime("%Y%m%dT%H%M%S")
