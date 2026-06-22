"""Shell Demo Mixin for InteractiveShell."""

import random
from collections.abc import Callable
from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from typing import Any

logger = get_logger(__name__)


class ShellDemoMixin:
    """Provides the demo functionality for InteractiveShell."""

    session_data: "dict[str, Any]"
    discovery: "Any"
    demo_runner: Callable[[str], bool] | None

    def do_demo(self, arg: str):
        """
        Run demonstration workflows.

        Usage: demo [module_name]

        Without arguments, runs demos for all working modules.
        With module name, runs demo for specific module if available.
        """
        print("🚀 " + "=" * 60)
        print("   DEMONSTRATION MODE")
        print("=" * 60)

        print(
            random.choice(
                [
                    "🎭 Setting up the stage for our performance...",
                    "🎪 Ladies and gentlemen, the show is about to begin!",
                    "🧪 Preparing laboratory demonstrations...",
                    "🎬 Lights, camera, action!",
                ]
            )
        )
        print()

        self.session_data["commands_run"] += 1

        if not self.discovery and not self.demo_runner:
            print("❌ Discovery system not available")
            return

        try:
            if arg:
                self._demo_specific_module(arg.strip())
            else:
                self._demo_all_modules()
        except Exception as e:
            print(f"❌ Demo failed: {e}")

        self.session_data["demos_run"] += 1

    def _demo_specific_module(self, module_name: str):
        """Run demo for a specific module."""
        if (
            self.discovery
            and getattr(self.discovery, "modules", None)
            and module_name not in self.discovery.modules
        ):
            print(f"🔍 Module '{module_name}' not found.")
            return

        if self.discovery and getattr(self.discovery, "modules", None):
            info = self.discovery.modules[module_name]
            if not info.is_importable:
                print(f"❌ Module '{module_name}' has import issues - cannot demo")
                return

        if self.demo_runner and self.demo_runner(module_name):
            return

        if not self.discovery and not self.demo_runner:
            print("❌ Discovery system not available")
            return

        if self.discovery and not getattr(self.discovery, "modules", None):
            print(f"🔍 Module '{module_name}' not found.")
            return

        if not self.demo_runner and module_name != "logging_monitoring":
            print(f"🤷 No specific demo available for {module_name}")
            print("💡 Try the general demo instead: 'demo'")
            return

        if module_name == "logging_monitoring":
            self._demo_logging()
            return

        print(f"🤷 No specific demo available for {module_name}")
        print("💡 Try the general demo instead: 'demo'")

    def _demo_all_modules(self):
        """Run demos for all working modules."""
        if not self.discovery:
            return
        self.discovery.run_demo_workflows()

    def _demo_logging(self):
        """Demo the logging system."""
        try:
            demo_logger = get_logger("interactive_demo")

            demo_logger.info("Starting interactive logging demo...")
            demo_logger.debug("This is a debug message")
            demo_logger.warning("This is a warning message")
            demo_logger.error("This is an error message (demo only)")
            demo_logger.info("Interactive logging demo completed successfully")

        except Exception as e:
            print(f"   ❌ Logging demo failed: {e}")

    def _demo_data_visualization(self, arg: str = ""):
        """Deprecated compatibility shim for external callers."""
        if self.demo_runner and self.demo_runner("data_visualization"):
            return
        print("🤷 No data_visualization demo runner configured")

    def _demo_code_execution(self, arg: str = ""):
        """Deprecated compatibility shim for external callers."""
        if self.demo_runner and self.demo_runner("coding"):
            return
        print("🤷 No coding demo runner configured")
