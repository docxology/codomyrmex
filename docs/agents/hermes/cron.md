# Hermes Cron & Scheduling

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Overview

Hermes includes a built-in cron scheduler that runs within the gateway process. It enables periodic automated tasks with results delivered to any connected platform (Telegram, WhatsApp, etc.).

## How It Works

### Cron Ticker

The gateway starts a background cron ticker with a 60-second interval:

```text
gateway.run: Cron ticker started (interval=60s)
```

Every 60 seconds, the ticker checks for due jobs and spawns isolated agent executions for each.

### Job Lifecycle

```text
Cron Ticker (60s interval)
  │
  ├── Check schedule for due jobs
  │
  ├── For each due job:
  │   ├── Spawn AIAgent with job prompt
  │   ├── Agent processes with full tool access
  │   └── Result delivered to target platform
  │
  └── Next tick
```

## Configuration

Jobs are stored in `$HERMES_HOME/cron/` as YAML files. The `cron/scheduler.py` manages
the ticker, and `cron/jobs.py` handles job loading, validation, and execution (both expanded
significantly in the v0.3.0 update).

```yaml
# $HERMES_HOME/cron/daily_summary.yaml
schedule: "0 9 * * *"      # cron expression: daily at 9:00 AM
prompt: "Summarize overnight activity and pending tasks"
target: telegram_user123    # delivery target (Telegram username or channel)
enabled: true               # toggle without deleting the file
timezone: America/Los_Angeles  # job-level timezone override
max_turns: 20               # limit turn count for cron agents
```

### Cron Expression Format

Standard 5-field cron format: `minute hour day month weekday`

```
*  *  *  *  *
│  │  │  │  │
│  │  │  │  └── Day of week (0-7, 0 and 7 = Sunday)
│  │  │  └───── Month (1-12)
│  │  └──────── Day of month (1-31)
│  └─────────── Hour (0-23)
└────────────── Minute (0-59)
```

**Examples**:

- `0 9 * * *` — Daily at 9:00 AM
- `*/30 * * * *` — Every 30 minutes
- `0 9 * * 1-5` — Weekdays at 9:00 AM
- `0 0 1 * *` — First of each month at midnight

## Delivery Targets

Cron job results are delivered to the platform/channel specified by `TELEGRAM_HOME_CHANNEL` (or equivalent for other platforms).

```bash
# .env
TELEGRAM_HOME_CHANNEL=ActiveInference   # cron results go here
```

## CLI Commands

```bash
hermes cron list          # list all scheduled jobs with next-run times
hermes cron status        # show cron system status (enabled jobs, next tick)
hermes cron tick          # manually trigger a cron tick (run all due jobs now)
```

Jobs can also be created and edited via natural language inside a chat session:

```
User: Schedule a daily 9am summary of my outstanding tasks
Hermes: Created cron job: daily_summary.yaml → runs at 09:00 America/Los_Angeles
```

## Monitoring

```bash
# Check cron status
HERMES_HOME=... hermes status
# Output shows: Jobs: 2 active, 2 total

# View cron execution in gateway logs
grep "cron" $HERMES_HOME/logs/gateway.log
```

## Related Documents

- [Gateway](gateway.md) — Gateway and ticker architecture
- [Tools](tools.md) — `cronjob_tools.py`
- [skills.md](skills.md) — Codomyrmex skill preload for scheduled / scripted Hermes use
