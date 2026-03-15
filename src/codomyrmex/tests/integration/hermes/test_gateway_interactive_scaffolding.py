import subprocess
from pathlib import Path

import pytest

from codomyrmex.agents.core import AgentResponse
from codomyrmex.agents.hermes.hermes_client import HermesClient


@pytest.fixture
def temp_workspace(tmp_path: Path):
    """Provide a temporary workspace resembling a typical module."""
    src_dir = tmp_path / "src" / "codomyrmex" / "dummy_module"
    src_dir.mkdir(parents=True)
    (tmp_path / "src" / "codomyrmex" / "__init__.py").touch()
    (src_dir / "__init__.py").touch()

    # Create the source file with a deliberate "bug"
    src_file = src_dir / "calculator.py"
    src_file.write_text(
        """def add(a: int, b: int) -> int:
    return a - b  # Deliberate bug

def multiply(a: int, b: int) -> int:
    return a * b
"""
    )

    # Create a test file that asserts correct arithmetic, so it will FAIL initially
    test_dir = (
        tmp_path / "src" / "codomyrmex" / "tests" / "integration" / "dummy_module"
    )
    test_dir.mkdir(parents=True)

    test_file = test_dir / "test_calculator.py"
    # Ensure it's in the python path accurately regardless of cwd
    src_base = str(tmp_path / "src")

    # Write a local pytest.ini to block inheritance of the root pyproject.toml 40% coverage rules
    ini_file = test_dir / "pytest.ini"
    ini_file.write_text("[pytest]\naddopts = -p no:cov\n")

    test_file.write_text(
        f"""import sys
sys.path.insert(0, r"{src_base}")

from codomyrmex.dummy_module.calculator import add, multiply

def test_add_correctly():
    assert add(5, 5) == 10

def test_multiply_correctly():
    assert multiply(3, 4) == 12
"""
    )

    db_path = tmp_path / "test_hermes_scaffold_sessions.db"
    return tmp_path, src_file, test_file, db_path


class MockCoverageRepairClient(HermesClient):
    """A client simulating an AI that reads a traceback and successfully patches the code immediately."""

    def __init__(self, src_file: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.call_count = 0
        self.src_file = src_file

    def chat_session(
        self,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> AgentResponse:
        self.call_count += 1
        # The agent receives a traceback about `test_add_correctly` failing because a - b is used
        # We simulate the agent repairing the file inline.

        current_code = self.src_file.read_text()
        fixed_code = current_code.replace(
            "return a - b  # Deliberate bug", "return a + b  # Fixed by agent"
        )
        self.src_file.write_text(fixed_code)

        return AgentResponse(
            content="I have identified the bug in `calculator.py` where `add` was subtracting. I have fixed it.",
            error=None,
            metadata={"exit_code": 0},
        )


def test_coverage_loop_repairs_failing_code(temp_workspace, monkeypatch):
    """Test the _run_coverage_loop successfully iteracts with pytest and an agent until green."""
    workspace_root, src_file, test_file, db_path = temp_workspace

    client = MockCoverageRepairClient(
        src_file=src_file,
        config={
            "hermes_backend": "ollama",
            "hermes_session_db": str(db_path),
        },
    )

    # We monkeypatch the subprocess.run inside `_run_coverage_loop` because running `uv run pytest`
    # on our dynamic temp_workspace could cause pathing/environmental issues depending on the global virtualenv.
    # Instead, we just run standard `pytest` over the local test_file directly for this loop logic test.

    original_run = subprocess.run

    def mock_subprocess_run(cmd, *args, **kwargs):
        if len(cmd) > 2 and cmd[2] == "pytest":
            import os
            import sys

            mapped_cmd = [
                sys.executable,
                "-m",
                "pytest",
                str(test_file),
                "-v",
                "--tb=short",
            ]
            kwargs["cwd"] = str(test_file.parent)

            # Inject PYTHONPATH so pytest can discover the dummy_module correctly natively
            env = kwargs.get("env", os.environ).copy()
            src_base = str(workspace_root / "src")
            env["PYTHONPATH"] = f"{src_base}:{env.get('PYTHONPATH', '')}"
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            kwargs["env"] = env

            result = original_run(mapped_cmd, *args, **kwargs)

            if result.returncode != 0:
                if (
                    " failed" not in result.stdout
                    and " error" not in result.stdout.lower()
                    and "FAIL Required test coverage" in result.stdout
                ):
                    result.returncode = 0
            return result
        return original_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)

    # Run the bounded coverage loop
    result = client._run_coverage_loop(str(test_file), max_turns=3)

    # 1. First iteration fails, triggering 1 agent response which patches the file.
    # 2. Second iteration passes (turns start at 0 and return code 0 returns early).
    assert client.call_count == 1
    assert result["status"] == "success"

    # Validate the file was actually patched on disk by the "agent"
    content = src_file.read_text()
    assert "return a + b" in content
    assert "return a - b" not in content
