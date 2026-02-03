"""Reverse Auction Module.

Enables agents to post anonymous demands and receive bids from providers.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class Bid:
    provider_id: str
    amount: float
    details: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AuctionRequest:
    id: str
    requester_persona_id: str  # Anonymous ID
    item_description: str
    max_price: float
    bids: List[Bid] = field(default_factory=list)
    status: str = "OPEN"

class ReverseAuction:
    """Manages anonymous reverse auctions."""

    def __init__(self):
        self._auctions: Dict[str, AuctionRequest] = {}

    def create_request(self, persona_id: str, description: str, max_price: float) -> str:
        """Create a new auction request."""
        auction_id = str(uuid.uuid4())
        request = AuctionRequest(
            id=auction_id,
            requester_persona_id=persona_id,
            item_description=description,
            max_price=max_price
        )
        self._auctions[auction_id] = request
        logger.info(f"Created auction {auction_id} for persona {persona_id}")
        return auction_id

    def place_bid(self, auction_id: str, provider_id: str, amount: float, details: str) -> bool:
        """Place a bid on an active auction."""
        if auction_id not in self._auctions:
            return False
            
        auction = self._auctions[auction_id]
        if auction.status != "OPEN":
            return False
            
        if amount > auction.max_price:
            logger.debug(f"Bid rejected: {amount} > {auction.max_price}")
            return False
            
        bid = Bid(provider_id=provider_id, amount=amount, details=details)
        auction.bids.append(bid)
        
        # Sort bids by amount ascending (best price first)
        auction.bids.sort(key=lambda x: x.amount)
        return True

    def get_best_bid(self, auction_id: str) -> Optional[Bid]:
        """Get the current best bid."""
        if auction_id not in self._auctions:
            return None
        auction = self._auctions[auction_id]
        if not auction.bids:
            return None
        return auction.bids[0]

    def close_auction(self, auction_id: str, requester_id: str) -> bool:
        """Close the auction and select winner."""
        if auction_id not in self._auctions:
            return False
        auction = self._auctions[auction_id]
        if auction.requester_persona_id != requester_id:
            return False # Not the owner
            
        auction.status = "CLOSED"
        return True

    def cancel_auction(self, auction_id: str, requester_id: str) -> bool:
        """Cancel an open auction."""
        if auction_id not in self._auctions:
            return False
        auction = self._auctions[auction_id]
        if auction.requester_persona_id != requester_id:
            return False
        if auction.status != "OPEN":
            return False
            
        auction.status = "CANCELLED"
        logger.info(f"Auction {auction_id} cancelled by {requester_id}")
        return True

    def get_history(self, persona_id: str) -> List[AuctionRequest]:
        """Get auction history for a persona."""
        return [
            a for a in self._auctions.values()
            if a.requester_persona_id == persona_id
        ]
