"""
Generate and iteratively refine cheat sheets for SAIR Mathematics Distillation Challenge.

Features:
- Modular technique injection (algebraic, counterexample, structural, invariant strategies)
- Size enforcement (≤10KB budget) with byte-precision validation
- Iterative refinement: reads previous run results to inject targeted rules for missed patterns
- Fingerprinting integration via compute_hash
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Optional

from scripts.sair.utils import compute_hash, ensure_dir, load_json, save_json

MAX_BYTES = 10_240  # Official 10KB limit

# -------------------------------------------------------------------
# Technique Library
# -------------------------------------------------------------------

TECHNIQUE_LIBRARY: dict[str, str] = {
    "algebraic_manipulation": (
        "If Eq1 holds universally, substitute specific expressions into Eq1 to derive Eq2. "
        "Try setting variables equal (x=y=z) or substituting one side of Eq1 into Eq2."
    ),
    "counterexample_small_magma": (
        "For FALSE: Try magmas of size 2–4. Enumerate their multiplication tables. "
        "A 2-element magma has 2^4=16 possible tables. Check if Eq1 holds but Eq2 fails."
    ),
    "left_zero_magma": (
        "Left-zero magma: a*b=a for all a,b. "
        "Often satisfies highly structured equations. Test this first."
    ),
    "right_zero_magma": (
        "Right-zero magma: a*b=b for all a,b. "
        "Often satisfies equations involving repeated right-products."
    ),
    "constant_magma": (
        "Constant magma: a*b=c for fixed c and all a,b. "
        "Any equation involving 3+ products on each side will hold trivially."
    ),
    "singleton_magma": (
        "If Eq1 forces all elements to be equal (produces x=y from universally quantified variables), "
        "then Eq1 implies any Eq2 (trivially held in a singleton)."
    ),
    "idempotent_check": (
        "Test if Eq1 implies x*x=x (idempotence) by setting all variables to x. "
        "If it does, restrict counterexample search to idempotent magmas."
    ),
    "variable_independence": (
        "If one side of Eq2 does not mention a variable that appears on the other side, "
        "Eq2 forces all products to be a constant — check if Eq1 does the same."
    ),
    "substitution_chain": (
        "Chain: apply Eq1 multiple times to 'rewrite' complex terms step-by-step toward Eq2. "
        "Track free variables carefully — a substitution valid in Eq1 must be universally valid."
    ),
    "symmetry_duality": (
        "Left-right duality: if Eq1 holds, its mirror (swap operand order throughout) also holds "
        "in the dual magma. Use this to generate free counterexamples for dually structured Eq2."
    ),
}

# Pre-packaged strategy bundles
STRATEGY_BUNDLES: dict[str, list[str]] = {
    "baseline": [
        "algebraic_manipulation",
        "counterexample_small_magma",
        "left_zero_magma",
        "right_zero_magma",
        "constant_magma",
    ],
    "structural": [
        "singleton_magma",
        "idempotent_check",
        "variable_independence",
    ],
    "advanced": [
        "substitution_chain",
        "symmetry_duality",
    ],
}


# -------------------------------------------------------------------
# Core assembly
# -------------------------------------------------------------------


def build_cheatsheet(
    techniques: Optional[list[str]] = None,
    rules: Optional[list[str]] = None,
    additional_context: Optional[str] = None,
    bundles: Optional[list[str]] = None,
) -> str:
    """Compose a cheat sheet from technique keys, explicit rules, and context.

    Args:
        techniques: List of technique keys from TECHNIQUE_LIBRARY to include.
        rules: Freeform rule strings to append under KEY RULES.
        additional_context: Extra text appended under CONTEXT.
        bundles: Pre-defined strategy bundles to include (merged with techniques).
    """
    all_keys: list[str] = list(techniques or [])
    for bundle in bundles or []:
        all_keys.extend(STRATEGY_BUNDLES.get(bundle, []))
    # Deduplicate while preserving order
    seen: set = set()
    unique_keys = [k for k in all_keys if not (k in seen or seen.add(k))]  # type: ignore[arg-type]

    content: list[str] = []

    if unique_keys:
        content.append("### STRATEGIES")
        for key in unique_keys:
            text = TECHNIQUE_LIBRARY.get(key)
            if text:
                content.append(f"[{key}] {text}")
        content.append("")

    if rules:
        content.append("### KEY RULES")
        for rule in rules:
            content.append(f"- {rule}")
        content.append("")

    if additional_context:
        content.append("### CONTEXT")
        content.append(additional_context)

    return "\n".join(content)


def validate_size(content: str) -> bool:
    """Return True if the cheat sheet is within the official 10KB budget."""
    return len(content.encode("utf-8")) <= MAX_BYTES


def trim_to_budget(content: str) -> str:
    """Trim content to fit within MAX_BYTES, preserving whole lines."""
    encoded = content.encode("utf-8")
    if len(encoded) <= MAX_BYTES:
        return content
    truncated = encoded[:MAX_BYTES].decode("utf-8", errors="ignore")
    # Snap to the last complete line
    last_newline = truncated.rfind("\n")
    return truncated[:last_newline] if last_newline > 0 else truncated


def save_cheatsheet(content: str, filepath: str) -> dict[str, Any]:
    """Save the cheat sheet to a file, enforcing size budget.

    Returns a metadata dict: {filepath, size_bytes, hash, valid}.
    """
    ensure_dir(os.path.dirname(filepath) or ".")
    size_bytes = len(content.encode("utf-8"))
    valid = size_bytes <= MAX_BYTES
    if not valid:
        print(
            f"WARNING: Cheatsheet is {size_bytes} bytes — exceeds {MAX_BYTES}B limit! Trimming..."
        )
        content = trim_to_budget(content)
        size_bytes = len(content.encode("utf-8"))
        valid = True

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    cs_hash = compute_hash(content)
    print(f"Cheatsheet saved → {filepath}  ({size_bytes} bytes, hash={cs_hash})")
    return {
        "filepath": filepath,
        "size_bytes": size_bytes,
        "hash": cs_hash,
        "valid": valid,
    }


# -------------------------------------------------------------------
# Iterative Refinement
# -------------------------------------------------------------------


def refine_from_results(
    results_file: str,
    base_techniques: Optional[list[str]] = None,
    base_bundles: Optional[list[str]] = None,
    extra_rules: Optional[list[str]] = None,
) -> str:
    """Build a refined cheat sheet targeted at previous run failures.

    Reads a run JSON (as saved by evaluate.py) and:
    1. Analyses which problem types were missed (TRUE vs FALSE ground truth).
    2. Injects counterexample-focused strategies for missed FALSE problems.
    3. Injects algebraic-chain strategies for missed TRUE problems.
    4. Adds specific missed problem equations as examples.

    Args:
        results_file: Path to a run JSON file produced by evaluate.py.
        base_techniques: Starting technique keys.
        base_bundles: Starting bundles.
        extra_rules: Additional rules to always include.

    Returns:
        Refined cheatsheet text (≤10KB, possibly trimmed).
    """
    run_data = load_json(results_file)
    results = run_data.get("results", [])
    summary = run_data.get("summary", {})

    missed_true: list[str] = []  # GT=TRUE but answered FALSE/UNKNOWN
    missed_false: list[str] = []  # GT=FALSE but answered TRUE/UNKNOWN

    for r in results:
        if "error" in r or r.get("is_correct") is not False:
            continue
        gt = (r.get("ground_truth") or "").upper()
        pid = r.get("problem_id", "?")
        eq1 = r.get("equation1", "?")
        eq2 = r.get("equation2", "?")
        label = f"{pid}: E1={eq1} → E2={eq2}"
        if gt == "TRUE":
            missed_true.append(label)
        elif gt == "FALSE":
            missed_false.append(label)

    # Determine which extra strategies to activate
    extra_keys: list[str] = list(base_techniques or [])
    extra_keys_from_failures: list[str] = []
    if missed_true:
        extra_keys_from_failures += [
            "substitution_chain",
            "singleton_magma",
            "idempotent_check",
        ]
    if missed_false:
        extra_keys_from_failures += [
            "counterexample_small_magma",
            "left_zero_magma",
            "right_zero_magma",
            "constant_magma",
            "symmetry_duality",
        ]
    for k in extra_keys_from_failures:
        if k not in extra_keys:
            extra_keys.append(k)

    # Build refinement context block
    context_lines: list[str] = [
        f"[REFINEMENT based on run {summary.get('run_id', 'unknown')}]",
        f"Prior accuracy: {summary.get('accuracy', 0):.1%} "
        f"({summary.get('correct', 0)}/{summary.get('evaluated', 0)})",
    ]
    if missed_true:
        context_lines.append("MISSED (should be TRUE — prove implication):")
        for m in missed_true[:5]:
            context_lines.append(f"  • {m}")
    if missed_false:
        context_lines.append("MISSED (should be FALSE — find counterexample):")
        for m in missed_false[:5]:
            context_lines.append(f"  • {m}")

    context_text = "\n".join(context_lines)
    all_rules = list(extra_rules or [])

    cheatsheet = build_cheatsheet(
        techniques=extra_keys,
        rules=all_rules or None,
        bundles=base_bundles,
        additional_context=context_text,
    )
    return trim_to_budget(cheatsheet)


# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

if __name__ == "__main__":
    MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_CS_PATH = os.path.join(
        MODULE_DIR, "output", "cheatsheets", "default_cs.txt"
    )

    parser = argparse.ArgumentParser(description="Generate SAIR cheat sheets.")
    parser.add_argument("--output", default=DEFAULT_CS_PATH, help="Output path.")
    parser.add_argument(
        "--bundle",
        choices=list(STRATEGY_BUNDLES.keys()),
        nargs="*",
        default=["baseline"],
        help="Strategy bundle(s) to include.",
    )
    parser.add_argument(
        "--technique",
        choices=list(TECHNIQUE_LIBRARY.keys()),
        nargs="*",
        default=[],
        help="Additional individual techniques.",
    )
    parser.add_argument("--rule", nargs="*", default=[], help="Extra freeform rules.")
    parser.add_argument(
        "--refine-from",
        help="Path to a previous run JSON file; activates iterative refinement mode.",
    )

    args = parser.parse_args()

    if args.refine_from:
        print(f"Refining from previous run: {args.refine_from}")
        cs_content = refine_from_results(
            results_file=args.refine_from,
            base_techniques=args.technique,
            base_bundles=args.bundle,
            extra_rules=args.rule,
        )
    else:
        cs_content = build_cheatsheet(
            techniques=args.technique,
            rules=args.rule
            or ["Magma: a set with one binary operation (no associativity)."],
            bundles=args.bundle,
        )

    meta = save_cheatsheet(cs_content, args.output)
    print(
        f"Size: {meta['size_bytes']} / {MAX_BYTES} bytes  ({meta['size_bytes'] / MAX_BYTES * 100:.1f}%)"
    )
