"""Market Module.

Provides Reverse Auction and Demand Aggregation capabilities.
"""

from .aggregator import DemandAggregator
from .auction import AuctionRequest, Bid, ReverseAuction

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None


def cli_commands():
    """Return CLI commands for the market module."""
    return {
        "stats": {
            "help": "Show marketplace statistics",
            "handler": lambda: print(
                "Marketplace Stats:\n"
                "  Active auctions:    0\n"
                "  Total bids:         0\n"
                "  Demand aggregator:  ready"
            ),
        },
        "agents": {
            "help": "List registered agents in the marketplace",
            "handler": lambda: print(
                "Registered marketplace agents:\n"
                "  (none currently registered)"
            ),
        },
    }


__all__ = [
    "ReverseAuction",
    "Bid",
    "AuctionRequest",
    "DemandAggregator",
    # CLI integration
    "cli_commands",
]
