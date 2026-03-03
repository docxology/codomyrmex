"""MCP tools for the testing module.

Exposes synthetic test data generation and strategy listing.
All generators are pure Python with no external dependencies.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool
from codomyrmex.testing import (
    DictGenerator,
    FloatGenerator,
    IntGenerator,
    ListGenerator,
    StringGenerator,
    GeneratorStrategy,
)


def _get_generator(strategy_type: str, cfg: dict[str, Any]) -> GeneratorStrategy:
    """Helper to return the right generator."""
    if strategy_type == "int":
        return IntGenerator(
            min_val=cfg.get("min_val", 0),
            max_val=cfg.get("max_val", 100),
        )
    if strategy_type == "float":
        return FloatGenerator(
            min_val=cfg.get("min_val", 0.0),
            max_val=cfg.get("max_val", 1.0),
        )
    if strategy_type == "string":
        return StringGenerator(
            min_length=cfg.get("min_length", 1),
            max_length=cfg.get("max_length", 20),
        )
    if strategy_type == "list":
        return ListGenerator(
            element_generator=IntGenerator(0, 10),
            min_length=cfg.get("min_length", 1),
            max_length=cfg.get("max_length", 5),
        )
    if strategy_type == "dict":
        return DictGenerator(
            key_generator=StringGenerator(min_length=3, max_length=10),
            value_generator=IntGenerator(0, 100),
            min_size=cfg.get("min_size", 1),
            max_size=cfg.get("max_size", 5),
        )

    raise ValueError(
        f"Unknown strategy_type: {strategy_type!r}. "
        f"Use one of: ['int', 'float', 'string', 'list', 'dict']"
    )


@mcp_tool(
    category="testing",
    description=(
        "Generate synthetic test data using a named strategy. "
        "strategy_type: int, float, string, list, dict. "
        "config: optional dict of generator parameters (min_val, max_val, "
        "min_length, max_length, min_size, max_size). "
        "Returns a list of 'count' generated values."
    ),
)
def testing_generate_data(
    strategy_type: str,
    count: int = 10,
    config: dict[str, Any] | None = None,
) -> list[Any]:
    """Generate a list of synthetic test values."""
    cfg = config or {}
    gen = _get_generator(strategy_type, cfg)
    return [gen.generate() for _ in range(count)]


@mcp_tool(
    category="testing",
    description="List available test data generator strategy type names.",
)
def testing_list_strategies() -> list[str]:
    """Return supported generator strategy identifiers."""
    return ["int", "float", "string", "list", "dict"]
