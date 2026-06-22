"""Terminal-local discovery view for the interactive shell.

This module intentionally avoids importing ``codomyrmex.system_discovery``.
The terminal interface sits in the foundation layer, so it keeps a small local
view that supports shell exploration without depending upward on application
services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class TerminalModuleInfo:
    """Minimal module metadata needed by the shell mixins."""

    name: str
    path: str
    description: str
    version: str = "unknown"
    last_modified: str = "unknown"
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[object] = field(default_factory=list)
    is_importable: bool = True
    has_tests: bool = False
    has_docs: bool = False


class TerminalDiscoveryView:
    """Small discovery adapter used by ``InteractiveShell``."""

    def __init__(self, module_name_loader: Callable[[], list[str]]) -> None:
        self._module_name_loader = module_name_loader
        self.modules: dict[str, TerminalModuleInfo] = {}

    def _discover_modules(self) -> None:
        """Populate module names without importing higher-layer services."""
        if self.modules:
            return
        for name in self._module_name_loader():
            self.modules[name] = TerminalModuleInfo(
                name=name,
                path=f"codomyrmex.{name}",
                description=f"Codomyrmex {name.replace('_', ' ')} module",
            )

    def discover_modules(self) -> list[dict[str, str]]:
        """Return tab-completion friendly module dictionaries."""
        self._discover_modules()
        return [{"name": name} for name in self.modules]

    def run_demo_workflows(self) -> None:
        """Report that demos must be routed through an injected runner."""
        print("🤷 No terminal demo runner selected for all-module demos.")

    def show_status_dashboard(self) -> None:
        """Print a compact terminal-local status summary."""
        self._discover_modules()
        print(f"   Modules visible to shell: {len(self.modules)}")

    def export_full_inventory(self) -> None:
        """Print a compact export hint instead of writing generated files."""
        self._discover_modules()
        print(f"   Inventory ready for {len(self.modules)} shell-visible modules.")


__all__ = ["TerminalDiscoveryView", "TerminalModuleInfo"]
