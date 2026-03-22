# Hermes Instance Templates

Reference templates for spawning non-overlapping Hermes instances with consistent best-in-class settings. Default: 300 turns, hunter-alpha, technical personality.

**Source in Codomyrmex**: `src/codomyrmex/agents/hermes/instance_templates/`
**Spawn script**: `src/codomyrmex/agents/hermes/scripts/spawn_instance.sh`

## Quick Start

```bash
# One-shot instance creation
src/codomyrmex/agents/hermes/scripts/spawn_instance.sh my-agent-name "My custom personality" openrouter/hunter-alpha ~/work

# Or manually: copy config.template.yaml + .env.example to ~/name/.hermes/
# customize, then run hermes doctor to validate
```

## Default Configuration

| Setting | Value |
|---------|-------|
| Model | `nvidia/nemotron-3-nano-30b-a3b:free` |
| max\_turns | `300` |
| reasoning\_effort | `high` |
| personality | `technical` |
| terminal.backend | `local` |
| compression | `enabled` at 90% |

## Required Inputs

| Input | Required | Source |
|-------|----------|--------|
| Instance name | Yes | Choose directory name |
| Model | Yes | OpenRouter model ID |
| OPENROUTER\_API\_KEY | Yes | Copy from main ~/.hermes/.env |
| Personality | Yes | Built-in or custom prompt |
| TELEGRAM\_BOT\_TOKEN | If Telegram | From @BotFather |
| TELEGRAM\_ALLOWED\_USERS | If Telegram | Username or "allow all" |
| TELEGRAM\_HOME\_CHANNEL | If Telegram | Channel name for outbound |

## Existing Instances

See [instances.md](instances.md) for full status of all active instances.

## Files in `instance_templates/`

| File | Purpose |
|------|---------|
| `config.template.yaml` | Best-in-class defaults (config version 10) |
| `.env.example` | All env vars with descriptions |
| `config.crescent-city.yaml` | Reference config (civic analysis, free model) |
| `hermes_example.py` | Python hermes\_tools usage example |
| `SOUL.md` | Hermes persona definition |

## Mutation Presets

Apply specializations from the spawner:

- `researcher` — Deep analysis, claude-sonnet-4, 300 turns
- `coder` — Software dev, hunter-alpha, 300 turns
- `writer` — Content creation, claude-sonnet-4, 300 turns
- `analyst` — Data analysis, hunter-alpha, 300 turns
- `assistant` — General purpose, hunter-alpha, 300 turns
- `monitor` — Periodic checks, nemotron-free, 200 turns
- `minimal` — Cost-optimized, nemotron-free, 150 turns

## Critical: Gateway Working Directory

Always start gateway with explicit working directory:

```bash
cd ~/my-project && HERMES_HOME=~/my-agent/.hermes hermes gateway run &
```

See [gotchas.md](gotchas.md) for why this matters.

## Navigation

- **Source templates**: [src/codomyrmex/agents/hermes/instance\_templates/](../../../src/codomyrmex/agents/hermes/instance_templates/)
- **Spawn script**: [scripts/spawn\_instance.sh](../../../src/codomyrmex/agents/hermes/scripts/spawn_instance.sh)
- **Active instances**: [instances.md](instances.md)
- **Gotchas**: [gotchas.md](gotchas.md)
- **Hermes README**: [README.md](README.md)
