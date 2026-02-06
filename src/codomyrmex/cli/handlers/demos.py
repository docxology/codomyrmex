
from ..utils import get_logger

# Lazy imports for demos to avoid hard dependencies
logger = get_logger(__name__)

def demo_data_visualization() -> bool:
    """Demo data visualization capabilities."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import os

        from codomyrmex.data_visualization import create_bar_chart, create_line_plot
        # Generate sample data
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        x = list(range(10))
        y = [i**2 for i in x]

        # Create visualizations
        create_line_plot(
            x, y, title="Demo: Quadratic Function", save_path="output/demo_line.png"
        )
        create_bar_chart(
            x, y, title="Demo: Bar Chart", save_path="output/demo_bar.png"
        )

        print("✅ Data visualization demo complete. Check output/ directory.")
        return True

    except ImportError:
        logger.warning("Data visualization module not available")
        print("❌ Data visualization module not available")
        return False
    except Exception as e:
        logger.error(f"Data visualization demo failed: {e}", exc_info=True)
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_ai_code_editing() -> bool:
    """Demo AI code editing capabilities."""
    try:
        from codomyrmex.agents.ai_code_editing import generate_code_snippet

        result = generate_code_snippet(
            prompt="Create a simple function to calculate factorial", language="python"
        )

        if result["status"] == "success":
            print("✅ AI Code Generation Demo:")
            print("Generated factorial function:")
            print("-" * 40)
            print(result["generated_code"])
            print("-" * 40)
            return True
        else:
            print(f"❌ Demo failed: {result['error_message']}")
            return False

    except ImportError:
        logger.warning("AI code editing module not available")
        print("❌ AI code editing module not available")
        return False
    except Exception as e:
        logger.error(f"AI code editing demo failed: {e}", exc_info=True)
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_code_execution() -> bool:
    """Demo code execution sandbox."""
    try:
        from codomyrmex.coding import execute_code

        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(8):
    print(f"fib({i}) = {fibonacci(i)}")
"""

        result = execute_code(language="python", code=code)

        if result.get("status") == "success":
            print("✅ Code Execution Demo:")
            print("Executed Fibonacci sequence:")
            print("-" * 40)
            print(result.get("stdout", "No output"))
            print("-" * 40)
            return True
        else:
            print(f"❌ Demo failed: {result.get('error_message', result.get('stderr', 'Unknown error'))}")
            return False

    except ImportError:
        logger.warning("Code execution sandbox module not available")
        print("❌ Code execution sandbox module not available")
        return False
    except Exception as e:
        logger.error(f"Code execution demo failed: {e}", exc_info=True)
        print(f"❌ Demo failed: {str(e)}")
        return False


def demo_git_operations() -> bool:
    """Demo git operations."""
    try:
        from codomyrmex.git_operations import get_current_branch, get_status

        status = get_status()
        branch = get_current_branch()

        print("✅ Git Operations Demo:")
        print(f"Current branch: {branch}")
        print(f"Repository status: {len(status.get('modified', []))} modified files")
        return True

    except ImportError:
        logger.warning("Git operations module not available")
        print("❌ Git operations module not available")
        return False
    except Exception as e:
        logger.error(f"Git operations demo failed: {e}", exc_info=True)
        print(f"❌ Demo failed: {str(e)}")
        return False


def handle_module_demo(module_name: str) -> bool:
    """Handle module demo command."""
    print(f"Running demo for module: {module_name}")

    demos = {
        "data_visualization": demo_data_visualization,
        "ai_code_editing": demo_ai_code_editing,
        "code": demo_code_execution,
        "git_operations": demo_git_operations,
    }

    if module_name in demos:
        return demos[module_name]()
    else:
        print(f"❌ No demo available for module: {module_name}")
        return False
