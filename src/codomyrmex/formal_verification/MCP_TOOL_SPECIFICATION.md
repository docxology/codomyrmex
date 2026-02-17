# Formal Verification — MCP Tool Specification

## Tools

### clear_model

Clear the entire constraint model, resetting to empty state.

- **Category**: formal_verification
- **Parameters**: None
- **Returns**: `{"status": "ok", "message": "Model cleared"}`

### add_item

Add a Z3 Python expression to the constraint model.

- **Category**: formal_verification
- **Parameters**:
  - `item` (string, required): Z3 Python code (e.g., `"x = Int('x')"`)
  - `index` (integer, optional): Position to insert at. Appends if omitted.
- **Returns**: `{"status": "ok", "index": <int>, "item": <string>}`

### delete_item

Delete the item at the specified index.

- **Category**: formal_verification
- **Parameters**:
  - `index` (integer, required): Zero-based index to delete.
- **Returns**: `{"status": "ok", "removed_item": <string>, "index": <int>}`
- **Error**: `{"status": "error", "error": "<message>"}` — returned for out-of-range index or empty model

### replace_item

Replace the item at the specified index with new content.

- **Category**: formal_verification
- **Parameters**:
  - `index` (integer, required): Zero-based index to replace.
  - `new_item` (string, required): New Z3 Python code.
- **Returns**: `{"status": "ok", "old_item": <string>, "new_item": <string>, "index": <int>}`
- **Error**: `{"status": "error", "error": "<message>"}` — returned for out-of-range index or empty model

### get_model

Retrieve the current constraint model as a numbered list.

- **Category**: formal_verification
- **Parameters**: None
- **Returns**: `{"status": "ok", "item_count": <int>, "items": [{"index": <int>, "content": <string>}]}`

### solve_model

Execute the Z3 solver on the current model.

- **Category**: formal_verification
- **Parameters**:
  - `timeout_ms` (integer, optional, default 30000): Maximum solving time in milliseconds.
- **Returns**: `{"status": "<sat|unsat|unknown|timeout|error>", "satisfiable": <bool>, "model": <dict|null>, "objective_value": <any>, "statistics": <dict>, "error": <string|null>}`

## Error Handling

All tools return `{"status": "error", "error": "<message>"}` when:
- Z3 solver is not installed (`BackendNotAvailableError`)
- Index is out of range or model is empty (`delete_item`, `replace_item`)

## Integration

Tools are registered via `@mcp_tool(category="formal_verification")` decorator and auto-discovered by the PAI MCP bridge.
