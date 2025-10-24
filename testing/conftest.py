"""Shared pytest fixtures and configuration for Codomyrmex testing."""

import pytest
import sys
import os
from pathlib import Path

# Add the src directory to Python path for imports
project_root = Path(__file__).parent.parent
code_path = project_root / "src"
if str(code_path) not in sys.path:
    sys.path.insert(0, str(code_path))
# Also add the package root (src/codomyrmex) so tests that import modules
# using the package-local names (e.g. `ai_code_editing`) will resolve.
package_root = code_path / "codomyrmex"
if str(package_root) not in sys.path:
    sys.path.insert(0, str(package_root))

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")

@pytest.fixture
def project_root():
    """Fixture providing the project root path."""
    return project_root

@pytest.fixture
def code_dir():
    """Fixture providing the code directory path."""
    return code_path

@pytest.fixture
def temp_env_file(tmp_path):
    """Fixture providing a temporary .env file path."""
    return tmp_path / ".env"

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Auto-use fixture to set up test environment."""
    # Ensure we're in test mode
    os.environ.setdefault("CODOMYRMEX_TEST_MODE", "true")
    yield
    # Cleanup after test
    if "CODOMYRMEX_TEST_MODE" in os.environ:
        del os.environ["CODOMYRMEX_TEST_MODE"]

