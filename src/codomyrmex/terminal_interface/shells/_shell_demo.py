"""Shell Demo Mixin for InteractiveShell."""

import random
from typing import TYPE_CHECKING

from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from typing import Any

logger = get_logger(__name__)


class ShellDemoMixin:
    """Provides the demo functionality for InteractiveShell."""

    session_data: "dict[str, Any]"
    discovery: "Any"

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

        if not self.discovery:
            print("❌ Discovery system not available")
            return

        if arg:
            self._demo_specific_module(arg.strip())
        else:
            self._demo_all_modules()

        self.session_data["demos_run"] += 1

    def _demo_specific_module(self, module_name: str):
        """Run demo for a specific module."""
        if module_name not in self.discovery.modules:
            print(f"🔍 Module '{module_name}' not found.")
            return

        info = self.discovery.modules[module_name]
        if not info.is_importable:
            print(f"❌ Module '{module_name}' has import issues - cannot demo")
            return

        print(f"🎯 Running demo for {module_name}...")

        try:
            if module_name == "data_visualization":
                self._demo_data_visualization()
            elif module_name == "logging_monitoring":
                self._demo_logging()
            elif module_name == "code":
                self._demo_code_execution()
            else:
                print(f"🤷 No specific demo available for {module_name}")
                print("💡 Try the general demo instead: 'demo'")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

    def _demo_all_modules(self):
        """Run demos for all working modules."""
        if not self.discovery:
            return
        self.discovery.run_demo_workflows()

    def _demo_data_visualization(self):
        """Demo the data visualization module."""
        try:
            import numpy as np

            from codomyrmex.data_visualization import create_bar_chart, create_line_plot

            print("   📊 Creating sample line plot...")
            x = np.linspace(0, 6.28, 100)
            y = np.sin(x) * np.exp(-x / 10)

            create_line_plot(
                x_data=x,
                y_data=y,
                title="Interactive Demo: Damped Sine Wave",
                x_label="Time",
                y_label="Amplitude",
                output_path="interactive_demo_line.png",
                show_plot=False,
            )

            print("   📊 Creating sample bar chart...")
            categories = ["Foraging", "Building", "Exploring", "Coding", "Testing"]
            values = np.random.randint(10, 100, size=len(categories))

            create_bar_chart(
                categories=categories,
                values=values,
                title="Interactive Demo: Ant Activity Levels",
                x_label="Activity",
                y_label="Level",
                output_path="interactive_demo_bar.png",
                show_plot=False,
            )

            print(
                "   ✅ Plots saved: interactive_demo_line.png, interactive_demo_bar.png"
            )

        except Exception as e:
            print(f"   ❌ Data visualization demo failed: {e}")

    def _demo_logging(self):
        """Demo the logging system."""
        try:
            demo_logger = get_logger("interactive_demo")

            demo_logger.info("🐜 Starting interactive logging demo...")
            demo_logger.debug("🔍 This is a debug message")
            demo_logger.warning("⚠️  This is a warning message")
            demo_logger.error(
                "❌ This is an error message (don't worry, it's just a demo!)"
            )
            demo_logger.info("✅ Interactive logging demo completed successfully!")

        except Exception as e:
            print(f"   ❌ Logging demo failed: {e}")

    def _demo_code_execution(self):
        """Demo the code execution sandbox."""
        try:
            from codomyrmex.coding import execute_code

            print("   🏃 Executing sample Python code in sandbox...")

            code = """
print("Hello from the Codomyrmex sandbox! 🐜")
print(f"The answer to everything: {6 * 7}")
print(f"Pi to 3 decimal places: {math.pi:.3f}")
for i in range(5):
    print(f"Foraging step {i+1}... 🔍")
print("Sandbox execution complete! ✅")
"""

            result = execute_code(language="python", code=code)

            if result.get("exit_code") == 0:
                print("   📤 Sandbox output:")
                for line in result.get("stdout", "").split("\n"):
                    if line.strip():
                        print(f"      {line}")
            else:
                print(
                    f"   ❌ Execution failed with exit code: {result.get('exit_code')}"
                )

        except Exception as e:
            print(f"   ❌ Code execution demo failed: {e}")
