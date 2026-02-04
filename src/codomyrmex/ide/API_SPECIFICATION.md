# IDE Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview
The `ide` module provides a unified interface for automating and interacting with Integrated Development Environments (IDEs) such as VS Code, Cursor, and Antigravity. It abstracts IDE-specific communication protocols into a standard set of commands and events.

## 2. Core Classes

### 2.1 `IDEClient` (Abstract Base Class)
The primary interface for all IDE integrations.

#### Properties
- `status: IDEStatus` - Current connection status (DISCONNECTED, CONNECTING, CONNECTED, ERROR).
- `command_history: List[IDECommandResult]` - Log of all executed commands.

#### Methods
- `connect() -> bool`: Establish connection to the IDE.
- `disconnect() -> None`: Terminate the connection.
- `is_connected() -> bool`: Check connection state.
- `execute_command(command: str, args: Optional[Dict]) -> Any`: Execute a command.
- `get_active_file() -> Optional[str]`: Get path of the currently focused file.
- `open_file(path: str) -> bool`: Open a file in the editor.
- `get_open_files() -> List[str]`: List all open files.
- `register_event_handler(event: str, handler: Callable) -> None`: Subscribe to IDE events.

### 2.2 Data Structures
- **`IDEStatus` (Enum)**: Connection states.
- **`IDECommand` (Dataclass)**: Encapsulates command request (name, args, timeout).
- **`IDECommandResult` (Dataclass)**: Encapsulates command response (success, output, error, timing).
- **`FileInfo` (Dataclass)**: File metadata (path, name, language, modification status).

## 3. Exceptions
- `IDEError`: Base exception.
- `ConnectionError`: Connection failures.
- `CommandExecutionError`: Command failures.
- `SessionError`: Session state issues.
- `ArtifactError`: File/resource access issues.

## 4. Usage Example

```python
from codomyrmex.ide import IDEClient, IDECommand

class CustomClient(IDEClient):
    # Implementation details...
    pass

client = CustomClient()
client.connect()

if client.is_connected():
    result = client.execute_command("editor.action.format")
    print(f"Format success: {result}")
```
