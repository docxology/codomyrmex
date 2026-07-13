"""Shared pytest fixtures and configuration for Codomyrmex testing."""

import contextlib
import functools
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

# Hypothesis seeds NumPy's RNG when available; on some Python/NumPy combos that
# import chain fails (e.g. ImportError: cannot import name randbits). Property
# tests here do not require NumPy-backed entropy. Force on (not setdefault) so
# a shell value cannot disable it; codomyrmex/conftest.py also sets this in
# pytest_configure.
os.environ["HYPOTHESIS_NO_NPY"] = "1"

# Collection can instantiate clients in marker expressions before function
# fixtures exist. Give every pytest worker a process-local persistence root,
# then narrow it to ``tmp_path`` inside the autouse fixture below.
_PROCESS_TEST_STATE_HANDLE = tempfile.TemporaryDirectory(
    prefix=f"codomyrmex-pytest-{os.getpid()}-"
)
_PROCESS_TEST_STATE = Path(_PROCESS_TEST_STATE_HANDLE.name)
os.environ["CODOMYRMEX_TRUST_LEDGER_PATH"] = str(
    _PROCESS_TEST_STATE / "trust-ledger.json"
)
os.environ["CODOMYRMEX_HERMES_SESSION_DB"] = str(
    _PROCESS_TEST_STATE / "hermes-sessions.db"
)


def _patch_hypothesis_is_local_module_file() -> None:
    """Third-party lazy loaders may set ``__file__`` to a non-str sentinel; Hypothesis 6.151+ then crashes in ``is_local_module_file``."""
    try:
        import hypothesis.internal.conjecture.providers as _prov
        from hypothesis.internal import constants_ast as _hca
    except ImportError:
        return
    cached = _hca.is_local_module_file
    _orig = getattr(cached, "__wrapped__", None)
    if _orig is None:
        return

    def _safe(path: str) -> bool:
        if not isinstance(path, str):
            return False
        return _orig(path)

    _wrapped = functools.lru_cache(4096)(_safe)
    _hca.is_local_module_file = _wrapped
    _prov.is_local_module_file = _wrapped


_patch_hypothesis_is_local_module_file()

import subprocess

import pytest

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

with contextlib.suppress(ImportError):
    from codomyrmex.logging_monitoring import get_logger, setup_logging


def pytest_configure(config):
    """Register custom pytest markers."""
    os.environ["HYPOTHESIS_NO_NPY"] = "1"
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "bench: Opt-in benchmark and timing tests")
    config.addinivalue_line("markers", "benchmark: Opt-in pytest-benchmark tests")
    config.addinivalue_line("markers", "performance: Performance test suite")


_TESTS_ROOT = Path(__file__).parent.resolve()


def _is_performance_test_path(path: Path) -> bool:
    """Return whether *path* belongs to the opt-in performance suite."""
    try:
        relative = path.resolve().relative_to(_TESTS_ROOT)
    except ValueError:
        return False
    return bool(relative.parts) and relative.parts[0] == "performance"


def pytest_itemcollected(item: pytest.Item) -> None:
    """Apply all benchmark aliases before pytest evaluates ``-m`` filters."""
    if _is_performance_test_path(Path(str(item.path))):
        item.add_marker(pytest.mark.bench)
        item.add_marker(pytest.mark.benchmark)
        item.add_marker(pytest.mark.performance)


@pytest.fixture
def project_root():
    """Fixture providing the project root path."""
    return Path(__file__).parent.parent


@pytest.fixture
def code_dir():
    """Fixture providing the code directory path."""
    return Path(__file__).parent.parent / "src"


@pytest.fixture
def temp_env_file(tmp_path):
    """Fixture providing a temporary .env file path."""
    return tmp_path / ".env"


@pytest.fixture
def sample_markdown_file(tmp_path):
    """Fixture providing a sample markdown file."""
    md_file = tmp_path / "sample.md"
    md_file.write_text(
        "# Sample Document\n\nThis is sample markdown content.", encoding="utf-8"
    )
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
def setup_test_environment(request: pytest.FixtureRequest):
    """Set up an isolated environment, including per-test trust persistence."""
    os.environ["HYPOTHESIS_NO_NPY"] = "1"
    # Ensure we're in test mode
    original_test_mode = os.environ.get("CODOMYRMEX_TEST_MODE")
    os.environ.setdefault("CODOMYRMEX_TEST_MODE", "true")

    # Prevent Git from opening an editor or terminal prompt during tests
    # This prevents VS Code or Vim auto-popping up if a command requires a message check
    original_git_editor = os.environ.get("GIT_EDITOR")
    original_git_prompt = os.environ.get("GIT_TERMINAL_PROMPT")
    original_trust_ledger = os.environ.get("CODOMYRMEX_TRUST_LEDGER_PATH")
    original_hermes_db = os.environ.get("CODOMYRMEX_HERMES_SESSION_DB")
    os.environ["GIT_EDITOR"] = "true"
    os.environ["GIT_TERMINAL_PROMPT"] = "0"
    test_token = hashlib.sha256(request.node.nodeid.encode()).hexdigest()[:16]
    test_state = _PROCESS_TEST_STATE / test_token
    trust_ledger = test_state / "codomyrmex-trust-ledger.json"
    hermes_db = test_state / "codomyrmex-hermes-sessions.db"
    os.environ["CODOMYRMEX_TRUST_LEDGER_PATH"] = str(trust_ledger)
    os.environ["CODOMYRMEX_HERMES_SESSION_DB"] = str(hermes_db)

    # Most trust tests import the module during collection, before fixtures
    # run. Redirect that already-created (but lazily unloaded) singleton too.
    trust_module = sys.modules.get("codomyrmex.agents.pai.trust_gateway")
    if trust_module is not None:
        registry = getattr(trust_module, "_registry", None)
        if registry is not None:
            registry.configure_ledger_path(trust_ledger, load_existing=False)

    client_factory_module = sys.modules.get(
        "codomyrmex.agents.hermes.mcp_tools_pkg._client"
    )
    if client_factory_module is not None:
        client_factory_module._factory_override = None

    yield

    # Cleanup after test
    if original_test_mode is not None:
        os.environ["CODOMYRMEX_TEST_MODE"] = original_test_mode
    else:
        os.environ.pop("CODOMYRMEX_TEST_MODE", None)

    if original_git_editor is not None:
        os.environ["GIT_EDITOR"] = original_git_editor
    elif "GIT_EDITOR" in os.environ:
        del os.environ["GIT_EDITOR"]

    if original_git_prompt is not None:
        os.environ["GIT_TERMINAL_PROMPT"] = original_git_prompt
    elif "GIT_TERMINAL_PROMPT" in os.environ:
        del os.environ["GIT_TERMINAL_PROMPT"]

    if original_trust_ledger is not None:
        os.environ["CODOMYRMEX_TRUST_LEDGER_PATH"] = original_trust_ledger
    else:
        os.environ.pop("CODOMYRMEX_TRUST_LEDGER_PATH", None)

    if original_hermes_db is not None:
        os.environ["CODOMYRMEX_HERMES_SESSION_DB"] = original_hermes_db
    else:
        os.environ.pop("CODOMYRMEX_HERMES_SESSION_DB", None)

    client_factory_module = sys.modules.get(
        "codomyrmex.agents.hermes.mcp_tools_pkg._client"
    )
    if client_factory_module is not None:
        client_factory_module._factory_override = None


# ===== REAL DATA FIXTURES =====
# These fixtures provide real implementations instead of mocks


@pytest.fixture
def real_logger_fixture(tmp_path):
    """Create a real logger instance with actual file output."""
    if get_logger is None or setup_logging is None:
        pytest.skip("logging_monitoring module not available")

    # set up real logging configuration
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
import pytest


def test_main():
    pytest.skip("placeholder — add real tests here")
""")

    (project_dir / "README.md").write_text(
        "# Test Project\n\nA test project for Codomyrmex testing."
    )
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
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True
    )

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
    """Check actual Docker daemon availability (not mocked)."""
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "{{json .ServerVersion}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (
        subprocess.SubprocessError,
        FileNotFoundError,
        OSError,
        subprocess.TimeoutExpired,
    ):
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
