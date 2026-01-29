#!/usr/bin/env python3
"""
Event system demonstration and utilities.

Usage:
    python event_demo.py [--demo TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
from collections import defaultdict
from typing import Callable
import time


class EventEmitter:
    """Simple event emitter implementation."""
    
    def __init__(self):
        self._handlers: dict = defaultdict(list)
        self._history: list = []
    
    def on(self, event: str, handler: Callable):
        """Register an event handler."""
        self._handlers[event].append(handler)
    
    def off(self, event: str, handler: Callable = None):
        """Remove event handler(s)."""
        if handler:
            self._handlers[event].remove(handler)
        else:
            self._handlers[event] = []
    
    def emit(self, event: str, *args, **kwargs):
        """Emit an event."""
        self._history.append({"event": event, "time": time.time()})
        for handler in self._handlers[event]:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                print(f"   ⚠️ Handler error: {e}")
    
    def get_stats(self) -> dict:
        """Get event statistics."""
        stats = defaultdict(int)
        for h in self._history:
            stats[h["event"]] += 1
        return dict(stats)


def demo_basic():
    """Basic event emitter demo."""
    print("📡 Basic Event Demo:\n")
    
    emitter = EventEmitter()
    
    # Register handlers
    def on_start(msg):
        print(f"   🟢 Started: {msg}")
    
    def on_complete(msg):
        print(f"   ✅ Completed: {msg}")
    
    def on_error(msg):
        print(f"   ❌ Error: {msg}")
    
    emitter.on("start", on_start)
    emitter.on("complete", on_complete)
    emitter.on("error", on_error)
    
    # Emit events
    emitter.emit("start", "Processing data...")
    emitter.emit("complete", "Task finished")
    emitter.emit("error", "Something went wrong")
    
    print(f"\n   Stats: {emitter.get_stats()}")


def demo_pipeline():
    """Event-driven pipeline demo."""
    print("🔄 Pipeline Demo:\n")
    
    emitter = EventEmitter()
    pipeline_data = {"stage": 0, "value": 0}
    
    def stage1(data):
        data["value"] += 10
        data["stage"] = 1
        print(f"   Stage 1: value = {data['value']}")
        emitter.emit("stage2", data)
    
    def stage2(data):
        data["value"] *= 2
        data["stage"] = 2
        print(f"   Stage 2: value = {data['value']}")
        emitter.emit("stage3", data)
    
    def stage3(data):
        data["value"] += 5
        data["stage"] = 3
        print(f"   Stage 3: value = {data['value']}")
        emitter.emit("complete", data)
    
    def on_complete(data):
        print(f"   ✅ Pipeline complete: {data}")
    
    emitter.on("stage1", stage1)
    emitter.on("stage2", stage2)
    emitter.on("stage3", stage3)
    emitter.on("complete", on_complete)
    
    # Start pipeline
    emitter.emit("stage1", pipeline_data)


def main():
    parser = argparse.ArgumentParser(description="Event system demo")
    parser.add_argument("--demo", "-d", choices=["basic", "pipeline", "all"], default="all")
    args = parser.parse_args()
    
    print("📡 Event System Demo\n")
    
    if args.demo in ["basic", "all"]:
        demo_basic()
        print()
    
    if args.demo in ["pipeline", "all"]:
        demo_pipeline()
    
    print("\n💡 Tips:")
    print("   - Use events for loose coupling between components")
    print("   - Consider pub/sub patterns for distributed systems")
    print("   - Add error handling and retry logic for production")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
