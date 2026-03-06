"""Logistics routing data models."""

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Location:
    """A geographic location."""

    id: str
    name: str
    latitude: float
    longitude: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def distance_to(self, other: "Location") -> float:
        """Calculate haversine distance to another location (in km)."""
        R = 6371
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return R * 2 * math.asin(math.sqrt(a))


@dataclass
class RoutingConstraints:
    """Constraints for routing optimization."""

    max_distance: float | None = None
    max_duration: float | None = None
    max_stops: int | None = None
    required_stops: list[str] = field(default_factory=list)
    avoid_locations: list[str] = field(default_factory=list)
    vehicle_capacity: float | None = None
    time_windows: dict[str, tuple[int, int]] = field(default_factory=dict)


@dataclass
class RouteStop:
    """A stop in a route."""

    location: Location
    arrival_time: float | None = None
    departure_time: float | None = None
    service_time: float = 0.0
    load: float = 0.0


@dataclass
class Route:
    """A complete route."""

    id: str
    stops: list[RouteStop]
    total_distance: float = 0.0
    total_duration: float = 0.0
    total_load: float = 0.0

    def add_stop(
        self,
        location: Location,
        distance_from_prev: float,
        service_time: float = 0.0,
        load: float = 0.0,
        speed: float = 50.0,
    ) -> None:
        duration = (distance_from_prev / speed) * 60
        arrival = 0.0
        if self.stops:
            prev = self.stops[-1]
            arrival = (prev.departure_time or 0) + duration
        self.stops.append(
            RouteStop(
                location=location,
                arrival_time=arrival,
                departure_time=arrival + service_time,
                service_time=service_time,
                load=load,
            )
        )
        self.total_distance += distance_from_prev
        self.total_duration += duration + service_time
        self.total_load += load

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stops": [
                {
                    "location_id": s.location.id,
                    "location_name": s.location.name,
                    "arrival": s.arrival_time,
                    "departure": s.departure_time,
                }
                for s in self.stops
            ],
            "total_distance_km": round(self.total_distance, 2),
            "total_duration_min": round(self.total_duration, 2),
        }
