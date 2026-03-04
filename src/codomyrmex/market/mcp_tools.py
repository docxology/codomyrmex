"""MCP tool definitions for the market module.

Exposes reverse auction and demand aggregation as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_auction():
    """Lazy import of ReverseAuction."""
    from codomyrmex.market.auction import ReverseAuction

    return ReverseAuction


def _get_aggregator():
    """Lazy import of DemandAggregator."""
    from codomyrmex.market.aggregator import DemandAggregator

    return DemandAggregator


@mcp_tool(
    category="market",
    description="Create a new reverse auction request with a maximum price constraint.",
)
def market_create_auction(
    persona_id: str, description: str, max_price: float
) -> dict[str, Any]:
    """Create a reverse auction request.

    Args:
        persona_id: Anonymous identity of the requester.
        description: Description of the item or service to auction.
        max_price: Maximum acceptable price.

    Returns:
        dict with keys: status, auction_id
    """
    try:
        auction_cls = _get_auction()
        auction = auction_cls()
        auction_id = auction.create_request(persona_id, description, max_price)
        return {"status": "success", "auction_id": auction_id}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="market",
    description="Get demand aggregation statistics for a product or service category.",
)
def market_demand_stats(category: str) -> dict[str, Any]:
    """Return demand statistics for a given category.

    Uses a fresh DemandAggregator instance. To get meaningful results
    the aggregator must have previously registered interest.

    Args:
        category: Product or service category name.

    Returns:
        dict with keys: status, category, stats (or message if no demand)
    """
    try:
        auction_cls = _get_auction()
        agg_cls = _get_aggregator()
        auction = auction_cls()
        aggregator = agg_cls(auction)
        stats = aggregator.get_stats(category)
        if stats is None:
            return {
                "status": "success",
                "category": category,
                "stats": None,
                "message": "No demand registered for this category",
            }
        return {
            "status": "success",
            "category": category,
            "stats": {
                "demand_count": stats.demand_count,
                "total_quantity": stats.total_quantity,
                "avg_max_price": stats.avg_max_price,
                "min_max_price": stats.min_max_price,
                "max_max_price": stats.max_max_price,
                "unique_personas": stats.unique_personas,
            },
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="market",
    description="List all available categories with pending demand in the aggregator.",
)
def market_list_categories() -> dict[str, Any]:
    """List demand categories tracked by the aggregator.

    Returns:
        dict with keys: status, categories, count
    """
    try:
        auction_cls = _get_auction()
        agg_cls = _get_aggregator()
        auction = auction_cls()
        aggregator = agg_cls(auction)
        categories = aggregator.list_categories()
        return {"status": "success", "categories": categories, "count": len(categories)}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
