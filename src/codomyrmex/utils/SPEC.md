# Utils Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## 1. Interface Definition

### `ScriptBase`

The abstract base class `codomyrmex.utils.ScriptBase` forms the contract for all executable scripts.

**Public Methods**:

- `__init__(name: str, description: str, version: str)`
- `execute(argv: list = None) -> int`: Main entry point. Handles exceptions and cleanup.
- `run(args: Namespace, config: ScriptConfig) -> dict`: Abstract method. Must be implemented by subclass.
- `log_info/warning/error(msg: str)`: Standardized logging.

**Configuration Contract (`ScriptConfig`)**:

- CLI args override Environment variables.
- Environment variables override Config file.
- Config file overrides Defaults.

### `run_command`

**Signature**:

```python
def run_command(
    command: Union[str, List[str]],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    check: bool = False,
    shell: bool = False
) -> SubprocessResult
```

**Return Type (`SubprocessResult`)**:

- `stdout: str`
- `stderr: str`
- `returncode: int`
- `command: str`
- `duration: float`

## 2. Dependencies

- **Internal**: `codomyrmex.logging_monitoring` (optional, graceful fallback provided).
- **External**: `pyyaml` (for config loading).

## 3. Constraints

- **Zero Circular Dependencies**: This module functions as a leaf node in the dependency graph (except for optional logging import). It must not import from Core or Service layers.
- **Stability**: API must be backward compatible. Breaking changes require major version bump.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```
