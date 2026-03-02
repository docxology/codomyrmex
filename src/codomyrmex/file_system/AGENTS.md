# File System Module AGENTS.md

## Directives
- **Zero-Mock Policy**: All unit tests for this module must interact with a real filesystem (use `pytest`'s `tmp_path` fixture). No `unittest.mock` for filesystem operations.
- **Path Handling**: Use `pathlib.Path` for all path-related logic. Avoid raw string manipulation for file paths.
- **Robustness**: Implement proper error handling (try-except) for all filesystem operations, especially for permissions and non-existent paths.
- **Logging**: Log all significant filesystem mutations (creates, deletes, moves) using the project's logging utility.
- **Documentation**: All public methods must include detailed docstrings with arguments, returns, and possible exceptions.

## Common Utilities
- Use `codomyrmex.utils.safe_json_loads` for JSON files.
- Prefer `shutil` for complex operations like recursive deletions or directory copies.
- Leverage `os.scandir` for efficient directory traversal in high-performance contexts.

## Maintenance
- Ensure the orchestrator script (`scripts/file_system/fs_utils.py`) is updated whenever the module's core API changes.
- Add performance benchmarks for large directory traversals if the module scales.
