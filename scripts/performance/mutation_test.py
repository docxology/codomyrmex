#!/usr/bin/env python3
"""Lightweight mutation testing for critical paths.

Applies simple mutations (operator swaps, boundary changes, return value swaps)
to targeted source files and runs the relevant tests against each mutant.
Reports kill ratio per file and overall.

Usage:
    uv run python scripts/mutation_test.py
"""

from __future__ import annotations

import ast
import copy
import os
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "codomyrmex"


# ── Mutation Targets ────────────────────────────────────────────────
@dataclass
class MutationTarget:
    source_file: Path
    test_files: list[str]
    label: str


TARGETS = [
    MutationTarget(
        source_file=SRC / "model_context_protocol" / "validation.py",
        test_files=[
            "src/codomyrmex/tests/unit/mcp/test_mcp_validation.py",
            "src/codomyrmex/tests/unit/validation/test_validation.py",
            "src/codomyrmex/tests/unit/mcp/test_mutation_kill.py",
        ],
        label="validation.py",
    ),
    MutationTarget(
        source_file=SRC / "model_context_protocol" / "schemas" / "mcp_schemas.py",
        test_files=[
            "src/codomyrmex/tests/unit/mcp/",
        ],
        label="mcp_schemas.py",
    ),
    MutationTarget(
        source_file=SRC / "agents" / "pai" / "trust_gateway.py",
        test_files=[
            "src/codomyrmex/tests/unit/agents/test_trust_gateway.py",
            "src/codomyrmex/tests/unit/agents/pai/test_trust_gateway_hardening.py",
        ],
        label="trust_gateway.py",
    ),
]


# ── Mutation Operators ──────────────────────────────────────────────
class MutationOperator(ast.NodeTransformer):
    """Base class — subclasses override visit_* to introduce mutations."""

    mutations_applied: int = 0
    target_index: int = -1  # which occurrence to mutate (-1 = count only)
    _current_index: int = 0


class ComparisonMutator(MutationOperator):
    """Swap comparison operators: == ↔ !=, < ↔ >, <= ↔ >=."""

    SWAPS = {
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.Gt,
        ast.Gt: ast.Lt,
        ast.LtE: ast.GtE,
        ast.GtE: ast.LtE,
    }

    def visit_Compare(self, node: ast.Compare) -> ast.Compare:
        self.generic_visit(node)
        new_ops = []
        for op in node.ops:
            swap = self.SWAPS.get(type(op))
            if swap:
                if self._current_index == self.target_index:
                    new_ops.append(swap())
                    self.mutations_applied += 1
                else:
                    new_ops.append(op)
                self._current_index += 1
            else:
                new_ops.append(op)
        node.ops = new_ops
        return node


class BoolOpMutator(MutationOperator):
    """Swap and ↔ or."""

    def visit_BoolOp(self, node: ast.BoolOp) -> ast.BoolOp:
        self.generic_visit(node)
        if self._current_index == self.target_index:
            if isinstance(node.op, ast.And):
                node.op = ast.Or()
            else:
                node.op = ast.And()
            self.mutations_applied += 1
        self._current_index += 1
        return node


class ReturnConstMutator(MutationOperator):
    """Mutate return True → return False and vice versa."""

    def visit_Return(self, node: ast.Return) -> ast.Return:
        self.generic_visit(node)
        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, bool):
                if self._current_index == self.target_index:
                    node.value.value = not node.value.value
                    self.mutations_applied += 1
                self._current_index += 1
        return node


class NoneReturnMutator(MutationOperator):
    """Mutate return <expr> → return None for non-None returns."""

    def visit_Return(self, node: ast.Return) -> ast.Return:
        self.generic_visit(node)
        if node.value is not None and not (
            isinstance(node.value, ast.Constant) and node.value.value is None
        ):
            if self._current_index == self.target_index:
                node.value = ast.Constant(value=None)
                self.mutations_applied += 1
            self._current_index += 1
        return node


class BinOpMutator(MutationOperator):
    """Swap + ↔ -, * ↔ //."""

    SWAPS = {
        ast.Add: ast.Sub,
        ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv,
        ast.FloorDiv: ast.Mult,
    }

    def visit_BinOp(self, node: ast.BinOp) -> ast.BinOp:
        self.generic_visit(node)
        swap = self.SWAPS.get(type(node.op))
        if swap:
            if self._current_index == self.target_index:
                node.op = swap()
                self.mutations_applied += 1
            self._current_index += 1
        return node


MUTATOR_CLASSES: list[type[MutationOperator]] = [
    ComparisonMutator,
    BoolOpMutator,
    ReturnConstMutator,
    NoneReturnMutator,
    BinOpMutator,
]


# ── Runner ──────────────────────────────────────────────────────────
@dataclass
class MutationResult:
    label: str
    total_mutants: int = 0
    killed: int = 0
    survived: int = 0
    errors: int = 0
    details: list[str] = field(default_factory=list)

    @property
    def kill_ratio(self) -> float:
        if self.total_mutants == 0:
            return 1.0
        return self.killed / self.total_mutants


def count_mutations(tree: ast.AST, mutator_cls: type[MutationOperator]) -> int:
    """Count how many mutation sites exist for a given mutator."""
    tree_copy = copy.deepcopy(tree)
    m = mutator_cls()
    m.target_index = -1  # counting mode
    m._current_index = 0
    m.visit(tree_copy)
    return m._current_index


def apply_mutation(
    source: str, mutator_cls: type[MutationOperator], index: int
) -> str | None:
    """Apply the i-th mutation and return mutated source, or None on failure."""
    tree = ast.parse(source)
    m = mutator_cls()
    m.target_index = index
    m._current_index = 0
    m.mutations_applied = 0
    mutated = m.visit(tree)
    if m.mutations_applied == 0:
        return None
    ast.fix_missing_locations(mutated)
    try:
        return ast.unparse(mutated)
    except Exception:
        return None


def run_tests(
    source_file: Path, mutated_source: str, test_files: list[str]
) -> bool:
    """Run tests against mutated source. Returns True if mutant was killed."""
    original = source_file.read_text()
    try:
        source_file.write_text(mutated_source)
        cmd = [
            sys.executable, "-m", "pytest",
            "--no-header", "-x", "-q",
            "--tb=no",
            "--override-ini=addopts=",
        ] + test_files
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT),
        )
        # If tests fail → mutant killed (good)
        return result.returncode != 0
    except subprocess.TimeoutExpired:
        return True  # timeout = killed
    except Exception:
        return True
    finally:
        source_file.write_text(original)


def run_mutation_testing(target: MutationTarget) -> MutationResult:
    """Run mutation testing on a single target."""
    result = MutationResult(label=target.label)
    source = target.source_file.read_text()
    tree = ast.parse(source)

    # Filter test files to those that actually exist
    test_files = [t for t in target.test_files if Path(ROOT / t).exists()]
    if not test_files:
        print(f"  ⚠ No test files found for {target.label}, skipping")
        return result

    for mutator_cls in MUTATOR_CLASSES:
        n_sites = count_mutations(tree, mutator_cls)
        mutator_name = mutator_cls.__name__

        for i in range(n_sites):
            mutated = apply_mutation(source, mutator_cls, i)
            if mutated is None:
                continue

            result.total_mutants += 1
            killed = run_tests(target.source_file, mutated, test_files)

            if killed:
                result.killed += 1
                status = "🔴 KILLED"
            else:
                result.survived += 1
                status = "🟢 SURVIVED"
                result.details.append(f"  {mutator_name}[{i}]")

            # Progress indicator
            ratio = result.killed / result.total_mutants * 100
            print(
                f"  {mutator_name}[{i}] → {status}  "
                f"({result.killed}/{result.total_mutants} = {ratio:.0f}%)",
                flush=True,
            )

    return result


def main() -> int:
    print("=" * 60)
    print("🧬 Mutation Testing — Critical Paths")
    print("=" * 60)

    # Quick sanity: ensure baseline tests pass
    print("\n📋 Verifying baseline tests pass...")
    all_test_files = []
    for t in TARGETS:
        all_test_files.extend(
            f for f in t.test_files if Path(ROOT / f).exists()
        )

    if all_test_files:
        baseline = subprocess.run(
            [sys.executable, "-m", "pytest", "--no-header", "-q", "--override-ini=addopts=", "--tb=short"]
            + all_test_files,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        if baseline.returncode != 0:
            print("❌ Baseline tests fail — fix tests before mutation testing")
            print(baseline.stdout[-500:] if len(baseline.stdout) > 500 else baseline.stdout)
            return 1

    print("✅ Baseline tests pass\n")

    results: list[MutationResult] = []
    for target in TARGETS:
        print(f"\n{'─' * 50}")
        print(f"🎯 {target.label} ({target.source_file.name})")
        print(f"{'─' * 50}")
        r = run_mutation_testing(target)
        results.append(r)
        if r.total_mutants > 0:
            print(
                f"\n  → {r.label}: {r.killed}/{r.total_mutants} killed "
                f"({r.kill_ratio * 100:.0f}%)"
            )
            if r.details:
                print(f"  Survivors:")
                for d in r.details[:10]:
                    print(f"    {d}")

    # Summary
    total = sum(r.total_mutants for r in results)
    killed = sum(r.killed for r in results)
    ratio = killed / total * 100 if total > 0 else 100

    print(f"\n{'=' * 60}")
    print(f"📊 OVERALL: {killed}/{total} mutants killed ({ratio:.0f}%)")
    for r in results:
        mark = "✅" if r.kill_ratio >= 0.80 else "❌"
        print(f"  {mark} {r.label}: {r.killed}/{r.total_mutants} ({r.kill_ratio * 100:.0f}%)")
    print(f"{'=' * 60}")

    gate = ratio >= 80.0
    if gate:
        print("✅ v0.2.1 gate: ≥80% mutation kill ratio MET")
    else:
        print("❌ v0.2.1 gate: ≥80% mutation kill ratio NOT MET")

    return 0 if gate else 1


if __name__ == "__main__":
    sys.exit(main())
