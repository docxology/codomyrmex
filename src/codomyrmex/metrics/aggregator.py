"""Unified metrics aggregation and reporting."""

from typing import Dict, List, Optional, Any
import time
import logging

logger = logging.getLogger(__name__)

class MetricAggregator:
    """Aggregates metrics locally before pushing or for local analysis."""
    
    def __init__(self):
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        
    def increment(self, name: str, value: float = 1.0):
        self._counters[name] = self._counters.get(name, 0.0) + value

    def set_gauge(self, name: str, value: float):
        self._gauges[name] = value

    def get_snapshot(self) -> Dict[str, Any]:
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "timestamp": time.time()
        }

    def reset(self):
        self._counters.clear()
        # Gauges usually persist their last value
