"""MCP tools for the testing module.

Exposes synthetic test data generation and strategy listing.
All generators are pure Python with no external dependencies.
"""

from __future__ import annotations

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs):
        def decorator(fn):
            fn._mcp_tool_meta = kwargs
            return fn
        return decorator


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
    config: dict | None = None,
) -> list:
    """Generate a list of synthetic test values."""
    from codomyrmex.testing import (
        DictGenerator,
        FloatGenerator,
        IntGenerator,
        ListGenerator,
        StringGenerator,
    )

    cfg = config or {}

    def _int_gen():
        return IntGenerator(
            min_val=cfg.get("min_val", 0),
            max_val=cfg.get("max_val", 100),
        )

    def _float_gen():
        return FloatGenerator(
            min_val=cfg.get("min_val", 0.0),
            max_val=cfg.get("max_val", 1.0),
        )

    def _string_gen():
        return StringGenerator(
            min_length=cfg.get("min_length", 1),
            max_length=cfg.get("max_length", 20),
        )

    def _list_gen():
        return ListGenerator(
            element_generator=IntGenerator(0, 10),
            min_length=cfg.get("min_length", 1),
            max_length=cfg.get("max_length", 5),
        )

    def _dict_gen():
        return DictGenerator(
            key_generator=StringGenerator(min_length=3, max_length=10),
            value_generator=IntGenerator(0, 100),
            min_size=cfg.get("min_size", 1),
            max_size=cfg.get("max_size", 5),
        )

    generators = {
        "int": _int_gen,
        "float": _float_gen,
        "string": _string_gen,
        "list": _list_gen,
        "dict": _dict_gen,
    }

    gen_factory = generators.get(strategy_type)
    if gen_factory is None:
        raise ValueError(
            f"Unknown strategy_type: {strategy_type!r}. "
            f"Use one of: {list(generators.keys())}"
        )

    gen = gen_factory()
    return [gen.generate() for _ in range(count)]


@mcp_tool(
    category="testing",
    description="List available test data generator strategy type names.",
)
def testing_list_strategies() -> list[str]:
    """Return supported generator strategy identifiers."""
    return ["int", "float", "string", "list", "dict"]
