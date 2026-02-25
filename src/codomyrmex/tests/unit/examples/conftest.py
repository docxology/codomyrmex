import shutil
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

# from conftest import FunctionName, ClassName
import pytest

"""Pytest configuration and fixtures for example testing.

Provides shared fixtures and configuration for testing Codomyrmex examples.
"""



@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    # From src/codomyrmex/tests/unit/examples/conftest.py, go up 6 levels to reach project root
    return Path(__file__).parent.parent.parent.parent.parent.parent


@pytest.fixture(scope="session")
def examples_dir(project_root: Path) -> Path:
    """Get the examples directory."""
    return project_root / "examples"


@pytest.fixture(scope="session")
def testing_dir(project_root: Path) -> Path:
    """Get the testing directory."""
    return project_root / "src" / "codomyrmex" / "tests"


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_config() -> dict[str, Any]:
    """Provide a mock configuration for testing."""
    return {
        "output": {
            "format": "json",
            "file": "output/test_results.json"
        },
        "logging": {
            "level": "INFO",
            "file": "logs/test.log"
        }
    }


@pytest.fixture(autouse=True)
def setup_test_environment(project_root: Path):
    """Setup test environment by adding project paths."""
    src_path = str(project_root / "src")
    examples_path = str(project_root / "examples")
    tests_path = str(project_root / "src" / "codomyrmex" / "tests")

    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    if examples_path not in sys.path:
        sys.path.insert(0, examples_path)
    if tests_path not in sys.path:
        sys.path.insert(0, tests_path)
