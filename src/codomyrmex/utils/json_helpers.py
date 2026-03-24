"""JSON extraction from LLM responses (Hermes/Ollama) for orchestrator evaluators."""

from __future__ import annotations

import json
import re
from typing import Any


def _extract_json_object(text: str) -> str | None:
    """Extract the first complete JSON object from *text* using brace-matching."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _sanitize_json_candidate(text: str) -> str:
    """Escape literal control characters inside JSON string values."""
    _ctrl = {
        "\n": "\\n",
        "\r": "\\r",
        "\t": "\\t",
        "\b": "\\b",
        "\f": "\\f",
    }
    result: list[str] = []
    in_string = False
    i = 0
    while i < len(text):
        ch = text[i]
        if in_string:
            if ch == "\\" and i + 1 < len(text):
                result.append(ch)
                result.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
                result.append(ch)
            elif ch in _ctrl:
                result.append(_ctrl[ch])
            else:
                result.append(ch)
        else:
            if ch == '"':
                in_string = True
            result.append(ch)
        i += 1
    return "".join(result)


def extract_json_from_response(content: str) -> dict[str, Any]:
    """Parse JSON from an LLM response (fenced block, embedded object, or raw JSON)."""
    if not content or not content.strip():
        return {
            "adherence_assessment": {
                "adheres": False,
                "reasoning": (
                    "Empty response from Hermes — backend may have timed out or returned nothing."
                ),
            },
            "technical_debt": ["Empty LLM response"],
            "underlying_improvements": [],
        }

    candidates: list[str] = []

    match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        candidates.append(match.group(1).strip())

    embedded = _extract_json_object(content)
    if embedded:
        candidates.append(embedded)

    candidates.append(content.strip())

    last_exc: Exception | None = None
    for raw_candidate in candidates:
        for candidate in (raw_candidate, _sanitize_json_candidate(raw_candidate)):
            try:
                result = json.loads(candidate)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError as exc:
                last_exc = exc

    prose = content.strip()
    if prose:
        lowered = prose.lower()
        adheres_signals = (
            "adheres to the thin orchestrator" in lowered
            or "follows the codomyrmex" in lowered
            or "meets all" in lowered
            or "complies with" in lowered
        )
        non_adheres_signals = (
            "does not adhere" in lowered
            or "fails to adhere" in lowered
            or "non-compliant" in lowered
            or "does not follow" in lowered
        )
        if adheres_signals and not non_adheres_signals:
            return {
                "adherence_assessment": {
                    "adheres": True,
                    "reasoning": f"[Prose-extracted verdict] {prose[:800]}",
                },
                "technical_debt": [],
                "underlying_improvements": [],
            }
        if non_adheres_signals:
            return {
                "adherence_assessment": {
                    "adheres": False,
                    "reasoning": f"[Prose-extracted verdict] {prose[:800]}",
                },
                "technical_debt": [prose[:300]],
                "underlying_improvements": [],
            }

    return {
        "adherence_assessment": {
            "adheres": False,
            "reasoning": f"Failed to parse JSON response (last error: {last_exc})",
        },
        "technical_debt": ["Malformed response from Hermes"],
        "underlying_improvements": [content[:500]],
    }
