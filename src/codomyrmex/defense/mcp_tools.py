"""MCP tools for the defense module.

Exposes active defense mechanisms, exploit detection, and rabbithole tools
as auto-discovered MCP tools.
"""

from typing import Any

from codomyrmex.defense.active import ActiveDefense
from codomyrmex.defense.rabbithole import RabbitHole
from codomyrmex.model_context_protocol.decorators import mcp_tool

# Module-level instances for stateful tools
_active_defense = ActiveDefense()
_rabbit_hole = RabbitHole()


@mcp_tool(
    category="defense",
    description="Detect potential cognitive exploits in input text.",
)
def defense_detect_exploit(input_text: str) -> dict[str, Any]:
    """Detect potential cognitive exploits in input.

    Args:
        input_text: The input to scan.

    Returns:
        Dict containing detection results.
    """
    result = _active_defense.detect_exploit(input_text)
    # Convert ThreatLevel enum to string for JSON serialization
    return {
        "detected": result["detected"],
        "patterns": result["patterns"],
        "threat_level": result["threat_level"].name,
    }


@mcp_tool(
    category="defense",
    description="Generate adversarial context to poison the attacker's model.",
)
def defense_poison_context(attacker_id: str, intensity: float = 0.5) -> dict[str, Any]:
    """Generate adversarial context to poison the attacker's model.

    Args:
        attacker_id: ID of the detected attacker.
        intensity: 0.0 to 1.0, how much noise to inject.

    Returns:
        Dict containing poisoned context and metadata.
    """
    return _active_defense.poison_context(attacker_id, intensity)


@mcp_tool(
    category="defense",
    description="Create a canary token embedded in content.",
)
def defense_create_honeytoken(label: str = "", context: str = "") -> str:
    """Create a canary token embedded in content.

    Args:
        label: Human-readable label for tracking.
        context: Additional context about where the token was planted.

    Returns:
        The honeytoken string.
    """
    return _active_defense.create_honeytoken(label=label, context=context)


@mcp_tool(
    category="defense",
    description="Scan text for any planted honeytokens.",
)
def defense_check_honeytoken(text: str) -> list[str]:
    """Scan text for any planted honeytokens.

    Args:
        text: Input text to scan.

    Returns:
        List of triggered honeytoken IDs.
    """
    return _active_defense.check_honeytoken(text)


@mcp_tool(
    category="defense",
    description="Engage an attacker in a rabbit hole session.",
)
def defense_rabbithole_engage(attacker_id: str) -> str:
    """Engage an attacker in a rabbit hole session.

    Args:
        attacker_id: ID of the attacker to engage.

    Returns:
        Initial deceptive response.
    """
    return _rabbit_hole.engage(attacker_id)


@mcp_tool(
    category="defense",
    description="Generate a deceptive response for an engaged attacker.",
)
def defense_rabbithole_generate_response(attacker_id: str, input_text: str = "") -> str:
    """Generate a nonsensical, high-latency response to keep attacker occupied.

    Args:
        attacker_id: ID of the attacker.
        input_text: The attacker's input.

    Returns:
        Deceptive response string.
    """
    return _rabbit_hole.generate_response(attacker_id, input_text)
