# Formal Verification — MCP Tool Specification

## Tools

### clear_model

Clear the entire constraint model, resetting to empty state.

- **Category**: formal_verification
- **Parameters**: None
- **Returns**: `{"status": "success", "message": "Model cleared"}`

### add_item

Add a Z3 Python expression to the constraint model.

- **Category**: formal_verification
- **Parameters**:
  - `item` (string, required): Z3 Python code (e.g., `"x = Int('x')"`)
  - `index` (integer, optional): Position to insert at. Appends if omitted.
- **Returns**: `{"status": "success", "index": <int>, "item": <string>}`

### delete_item

Delete the item at the specified index.

- **Category**: formal_verification
- **Parameters**:
  - `index` (integer, required): Zero-based index to delete.
- **Returns**: `{"status": "success", "removed_item": <string>, "index": <int>}`
- **Error**: `{"status": "error", "message": "<message>"}` — returned for out-of-range index, empty model, or unavailable backend

### replace_item

Replace the item at the specified index with new content.

- **Category**: formal_verification
- **Parameters**:
  - `index` (integer, required): Zero-based index to replace.
  - `new_item` (string, required): New Z3 Python code.
- **Returns**: `{"status": "success", "old_item": <string>, "new_item": <string>, "index": <int>}`
- **Error**: `{"status": "error", "message": "<message>"}` — returned for out-of-range index, empty model, or unavailable backend

### get_model

Retrieve the current constraint model as a numbered list.

- **Category**: formal_verification
- **Parameters**: None
- **Returns**: `{"status": "success", "item_count": <int>, "items": [{"index": <int>, "content": <string>}]}`

### solve_model

Execute the Z3 solver on the current model.

- **Category**: formal_verification
- **Parameters**:
  - `timeout_ms` (integer, optional, default 30000): Maximum solving time in milliseconds.
- **Returns**: `{"status": "<sat|unsat|unknown|timeout|error>", "satisfiable": <bool>, "model": <dict|null>, "objective_value": <any>, "statistics": <dict>, "error": <string|null>}`

### push

Start a new incremental solver scope.

- **Category**: formal_verification
- **Parameters**: None
- **Returns**: `{"status": "success", "message": "Solver scope pushed"}`
- **Error**: `{"status": "error", "message": "<message>"}` — returned when the backend is unavailable

### pop

Pop one or more incremental solver scopes.

- **Category**: formal_verification
- **Parameters**:
  - `n` (integer, optional, default `1`): Number of scopes to pop.
- **Returns**: `{"status": "success", "message": "Popped <n> scope(s)"}`
- **Error**: `{"status": "error", "message": "<message>"}` — returned when the backend is unavailable or the scope is invalid

## Error Handling

The stateful model tools return `{"status": "error", "message": "<message>"}` when:
- Z3 solver is not installed (`BackendNotAvailableError`)
- Index is out of range or model is empty (`delete_item`, `replace_item`)

`solve_model` uses the solver status values (`sat`, `unsat`, `unknown`,
`timeout`, `error`) and returns solver-specific details in its `error` field.

## Integration

Tools are registered via `@mcp_tool(category="formal_verification")` decorator and auto-discovered by the PAI MCP bridge.
