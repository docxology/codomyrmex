"""Terminal demo runner for module-specific interactive shell demos."""

from __future__ import annotations

from typing import Any


def run_terminal_demo(module_name: str) -> bool:
    """Run a known terminal demo and return whether it was handled."""
    if module_name == "data_visualization":
        _run_data_visualization_demo()
        return True
    if module_name in {"code", "coding"}:
        _run_code_execution_demo()
        return True
    return False


def _run_data_visualization_demo() -> None:
    import numpy as np

    from codomyrmex.data_visualization import create_bar_chart, create_line_plot

    print("   Creating sample line plot...")
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

    print("   Creating sample bar chart...")
    categories = ["Foraging", "Building", "Exploring", "Coding", "Testing"]
    values = np.random.randint(10, 100, size=len(categories))

    create_bar_chart(
        categories=categories,
        values=values,
        title="Interactive Demo: Activity Levels",
        x_label="Activity",
        y_label="Level",
        output_path="interactive_demo_bar.png",
        show_plot=False,
    )

    print("   Plots saved: interactive_demo_line.png, interactive_demo_bar.png")


def _run_code_execution_demo() -> None:
    from codomyrmex.coding import execute_code

    print("   Executing sample Python code in sandbox...")

    code = """
import math
print("Hello from the Codomyrmex sandbox")
print(f"The answer to everything: {6 * 7}")
print(f"Pi to 3 decimal places: {math.pi:.3f}")
for i in range(5):
    print(f"Foraging step {i + 1}...")
print("Sandbox execution complete")
"""

    result: dict[str, Any] = execute_code(language="python", code=code)

    if result.get("exit_code") == 0:
        print("   Sandbox output:")
        for line in str(result.get("stdout", "")).split("\n"):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   Execution failed with exit code: {result.get('exit_code')}")


__all__ = ["run_terminal_demo"]
