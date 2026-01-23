"""ROS2 bridge implementation."""

import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class ROS2Bridge:
    """Mock-friendly ROS2 bridge."""
    
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.publishers: Dict[str, Any] = {}
        self.subscribers: Dict[str, Callable] = {}
        logger.info(f"ROS2 node '{node_name}' initialized")

    def publish(self, topic: str, message: Dict[str, Any]):
        """Publish a message to a topic."""
        logger.debug(f"Publishing to {topic}: {message}")
        # In real ROS2, this would use rclpy
        return True

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic."""
        self.subscribers[topic] = callback
        logger.info(f"Subscribed to {topic}")

    def simulate_message(self, topic: str, message: Dict[str, Any]):
        """Utility for testing: simulate an incoming message."""
        if topic in self.subscribers:
            self.subscribers[topic](message)
