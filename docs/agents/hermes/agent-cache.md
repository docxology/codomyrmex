# Gateway Agent Cache

**Version**: v2.5.0 | **Last Updated**: March 2026

## Overview

The Hermes gateway (`GatewayRunner`) maintains a per-session **AIAgent cache** to avoid rebuilding agents on every incoming message. This significantly reduces latency for multi-turn conversations and preserves the frozen system prompt across turns.

---

## Architecture

```
Message arrives (session_key = "telegram:12345")
    │
    ├── Compute config_signature = MD5(model + base_url + provider + toolsets + sys_prompt)
    │
    ├── Look up _agent_cache[session_key]
    │       ├── Hit AND signature matches → reuse cached agent (fast path)
    │       └── Miss OR signature mismatch → build new AIAgent → store in cache
    │
    ├── Update per-message state (no eviction):
    │       ├── agent.reasoning_config = {…}
    │       ├── agent.tool_progress_callback = cb
    │       ├── agent.step_callback = cb
    │       └── agent.stream_delta_callback = cb
    │
    └── run_conversation(agent, message)
```

---

## Config Signature

The cache key combines two components:
- **`session_key`**: platform + user ID (e.g., `"telegram:12345"`, `"discord:99001:987654"`)
- **`config_signature`**: MD5 hash of `(model, base_url, provider, sorted_toolsets, system_prompt)`

```python
# Pseudocode of GatewayRunner._agent_config_signature
import hashlib, json

def _agent_config_signature(model, runtime, toolsets, system_prompt):
    key_data = {
        "model": model,
        "base_url": runtime.get("base_url", ""),
        "provider": runtime.get("provider", ""),
        "toolsets": sorted(toolsets),
        "system_prompt": system_prompt,
    }
    return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
```

> **Reasoning config is NOT part of the signature.** It is updated in-place (see below).

---

## Cache Lifecycle

### Cache Hit (fast path)

When a message arrives with the same config as the previous message in that session:

1. Look up `_agent_cache[session_key]`
2. Compare stored signature with new signature → match
3. **Reuse cached agent** — system prompt NOT rebuilt
4. Update per-message callbacks and reasoning config

Benefit: system prompt computation (which may involve skills resolution, template rendering, etc.) is skipped entirely.

### Cache Miss (build path)

When config changes (model, provider, toolsets):

1. Build a fresh `AIAgent` with new config
2. Store in cache: `runner._agent_cache[session_key] = (agent, new_sig)`
3. Previous agent is dropped (garbage collected)

### In-Place Updates (no eviction)

These fields are updated per-message on the cached agent **without** rebuilding:

| Field | Updated When |
|-------|-------------|
| `reasoning_config` | Model send reasoning settings change |
| `tool_progress_callback` | Per-message gateway callback |
| `step_callback` | Per-message gateway callback |
| `stream_delta_callback` | Per-message gateway callback |
| `status_callback` | Per-message gateway callback |

### Eviction Triggers

| Trigger | Action |
|---------|--------|
| User sends `/reset` | `_evict_cached_agent(session_key)` |
| Fallback provider activated | `_evict_cached_agent(session_key)` |
| Model/provider/toolset changes | Implicit eviction (signature mismatch → new agent stored) |

Eviction removes the session from `_agent_cache`:
```python
def _evict_cached_agent(self, session_key: str) -> None:
    with self._agent_cache_lock:
        self._agent_cache.pop(session_key, None)
```

---

## Thread Safety

```python
class GatewayRunner:
    def __init__(self, ...):
        self._agent_cache: dict[str, tuple[AIAgent, str]] = {}
        self._agent_cache_lock = threading.Lock()
```

All reads and writes use `with self._agent_cache_lock`. This ensures safe concurrent access from asyncio tasks dispatching to multiple sessions simultaneously.

---

## Frozen System Prompt

Once an agent is built and cached, its `_cached_system_prompt` is set on the first `run_conversation` call and **not rebuilt on subsequent turns** unless the agent is evicted.

This means:
- Skill files are resolved once per session (not per message)
- System prompt template is rendered once
- Context files are loaded once

**Implication**: if skills or templates change mid-session, the agent must be evicted to pick up changes.

---

## Reasoning Config Updates In-Place

A key insight: `reasoning_config` (e.g., `{"enabled": True, "effort": "high"}`) changes per-message based on user preferences or model routing. Rather than evicting the agent (which would rebuild the system prompt), reasoning config is updated directly:

```python
# Gateway per-message path
cached_agent.reasoning_config = new_reasoning_config  # no eviction
```

System prompt rebuild is NOT triggered by reasoning changes.

---

## Cache Storage

The cache is an **in-memory dict** — it is not persisted to disk. On gateway restart, all sessions start fresh. This is intentional: the cache is a performance optimization, not a state store.

---

## Disabling the Cache

If you need to force a fresh agent on every message (e.g., debugging tool resolution issues):

```yaml
# config.yaml
gateway_agent_cache_enabled: false
```

With the cache disabled, every message builds a new `AIAgent`. This is significantly slower but ensures fresh state.

---

## Navigation

- [← Context References](context-references.md)
- [← Plugins](plugins.md)
- [← Hermes SPEC](../../../src/codomyrmex/agents/hermes/SPEC.md)
