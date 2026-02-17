# PAI-Codomyrmex Tools Reference

**Version**: v0.4.0 | **Last Updated**: February 2026

## Overview

Codomyrmex exposes tools to PAI via two mechanisms:
1. **Static tools** (18): Defined in `mcp_bridge.py`, always available
2. **Dynamic tools** (variable): Auto-discovered from module public functions at runtime

The PAI Skill (`SKILL.md`) curates a subset for MCP consumption.

## Static Tools (18)

### File Operations

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.read_file` | Safe | Read file contents with metadata |
| `codomyrmex.write_file` | **Destructive** | Write content to a file |
| `codomyrmex.list_directory` | Safe | List directory contents with filtering |

#### `codomyrmex.read_file`
- **Parameters**: `path` (required), `encoding` (default: "utf-8"), `max_size` (default: 1000000)
- **Returns**: File contents with metadata

#### `codomyrmex.write_file`
- **Parameters**: `path` (required), `content` (required), `create_dirs` (default: true)
- **Returns**: Write confirmation
- **Trust**: Requires TRUSTED level

#### `codomyrmex.list_directory`
- **Parameters**: `path` (default: "."), `pattern` (default: "*"), `recursive` (default: false), `max_items` (default: 200)
- **Returns**: Directory listing

### Code Analysis

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.analyze_python` | Safe | Analyze Python file structure and metrics |
| `codomyrmex.search_codebase` | Safe | Search for patterns (regex supported) |

#### `codomyrmex.analyze_python`
- **Parameters**: `path` (required)
- **Returns**: Structure analysis (classes, functions, imports, metrics)

#### `codomyrmex.search_codebase`
- **Parameters**: `pattern` (required), `path` (default: "."), `file_types` (array), `case_sensitive` (default: false), `max_results` (default: 100)
- **Returns**: Matching files and lines

### Git Operations

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.git_status` | Safe | Get git repository status |
| `codomyrmex.git_diff` | Safe | Get git diff for changes |

#### `codomyrmex.git_status`
- **Parameters**: `path` (default: ".")
- **Returns**: Repository status (branch, staged, modified, untracked)

#### `codomyrmex.git_diff`
- **Parameters**: `path` (default: "."), `staged` (default: false)
- **Returns**: Diff output

### Shell

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.run_command` | **Destructive** | Execute shell commands safely |

#### `codomyrmex.run_command`
- **Parameters**: `command` (required), `cwd` (default: "."), `timeout` (default: 30)
- **Returns**: stdout, stderr, return code
- **Trust**: Requires TRUSTED level

### Data Utilities

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.json_query` | Safe | Read/query JSON files via dot-notation |
| `codomyrmex.checksum_file` | Safe | Calculate file checksum (md5, sha1, sha256) |

#### `codomyrmex.json_query`
- **Parameters**: `path` (required), `query` (optional dot-notation path)
- **Returns**: JSON data or queried subset

#### `codomyrmex.checksum_file`
- **Parameters**: `path` (required), `algorithm` (default: "sha256")
- **Returns**: Hex digest string

### Discovery

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.list_modules` | Safe | List all available Codomyrmex modules |
| `codomyrmex.module_info` | Safe | Get module docstring, exports, path |

#### `codomyrmex.list_modules`
- **Parameters**: none
- **Returns**: `{modules: [...], count: N}`

#### `codomyrmex.module_info`
- **Parameters**: `module_name` (required)
- **Returns**: `{module, docstring, exports, export_count, path}`

### PAI

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.pai_status` | Safe | Get PAI installation status and components |
| `codomyrmex.pai_awareness` | Safe | Get full PAI awareness data |

#### `codomyrmex.pai_status`
- **Parameters**: none
- **Returns**: Installation status with component counts (skills, tools, hooks, agents, memory)

#### `codomyrmex.pai_awareness`
- **Parameters**: none
- **Returns**: Missions, projects, tasks, TELOS, memory data

### Testing

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.run_tests` | **Destructive** | Run pytest for a module or project |

#### `codomyrmex.run_tests`
- **Parameters**: `module` (optional), `verbose` (default: false)
- **Returns**: `{returncode, passed, stdout, stderr}`
- **Trust**: Requires TRUSTED level (test execution may have side effects)

### Universal Module Proxy (3 tools)

These tools provide generic access to **any** Codomyrmex module's public API:

| Tool | Trust | Description |
|------|-------|-------------|
| `codomyrmex.list_module_functions` | Safe | List all public callables in a module |
| `codomyrmex.call_module_function` | **Destructive** | Call any public function by path |
| `codomyrmex.get_module_readme` | Safe | Read module README/SPEC docs |

#### `codomyrmex.list_module_functions`
- **Parameters**: `module` (required, e.g. "encryption", "cache")
- **Returns**: `{module, functions: [{name, signature, docstring}], classes: [{name, docstring, public_methods}], total_callables}`

#### `codomyrmex.call_module_function`
- **Parameters**: `function` (required, e.g. "encryption.encrypt"), `kwargs` (optional dict)
- **Returns**: `{result: ...}` or `{error: ...}`
- **Trust**: Requires TRUSTED level (arbitrary code execution)
- **Safety**: Private functions (underscore-prefixed) are blocked

#### `codomyrmex.get_module_readme`
- **Parameters**: `module` (required)
- **Returns**: `{module, path, content}` (truncated at 5000 chars)

## Dynamic Tool Discovery

Beyond the 18 static tools, the MCP bridge auto-discovers additional tools at runtime:

1. **Decorated tools**: Functions with `@mcp_tool` decorator in targeted modules
2. **Public functions**: All public functions from every Codomyrmex module

Targeted scan modules include: `data_visualization`, `llm`, `agentic_memory`, `security`, `git_operations`, `coding`, `documentation`, `terminal_interface`.

### Trust Classification for Dynamic Tools

Dynamic tools are classified using pattern matching on function names:
- Names containing `write`, `delete`, `execute`, `run`, `create`, `modify`, etc. → **Destructive**
- All others → **Safe**

See `_DESTRUCTIVE_PATTERNS` in `trust_gateway.py` for the full list.

## Tool Count Summary

| Category | Count | Trust |
|----------|-------|-------|
| Static safe | 14 | Auto-VERIFIED |
| Static destructive | 4 | Requires TRUSTED |
| Dynamic | Variable | Pattern-classified |
| **Total static** | **18** | — |

## Navigation

- **Index**: [README.md](README.md)
- **Architecture**: [architecture.md](architecture.md)
- **API**: [api-reference.md](api-reference.md)
- **Workflows**: [workflows.md](workflows.md)
