# Personal AI Infrastructure — Utils Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Utilities Package. This is an **Extended Layer** module.

## PAI Capabilities

```python
from codomyrmex.utils import ScriptBase, ScriptConfig, ScriptResult, ensure_directory, safe_json_loads, safe_json_dumps
```

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `ensure_directory` | Function/Constant | Ensure directory |
| `safe_json_loads` | Function/Constant | Safe json loads |
| `safe_json_dumps` | Function/Constant | Safe json dumps |
| `hash_content` | Function/Constant | Hash content |
| `hash_file` | Function/Constant | Hash file |
| `timing_decorator` | Function/Constant | Timing decorator |
| `retry` | Function/Constant | Retry |
| `get_timestamp` | Function/Constant | Get timestamp |
| `truncate_string` | Function/Constant | Truncate string |
| `get_env` | Function/Constant | Get env |
| `flatten_dict` | Function/Constant | Flatten dict |
| `deep_merge` | Function/Constant | Deep merge |
| `ScriptBase` | Class | Scriptbase |
| `ScriptConfig` | Class | Scriptconfig |
| `ScriptResult` | Class | Scriptresult |

*Plus 28 additional exports.*


## PAI Algorithm Phase Mapping

| Phase | Utils Contribution |
|-------|————————————————————|
| **OBSERVE** | Data gathering and state inspection |
| **EXECUTE** | Execution and deployment |
| **VERIFY** | Validation and quality checks |
| **LEARN** | Learning and knowledge capture |

## Architecture Role

**Extended Layer** — Part of the codomyrmex layered architecture.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
