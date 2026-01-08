from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

from src.main import main
import nonexistent_module
import pytest
import yaml

from codomyrmex.logging_monitoring import get_logger, setup_logging




























"""Shared pytest fixtures and configuration for Codomyrmex testing."""


try:
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Add the src directory to Python path for imports
# From src/codomyrmex/tests/conftest.py, go up 4 levels to reach project root
project_root = Path(__file__).parent.parent.parent.parent
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

@pytest.fixture
def sample_markdown_file(tmp_path):
    """Fixture providing a sample markdown file."""
    md_file = tmp_path / "sample.md"
    md_file.write_text("# Sample Document\n\nThis is sample markdown content.", encoding="utf-8")
    return md_file


@pytest.fixture
def sample_json_file(tmp_path):
    """Fixture providing a sample JSON file."""
    json_file = tmp_path / "sample.json"
    data = {"name": "Test", "value": 42, "items": ["a", "b", "c"]}
    json_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return json_file


@pytest.fixture
def sample_yaml_file(tmp_path):
    """Fixture providing a sample YAML file."""
    yaml_file = tmp_path / "sample.yaml"
    yaml_content = """name: Test
value: 42
items:
  - a
  - b
  - c
"""
    yaml_file.write_text(yaml_content, encoding="utf-8")
    return yaml_file


@pytest.fixture
def sample_yaml_file_with_yaml(tmp_path):
    """Fixture providing a sample YAML file (requires yaml library)."""
    if not YAML_AVAILABLE:
        pytest.skip("YAML not available")
    return sample_yaml_file(tmp_path)


@pytest.fixture
def sample_text_file(tmp_path):
    """Fixture providing a sample text file."""
    text_file = tmp_path / "sample.txt"
    text_file.write_text("This is plain text content.", encoding="utf-8")
    return text_file


@pytest.fixture
def sample_code_with_vulnerability(tmp_path):
    """Fixture providing sample code with potential security issues."""
    code_file = tmp_path / "vulnerable.py"
    code_content = """import os
password = "secret123"
def login(username, pwd):
    if pwd == password:
        return True
    return False
"""
    code_file.write_text(code_content, encoding="utf-8")
    return code_file


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Auto-use fixture to set up test environment."""
    # Ensure we're in test mode
    os.environ.setdefault("CODOMYRMEX_TEST_MODE", "true")
    yield
    # Cleanup after test
    if "CODOMYRMEX_TEST_MODE" in os.environ:
        del os.environ["CODOMYRMEX_TEST_MODE"]


# ===== REAL DATA FIXTURES =====
# These fixtures provide real implementations instead of mocks

@pytest.fixture
def real_logger_fixture(tmp_path):
    """Create a real logger instance with actual file output."""
    try:
    except ImportError:
        pytest.skip("logging_monitoring module not available")

    # Set up real logging configuration
    log_file = tmp_path / "test.log"
    os.environ["CODOMYRMEX_LOG_FILE"] = str(log_file)
    os.environ["CODOMYRMEX_LOG_LEVEL"] = "DEBUG"

    setup_logging()
    logger = get_logger("test_logger")

    return {"logger": logger, "log_file": log_file}


@pytest.fixture
def real_temp_project(tmp_path):
    """Create a temporary project directory with real files."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create basic project structure
    (project_dir / "src").mkdir()
    (project_dir / "tests").mkdir()
    (project_dir / "docs").mkdir()

    # Create real Python files
    (project_dir / "src" / "__init__.py").write_text("")
    (project_dir / "src" / "main.py").write_text("""
def main():
    print("Hello from test project")

if __name__ == "__main__":
    main()
""")

    (project_dir / "tests" / "__init__.py").write_text("")
    (project_dir / "tests" / "test_main.py").write_text("""
def test_main():
    # Test would go here
    assert True
""")

    (project_dir / "README.md").write_text("# Test Project\n\nA test project for Codomyrmex testing.")
    (project_dir / "requirements.txt").write_text("pytest>=7.0.0\n")

    return project_dir


@pytest.fixture
def real_code_samples(tmp_path):
    """Provide actual Python code samples for testing."""
    samples = {}

    # Valid Python code
    valid_code = tmp_path / "valid_code.py"
    valid_code.write_text("""
def calculate_sum(a, b):
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b

class Calculator:
    \"\"\"A simple calculator class.\"\"\"
    def add(self, x, y):
        return x + y

    def multiply(self, x, y):
        return x * y
""")
    samples["valid"] = valid_code

    # Code with syntax errors
    syntax_error_code = tmp_path / "syntax_error.py"
    syntax_error_code.write_text("""
def broken_function(
    print("Missing closing parenthesis"
""")
    samples["syntax_error"] = syntax_error_code

    # Code with undefined variables
    undefined_var_code = tmp_path / "undefined_var.py"
    undefined_var_code.write_text("""
def problematic_function():
    result = undefined_variable + 1
    return result
""")
    samples["undefined_var"] = undefined_var_code

    # Code with import issues
    import_error_code = tmp_path / "import_error.py"
    import_error_code.write_text("""
print("This should not execute")
""")
    samples["import_error"] = import_error_code

    return samples


@pytest.fixture
def real_git_repo(tmp_path):
    """Create a real git repository with actual commits."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Initialize git repository
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)

    # Configure git
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)

    # Create initial file and commit
    readme = repo_dir / "README.md"
    readme.write_text("# Test Repository\n\nThis is a test git repository.")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

    # Create a feature branch
    subprocess.run(["git", "checkout", "-b", "feature/test"], cwd=repo_dir, check=True)

    # Add another file
    main_py = repo_dir / "main.py"
    main_py.write_text("""
def main():
    print("Hello from test repo")

if __name__ == "__main__":
    main()
""")
    subprocess.run(["git", "add", "main.py"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "Add main.py"], cwd=repo_dir, check=True)

    return repo_dir


@pytest.fixture
def real_env_file(tmp_path):
    """Create a temporary .env file with real configuration."""
    env_file = tmp_path / ".env"

    env_content = """# Test environment configuration
CODOMYRMEX_LOG_LEVEL=INFO
CODOMYRMEX_LOG_FILE=/tmp/test.log
CODOMYRMEX_LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
CODOMYRMEX_API_KEY=test_api_key_12345
OPENAI_API_KEY=test_openai_key
ANTHROPIC_API_KEY=test_anthropic_key
"""

    env_file.write_text(env_content)
    return env_file


@pytest.fixture
def real_docker_available():
    """Check actual Docker availability (not mocked)."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


@pytest.fixture
def real_subprocess_result():
    """Execute real subprocess commands in test environment."""
    def run_command(cmd, **kwargs):
        """Run a real subprocess command."""
        try:
            return subprocess.run(cmd, capture_output=True, text=True, **kwargs)
        except subprocess.SubprocessError as e:
            # Return a result-like object with error info
            class SubprocessError:
                def __init__(self, error):
                    self.returncode = 1
                    self.stdout = ""
                    self.stderr = str(error)
                    self.exception = error
            return SubprocessError(e)

    return run_command

