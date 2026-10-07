"""Bounded ``fn_expr`` evaluation used by ``orchestrator_run_dag``.

Real evaluator, no mocks: each case parses and evaluates an expression with
the same helpers the MCP tool uses.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.orchestrator.mcp_tools import (
    _MAX_INT_BITS,
    _compile_safe_expression,
    _safe_eval,
    orchestrator_run_dag,
)


def _eval(expr: str) -> object:
    return _safe_eval(_compile_safe_expression(expr))


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1 + 2 * 3", 7),
        ("-5 + +2", -3),
        ("not 0", True),
        ("2 ** 10", 1024),
        ("2 ** -1", 0.5),
        ("len('hello')", 5),
        ("sum([1, 2, 3])", 6),
        ("max((4, 9, 2))", 9),
        ("round(2.5)", 2),
        ("{'a': 1}['a']", 1),
        ("[1, 2, 3][1]", 2),
        ("1 < 2 < 3", True),
        ("3 in [1, 2, 3]", True),
        ("'x' not in 'abc'", True),
        ("0 or '' or 7", 7),
        ("1 and 0 and 9", 0),
        ("'ab' * 3", "ababab"),
    ],
)
def test_supported_expressions(expr: str, expected: object) -> None:
    assert _eval(expr) == expected


@pytest.mark.parametrize(
    ("expr", "message"),
    [
        ("__import__('os')", "Double underscores"),
        ("open('/etc/passwd')", "Unsupported function call"),
        ("round(3.14159, ndigits=2)", "Keyword and starred"),
        ("max(*[1, 2])", "Keyword and starred"),
        ("{**{'a': 1}}", "Dictionary unpacking"),
        ("'abc'[0:2]", "Slicing"),
        ("(lambda: 1)()", "Unsupported function call"),
        ("1 << 2", "Unsupported operator"),
        ("~1", "Unsupported operator"),
        ("1 is 1", "Unsupported comparison operator"),
        ("x", "Unknown variable"),
        ("1 +", "Invalid expression syntax"),
    ],
)
def test_rejected_expressions(expr: str, message: str) -> None:
    with pytest.raises((ValueError, SyntaxError), match=message):
        _eval(expr)


def test_expression_length_is_bounded() -> None:
    with pytest.raises(ValueError, match="at most 256 characters"):
        _compile_safe_expression("1+" * 200 + "1")


def test_non_string_expression_rejected() -> None:
    with pytest.raises(ValueError, match="must be a string"):
        _compile_safe_expression(42)


@pytest.mark.parametrize(
    "expr",
    [
        "9 ** 9 ** 9 ** 9",
        "10 ** 100000",
        "(10 ** 300) ** 300",
        "'a' * 10 ** 9",
        "[0] * 10 ** 8",
        "10 ** 9 * 'a'",
    ],
)
def test_resource_exhaustion_is_rejected_quickly(expr: str) -> None:
    start = time.perf_counter()
    with pytest.raises(ValueError, match="exceeds"):
        _eval(expr)
    assert time.perf_counter() - start < 1.0


def test_large_but_bounded_power_is_allowed() -> None:
    result = _eval("2 ** 4000")
    assert isinstance(result, int)
    assert result.bit_length() <= _MAX_INT_BITS + 1


def test_run_dag_reports_bounded_evaluation_errors() -> None:
    result = orchestrator_run_dag("fan_out", [{"id": "bomb", "fn_expr": "9**9**9**9"}])
    assert result["status"] == "failed"
    assert "exceeds" in str(result)
