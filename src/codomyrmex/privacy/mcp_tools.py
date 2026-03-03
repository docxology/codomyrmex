"""Model Context Protocol (MCP) tools for the privacy module."""

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.privacy.crumbs import CrumbCleaner
from codomyrmex.privacy.mixnet import MixnetProxy
from codomyrmex.privacy.privacy import PrivacyRule, create_privacy

# Shared instances for tool usage
_crumb_cleaner = CrumbCleaner()
_mixnet_proxy = MixnetProxy()


@mcp_tool()
def privacy_scan(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Scan the provided data for PII and privacy issues.

    Args:
        data: A flat dict of field->value pairs to scan.

    Returns:
        A list of dicts representing detected PII occurrences.
    """
    if not isinstance(data, dict):
        raise TypeError("Input 'data' must be a dictionary")

    privacy = create_privacy()
    matches = privacy.scan_pii(data)

    return [
        {
            "field": match.field,
            "pii_type": match.pii_type,
            "value": match.value,
            "start": match.start,
            "end": match.end,
        }
        for match in matches
    ]


@mcp_tool()
def privacy_scrub_crumbs(data: Any) -> Any:
    """Sanitizes data by recursively removing tracking crumbs and metadata.

    Args:
        data: The dictionary or list to scrub.

    Returns:
        A sanitized copy of the input data.
    """
    if data is None:
        raise ValueError("Input 'data' cannot be None")

    return _crumb_cleaner.scrub(data)


@mcp_tool()
def privacy_route_payload(payload: str, hops: int = 3) -> str:
    """Route a string payload through simulated anonymous mix nodes.

    Args:
        payload: The string data to route.
        hops: Number of nodes to route through (default: 3).

    Returns:
        The payload after routing, as a string.
    """
    if not isinstance(payload, str):
        raise TypeError("Input 'payload' must be a string")

    if not isinstance(hops, int):
        raise TypeError("Input 'hops' must be an integer")

    if hops < 1:
        raise ValueError("Input 'hops' must be at least 1")

    payload_bytes = payload.encode("utf-8")
    routed_bytes = _mixnet_proxy.route_payload(payload_bytes, hops=hops)
    return routed_bytes.decode("utf-8")


@mcp_tool()
def privacy_process(
    data: dict[str, Any], rules: list[dict[str, Any]]
) -> dict[str, Any]:
    """Apply configured privacy rules to anonymize a specific payload.

    Args:
        data: A flat dict of field->value pairs.
        rules: A list of dicts representing rules. Each dict must have 'field' and 'strategy'.
               May optionally have 'params' (dict).

    Returns:
        A copy of the data with anonymized fields.
    """
    if not isinstance(data, dict):
        raise TypeError("Input 'data' must be a dictionary")

    if not isinstance(rules, list):
        raise TypeError("Input 'rules' must be a list of dictionaries")

    privacy = create_privacy()

    for rule_data in rules:
        if not isinstance(rule_data, dict):
            raise TypeError("Each rule must be a dictionary")

        field = rule_data.get("field")
        strategy = rule_data.get("strategy")
        params = rule_data.get("params", {})

        if not field or not strategy:
            raise ValueError("Rule must have 'field' and 'strategy' defined")

        privacy.add_rule(PrivacyRule(field=field, strategy=strategy, params=params))

    return privacy.process(data)
