"""MCP Tools for the Market Module.

Provides model context protocol tools for reverse auctions and demand aggregation.
"""

from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger
from codomyrmex.market.aggregator import DemandAggregator
from codomyrmex.market.auction import ReverseAuction
from codomyrmex.market.market import Market
from codomyrmex.model_context_protocol.decorators import mcp_tool

logger = get_logger(__name__)

# Global instances for MCP tools
_auction_system = ReverseAuction()
_demand_aggregator = DemandAggregator(_auction_system)
_market_system = Market()


@mcp_tool(category="market", description="Create a new reverse auction request.")
def market_create_auction(persona_id: str, description: str, max_price: float) -> dict[str, Any]:
    """Create a new auction request.

    Args:
        persona_id: ID of the requesting persona.
        description: Description of the requested item or service.
        max_price: Maximum acceptable price.

    Returns:
        A dictionary containing the auction ID and status.
    """
    try:
        auction_id = _auction_system.create_request(persona_id, description, max_price)
        return {"status": "success", "auction_id": auction_id}
    except Exception as e:
        logger.error(f"Error creating auction: {e}")
        return {"status": "error", "message": str(e)}


@mcp_tool(category="market", description="Place a bid on an active auction.")
def market_place_bid(auction_id: str, provider_id: str, amount: float, details: str) -> dict[str, Any]:
    """Place a bid on an active auction.

    Args:
        auction_id: ID of the auction to bid on.
        provider_id: ID of the bidding provider.
        amount: Bid amount (must be <= max_price).
        details: Additional details for the bid.

    Returns:
        A dictionary containing the bid placement status.
    """
    try:
        success = _auction_system.place_bid(auction_id, provider_id, amount, details)
        if success:
            return {"status": "success", "message": "Bid placed successfully"}
        else:
            return {"status": "error", "message": "Failed to place bid. Check auction status or max price."}
    except Exception as e:
        logger.error(f"Error placing bid: {e}")
        return {"status": "error", "message": str(e)}


@mcp_tool(category="market", description="Get the best bid for an auction.")
def market_get_best_bid(auction_id: str) -> dict[str, Any]:
    """Get the current best bid.

    Args:
        auction_id: ID of the auction.

    Returns:
        A dictionary containing the best bid details or an error message.
    """
    try:
        best_bid = _auction_system.get_best_bid(auction_id)
        if best_bid:
            return {
                "status": "success",
                "bid": {
                    "provider_id": best_bid.provider_id,
                    "amount": best_bid.amount,
                    "details": best_bid.details,
                    "timestamp": best_bid.timestamp.isoformat()
                }
            }
        else:
            return {"status": "success", "message": "No bids found or auction does not exist"}
    except Exception as e:
        logger.error(f"Error getting best bid: {e}")
        return {"status": "error", "message": str(e)}


@mcp_tool(category="market", description="Register demand for a specific category.")
def market_register_demand(category: str, persona_id: str, max_price: float, quantity: int = 1) -> dict[str, Any]:
    """Register demand for a category to participate in collective bargaining.

    Args:
        category: Product or service category.
        persona_id: ID of the requesting persona.
        max_price: Maximum acceptable price per unit.
        quantity: Number of units desired.

    Returns:
        A dictionary containing the registration status.
    """
    try:
        entry = _demand_aggregator.register_interest(category, persona_id, max_price, quantity)
        return {
            "status": "success",
            "message": "Demand registered successfully",
            "entry": {
                "persona_id": entry.persona_id,
                "category": entry.category,
                "max_price": entry.max_price,
                "quantity": entry.quantity
            }
        }
    except Exception as e:
        logger.error(f"Error registering demand: {e}")
        return {"status": "error", "message": str(e)}


@mcp_tool(category="market", description="Trigger a bulk auction for a category if demand meets the threshold.")
def market_trigger_bulk_auction(category: str, threshold: int | None = None) -> dict[str, Any]:
    """Trigger a bulk auction if enough demand is gathered.

    Args:
        category: Category to check.
        threshold: Override threshold (default: per-category or global).

    Returns:
        A dictionary containing the triggered auction ID or status message.
    """
    try:
        auction_id = _demand_aggregator.trigger_bulk_auction(category, threshold)
        if auction_id:
            return {"status": "success", "auction_id": auction_id}
        else:
            return {"status": "success", "message": "Threshold not met or no demand found"}
    except Exception as e:
        logger.error(f"Error triggering bulk auction: {e}")
        return {"status": "error", "message": str(e)}

@mcp_tool(category="market", description="Get statistics for marketplace.")
def market_get_stats() -> dict[str, Any]:
    """Get marketplace statistics including agents and tasks.

    Returns:
        A dictionary containing marketplace statistics.
    """
    try:
        stats = _market_system.get_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Error getting market stats: {e}")
        return {"status": "error", "message": str(e)}
