#!/usr/bin/env python3
"""Interactive Shell for Codomyrmex

Provides an engaging, interactive terminal interface for exploring the
Codomyrmex ecosystem - like being an epistemic forager in a vast,
structured nest.
"""

import cmd
import logging
from typing import TypedDict

from codomyrmex.logging_monitoring import get_logger

from ._shell_capabilities import ShellCapabilitiesMixin
from ._shell_demo import ShellDemoMixin
from ._shell_explore import ShellExploreMixin
from ._shell_forage import ShellForageMixin
from ._shell_session import ShellSessionMixin


class SessionData(TypedDict):
    commands_run: int
    modules_explored: set[str]
    discoveries_made: list[str]
    demos_run: int


# NOTE: Core-layer imports (coding, data_visualization) are loaded lazily
# inside the methods that need them to respect the Foundation → Core layer
# boundary.  Only Foundation-layer imports appear at the top level.
# system_discovery (Application layer) is NOT imported — _ensure_discovery()
# uses pkgutil instead.

try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class InteractiveShell(
    ShellExploreMixin,
    ShellCapabilitiesMixin,
    ShellDemoMixin,
    ShellForageMixin,
    ShellSessionMixin,
    cmd.Cmd,
):
    """
    Interactive shell for exploring the Codomyrmex ecosystem.

    This shell provides a fun, accessible way to discover modules,
    run demos, check status, and interact with the system like
    an epistemic forager exploring a vast nest.
    """

    intro = """
🐜 Welcome to the Codomyrmex Interactive Shell! 🐜

You are now an epistemic forager in the vast Codomyrmex nest.
Explore modules, discover capabilities, and forage for knowledge!

Type 'help' or '?' to list commands.
Type 'help <command>' for detailed information about a command.
Type 'explore' to begin your foraging adventure!
    """

    prompt = "🐜 codomyrmex> "

    def __init__(self):
        """Initialize the interactive shell."""
        super().__init__()

        # SystemDiscovery (Application layer) is NOT imported here — this module
        # is Foundation layer.  _ensure_discovery() uses pkgutil for module names.
        self.discovery = None
        self._module_names: list[str] = []

        # Track session data
        self.session_data: SessionData = {
            "commands_run": 0,
            "modules_explored": set(),
            "discoveries_made": [],
            "demos_run": 0,
        }

        # Fun foraging messages
        self.foraging_messages = [
            "🔍 Sniffing around for interesting modules...",
            "🐜 Following the scent trail of code...",
            "🍯 Found some sweet capabilities!",
            "🏃 Scurrying through the codebase...",
            "🌿 Exploring new territories in the nest...",
            "🔬 Examining specimens under the microscope...",
            "🎯 Zeroing in on valuable resources...",
            "🚀 Launching discovery expedition...",
        ]

        print(self.intro)

    def _ensure_discovery(self) -> None:
        """Build the module name list using pkgutil (Foundation-layer safe).

        Populates ``self._module_names`` without importing any Core/Application
        layer modules, preserving the Foundation → Core layer boundary.
        ``self.discovery`` remains ``None``; commands that need rich discovery
        data report limited-mode status as designed.
        """
        if not self._module_names:
            try:
                import pkgutil

                import codomyrmex

                self._module_names = [
                    name for _, name, _ in pkgutil.iter_modules(codomyrmex.__path__)
                ]
            except (ImportError, AttributeError, OSError) as exc:
                logger.warning("pkgutil module scan failed: %s", exc)
                self._module_names = []

    def precmd(self, line: str) -> str:
        """Ensure discovery engine is initialised before any command runs."""
        self._ensure_discovery()
        return line

    def emptyline(self):
        """Handle empty lines gracefully without repeating the last command."""
        return False

    def default(self, line):
        """Handle unknown commands with helpful suggestions."""
        print(f"🤔 Unknown command: '{line}'")
        print(
            "💡 Try 'help' to see available commands, or 'explore' to start foraging!"
        )

    def complete_explore(self, text, line, begidx, endidx):
        """Tab completion for explore command."""
        if not self.discovery:
            return []

        try:
            modules = self.discovery.discover_modules()
            module_names = [
                module.get("name", "") for module in modules if "name" in module
            ]
            if text:
                return [name for name in module_names if name.startswith(text)]
            return module_names
        except Exception as e:
            logger.error("Error in tab completion: %s", e)
            return []

    def run(self):
        """Run the interactive shell."""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print("\n\n🐜 Interrupted! Thanks for exploring the Codomyrmex nest!")
        except Exception as e:
            logger.error("Error in interactive shell: %s", e)
            print(f"\n❌ An error occurred: {e}")
            print("🐜 Thanks for exploring the Codomyrmex nest!")


if __name__ == "__main__":
    # Allow running this module directly for testing
    shell = InteractiveShell()
    shell.run()
