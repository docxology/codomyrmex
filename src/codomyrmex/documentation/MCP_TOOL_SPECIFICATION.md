# Documentation -- MCP Tool Specification

This document specifies the MCP-discoverable tools exposed by the `documentation` module. These tools provide documentation generation and RASP compliance auditing for Codomyrmex modules.

## General Considerations

- **Auto-Discovery**: Tools use the `@mcp_tool(category="documentation")` decorator and are auto-discovered via the MCP bridge.
- **Dependencies**: Requires the `documentation` module's internal `write_pai_md` and `audit_rasp` functions.
- **Working Directory**: Module paths are resolved relative to `src/codomyrmex/` in the project root.
- **Error Handling**: All tools return `{"status": "error", "message": "..."}` on failure.

---

## Tool: `generate_module_docs`

### 1. Tool Purpose and Description

Generate or update the RASP documentation suite (README.md, AGENTS.md, SPEC.md, PAI.md) for a specific module. Currently focuses on generating the PAI.md file for the target module.

### 2. Invocation Name

`generate_module_docs`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `module_name` | `string` | Yes | Name of the module to generate documentation for (must exist under `src/codomyrmex/`) | `"cerebrum"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `message` | `string` | Confirmation or error description | `"Documentation generated for cerebrum"` |
| `paths` | `array` | List of file paths that were generated (only on success) | `["src/codomyrmex/cerebrum/PAI.md"]` |

### 5. Error Handling

- If the module directory does not exist at `src/codomyrmex/{module_name}`, returns an error with `"Module {module_name} not found."`.
- Documentation generation failures (import errors, write errors) return an error with the exception message.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Regenerating documentation for the same module overwrites the same files with the same content (assuming the module source has not changed). Safe to call repeatedly.

### 7. Usage Examples

```json
{
  "tool_name": "generate_module_docs",
  "arguments": {
    "module_name": "crypto"
  }
}
```

### 8. Security Considerations

- This tool writes files to the module directory. It should be gated by the trust gateway.
- The tool only writes to the module's own directory under `src/codomyrmex/`. Path traversal via `module_name` is limited by the `Path(f"src/codomyrmex/{module_name}")` construction, but callers should still validate module names.

---

## Tool: `audit_rasp_compliance`

### 1. Tool Purpose and Description

Audit the repository for RASP (README, AGENTS, SPEC, PAI) compliance. Can audit a single module or the entire `src/codomyrmex/` tree. Returns the count of missing documentation files.

### 2. Invocation Name

`audit_rasp_compliance`

### 3. Input Schema (Parameters)

| Parameter Name | Type | Required | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `module_name` | `string \ | null` | No | Module name to audit specifically. If not provided (or null), audits the entire repository. `"agents"` |

### 4. Output Schema (Return Value)

| Field Name | Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `status` | `string` | `"success"` or `"error"` | `"success"` |
| `compliant` | `boolean` | Whether the audited scope is fully RASP-compliant (no missing files) | `true` |
| `missing_count` | `integer` | Number of missing RASP documentation files found | `0` |
| `message` | `string` | Error description (only on error) | `"Audit function not available"` |

### 5. Error Handling

- Import failures for the `audit_rasp` function return an error status.
- File system access errors during the audit return an error with the exception message.

### 6. Idempotency

- **Idempotent**: Yes
- **Explanation**: Auditing is a read-only operation that scans for the presence of documentation files without modifying anything.

### 7. Usage Examples

Audit a single module:

```json
{
  "tool_name": "audit_rasp_compliance",
  "arguments": {
    "module_name": "cerebrum"
  }
}
```

Audit the entire repository:

```json
{
  "tool_name": "audit_rasp_compliance",
  "arguments": {}
}
```

### 8. Security Considerations

- This is a read-only operation that only checks for file existence. No elevated trust level required.
- Audit results may reveal information about the project's documentation structure.

---

## Navigation Links

- **Parent**: [Module README](./README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Home**: [Root README](../../../README.md)
