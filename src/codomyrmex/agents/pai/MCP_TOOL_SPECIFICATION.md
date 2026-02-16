# MCP Tool Specification — PAI Bridge

**Version**: 0.3.0 | **Server**: `codomyrmex-mcp-server`

This document specifies all MCP tools registered by the PAI ↔ Codomyrmex MCP bridge.

## Tool Inventory

### File Operations

#### `codomyrmex.read_file`

**Description**: Read file contents with metadata.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string", "description": "File path to read"},
    "encoding": {"type": "string", "default": "utf-8"},
    "max_size": {"type": "integer", "default": 1000000}
  },
  "required": ["path"]
}
```

**Output**: `{"content": "...", "size": 1234, "encoding": "utf-8"}`
**Idempotent**: Yes

#### `codomyrmex.write_file`

**Description**: Write content to a file.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string"},
    "content": {"type": "string"},
    "create_dirs": {"type": "boolean", "default": true}
  },
  "required": ["path", "content"]
}
```

**Output**: `{"success": true, "path": "...", "size": 1234}`
**Idempotent**: Yes (overwrites)

#### `codomyrmex.list_directory`

**Description**: List directory contents with glob filtering.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string", "default": "."},
    "pattern": {"type": "string", "default": "*"},
    "recursive": {"type": "boolean", "default": false},
    "max_items": {"type": "integer", "default": 200}
  }
}
```

**Output**: `{"items": [...], "count": 42}`
**Idempotent**: Yes

---

### Code Analysis

#### `codomyrmex.analyze_python`

**Description**: Analyze a Python file for AST structure and metrics.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "path": {"type": "string", "description": "Python file path"}
  },
  "required": ["path"]
}
```

**Output**: `{"classes": [...], "functions": [...], "imports": [...], "metrics": {...}}`
**Idempotent**: Yes

#### `codomyrmex.search_codebase`

**Description**: Search for patterns in code files (regex supported).
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "pattern": {"type": "string"},
    "path": {"type": "string", "default": "."},
    "file_types": {"type": "array", "items": {"type": "string"}},
    "case_sensitive": {"type": "boolean", "default": false},
    "max_results": {"type": "integer", "default": 100}
  },
  "required": ["pattern"]
}
```

**Output**: `{"matches": [...], "total_matches": 15}`
**Idempotent**: Yes

---

### Git Operations

#### `codomyrmex.git_status`

**Description**: Get git repository status.
**Input Schema**: `{"type": "object", "properties": {"path": {"type": "string", "default": "."}}}`
**Output**: `{"branch": "main", "changes": [...], "clean": false}`
**Idempotent**: Yes

#### `codomyrmex.git_diff`

**Description**: Get git diff for changes.
**Input Schema**: `{"type": "object", "properties": {"path": {"type": "string"}, "staged": {"type": "boolean"}}}`
**Output**: `{"diff": "..."}`
**Idempotent**: Yes

---

### Shell

#### `codomyrmex.run_command`

**Description**: Execute a shell command safely.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "command": {"type": "string"},
    "cwd": {"type": "string", "default": "."},
    "timeout": {"type": "integer", "default": 30}
  },
  "required": ["command"]
}
```

**Output**: `{"stdout": "...", "stderr": "...", "exit_code": 0}`
**Idempotent**: No
**Security**: Commands are sandboxed with timeout.

---

### Data Utilities

#### `codomyrmex.json_query`

**Description**: Read and optionally query a JSON file via dot-notation.
**Input Schema**: `{"type": "object", "properties": {"path": {"type": "string"}, "query": {"type": "string"}}, "required": ["path"]}`
**Output**: `{"data": {...}}`
**Idempotent**: Yes

#### `codomyrmex.checksum_file`

**Description**: Calculate file checksum (md5, sha1, sha256).
**Input Schema**: `{"type": "object", "properties": {"path": {"type": "string"}, "algorithm": {"type": "string", "default": "sha256"}}, "required": ["path"]}`
**Output**: `{"checksum": "abc123...", "algorithm": "sha256", "size": 1234}`
**Idempotent**: Yes

---

### Discovery

#### `codomyrmex.list_modules`

**Description**: List all available Codomyrmex modules.
**Input Schema**: `{"type": "object", "properties": {}}`
**Output**: `{"modules": ["agents", "llm", ...], "count": 100}`
**Idempotent**: Yes

#### `codomyrmex.module_info`

**Description**: Get info about a specific module.
**Input Schema**: `{"type": "object", "properties": {"module_name": {"type": "string"}}, "required": ["module_name"]}`
**Output**: `{"module": "llm", "docstring": "...", "exports": [...], "path": "..."}`
**Idempotent**: Yes

---

### Universal Module Proxy

These tools provide **dynamic access to all 106 modules** without per-module MCP decoration.

#### `codomyrmex.list_module_functions`

**Description**: List all public callable functions and classes in any Codomyrmex module.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "module": {"type": "string", "description": "Module path, e.g. 'encryption', 'cache'"}
  },
  "required": ["module"]
}
```

**Output**: `{"module": "codomyrmex.encryption", "functions": [...], "classes": [...], "total_callables": 21}`
**Idempotent**: Yes

#### `codomyrmex.call_module_function`

**Description**: Call any public function from any module by path.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "function": {"type": "string", "description": "e.g. 'encryption.encrypt'"},
    "kwargs": {"type": "object", "description": "Keyword arguments to pass"}
  },
  "required": ["function"]
}
```

**Output**: `{"result": ...}` or `{"error": "..."}`
**Idempotent**: Depends on function called
**Security**: Private functions (prefixed `_`) are blocked. **DESTRUCTIVE** — requires TRUSTED level.

#### `codomyrmex.get_module_readme`

**Description**: Read the README.md or SPEC.md for any module.
**Input Schema**:

```json
{
  "type": "object",
  "properties": {
    "module": {"type": "string", "description": "Module name, e.g. 'encryption'"}
  },
  "required": ["module"]
}
```

**Output**: `{"module": "codomyrmex.encryption", "path": "...", "content": "..."}`
**Idempotent**: Yes

---

### PAI

#### `codomyrmex.pai_status`

**Description**: Get PAI installation status and component inventory.
**Input Schema**: `{"type": "object", "properties": {}}`
**Output**: `{"installed": true, "pai_root": "...", "components": {...}}`
**Idempotent**: Yes

#### `codomyrmex.pai_awareness`

**Description**: Get full PAI awareness data.
**Input Schema**: `{"type": "object", "properties": {}}`
**Output**: `{"missions": [...], "projects": [...], "tasks": [...], "metrics": {...}}`
**Idempotent**: Yes

---

### Testing

#### `codomyrmex.run_tests`

**Description**: Run pytest for a specific module or the whole project.
**Input Schema**: `{"type": "object", "properties": {"module": {"type": "string"}, "verbose": {"type": "boolean", "default": false}}}`
**Output**: `{"passed": true, "returncode": 0, "stdout": "..."}`
**Idempotent**: Yes

---

## Usage Example (MCP format)

```json
{
  "tool_name": "codomyrmex.list_module_functions",
  "arguments": {
    "module": "encryption"
  }
}
```

## Security Considerations

- `codomyrmex.write_file` — validates parent directory creation
- `codomyrmex.run_command` — timeout-enforced, no shell injection
- `codomyrmex.run_tests` — 120s timeout, read-only operations
- `codomyrmex.call_module_function` — blocks private functions, requires TRUSTED trust level
- All tools return structured errors via `MCPToolResult`
