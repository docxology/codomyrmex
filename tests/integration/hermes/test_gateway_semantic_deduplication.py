"""Integration tests for Semantic Deduplication."""

import pytest

from codomyrmex.agents.hermes.mcp_tools import hermes_read_log_chunk
from codomyrmex.coding.execution.executor import (
    _compress_trace,
    _paginate_output,
    execute_code,
)


def test_semantic_deduplication_trace_compression():
    """Verify that _compress_trace removes tight repeating blocks of loops."""
    # Simulating a python error loops 10 times
    trace = "Traceback (most recent call last):\n"
    trace += '  File "main.py", line 4, in <module>\n'
    trace += '    raise ValueError("Ahhh!")\n'

    # 20 distinct repetitions of the block
    full_trace = trace + "\n".join(["ValueError: Ahhh!"] * 20)

    compressed = _compress_trace(full_trace)

    # It should shrink significantly
    assert len(compressed.splitlines()) < 10
    assert "... [Line repeated 19 more times] ..." in compressed


def test_semantic_deduplication_block_compression():
    """Verify _compress_trace spots identical repeating multi-line blocks."""
    lines = []
    for _ in range(10):
        lines.append("import sys")
        lines.append("sys.exit(1)")
        lines.append("ZeroDivisionError: division by zero")

    full_trace = "\n".join(lines)
    compressed = _compress_trace(full_trace)

    assert len(compressed.splitlines()) < 10
    # Block size is 3 lines
    assert "... [Above block of 3 lines repeated 9 more times] ..." in compressed


def test_semantic_deduplication_pagination():
    """Verify _paginate_output truncates extremely large outputs cleanly."""
    lines = ["log output line"] * 6000
    full_output = "\n".join(lines)

    paginated = _paginate_output(full_output)

    # The output should show the first 500 lines and a truncation message.
    # Total lines: 500 + 1 for \n\n + 1 for truncation message = 502
    paginated_lines = paginated.splitlines()
    assert len(paginated_lines) == 502
    assert "Output truncated" in paginated
    assert "hermes_read_log_chunk" in paginated

    # Extract file path
    path_start = paginated.find("File cached at ") + len("File cached at ")
    path_end = paginated.find(". Use hermes_read_log_chunk", path_start)
    path = paginated[path_start:path_end]

    # Test reading the chunk natively
    res = hermes_read_log_chunk(file_path=path, offset=500, length=10)
    assert res["status"] == "success"
    assert res["total_lines"] == 6000
    assert len(res["content"].splitlines()) == 10


def test_execution_tool_integration(monkeypatch):
    """Verify execute_code natively calls the compressor on massive outputs natively."""
    from codomyrmex.coding.sandbox.container import check_docker_available

    if not check_docker_available():
        pytest.skip("Docker is not available. Skipping native execution integration.")

    # We execute a bash script emitting endless identical lines
    script = "for i in {1..7000}; do echo 'identical log output'; done"

    # Needs a real execution run
    res = execute_code(language="bash", code=script, timeout=10)

    assert res["exit_code"] == 0
    stdout = res["stdout"]

    # First, compression takes it down drastically
    assert "... [Line repeated" in stdout
