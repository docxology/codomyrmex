# Hermes Instance Templates

Reference templates for spawning non-overlapping Hermes instances with consistent best-in-class settings.

## Quick Start

```bash
./spawn.sh my-agent-name "My custom personality description"
```

Or manually: copy `config.yaml` + `.env.example` to `~/name/.hermes/`, customize, run `hermes doctor` to validate.

## Required Inputs for Telegram-Connected Instance

| Input | Required | Source |
|-------|----------|--------|
| Instance name | Yes | Choose directory name |
| Model | Yes | OpenRouter model ID |
| OPENROUTER_API_KEY | Yes | Copy from main ~/.hermes/.env |
| Personality | Yes | Built-in (technical/concise/researcher) or custom prompt |
| TELEGRAM_BOT_TOKEN | If Telegram | From @BotFather |
| TELEGRAM_ALLOWED_USERS | If Telegram | Username or "allow all" |
| TELEGRAM_HOME_CHANNEL | If Telegram | Channel name for outbound |

## Existing Instances

| Instance | HERMES_HOME | Model | Telegram | Gateway PID |
|----------|-------------|-------|----------|-------------|
| Main | ~/.hermes | openrouter/hunter-alpha | @ActiveInference | 7078 |
| Crescent City | ~/hermes-crescent-city/.hermes | nemotron-free | configured | 6801 |
| Template Bot | ~/hermes-template-bot/.hermes | openrouter/hunter-alpha | @a_template_bot | 25577 |

## Files

- `config.yaml` — Best-in-class defaults (hunter-alpha, technical personality, compression, all toolsets)
- `.env.example` — All env vars with descriptions
- `QUESTIONS.md` — Full questionnaire for new instances
- `spawn.sh` — One-shot instance creation
- `config.crescent-city.yaml` — Reference config (civic analysis, free model)
- `GOTCHAS.md` — Known issues and fixes (CWD crash, launchd sharing, etc.)

## Critical: Gateway Working Directory

Always start gateway with explicit working directory:
```bash
cd ~/my-project && HERMES_HOME=~/my-agent/.hermes hermes gateway run &
```
See GOTCHAS.md for why this matters.
