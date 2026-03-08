# agents/openfang — Specification

## Architecture

```
┌─────────────────────────────────────────────────┐
│  MCP layer (mcp_tools.py)                        │
│  7 @mcp_tool functions with import guards        │
├─────────────────────────────────────────────────┤
│  Core layer (core.py)                            │
│  OpenFangRunner: subprocess → openfang binary    │
├─────────────────────────────────────────────────┤
│  Config layer (config.py)                        │
│  OpenFangConfig: all values from os.getenv()     │
├─────────────────────────────────────────────────┤
│  Vendor layer (vendor/openfang/)                 │
│  git submodule → github.com/RightNow-AI/openfang │
└─────────────────────────────────────────────────┘
```

## Design Decisions

### Subprocess over FFI

openfang is a rapidly-evolving Rust codebase. Using the CLI binary via subprocess
future-proofs against internal API churn — only the CLI contract matters, not
Rust internals. This matches the aider and soul integration patterns.

### Git submodule for upstream tracking

`vendor/openfang/` is a git submodule pointing to the upstream repository.
This allows:
- `git submodule update --remote` to fetch the latest commits
- `cargo build --release` to compile from pinned source
- Explicit version pinning via submodule SHA

### Feature flag at import time

`HAS_OPENFANG = shutil.which("openfang") is not None` runs once at module import.
MCP tools check this flag before attempting subprocess calls, returning structured
error dicts rather than raising exceptions at the tool boundary.

## Configuration Schema

| Field | Type | Env var | Default |
|-------|------|---------|---------|
| `command` | str | `OPENFANG_COMMAND` | `"openfang"` |
| `timeout` | int | `OPENFANG_TIMEOUT` | `120` |
| `gateway_url` | str | `OPENFANG_GATEWAY_URL` | `"ws://localhost:3000"` |
| `vendor_dir` | str | — | `<module>/vendor/openfang` |
| `install_dir` | str | `OPENFANG_INSTALL_DIR` | `"/usr/local/bin"` |

## CLI Command Coverage

| OpenFangRunner method | CLI command |
|----------------------|-------------|
| `execute(prompt)` | `openfang agent --message <prompt>` |
| `stream(prompt)` | `openfang agent --message <prompt> --stream` |
| `hands_list()` | `openfang hands list` |
| `hands_run(name)` | `openfang hands run <name>` |
| `send_message(ch, to, msg)` | `openfang message send --channel --to --message` |
| `gateway_action(action)` | `openfang gateway <start|stop|status>` |
| `doctor()` | `openfang doctor` |
| `version()` | `openfang --version` |

## Return Shape

All public `OpenFangRunner` methods and MCP tools return `dict[str, str | Any]`:

```python
# Success from runner:
{"stdout": str, "stderr": str, "returncode": str}

# Success from MCP tool:
{"status": "success", "stdout": str, "stderr": str, "returncode": str}

# Error from MCP tool:
{"status": "error", "message": str}
```

## Build Pipeline

```
update_submodule()    → git submodule update --remote --merge
build_from_source()   → cargo build --release in vendor/openfang/
install_binary()      → shutil.copy2(target/release/openfang → install_dir)
build_and_install()   → build_from_source() + install_binary()
```

## Version Strategy

- Module version: `__version__ = "1.0.0"` in `__init__.py`
- Upstream tracking: git SHA via `get_upstream_version()`
- Binary version: `openfang --version` via `get_openfang_version()`

## Test Coverage

6 test files, ~145 tests:
- `test_openfang_exceptions.py` — hierarchy, messages, raise/catch
- `test_openfang_config.py` — defaults, env overrides, properties
- `test_openfang_core.py` — runner init, binary detection, version
- `test_openfang_hands.py` — parse_list_output, Hand dataclass
- `test_openfang_update.py` — error paths, filesystem edge cases
- `test_openfang_mcp_tools.py` — return shapes, guards, all 7 tools
