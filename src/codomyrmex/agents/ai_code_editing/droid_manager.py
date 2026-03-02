"""Enhanced Droid Manager for Codomyrmex TODO System.

This module provides comprehensive management capabilities for the Codomyrmex droid system,
including TODO list management, task execution, statistics tracking, and system monitoring.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


# Import core droid components
try:
    # Try relative imports first (when used as module)
    from codomyrmex.agents.droid.controller import (
        DroidController,
    )
    from codomyrmex.agents.droid.todo import TodoManager
except ImportError:
    try:
        # Try absolute imports (when run directly)
        from codomyrmex.agents.droid.controller import (
            DroidController,
        )
        from codomyrmex.agents.droid.todo import TodoManager
    except ImportError as e:
        print(f"❌ Failed to import droid components: {e}")
        print("💡 Make sure you're running from the correct directory")
        sys.exit(1)


class DroidSystemManager:
    """Enhanced manager for the Codomyrmex droid system."""

    def __init__(self, droid_dir: str | Path | None = None):
        """Initialize the droid system manager."""
        if droid_dir is None:
            current_file = Path(__file__)
            droid_dir = current_file.parent / "droid"
        else:
            droid_dir = Path(droid_dir)

        self.droid_dir = droid_dir
        self.todo_file = droid_dir / "todo_list.txt"
        self.config_file = droid_dir / "droid_config.json"

        # Initialize components
        self.controller: DroidController | None = None
        self.todo_manager = TodoManager(self.todo_file)

        # System state
        self.start_time = time.time()
        self.session_stats = {
            "total_sessions": 0,
            "total_tasks_executed": 0,
            "total_tasks_failed": 0,
            "last_execution_time": None,
            "uptime_seconds": 0,
        }

        print("🤖 Codomyrmex Droid System Manager initialized")
        print(f"📁 Droid directory: {self.droid_dir}")

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        todo_items, completed_items = self.todo_manager.load()

        status = {
            "system": {
                "uptime_seconds": time.time() - self.start_time,
                "droid_dir": str(self.droid_dir),
                "controller_active": self.controller is not None,
                "config_loaded": self.config_file.exists(),
            },
            "todo_stats": {
                "total_todos": len(todo_items),
                "completed_todos": len(completed_items),
                "completion_rate": len(completed_items)
                / max(len(todo_items) + len(completed_items), 1)
                * 100,
            },
            "session_stats": self.session_stats.copy(),
            "controller_metrics": self.controller.metrics if self.controller else {},
        }

        return status

    def display_system_status(self) -> None:
        """Display comprehensive system status in terminal."""
        status = self.get_system_status()

        print("\n🤖 Codomyrmex Droid System Status")
        print("=" * 50)

        # System info
        system = status["system"]
        print("📊 System Information:")
        print(f"   Uptime: {system['uptime_seconds']:.1f} seconds")
        print(f"   Droid Directory: {system['droid_dir']}")
        print(f"   Controller Active: {'✅' if system['controller_active'] else '❌'}")
        print(f"   Configuration Loaded: {'✅' if system['config_loaded'] else '❌'}")

        # Stats Display
        todo_stats = status["todo_stats"]
        print("\n📋 TODO Statistics:")
        print(f"   Total TODOs: {todo_stats['total_todos']}")
        print(f"   Completed TODOs: {todo_stats['completed_todos']}")
        print(f"   Completion Rate: {todo_stats['completion_rate']:.1f}%")

        # Session stats
        session = status["session_stats"]
        print("\n📈 Session Statistics:")
        print(f"   Total Sessions: {session['total_sessions']}")
        print(f"   Tasks Executed: {session['total_tasks_executed']}")
        print(f"   Tasks Failed: {session['total_tasks_failed']}")


# Convenience functions
def get_droid_manager(droid_dir: str | Path | None = None) -> DroidSystemManager:
    """Get a droid system manager instance."""
    return DroidSystemManager(droid_dir)


def show_droid_status(droid_dir: str | Path | None = None) -> None:
    """Show droid system status."""
    manager = DroidSystemManager(droid_dir)
    manager.display_system_status()


__all__ = [
    "DroidSystemManager",
    "get_droid_manager",
    "show_droid_status",
]
