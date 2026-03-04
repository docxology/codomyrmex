"""MCP tool definitions for the defense module.

Exposes threat detection, rate limiting, and defense status as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_defense(config: dict[str, Any] | None = None):
    """Lazy import of Defense."""
    from codomyrmex.defense.defense import Defense

    return Defense(config)


def _get_active_defense():
    """Lazy import of ActiveDefense."""
    from codomyrmex.defense.active import ActiveDefense

    return ActiveDefense()


@mcp_tool(
    category="defense",
    description="Detect cognitive exploits and injection patterns in input text.",
)
def defense_detect_exploit(input_text: str) -> dict[str, Any]:
    """Scan input text for cognitive exploit patterns.

    Args:
        input_text: The text to scan for exploit patterns.

    Returns:
        dict with keys: status, detected, patterns, threat_level
    """
    try:
        active = _get_active_defense()
        result = active.detect_exploit(input_text)
        return {
            "status": "success",
            "detected": result["detected"],
            "patterns": result["patterns"],
            "threat_level": result["threat_level"].name,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="defense",
    description=(
        "Process a request through the defense pipeline including "
        "rate limiting, blocklist checks, and threat detection."
    ),
)
def defense_process_request(
    source: str,
    request_path: str = "/",
    request_method: str = "GET",
    request_input: str = "",
) -> dict[str, Any]:
    """Process a request through the full defense pipeline.

    Args:
        source: Source identifier (e.g., IP address).
        request_path: Request path.
        request_method: HTTP method.
        request_input: Optional input text to scan for exploits.

    Returns:
        dict with keys: status, allowed, threats, threat_count
    """
    try:
        defense = _get_defense()
        request: dict[str, Any] = {"path": request_path, "method": request_method}
        if request_input:
            request["input"] = request_input
        allowed, threats = defense.process_request(source=source, request=request)
        return {
            "status": "success",
            "allowed": allowed,
            "threat_count": len(threats),
            "threats": [
                {
                    "category": t.category,
                    "severity": t.severity.value,
                    "description": t.description,
                    "response": t.response.value if t.response else None,
                }
                for t in threats
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="defense",
    description="Get a threat report with current defense metrics and active pattern counts.",
)
def defense_threat_report() -> dict[str, Any]:
    """Get a summary of current defense metrics.

    Returns:
        dict with keys: status, active_patterns, exploits_detected,
        honeytokens_active, honeytokens_triggered
    """
    try:
        active = _get_active_defense()
        report = active.get_threat_report()
        return {
            "status": "success",
            **report,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
