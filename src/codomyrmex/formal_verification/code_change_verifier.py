"""Code-change verifier using AST analysis and invariant rules.

Provides a framework for verifying that proposed code changes preserve
structural invariants (e.g. no deleted public functions, parameter
compatibility, signature stability). Rules are pluggable and composable.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


@dataclass
class ChangeProposal:
    """A proposed code change to verify.

    Attributes:
        file_path: Path to the file being changed.
        original_source: Original Python source code.
        modified_source: Modified Python source code.
    """

    file_path: str
    original_source: str
    modified_source: str


@dataclass
class RuleResult:
    """Result of evaluating a single invariant rule.

    Attributes:
        rule_name: Name of the rule.
        passed: Whether the rule passed.
        message: Human-readable explanation.
        details: Optional structured details.
    """

    rule_name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationResult:
    """Aggregate result of all invariant checks.

    Attributes:
        passed: True if all rules passed.
        rule_results: Per-rule results.
        summary: Human-readable summary.
    """

    passed: bool
    rule_results: list[RuleResult] = field(default_factory=list)
    summary: str = ""


@dataclass
class InvariantRule:
    """An invariant rule for code-change verification.

    Attributes:
        name: Rule identifier.
        description: Human-readable description of what the rule checks.
        check_fn: Callable(ChangeProposal) -> RuleResult.
    """

    name: str
    description: str
    check_fn: Callable[[ChangeProposal], RuleResult]


# ── AST Helpers ──────────────────────────────────────────────────────


def _extract_public_functions(source: str) -> dict[str, ast.FunctionDef]:
    """Extract public (non-underscore) function definitions from source.

    Args:
        source: Python source code.

    Returns:
        Dict mapping function name to its AST node.
    """
    result: dict[str, ast.FunctionDef] = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                result[node.name] = node

    return result


def _extract_function_params(node: ast.FunctionDef) -> list[str]:
    """Extract parameter names from a function definition.

    Args:
        node: AST function definition node.

    Returns:
        List of parameter names (excluding 'self' and 'cls').
    """
    params = []
    for arg in node.args.args:
        name = arg.arg
        if name not in ("self", "cls"):
            params.append(name)
    return params


# ── Built-in Rules ───────────────────────────────────────────────────


def _check_no_deleted_public_functions(proposal: ChangeProposal) -> RuleResult:
    """Verify no public functions were deleted."""
    original_fns = _extract_public_functions(proposal.original_source)
    modified_fns = _extract_public_functions(proposal.modified_source)

    deleted = set(original_fns.keys()) - set(modified_fns.keys())

    if deleted:
        return RuleResult(
            rule_name="no_deleted_public_functions",
            passed=False,
            message=f"Public functions deleted: {', '.join(sorted(deleted))}",
            details={"deleted_functions": sorted(deleted)},
        )

    return RuleResult(
        rule_name="no_deleted_public_functions",
        passed=True,
        message=f"All {len(original_fns)} public functions preserved.",
    )


def _check_no_removed_parameters(proposal: ChangeProposal) -> RuleResult:
    """Verify no parameters were removed from existing public functions."""
    original_fns = _extract_public_functions(proposal.original_source)
    modified_fns = _extract_public_functions(proposal.modified_source)

    violations: dict[str, list[str]] = {}

    for fn_name, orig_node in original_fns.items():
        if fn_name in modified_fns:
            orig_params = set(_extract_function_params(orig_node))
            mod_params = set(_extract_function_params(modified_fns[fn_name]))
            removed = orig_params - mod_params
            if removed:
                violations[fn_name] = sorted(removed)

    if violations:
        return RuleResult(
            rule_name="no_removed_parameters",
            passed=False,
            message=f"Parameters removed in {len(violations)} function(s).",
            details={"violations": violations},
        )

    return RuleResult(
        rule_name="no_removed_parameters",
        passed=True,
        message="No parameters removed from public functions.",
    )


def _check_signature_compat(proposal: ChangeProposal) -> RuleResult:
    """Verify signature compatibility: existing params keep same order."""
    original_fns = _extract_public_functions(proposal.original_source)
    modified_fns = _extract_public_functions(proposal.modified_source)

    violations: list[str] = []

    for fn_name, orig_node in original_fns.items():
        if fn_name in modified_fns:
            orig_params = _extract_function_params(orig_node)
            mod_params = _extract_function_params(modified_fns[fn_name])

            # Check that original params appear in same order in modified
            orig_idx = 0
            for param in mod_params:
                if orig_idx < len(orig_params) and param == orig_params[orig_idx]:
                    orig_idx += 1

            if orig_idx != len(orig_params):
                violations.append(fn_name)

    if violations:
        return RuleResult(
            rule_name="signature_compat",
            passed=False,
            message=f"Parameter order changed in: {', '.join(violations)}",
            details={"reordered_functions": violations},
        )

    return RuleResult(
        rule_name="signature_compat",
        passed=True,
        message="All function signatures are order-compatible.",
    )


# ── Pre-built rule instances ─────────────────────────────────────────

NO_DELETED_PUBLIC_FUNCTIONS = InvariantRule(
    name="no_deleted_public_functions",
    description="Ensures no public functions are removed.",
    check_fn=_check_no_deleted_public_functions,
)

NO_REMOVED_PARAMETERS = InvariantRule(
    name="no_removed_parameters",
    description="Ensures no parameters are removed from public function signatures.",
    check_fn=_check_no_removed_parameters,
)

SIGNATURE_COMPAT = InvariantRule(
    name="signature_compat",
    description="Ensures existing parameter ordering is preserved.",
    check_fn=_check_signature_compat,
)

DEFAULT_RULES: list[InvariantRule] = [
    NO_DELETED_PUBLIC_FUNCTIONS,
    NO_REMOVED_PARAMETERS,
    SIGNATURE_COMPAT,
]


# ── Verifier ─────────────────────────────────────────────────────────


class CodeChangeVerifier:
    """Verifies code changes against a set of invariant rules.

    Example::

        verifier = CodeChangeVerifier()  # uses DEFAULT_RULES
        result = verifier.verify(
            ChangeProposal(
                file_path="module.py",
                original_source=old_code,
                modified_source=new_code,
            )
        )
        print(result.passed, result.summary)
    """

    def __init__(self, rules: list[InvariantRule] | None = None) -> None:
        """Initialize with invariant rules.

        Args:
            rules: List of InvariantRule to apply. Defaults to DEFAULT_RULES.
        """
        self._rules: list[InvariantRule] = list(rules or DEFAULT_RULES)

    def add_rule(self, rule: InvariantRule) -> None:
        """Register an additional invariant rule.

        Args:
            rule: Rule to add.
        """
        self._rules.append(rule)

    def verify(self, proposal: ChangeProposal) -> VerificationResult:
        """Run all invariant rules against a change proposal.

        Args:
            proposal: The proposed code change.

        Returns:
            VerificationResult with per-rule outcomes.
        """
        results: list[RuleResult] = []

        for rule in self._rules:
            try:
                result = rule.check_fn(proposal)
            except Exception as exc:
                logger.warning("Rule '%s' raised: %s", rule.name, exc)
                result = RuleResult(
                    rule_name=rule.name,
                    passed=False,
                    message=f"Rule raised an exception: {exc}",
                )
            results.append(result)

        all_passed = all(r.passed for r in results)
        passed_count = sum(1 for r in results if r.passed)
        total = len(results)

        summary = f"{passed_count}/{total} rules passed"
        if not all_passed:
            failed = [r.rule_name for r in results if not r.passed]
            summary += f" — FAILED: {', '.join(failed)}"

        logger.info(
            "Verification of '%s': %s",
            proposal.file_path,
            "PASSED" if all_passed else "FAILED",
        )

        return VerificationResult(
            passed=all_passed,
            rule_results=results,
            summary=summary,
        )


__all__ = [
    "DEFAULT_RULES",
    "NO_DELETED_PUBLIC_FUNCTIONS",
    "NO_REMOVED_PARAMETERS",
    "SIGNATURE_COMPAT",
    "ChangeProposal",
    "CodeChangeVerifier",
    "InvariantRule",
    "RuleResult",
    "VerificationResult",
]
