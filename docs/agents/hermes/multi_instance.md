# Running Multiple Hermes Instances

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

You can run multiple Hermes bots on the same machine, each with its own identity, personality, model, and platform connections. The key is giving each instance its own `HERMES_HOME` directory with unique bot tokens.

## Architecture

```
Machine
├── ~/.hermes/                          (Instance 1: Primary)
│   ├── .env                            BOT_TOKEN=1111...
│   ├── config.yaml                     personality: helpful
│   ├── state.db, sessions/, skills/
│   └── gateway.pid
│
├── ~/hermes-crescent-city/.hermes/     (Instance 2: Crescent City)
│   ├── .env                            BOT_TOKEN=2222...
│   ├── config.yaml                     personality: civic_analyst
│   ├── state.db, sessions/, skills/
│   └── gateway.pid
│
└── ~/hermes-research/.hermes/          (Instance 3: Research)
    ├── .env                            BOT_TOKEN=3333...
    ├── config.yaml                     personality: researcher
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
  summary_model: google/gemini-3-flash-preview
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

### 5. Create a Service (macOS)

See [launchd.md](launchd.md) for the complete plist template.

## Critical Rules

### One Bot Token = One Poller

Each Telegram bot token can only have **one** `getUpdates` poller. If two gateway processes use the same token, both get `409 Conflict` errors and neither receives messages reliably.

```
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
tail -f ~/.hermes/logs/gateway.log ~/hermes-bot2/.hermes/logs/gateway.log
```

## Troubleshooting

| Symptom | Cause | Fix |
|:---|:---|:---|
| 409 Conflict errors | Two instances using same bot token | Ensure unique tokens per instance |
| "Gateway already running" | Stale PID file | `HERMES_HOME=... hermes gateway stop` |
| Bot uses wrong personality | HERMES_HOME not set correctly | Check env var in service definition |
| Config changes not applied | Gateway not restarted | `launchctl stop` then `start` |

## Related Documents

- [launchd](launchd.md) — macOS service files
- [Telegram](telegram.md) — Bot token setup
- [Environment](environment.md) — HERMES_HOME reference
- [Troubleshooting](troubleshooting.md) — Common issues
