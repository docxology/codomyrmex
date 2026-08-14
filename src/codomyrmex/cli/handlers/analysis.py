import json
import os
import re
import subprocess
import sys
from pathlib import Path

from codomyrmex.cli.utils import print_error, print_success
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

_MODULE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
_DEFAULT_MODULE_TEST_TIMEOUT = 120.0


def _module_test_timeout() -> float:
    """Return a bounded module-test timeout from the environment."""
    raw_timeout = os.environ.get("CODOMYRMEX_MODULE_TEST_TIMEOUT", "120")
    try:
        timeout = float(raw_timeout)
    except ValueError:
        logger.warning(
            "Invalid CODOMYRMEX_MODULE_TEST_TIMEOUT=%r; using %.1fs",
            raw_timeout,
            _DEFAULT_MODULE_TEST_TIMEOUT,
        )
        return _DEFAULT_MODULE_TEST_TIMEOUT
    if timeout <= 0:
        logger.warning(
            "CODOMYRMEX_MODULE_TEST_TIMEOUT must be positive; using %.1fs",
            _DEFAULT_MODULE_TEST_TIMEOUT,
        )
        return _DEFAULT_MODULE_TEST_TIMEOUT
    return min(timeout, 900.0)


def handle_code_analysis(path: str, output_dir: str | None) -> bool:
    """Handle code analysis command."""
    try:
        from codomyrmex.coding.static_analysis import analyze_project

        print(f"Analyzing project at: {path}...")
        result = analyze_project(path)

        print_success(f"Code quality analysis for: {path}")
        print(f"Quality Score: {result.get('score', 'N/A')}/10")

        if output_dir:
            output_file = Path(output_dir) / "analysis_report.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print_success(f"Report saved to: {output_file}")

        return True

    except ImportError:
        logger.warning("Static analysis module not available")
        print_error("Static analysis module not available")
        return False
    except (
        ValueError,
        TypeError,
        AttributeError,
        RuntimeError,
        OSError,
        FileNotFoundError,
    ) as e:
        logger.error("Error analyzing code: %s", e, exc_info=True)
        print_error(f"Error analyzing code: {e!s}")
        return False


def handle_git_analysis(repo_path: str) -> bool:
    """Handle git repository analysis command."""
    try:
        from codomyrmex.data_visualization.git.git_visualizer import (
            visualize_git_repository,
        )

        print(f"Analyzing git repository at: {repo_path}...")
        result = visualize_git_repository(repo_path, output_dir="./git_analysis")

        if result:
            print_success("Git analysis complete. Check ./git_analysis/ for results.")
            return True
        print_error("Git analysis failed")
        return False

    except ImportError:
        logger.warning("Git operations or data visualization modules not available")
        print_error("Git operations or data visualization modules not available")
        return False
    except Exception as e:
        logger.error("Error analyzing git repository: %s", e, exc_info=True)
        print_error(f"Error analyzing git repository: {e!s}")
        return False


def handle_module_test(module_name: str) -> bool:
    """Handle module testing command."""
    try:
        if not isinstance(module_name, str) or not _MODULE_NAME_RE.fullmatch(
            module_name
        ):
            print_error(f"Invalid module name: {module_name!r}")
            return False

        # Try a few common test locations
        test_locations = [
            Path("src/codomyrmex") / module_name / "tests",
            Path("tests/unit") / module_name,
        ]

        test_path = None
        for loc in test_locations:
            if loc.exists():
                test_path = loc
                break

        if not test_path:
            print_error(
                f"Tests not found for module '{module_name}'. Checked: {', '.join(str(loc) for loc in test_locations)}"
            )
            return False

        print(f"Running tests for module: {module_name} (at {test_path})...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_path),
                "-q",
                "--no-cov",  # Disable coverage for quick runs
            ],
            capture_output=True,
            text=True,
            timeout=_module_test_timeout(),
        )

        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        if result.returncode == 0:
            print_success(f"Tests passed for module: {module_name}")
        else:
            print_error(
                f"Tests failed for module: {module_name} (exit code: {result.returncode})"
            )

        return result.returncode == 0

    except subprocess.TimeoutExpired as e:
        logger.warning(
            "Module tests timed out after %.1fs: %s",
            _module_test_timeout(),
            module_name,
        )
        print_error(
            f"Tests timed out for module '{module_name}' "
            f"after {_module_test_timeout():.1f}s"
        )
        return False
    except Exception as e:
        logger.error("Error testing module: %s", e, exc_info=True)
        print_error(f"Error testing module: {e!s}")
        return False
