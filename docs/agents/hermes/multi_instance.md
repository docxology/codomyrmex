# Running Multiple Hermes Instances

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Overview

You can run multiple Hermes bots on the same machine, each with its own identity, personality, model, and platform connections. The key is giving each instance its own `HERMES_HOME` directory with unique bot tokens.

## Architecture

```text
Machine
├── ~/.hermes/                          (Instance 1: Primary)
│   ├── .env                            BOT_TOKEN=8626408153:AAFky...
│   ├── config.yaml                     model: nvidia/nemotron-3-super-120b-a12b:free
│   ├── state.db, sessions/, skills/
│   └── gateway.pid
│
├── ~/hermes-crescent-city/.hermes/     (Instance 2: Crescent City)
│   ├── .env                            BOT_TOKEN=8754235534:AAHFa...
│   ├── config.yaml                     personality: civic_analyst
│   ├── state.db, sessions/, skills/
│   └── gateway.pid
│
├── ~/hermes-template-bot/.hermes/      (Instance 3: Template Bot)
│   ├── .env                            BOT_TOKEN=unique_token_3
│   ├── config.yaml                     personality: template_architect
│   ├── state.db, sessions/, skills/
│   └── gateway.pid
│
└── ~/help/.hermes/                     (Instance 4: Help Bot)
    ├── .env                            BOT_TOKEN=unique_token_4
    ├── config.yaml                     personality: technical
    ├── state.db, sessions/, skills/
    └── gateway.pid
```

## Setup Steps

### 1. Create the Instance Directory

```bash
mkdir -p ~/hermes-bot2/.hermes/{logs,sessions,skills,memories,cron}
```

### 2. Create the `.env` File

```bash
cat > ~/hermes-bot2/.hermes/.env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
TELEGRAM_BOT_TOKEN=9876543210:AAxxxxxxxxxxxxxxx
TELEGRAM_ALLOWED_USERS=username1,username2
TELEGRAM_HOME_CHANNEL=username1
EOF
chmod 600 ~/hermes-bot2/.hermes/.env
```

### 3. Create `config.yaml`

```bash
cat > ~/hermes-bot2/.hermes/config.yaml << 'EOF'
model: nvidia/nemotron-3-super-120b-a12b:free
fallback_models:
- google/gemini-2.0-flash-001
- anthropic/claude-3-haiku
toolsets:
  - all
agent:
  max_turns: 150
  reasoning_effort: medium
  personality: my_custom_personality
  personalities:
    my_custom_personality: |
      You are a specialized assistant for...
terminal:
  backend: local
  timeout: 180
compression:
  enabled: true
  threshold: 0.85
  summary_model: google/gemini-2.0-flash-001
telegram:
  require_mention: true
  free_response_channels: ""
EOF
```

### 4. Test Manually

```bash
export HERMES_HOME=~/hermes-bot2/.hermes
hermes status    # verify config is loaded
hermes gateway run  # test that it connects
```

### 5. Install as launchd Service (macOS)

```bash
# Install and start the service (recommended — persists across reboots)
HERMES_HOME=~/hermes-bot2/.hermes hermes gateway install

# Or manually: see launchd.md for the plist template
```

The `hermes gateway install` command auto-generates the launchd plist, loads it, and
starts the service. The `--replace` flag is included automatically.

## Critical Rules

### One Bot Token = One Poller

Each Telegram bot token can only have **one** `getUpdates` poller. If two gateway processes use the same token, both get `409 Conflict` errors and neither receives messages reliably.

```text
✅ Instance 1: token_AAA → @bot_one
✅ Instance 2: token_BBB → @bot_two

❌ Instance 1: token_AAA → @bot_one
❌ Instance 2: token_AAA → @bot_one  ← CONFLICT!
```

### Shared Runtime, Separate Data

All instances share the same Python runtime at `~/.hermes/hermes-agent/venv/`. Only the **data directory** (`HERMES_HOME`) differs. This means:

- ✅ Updating Hermes updates all instances
- ⚠️ A bad Hermes update breaks all instances simultaneously

### PID File Isolation

Each instance writes its own `gateway.pid` in its `HERMES_HOME`. There is no conflict as long as `HERMES_HOME` is unique per instance.

### Session Storage

The gateway log may show `Session storage: /Users/mini/.hermes/sessions` even for non-primary instances. This is a known display issue — actual session data is stored in `$HERMES_HOME/state.db` and `$HERMES_HOME/sessions/` based on the resolved HERMES_HOME.

## Monitoring Multiple Instances

```bash
# Check all running gateways
ps aux | grep "hermes.*gateway" | grep -v grep

# Check launchd services
launchctl list | grep hermes

# Tail all logs simultaneously
tail -f ~/.hermes/logs/gateway.log \
        ~/hermes-crescent-city/.hermes/logs/gateway.log \
        ~/hermes-template-bot/.hermes/logs/gateway.log
```

## Troubleshooting

| Symptom                    | Cause                              | Fix                                   |
| :------------------------- | :--------------------------------- | :------------------------------------ |
| 409 Conflict errors        | Two instances using same bot token | Ensure unique tokens per instance     |
| "Gateway already running"  | Stale PID file                     | `HERMES_HOME=... hermes gateway stop` |
| Bot uses wrong personality | HERMES_HOME not set correctly      | Check env var in service definition   |
| Config changes not applied | Gateway not restarted              | `launchctl stop` then `start`         |

## Related Documents

- [launchd](launchd.md) — macOS service files
- [Telegram](telegram.md) — Bot token setup
- [Environment](environment.md) — HERMES_HOME reference
- [Troubleshooting](troubleshooting.md) — Common issues
- [skills.md](skills.md) — `.codomyrmex/` skill profile is per cwd, not per `HERMES_HOME`
