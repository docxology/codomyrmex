"""Demos Module.

Centralized registry and orchestration for system demonstrations.
"""

from .registry import DemoRegistry, demo, get_registry

__all__ = ["DemoRegistry", "demo", "get_registry"]
