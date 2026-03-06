"""Logistics routing algorithms."""

from .algorithms import NearestNeighborRouting, RoutingAlgorithm, TwoOptRouting
from .graph import AStarRouting, DijkstraRouting
from .models import Location, Route, RouteStop, RoutingConstraints


def create_routing_algorithm(algorithm_type: str, **kwargs) -> RoutingAlgorithm:
    """Factory function for routing algorithms."""
    algorithms: dict[str, type[RoutingAlgorithm]] = {
        "nearest_neighbor": NearestNeighborRouting,
        "two_opt": TwoOptRouting,
    }
    algo_class = algorithms.get(algorithm_type)
    if not algo_class:
        raise ValueError(f"Unknown algorithm: {algorithm_type}")
    return algo_class(**kwargs)


__all__ = [
    "AStarRouting",
    "DijkstraRouting",
    "Location",
    "NearestNeighborRouting",
    "Route",
    "RouteStop",
    "RoutingAlgorithm",
    "RoutingConstraints",
    "TwoOptRouting",
    "create_routing_algorithm",
]
