# aider -- MCP Tool Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

All tools are auto-discovered via the `@mcp_tool` decorator in `mcp_tools.py` and surfaced through the PAI MCP bridge. No manual registration required.

---

## aider_check

**Category**: `aider`
**Description**: Check if aider is installed and return version + configured model.

### Parameters

None.

### Return Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` or `"error"` |
| `installed` | `bool` | True if aider binary found in PATH |
| `version` | `str` | Installed aider version (e.g. `"0.77.0"`) |
| `model` | `str` | Currently configured model |
| `install_hint` | `str` | Present when `installed=false`; contains install command |
| `message` | `str` | Present when `status="error"` |

### Example

```json
// Request
{"tool": "aider_check"}

// Response (installed)
{"status": "success", "installed": true, "version": "0.77.0", "model": "claude-sonnet-4-6"}

// Response (not installed)
{"status": "success", "installed": false, "version": "", "model": "claude-sonnet-4-6", "install_hint": "uv tool install aider-chat"}
```

### Error Cases

- Internal exception: `{"status": "error", "message": "..."}`

---

## aider_edit

**Category**: `aider`
**Description**: Edit files using aider AI pair programming. Applies code changes based on a natural-language instruction.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | -- | List of file paths to edit |
| `instruction` | `str` | Yes | -- | Natural-language instruction describing the change |
| `model` | `str` | No | `"claude-sonnet-4-6"` | LLM model to use |
| `timeout` | `int` | No | `300` | Subprocess timeout in seconds |

### Return Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` or `"error"` |
| `output` | `str` | Captured stdout from aider |
| `stderr` | `str` | Captured stderr from aider |
| `returncode` | `str` | Process return code (`"0"` = success) |
| `message` | `str` | Present when `status="error"` |

### Example

```json
// Request
{
  "tool": "aider_edit",
  "file_paths": ["src/app.py"],
  "instruction": "Add comprehensive error handling to all HTTP calls",
  "model": "claude-sonnet-4-6"
}

// Response
{
  "status": "success",
  "output": "Applied changes to src/app.py\n...",
  "stderr": "",
  "returncode": "0"
}
```

### Error Cases

- Empty file_paths: `{"status": "error", "message": "file_paths must not be empty"}`
- Aider not installed: `{"status": "error", "message": "aider binary not found in PATH..."}`
- Timeout: `{"status": "error", "message": "aider subprocess timed out after 300s"}`

---

## aider_ask

**Category**: `aider`
**Description**: Ask aider a question about code without making any file changes. Returns analysis or explanation.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | -- | Files to include as context |
| `question` | `str` | Yes | -- | Question to ask about the code |
| `model` | `str` | No | `"claude-sonnet-4-6"` | LLM model to use |
| `timeout` | `int` | No | `120` | Subprocess timeout in seconds |

### Return Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` or `"error"` |
| `answer` | `str` | Aider's response to the question |
| `stderr` | `str` | Captured stderr |
| `message` | `str` | Present when `status="error"` |

### Example

```json
// Request
{
  "tool": "aider_ask",
  "file_paths": ["src/auth.py"],
  "question": "Is this JWT implementation secure? What vulnerabilities exist?"
}

// Response
{
  "status": "success",
  "answer": "The JWT implementation has several considerations...",
  "stderr": ""
}
```

### Error Cases

- Aider not installed: `{"status": "error", "message": "aider binary not found in PATH..."}`
- Timeout: `{"status": "error", "message": "aider subprocess timed out after 120s"}`

---

## aider_architect

**Category**: `aider`
**Description**: Use aider's architect mode for complex multi-step refactoring. Uses two-model workflow: one plans, one edits.

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `file_paths` | `list[str]` | Yes | -- | Files to include |
| `task` | `str` | Yes | -- | Complex task description |
| `model` | `str` | No | `"claude-sonnet-4-6"` | Architect model (planner) |
| `editor_model` | `str` | No | `""` | Editor model (defaults to architect model) |
| `timeout` | `int` | No | `600` | Subprocess timeout in seconds |

### Return Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` or `"error"` |
| `output` | `str` | Captured stdout from aider |
| `stderr` | `str` | Captured stderr |
| `returncode` | `str` | Process return code (`"0"` = success) |
| `message` | `str` | Present when `status="error"` |

### Example

```json
// Request
{
  "tool": "aider_architect",
  "file_paths": ["src/"],
  "task": "Add comprehensive logging to all service methods",
  "editor_model": "claude-haiku-4-5-20251001"
}

// Response
{
  "status": "success",
  "output": "Architect plan:\n...\nApplied changes to...",
  "stderr": "",
  "returncode": "0"
}
```

### Error Cases

- Empty file_paths: `{"status": "error", "message": "file_paths must not be empty"}`
- Aider not installed: `{"status": "error", "message": "aider binary not found in PATH..."}`
- Timeout: `{"status": "error", "message": "aider subprocess timed out after 600s"}`

---

## aider_config

**Category**: `aider`
**Description**: Return current aider configuration: model, API key presence, and timeout settings.

### Parameters

None.

### Return Schema

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` or `"error"` |
| `model` | `str` | Configured model name |
| `has_anthropic_key` | `bool` | True if ANTHROPIC_API_KEY is set |
| `has_openai_key` | `bool` | True if OPENAI_API_KEY is set |
| `has_any_key` | `bool` | True if at least one API key is set |
| `timeout` | `int` | Configured timeout in seconds |
| `message` | `str` | Present when `status="error"` |

### Example

```json
// Request
{"tool": "aider_config"}

// Response
{
  "status": "success",
  "model": "claude-sonnet-4-6",
  "has_anthropic_key": true,
  "has_openai_key": false,
  "has_any_key": true,
  "timeout": 300
}
```

### Error Cases

- Internal exception: `{"status": "error", "message": "..."}`

---

## Navigation

- **Module README**: [README.md](README.md)
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **Agent Capabilities**: [AGENTS.md](AGENTS.md)
- **Technical Spec**: [SPEC.md](SPEC.md)
- **PAI Integration**: [PAI.md](PAI.md)
