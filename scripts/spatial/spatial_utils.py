#!/usr/bin/env python3
"""
Spatial data utilities.

Usage:
    python spatial_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def bbox_area(min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> float:
    """Calculate bounding box area in km²."""
    width = haversine_distance(min_lat, min_lon, min_lat, max_lon)
    height = haversine_distance(min_lat, min_lon, max_lat, min_lon)
    return width * height


def point_in_bbox(lat: float, lon: float, bbox: tuple) -> bool:
    """Check if point is in bounding box."""
    min_lat, min_lon, max_lat, max_lon = bbox
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def main():
    parser = argparse.ArgumentParser(description="Spatial utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Distance command
    dist = subparsers.add_parser("distance", help="Calculate distance")
    dist.add_argument("lat1", type=float)
    dist.add_argument("lon1", type=float)
    dist.add_argument("lat2", type=float)
    dist.add_argument("lon2", type=float)
    
    # Area command
    area = subparsers.add_parser("area", help="Calculate bbox area")
    area.add_argument("min_lat", type=float)
    area.add_argument("min_lon", type=float)
    area.add_argument("max_lat", type=float)
    area.add_argument("max_lon", type=float)
    
    args = parser.parse_args()
    
    if not args.command:
        print("🌍 Spatial Utilities\n")
        print("Commands:")
        print("  distance - Calculate distance between points")
        print("  area     - Calculate bounding box area")
        print("\nExamples:")
        print("  python spatial_utils.py distance 40.7128 -74.0060 34.0522 -118.2437")
        print("  python spatial_utils.py area 40.0 -75.0 41.0 -73.0")
        return 0
    
    if args.command == "distance":
        d = haversine_distance(args.lat1, args.lon1, args.lat2, args.lon2)
        print(f"📏 Distance: {d:.2f} km ({d * 0.621371:.2f} mi)")
        print(f"   From: ({args.lat1}, {args.lon1})")
        print(f"   To: ({args.lat2}, {args.lon2})")
    
    elif args.command == "area":
        a = bbox_area(args.min_lat, args.min_lon, args.max_lat, args.max_lon)
        print(f"📐 Area: {a:.2f} km² ({a * 0.386102:.2f} mi²)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
