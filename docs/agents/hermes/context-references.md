# @ Context References

**Version**: v2.5.0 | **Last Updated**: March 2026

## Overview

The `@` context reference syntax allows you to **inline file contents, git diffs, and web pages** directly into messages sent through the Hermes gateway. References are expanded before the message reaches the model.

---

## Syntax Reference

| Token | Expands To | Example |
|-------|-----------|---------|
| `@file:path` | File contents (fenced code block) | `@file:src/main.py` |
| `@file:path:L-R` | Lines L through R only | `@file:src/main.py:10-50` |
| `@file:path:L` | Single line L | `@file:config.yaml:42` |
| `@folder:path` | Directory tree listing | `@folder:src/` |
| `@diff` | `git diff` (unstaged changes) | `@diff` |
| `@staged` | `git diff --staged` | `@staged` |
| `@git:N` | `git log -N -p` (last N commits, max 10) | `@git:3` |
| `@url:https://...` | Web page content (Markdown) | `@url:https://docs.example.com/api` |

### Usage in Messages

```
What's wrong with this code? @file:src/gauss_runner.py
```

```
Compare my changes to the last commit: @diff @git:1
```

```
Summarize this RFC: @url:https://example.com/rfc-1234
```

---

## Token Budget

Injected content is measured in tokens before dispatch:

| Injected Tokens | Behaviour |
|-----------------|-----------|
| ≤ 25% of context window | Injected silently |
| 25%–50% of context window | Warning appended to message |
| > 50% of context window | **Blocked** — original message sent unchanged |

The hard limit (50%) is enforced to prevent context overflow. The soft limit (25%) is advisory.

Example warning message appended:
```
--- Context Warnings ---
- @ context injection warning: 32800 tokens exceeds the 25% soft limit (25000).
```

Example block:
```
--- Context Warnings ---
- @ context injection refused: 68000 tokens exceeds the 50% hard limit (50000).
```

When blocked, `ContextReferenceResult.blocked = True` and the original message is sent as-is.

---

## Expansion Output Format

Each expanded reference gets a labelled block:

```
📄 @file:src/main.py (892 tokens)
```python
def main():
    ...
```

📁 @folder:src/ (45 tokens)
src/
  - fep_topics.py (312 lines)
  - gauss_runner.py (201 lines)

🧾 git diff (1240 tokens)
```diff
+++ b/src/main.py
...
```

🌐 @url:https://example.com/api (720 tokens)
## API Reference
...
```

Blocks are appended after the user message, separated by `--- Attached Context ---`.

---

## File Reference Details

### Full File (`@file:path`)

- Path resolved relative to CWD; absolute paths accepted.
- Language of fenced code block inferred from extension (`.py` → `python`, `.yaml` → `yaml`, etc.).
- Binary files are rejected with a warning.

### Line Range (`@file:path:L-R`)

```
@file:src/main.py:10-50    # lines 10 to 50
@file:src/main.py:42       # line 42 only
```

Lines are 1-indexed and inclusive. Out-of-range lines are clamped.

### Folder Listing (`@folder:path`)

- Uses `rg --files` (ripgrep) when available for speed and gitignore awareness.
- Falls back to `os.walk` skipping `.` and `__pycache__` directories.
- Limited to 200 entries (appends `- ...` if truncated).
- Shows file sizes for text files (`N lines`) and binary files (`N bytes`).

---

## Git References

### `@diff` (unstaged changes)

Runs `git diff` in the CWD. Output wrapped in a `diff` code block.

### `@staged`

Runs `git diff --staged` in the CWD.

### `@git:N`

Runs `git log -N -p` (shows last N commits with patches). N is clamped to [1, 10].

---

## URL References (`@url:https://...`)

- Fetches via `web_extract_tool` (Markdown extraction).
- No authentication — only public URLs.
- Returns empty warning if no content extracted.
- Async-safe: runs in thread pool inside the gateway, `asyncio.run()` in CLI.

---

## Workspace Sandbox (`allowed_root`)

The gateway can restrict `@file` and `@folder` paths to a workspace:

```python
result = preprocess_context_references(
    message,
    cwd="/repo/src",
    context_length=128000,
    allowed_root="/repo"    # paths outside /repo → ValueError → warning
)
```

Attempts to reference files outside `allowed_root` produce a warning, not an error that aborts the message.

---

## Trailing Punctuation Stripping

Reference tokens are stripped of trailing punctuation before expansion:

```
@file:main.py,  → @file:main.py
@file:main.py.  → @file:main.py
```

Balanced parentheses/brackets are preserved:

```
(@file:main.py)  → @file:main.py  (outer parens stripped if unbalanced)
```

---

## Result Object (`ContextReferenceResult`)

```python
@dataclass
class ContextReferenceResult:
    message: str              # Final message with context appended
    original_message: str     # Original before expansion
    references: list[ContextReference]
    warnings: list[str]       # Token budget or access warnings
    injected_tokens: int      # Total tokens injected
    expanded: bool            # True if any block was injected
    blocked: bool             # True if hard limit exceeded
```

---

## Navigation

- [← Plugins](plugins.md)
- [Agent Cache →](agent-cache.md)
- [← Hermes SPEC](../../../src/codomyrmex/agents/hermes/SPEC.md)
