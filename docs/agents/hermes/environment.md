# Hermes Environment & API Keys

**Version**: v0.2.0 | **Last Updated**: March 2026

## HERMES_HOME

The `HERMES_HOME` environment variable is the single most important configuration knob. It determines where Hermes reads **all** its data from.

### Resolution

```python
# hermes_cli/config.py, line 37
return Path(os.getenv("HERMES_HOME", Path.home() / ".hermes"))
```

### What It Controls

| Path | Purpose |
|:---|:---|
| `$HERMES_HOME/.env` | API keys and secrets |
| `$HERMES_HOME/config.yaml` | Agent configuration |
| `$HERMES_HOME/state.db` | SQLite session/memory database |
| `$HERMES_HOME/sessions/` | Session JSON backups |
| `$HERMES_HOME/skills/` | Loaded skills |
| `$HERMES_HOME/memories/` | Agent memory storage |
| `$HERMES_HOME/logs/` | Gateway and error logs |
| `$HERMES_HOME/cron/` | Scheduled job definitions |
| `$HERMES_HOME/gateway.pid` | Gateway process ID file |

### Setting HERMES_HOME

```bash
# Shell export (temporary)
export HERMES_HOME=~/my-custom-bot/.hermes
hermes gateway run

# Persistent via launchd (macOS)
# See launchd.md for plist configuration

# Persistent via systemd (Linux)
# See the systemd section in multi_instance.md
```

## .env File Reference

The `.env` file in `$HERMES_HOME/` is loaded via `python-dotenv` at startup.

### Required Keys

```bash
# LLM Provider — at least one required
OPENROUTER_API_KEY=sk-or-v1-...   # OpenRouter (recommended, access to many models)
```

### Platform Keys

```bash
# Telegram
TELEGRAM_BOT_TOKEN=1234567890:AAxxxxxxxxxxxxxxxxx
TELEGRAM_ALLOWED_USERS=username1,username2   # comma-separated Telegram usernames
TELEGRAM_HOME_CHANNEL=channel_name           # for cron/proactive messages

# WhatsApp
WHATSAPP_ENABLED=false

# Discord
DISCORD_TOKEN=...

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Email
EMAIL_ADDRESS=bot@example.com
EMAIL_PASSWORD=...
```

### Optional Service Keys

```bash
# Additional LLM providers
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...

# Tool integrations
# FIRECRAWL_API_KEY=...        # web scraping
# FAL_KEY=...                   # image generation
# BROWSERBASE_API_KEY=...       # browser automation
# VOICE_TOOLS_OPENAI_KEY=...    # TTS/STT
# GITHUB_TOKEN=ghp_...          # GitHub access
# WANDB_API_KEY=...             # experiment tracking
# HONCHO_API_KEY=...            # user modeling
```

## Security Best Practices

1. **Never commit `.env` files** — add to `.gitignore`
2. **Use restrictive permissions** — `chmod 600 $HERMES_HOME/.env`
3. **Rotate keys periodically** — especially after any suspected leak
4. **Use `TELEGRAM_ALLOWED_USERS`** — always restrict who can interact with the bot
5. **Separate keys per instance** — each bot instance should have unique API keys where possible

## Common Issues

### .env Not Being Loaded

If the gateway starts but uses wrong credentials, verify:
```bash
# Check which HERMES_HOME is active
echo $HERMES_HOME

# Verify .env exists in the right place
cat $HERMES_HOME/.env | head -5

# Check from Python's perspective
python3 -c "
import os
from pathlib import Path
home = Path(os.getenv('HERMES_HOME', Path.home() / '.hermes'))
print(f'HERMES_HOME: {home}')
print(f'.env exists: {(home / \".env\").exists()}')
"
```

### launchd Doesn't Inherit Shell Variables

The `HERMES_HOME` export in your `.zshrc` is **not** available to launchd services. You must set it explicitly in the plist file's `EnvironmentVariables` section. See [launchd.md](launchd.md).

## Related Documents

- [Configuration](configuration.md) — `config.yaml` reference
- [Multi-Instance](multi_instance.md) — Running multiple bots
- [Security](security.md) — API key hygiene
- [launchd](launchd.md) — macOS service management
