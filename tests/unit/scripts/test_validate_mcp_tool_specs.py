"""Tests for scripts/documentation/validate_mcp_tool_specs.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from tests.support.repo_paths import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "documentation" / "validate_mcp_tool_specs.py"


def _load():
    spec = importlib.util.spec_from_file_location("validate_mcp_tool_specs", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


vmts = _load()

SOURCE = '''\
"""Example tools. ``@mcp_tool`` in a docstring is not a decorator."""

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(category="alpha")
def alpha_status() -> dict:
    return {}


@mcp_tool(name="codomyrmex.alpha_renamed", category="alpha")
def _implementation() -> dict:
    return {}


@mcp_tool("alpha_positional")
async def alpha_async() -> dict:
    return {}


class Graph:
    @mcp_tool(name="Graph.walk")
    def walk(self) -> list:
        return []

    def get_tool_definitions(self) -> dict:
        return {"adapter_run": {"name": "adapter_run"}, "adapter_list": {}}


def register_mcp_tools(server) -> None:
    @server.tool()
    def fastmcp_tool() -> str:
        return ""


@other_decorator
def not_a_tool() -> None:
    pass
'''

STATIC = """\
TOOL_DEFINITIONS: list = [
    ("codomyrmex.read_file", "Read a file", None, {}),
    ("codomyrmex.list_workflows", "List workflows", None, {}),
]
"""

DOC = """\
# Alpha - MCP Tool Specification

## Tool Reference

## Tool: `alpha_status`

### 2. Invocation Name

`alpha_status`

### `codomyrmex.alpha_renamed()`

### `alpha_positional` / `Graph.walk`

## adapter_run

| Tool | Purpose |
| :--- | :--- |
| `adapter_list` | Listed in a tool table |
| **`missing_from_table`** | Broken |

| Parameter Name | Type |
| :--- | :--- |
| `not_a_tool_param` | `string` |

## Tool: `[YourToolName]`

### Overview

```python
@mcp_tool()
def fenced_example(): ...
```

## `after_fence`

<!--
## `commented_out`
-->

Prose mentioning `prose_only` is not documentation of a tool.
"""


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _make_repo(root: Path) -> None:
    """A miniature repository with two modules and the PAI static tools."""
    _write(root / "src/codomyrmex/alpha/mcp_tools.py", SOURCE)
    _write(
        root / "src/codomyrmex/beta/mcp_tools.py",
        "@mcp_tool()\ndef beta_only() -> None:\n    pass\n\n"
        "@mcp_tool()\ndef beta_undocumented() -> None:\n    pass\n",
    )
    _write(root / "src/codomyrmex/agents/pai/mcp/definitions.py", STATIC)
    _write(
        root / "src/codomyrmex/beta/tests/mcp_tools.py",
        "@mcp_tool()\ndef test_only_tool() -> None:\n    pass\n",
    )
    _write(
        root / "src/codomyrmex/agents/hermes/evolution/mcp_tools.py",
        "@mcp_tool()\ndef vendored_tool() -> None:\n    pass\n",
    )


@pytest.mark.unit
def test_tools_in_source_reads_decorators_names_and_adapters() -> None:
    tools = vmts.tools_in_source(SOURCE, "alpha/mcp_tools.py")
    assert sorted(t.name for t in tools) == [
        "Graph.walk",
        "adapter_list",
        "adapter_run",
        "alpha_positional",
        "alpha_renamed",
        "alpha_status",
        "fastmcp_tool",
    ]
    by_name = {t.name: t for t in tools}
    assert by_name["alpha_status"].line == 7
    assert by_name["alpha_renamed"].path == "alpha/mcp_tools.py"


@pytest.mark.unit
def test_static_definition_tools_strip_the_bridge_prefix() -> None:
    names = [t.name for t in vmts.static_definition_tools(STATIC, "definitions.py")]
    assert names == ["read_file", "list_workflows"]


@pytest.mark.unit
def test_normalize_strips_backticks_call_parens_and_prefix() -> None:
    assert vmts.normalize(" `codomyrmex.list_modules()` ") == "list_modules"
    assert vmts.normalize("Graph.walk") == "Graph.walk"


@pytest.mark.unit
def test_extract_documented_tools_handles_heading_and_table_styles() -> None:
    documented = vmts.extract_documented_tools(DOC, "spec.md")
    assert [(d.name, d.line) for d in documented] == [
        ("alpha_status", 5),
        ("alpha_status", 9),
        ("alpha_renamed", 11),
        ("alpha_positional", 13),
        ("Graph.walk", 13),
        ("adapter_run", 15),
        ("adapter_list", 19),
        ("missing_from_table", 20),
        ("after_fence", 35),
    ]


@pytest.mark.unit
def test_spec_scope_maps_specs_and_mirrors_to_packages(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    (tmp_path / "src/codomyrmex/alpha/docs").mkdir()
    assert vmts.spec_scope(
        "src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md", tmp_path
    ) == ("src/codomyrmex/alpha/")
    assert vmts.spec_scope(
        "src/codomyrmex/alpha/docs/MCP_TOOL_SPECIFICATION.md", tmp_path
    ) == ("src/codomyrmex/alpha/")
    assert vmts.spec_scope("docs/modules/beta/MCP_TOOL_SPECIFICATION.md", tmp_path) == (
        "src/codomyrmex/beta/"
    )
    assert (
        vmts.spec_scope("docs/modules/gamma/MCP_TOOL_SPECIFICATION.md", tmp_path)
        is None
    )
    assert vmts.spec_scope("MCP_TOOL_SPECIFICATION.md", tmp_path) is None


@pytest.mark.unit
def test_scan_reports_broken_skipped_and_undocumented(tmp_path: Path) -> None:
    _make_repo(tmp_path)
    alpha = _write(tmp_path / "src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md", DOC)
    _write(
        tmp_path / "docs/modules/alpha/MCP_TOOL_SPECIFICATION.md",
        "## Tool: `alpha_status`\n\n## Tool: `beta_only`\n\n## Tool: `read_file`\n",
    )
    _write(
        tmp_path / "src/codomyrmex/beta/MCP_TOOL_SPECIFICATION.md",
        "<!-- docs-check: skip-mcp-tools -->\n\n## Tool: `planned_tool`\n",
    )
    _write(
        tmp_path / "src/codomyrmex/agents/hermes/evolution/MCP_TOOL_SPECIFICATION.md",
        "## Tool: `vendored_tool`\n",
    )

    report = vmts.scan(tmp_path)

    assert report.specs_scanned == 3
    assert report.specs_skipped == ["src/codomyrmex/beta/MCP_TOOL_SPECIFICATION.md"]
    assert "test_only_tool" not in report.tools
    assert "vendored_tool" not in report.tools
    broken = {(b.tool.path, b.tool.name): b.reason for b in report.broken}
    assert set(broken) == {
        ("src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md", "missing_from_table"),
        ("src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md", "after_fence"),
        ("docs/modules/alpha/MCP_TOOL_SPECIFICATION.md", "beta_only"),
    }
    assert (
        "no tool with this name"
        in broken[("src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md", "after_fence")]
    )
    assert (
        "src/codomyrmex/beta/mcp_tools.py"
        in broken[("docs/modules/alpha/MCP_TOOL_SPECIFICATION.md", "beta_only")]
    )
    # Every alpha tool is documented; the skipped beta spec documents nothing.
    undocumented = {(tool.name, spec) for tool, spec in report.undocumented}
    assert undocumented == {
        ("beta_only", "src/codomyrmex/beta/MCP_TOOL_SPECIFICATION.md"),
        ("beta_undocumented", "src/codomyrmex/beta/MCP_TOOL_SPECIFICATION.md"),
        ("fastmcp_tool", "src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md"),
    }
    data = report.to_dict()
    assert data["broken_tools"] == 3
    assert data["undocumented_tools"] == 3
    locations = {b["tool"]: b["location"] for b in data["broken"]}
    assert locations["after_fence"] == f"{alpha.relative_to(tmp_path)}:35"


@pytest.mark.unit
def test_cli_exit_codes_and_json_output(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    _make_repo(tmp_path)
    good = _write(
        tmp_path / "src/codomyrmex/alpha/MCP_TOOL_SPECIFICATION.md",
        "## Tool: `alpha_status`\n",
    )
    bad = _write(
        tmp_path / "docs/modules/alpha/MCP_TOOL_SPECIFICATION.md",
        "## Tool: `no_such_tool`\n",
    )
    output = tmp_path / "out" / "report.json"

    assert vmts.main(["--repo-root", str(tmp_path), "--fail-on-broken", str(good)]) == 0
    assert vmts.main(["--repo-root", str(tmp_path), str(bad)]) == 0
    capsys.readouterr()
    assert (
        vmts.main(
            [
                "--repo-root",
                str(tmp_path),
                "--format",
                "json",
                "--output",
                str(output),
                "--fail-on-broken",
                str(bad),
            ]
        )
        == 1
    )
    printed = json.loads(capsys.readouterr().out)
    assert printed == json.loads(output.read_text(encoding="utf-8"))
    assert printed["broken"][0]["tool"] == "no_such_tool"
    assert printed["broken"][0]["location"] == (
        "docs/modules/alpha/MCP_TOOL_SPECIFICATION.md:1"
    )


@pytest.mark.unit
def test_repository_specs_document_only_real_tools() -> None:
    report = vmts.scan(REPO_ROOT)
    assert report.specs_scanned > 0
    assert len(report.tools) > 0
    assert [
        f"{b.tool.path}:{b.tool.line} {b.tool.name} ({b.reason})" for b in report.broken
    ] == []
