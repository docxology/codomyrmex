"""Tests for codomyrmex.utils.json_helpers (zero-mock, string fixtures only)."""

from __future__ import annotations

import json

import pytest

from codomyrmex.utils.json_helpers import extract_json_from_response


@pytest.mark.unit
def test_extract_json_from_response_direct_object() -> None:
    payload = {
        "adherence_assessment": {"adheres": True, "reasoning": "ok"},
        "technical_debt": [],
        "underlying_improvements": [],
    }
    text = json.dumps(payload)
    out = extract_json_from_response(text)
    assert out["adherence_assessment"]["adheres"] is True


@pytest.mark.unit
def test_extract_json_from_response_fenced_block() -> None:
    inner = '{"adherence_assessment": {"adheres": false, "reasoning": "x"}, "technical_debt": [], "underlying_improvements": []}'
    text = f"Here:\n```json\n{inner}\n```\n"
    out = extract_json_from_response(text)
    assert out["adherence_assessment"]["adheres"] is False


@pytest.mark.unit
def test_extract_json_from_response_empty() -> None:
    out = extract_json_from_response("   ")
    assert out["adherence_assessment"]["adheres"] is False
    assert "Empty" in out["technical_debt"][0]
