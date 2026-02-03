"""Demand Aggregation Module.

Aggregates demand from multiple entities to increase negotiation power.
"""

from typing import List, Dict
from .auction import ReverseAuction
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

class DemandAggregator:
    """Aggregates similar demands into a bulk auction."""

    def __init__(self, auction_system: ReverseAuction):
        self.auction_system = auction_system
        # category -> list of (persona_id, max_price)
        self._pending_demands: Dict[str, List[tuple]] = {} 

    def register_interest(self, category: str, persona_id: str, max_price: float) -> None:
        """Register interest in a specific category (e.g., 'GPU Compute')."""
        if category not in self._pending_demands:
            self._pending_demands[category] = []
        
        self._pending_demands[category].append((persona_id, max_price))
        logger.info(f"Registered demand for {category} from {persona_id}")

    def trigger_bulk_auction(self, category: str, threshold: int = 5) -> str:
        """
        Trigger a bulk auction if enough demand is gathered.
        Returns the auction ID if created.
        """
        if category not in self._pending_demands:
            return ""
            
        demands = self._pending_demands[category]
        if len(demands) < threshold:
            logger.debug(f"Not enough demand for {category} ({len(demands)}/{threshold})")
            return ""
            
        # Calculate bulk parameters
        total_items = len(demands)
        avg_price = sum(p for _, p in demands) / total_items
        # Apply bulk discount expectation (e.g. 10%)
        target_price_per_unit = avg_price * 0.90
        
        description = f"Bulk Request: {total_items} units of {category}"
        
        # Use a system-level persona or the first user as proxy
        proxy_persona = demands[0][0] 
        
        auction_id = self.auction_system.create_request(
            persona_id=proxy_persona,
            description=description,
            max_price=target_price_per_unit * total_items
        )
        
        # Clear pending
        del self._pending_demands[category]
        logger.info(f"Triggered bulk auction {auction_id} for {category}")
        return auction_id
