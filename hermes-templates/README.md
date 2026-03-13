# Hermes Instance Templates

Reference templates for spawning non-overlapping Hermes instances with consistent best-in-class settings. Default: 300 turns, hunter-alpha, technical personality.

## Quick Start

```bash
# From master template (~/.hermes)
~/.hermes/spawn-clone.sh my-agent-name "My custom personality" openrouter/hunter-alpha ~/work

# Batch spawn
~/.hermes/spawn-clone.sh --batch manifest.txt

# With preset
~/.hermes/template-sync.sh apply-preset ~/my-agent/.hermes researcher
```

Or manually: copy `config.yaml` + `.env.example` to `~/name/.hermes/`, customize, run `hermes doctor` to validate.

## Default Configuration

| Setting | Value |
|---------|-------|
| Model | `openrouter/hunter-alpha` |
| max_turns | `300` |
| reasoning_effort | `medium` |
| personality | `technical` |
| terminal.backend | `local` |
| compression | `enabled` at 85% |

## Required Inputs

| Input | Required | Source |
|-------|----------|--------|
| Instance name | Yes | Choose directory name |
| Model | Yes | OpenRouter model ID |
| OPENROUTER_API_KEY | Yes | Copy from main ~/.hermes/.env |
| Personality | Yes | Built-in or custom prompt |
| TELEGRAM_BOT_TOKEN | If Telegram | From @BotFather |
| TELEGRAM_ALLOWED_USERS | If Telegram | Username or "allow all" |
| TELEGRAM_HOME_CHANNEL | If Telegram | Channel name for outbound |

## Existing Instances

| Instance | HERMES_HOME | Model | Turns | Telegram |
|----------|-------------|-------|-------|----------|
| Main (template) | ~/.hermes | hunter-alpha | 300 | @ActiveInference |
| Crescent City | ~/hermes-crescent-city/.hermes | nemotron-free | 150 | configured |
| Template Bot | ~/hermes-template-bot/.hermes | hunter-alpha | 300 | @a_template_bot |

## Files

- `config.yaml` — Best-in-class defaults (300 turns, hunter-alpha, technical, compression)
- `.env.example` — All env vars with descriptions
- `QUESTIONS.md` — Full questionnaire for new instances
- `spawn.sh` — One-shot instance creation
- `config.crescent-city.yaml` — Reference config (civic analysis, free model)
- `GOTCHAS.md` — Known issues and fixes (CWD crash, launchd sharing, etc.)

## Mutation Presets

Apply specializations from the master template:
- `researcher` — Deep analysis, claude-sonnet-4, 300 turns
- `coder` — Software dev, hunter-alpha, 300 turns
- `writer` — Content creation, claude-sonnet-4, 300 turns
- `analyst` — Data analysis, hunter-alpha, 300 turns
- `assistant` — General purpose, hunter-alpha, 300 turns
- `monitor` — Periodic checks, nemotron-free, 200 turns
- `minimal` — Cost-optimized, nemotron-free, 150 turns

## Template Operations

All template operations live in `~/.hermes/`:
```bash
# Health check
~/.hermes/template-health.sh

# Validate clone
~/.hermes/validate-clone.sh <path>

# List instances
~/.hermes/template-sync.sh list

# Push/pull sync
~/.hermes/template-sync.sh push [path]
~/.hermes/template-sync.sh pull <path>
```

## Critical: Gateway Working Directory

Always start gateway with explicit working directory:
```bash
cd ~/my-project && HERMES_HOME=~/my-agent/.hermes hermes gateway run &
```
See GOTCHAS.md for why this matters.
