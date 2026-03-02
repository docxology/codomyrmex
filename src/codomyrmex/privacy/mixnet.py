"""Mixnet Proxy Module.

Simulates anonymous routing via an overlay network (Melange Mixnet).
"""

import random
import time
import uuid
from dataclasses import dataclass

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

@dataclass
class Packet:
    """Functional component: Packet."""
    payload: bytes
    route_id: str
    hops_remaining: int

class MixNode:
    """A single node in the mixnet overlay."""
    def __init__(self, node_id: str):
        self.node_id = node_id

    def relay(self, packet: Packet) -> Packet | None:
        """Process and forward a packet."""
        # Simulate processing delay to thwart timing analysis
        time.sleep(random.uniform(0.01, 0.05))

        if packet.hops_remaining <= 0:
            return packet

        return Packet(
            payload=packet.payload,
            route_id=packet.route_id,
            hops_remaining=packet.hops_remaining - 1
        )

class MixnetProxy:
    """Manages anonymous routing through the mixnet."""

    def __init__(self):
        self._nodes = [MixNode(f"node_{i}") for i in range(10)]

    def route_payload(self, payload: bytes, hops: int = 3) -> bytes:
        """
        Route a payload through random mix nodes.
        Returns the payload as 'received' at the destination.
        """
        route_id = str(uuid.uuid4())
        packet = Packet(payload, route_id, hops)

        # Select random path
        path = random.sample(self._nodes, k=min(hops, len(self._nodes)))
        logger.info(f"Routing packet {route_id} via {len(path)} hops")

        current_packet = packet
        for node in path:
            current_packet = node.relay(current_packet)
            # logger.debug(f"Relayed via {node.node_id}")

        return current_packet.payload
