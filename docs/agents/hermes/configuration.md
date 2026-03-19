# Hermes Configuration Reference

**Version**: v0.3.0 | **Last Updated**: March 2026 (73-commit update)

## Overview

Hermes configuration lives in `$HERMES_HOME/config.yaml`. This file controls model selection, agent behavior, tool availability, platform connections, and context compression.

## Complete `config.yaml` Reference

```yaml
# =============================================================================
# Model / Provider
# =============================================================================
model: nousresearch/hermes-3-llama-3.1-405b-instruct:free
provider: openrouter   # openrouter | nous | zai | kimi-coding | minimax
fallback_models:
  - meta-llama/llama-3.1-70b-instruct:free
  - google/gemini-2.0-flash:free

# =============================================================================
# Toolsets
# =============================================================================
toolsets:
  - all   # enable all tool categories

# =============================================================================
# Agent behavior & personalities
# =============================================================================
agent:
  max_turns: 150           # max tool-calling turns per conversation
  verbose: false           # show internal reasoning in logs
  reasoning_effort: medium # low | medium | high
  personality: helpful     # active personality name (must exist below)
  personalities:
    helpful: You are a helpful, friendly AI assistant.
    technical: You are a technical expert. Provide detailed, accurate information.

# =============================================================================
# Terminal backend
# =============================================================================
terminal:
  backend: local           # local | docker | ssh | daytona | singularity | modal
  cwd: .                   # working directory for commands
  timeout: 180             # command timeout in seconds

# =============================================================================
# Context compression
# =============================================================================
compression:
  enabled: true
  threshold: 0.85          # compress when context reaches 85% of model limit
  summary_model: google/gemini-2.0-flash
  summary_provider: auto

# =============================================================================
# Smart Model Routing (v0.3.0)
# Route short/simple messages to a cheap model
# =============================================================================
smart_model_routing:
  enabled: false
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model:
    provider: openrouter
    model: google/gemini-2.0-flash

# =============================================================================
# Security (v0.3.0)
# =============================================================================
security:
  redact_secrets: true     # mask API keys in logs/responses
  tirith_enabled: true     # enable Tirith policy engine
  tirith_path: tirith      # path to tirith binary
  tirith_timeout: 5        # timeout in seconds before fail-open
  tirith_fail_open: true   # allow if Tirith times out
  website_blocklist:
    enabled: false
    domains: []

# =============================================================================
# Session auto-reset
# =============================================================================
session_reset:
  mode: both               # off | idle | daily | both
  idle_minutes: 1440       # reset after N minutes of inactivity
  at_hour: 3               # daily reset at this hour (local time)

# =============================================================================
# Display
# =============================================================================
display:
  compact: false
  personality: technical   # display personality name
  resume_display: full     # full | compact
  bell_on_complete: false
  show_reasoning: true
  streaming: false
  show_cost: false
  skin: default            # default | minimal | rich
  tool_progress: all       # all | errors | none
  background_process_notifications: all

# =============================================================================
# Delegation (subagent spawning)
# =============================================================================
delegation:
  model: ""                # override model for subagents
  provider: ""
  max_iterations: 75
  default_toolsets:
    - terminal
    - file
    - web

# =============================================================================
# Telegram platform
# =============================================================================
telegram:
  require_mention: true    # only respond when @mentioned
  free_response_channels: "" # channel IDs for auto-response (empty = none)

# =============================================================================
# Approvals
# =============================================================================
approvals:
  mode: manual             # manual | auto | off
```

## Critical YAML Pitfalls

### Duplicate Top-Level Keys

YAML silently overwrites duplicate keys. The **last** occurrence wins.

```yaml
# ❌ BAD: second agent: block silently overwrites the first
agent:
  max_turns: 150
  personality: technical

agent:
  personalities:
    technical: You are a technical expert.
# Result: max_turns and personality are LOST
```

```yaml
# ✅ GOOD: single agent: block with all settings
agent:
    max_turns: 150
    personality: technical
    personalities:
        technical: You are a technical expert.
```

> **Lesson learned**: Always validate your YAML after editing. Use `python3 -c "import yaml; print(yaml.safe_load(open('config.yaml')))"` to see what the parser actually reads.

### Unicode in Comments

Hermes config files may contain non-breaking hyphens (`‑`, U+2011) in comments if copy-pasted from documentation. These are valid YAML but can cause confusion when grepping or diffing.

### String Quoting

For personalities with special characters, use YAML block scalars:

```yaml
# ✅ Use | for multi-line strings
personality_name: |
  Line one of the personality.
  Line two with "quotes" and special chars.

# ✅ Use > for folded (single-line) strings
personality_name: >
  This all becomes
  one long line.
```

## Configuration Load Order

1. `hermes_cli/config.py` resolves `HERMES_HOME` from environment
2. `$HERMES_HOME/.env` loaded via `python-dotenv` → sets environment variables
3. `$HERMES_HOME/config.yaml` parsed → merges with defaults
4. `.env` values **override** corresponding `config.yaml` inline values

## Validation

```bash
# Parse and pretty-print the effective config
python3 -c "
import yaml
with open('$HERMES_HOME/config.yaml') as f:
    data = yaml.safe_load(f)
import json
print(json.dumps(data, indent=2))
"

# Check for duplicate keys
yamllint $HERMES_HOME/config.yaml

# Full diagnostics
hermes doctor
```

## Codomyrmex `HermesClient` (not `config.yaml`)

Hermes’s **`$HERMES_HOME/config.yaml`** does not define Codomyrmex’s skill preload pipeline. For **project skill profiles**, **bundled skill id registry**, **`CODOMYRMEX_SKILLS_REGISTRY`**, and **`HermesClient`** constructor keys (`hermes_default_skill_ids`, `hermes_default_hermes_skills`, `hermes_skill_profile_disable`), see [skills.md](skills.md) and [environment.md](environment.md).

## Related Documents

- [Environment Variables](environment.md) — `.env` and `HERMES_HOME`
- [Models](models.md) — Model selection and OpenRouter
- [Personalities](personalities.md) — Custom persona definitions
- [skills.md](skills.md) — Unified skill registry, merge order, MCP skill tools
- [codomyrmex_integration.md](codomyrmex_integration.md) — Full MCP surface (48 tools)
