# Utils Module Specification

**Version**: v1.2.8 | **Status**: Active | **Last Updated**: April 2026

## 1. Interface Definition

### Retry surfaces

- **`codomyrmex.utils.retry`** (defined in `__init__.py`): synchronous decorator; parameters `max_attempts`, `delay`, `backoff`, `exceptions`.
- **`codomyrmex.utils.retry_sync`**: module `retry_sync.py` — `RetryConfig`, synchronous `retry` with jitter and delay caps, and `async_retry` for coroutines. Re-exports `RetryConfig` and `async_retry` also appear in package `__all__` for convenience.
- **Naming**: there is no `utils/retry.py` package submodule; that name would shadow the package `retry` callable.

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

## 3. Dependencies

- **Internal**: `codomyrmex.logging_monitoring` for `get_logger` (standard path for this package).
- **External**: `pyyaml` (for config loading).

## 4. Constraints

- **Dependency posture**: Prefer minimal imports; avoid pulling in heavy optional stacks from unrelated modules. Logging is a normal dependency here.
- **Stability**: Public symbols in `__all__` should remain backward compatible; breaking changes require a major version bump.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k utils -v
```
