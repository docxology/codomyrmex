from typing import Optional
from pathlib import Path
import json
import subprocess
import sys
from ..utils import get_logger

logger = get_logger(__name__)

def handle_code_analysis(path: str, output_dir: Optional[str]) -> bool:
    """Handle code analysis command."""
    try:
        from codomyrmex.static_analysis import analyze_project

        result = analyze_project(path)
        print(f"Code quality analysis for: {path}")
        print(f"Quality Score: {result.get('score', 'N/A')}/10")

        if output_dir:
            output_file = Path(output_dir) / "analysis_report.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Report saved to: {output_file}")

        return True

    except ImportError:
        logger.warning("Static analysis module not available")
        print("❌ Static analysis module not available")
        return False
    except (ValueError, TypeError, AttributeError, RuntimeError, OSError, FileNotFoundError) as e:
        logger.error(f"Error analyzing code: {e}", exc_info=True)
        print(f"❌ Error analyzing code: {str(e)}")
        return False


def handle_git_analysis(repo_path: str) -> bool:
    """Handle git repository analysis command."""
    try:
        from codomyrmex.data_visualization.git_visualizer import visualize_git_repository

        result = visualize_git_repository(repo_path, output_dir="./git_analysis")

        if result:
            print("✅ Git analysis complete. Check ./git_analysis/ for results.")
            return True
        else:
            print("❌ Git analysis failed")
            return False

    except ImportError:
        logger.warning("Git operations or data visualization modules not available")
        print("❌ Git operations or data visualization modules not available")
        return False
    except Exception as e:
        logger.error(f"Error analyzing git repository: {e}", exc_info=True)
        print(f"❌ Error analyzing git repository: {str(e)}")
        return False


def handle_module_test(module_name: str) -> bool:
    """Handle module testing command."""
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                f"src/codomyrmex/{module_name}/tests/",
                "-v",
            ],
            capture_output=True,
            text=True,
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        logger.error(f"Error testing module: {e}", exc_info=True)
        print(f"❌ Error testing module: {str(e)}")
        return False
