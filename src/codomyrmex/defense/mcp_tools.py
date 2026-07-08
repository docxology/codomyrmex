from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .defense import Defense, ThreatEvent

_defense = Defense()


def _event_to_dict(event: ThreatEvent) -> dict[str, Any]:
    return {
        "source": event.source,
        "category": event.category,
        "severity": event.severity.value,
        "description": event.description,
        "response": event.response.value if event.response is not None else None,
        "metadata": dict(event.metadata),
    }


@mcp_tool(category="defense")
def defense_detect_exploit(input_text: str) -> dict[str, Any]:
    result = _defense.active.detect_exploit(input_text)
    return {
        "status": "success",
        "detected": result["detected"],
        "patterns": result["patterns"],
        "threat_level": result["threat_level"].name,
    }


@mcp_tool(category="defense")
def defense_process_request(
    source: str,
    request_path: str = "/",
    request_method: str = "GET",
    request_input: str = "",
) -> dict[str, Any]:
    allowed, threats = _defense.process_request(
        source,
        {
            "path": request_path,
            "method": request_method,
            "input": request_input,
        },
    )
    return {
        "status": "success",
        "allowed": allowed,
        "threat_count": len(threats),
        "threats": [_event_to_dict(event) for event in threats],
    }


@mcp_tool(category="defense")
def defense_threat_report() -> dict[str, Any]:
    return {"status": "success", **_defense.active.get_threat_report()}
