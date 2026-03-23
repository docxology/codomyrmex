# Hermes Environment & API Keys

**Version**: v0.4.0 | **Last Updated**: March 2026 (v0.4.0 update)

## HERMES_HOME

The `HERMES_HOME` environment variable is the single most important configuration knob. It determines where Hermes reads **all** its data from.

### Resolution

```python
# hermes_cli/config.py, line 37
return Path(os.getenv("HERMES_HOME", Path.home() / ".hermes"))
```

### What It Controls

| Path                       | Purpose                        |
| :------------------------- | :----------------------------- |
| `$HERMES_HOME/.env`        | API keys and secrets           |
| `$HERMES_HOME/config.yaml` | Agent configuration            |
| `$HERMES_HOME/state.db`    | SQLite session/memory database |
| `$HERMES_HOME/sessions/`   | Session JSON backups           |
| `$HERMES_HOME/skills/`     | Loaded skills                  |
| `$HERMES_HOME/memories/`   | Agent memory storage           |
| `$HERMES_HOME/logs/`       | Gateway and error logs         |
| `$HERMES_HOME/cron/`       | Scheduled job definitions      |
| `$HERMES_HOME/gateway.pid` | Gateway process ID file        |

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
TELEGRAM_ALLOWED_USERS=username1,username2  # Legacy — prefer pairing/telegram-approved.json (see telegram.md)
TELEGRAM_HOME_CHANNEL=channel_name          # for cron/proactive messages

# Gateway — multi-platform authorization (v0.4.0)
GATEWAY_ALLOWED_USERS=123456789,987654321  # cross-platform trusted IDs
GATEWAY_ALLOW_ALL_USERS=false              # true = open access (private deployments only)

# WhatsApp (via Baileys bridge)
WHATSAPP_ENABLED=false

# Discord
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_ALLOWED_USER_IDS=123456789,987654321  # optional allow-list of user IDs

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Email
EMAIL_ADDRESS=bot@example.com
EMAIL_PASSWORD=...
```

### LLM Provider Keys

```bash
OPENROUTER_API_KEY=sk-or-v1-...   # OpenRouter (recommended)
ANTHROPIC_API_KEY=sk-ant-...      # Direct Anthropic (BYOK)
OPENAI_API_KEY=sk-...             # Direct OpenAI (BYOK)
ZAI_API_KEY=...                   # Z.AI / GLM
KIMI_API_KEY=...                  # Kimi / Moonshot
MINIMAX_API_KEY=...               # MiniMax
```

### Copilot ACP Keys (v0.3.0)

```bash
# GitHub Copilot ACP backend
HERMES_COPILOT_ACP_COMMAND=copilot    # path to copilot binary (default: copilot)
COPILOT_CLI_PATH=~/.local/bin/copilot # alternative path
HERMES_COPILOT_ACP_ARGS=--acp --stdio # override default CLI args
GITHUB_TOKEN=ghp_...                  # GitHub auth token (set by hermes copilot login)
```

### Codomyrmex Hermes skill registry (optional)

When driving Hermes through **Codomyrmex** (`HermesClient` or MCP), you can extend the bundled skill id registry with extra YAML:

```bash
# Path to additional registry YAML (same shape as bundled skills_registry.yaml)
CODOMYRMEX_SKILLS_REGISTRY=/path/to/extra_skills_registry.yaml
```

Project defaults use **`.codomyrmex/hermes_skills_profile.yaml`** discovered from the process **current working directory** (walk upward). That path is independent of `HERMES_HOME`. Full merge order and client keys: [skills.md](skills.md).

### Optional Service Keys

```bash
# Web & browser tools
# FIRECRAWL_API_KEY=...        # web scraping
# TAVILY_API_KEY=...           # web search
# BROWSERBASE_API_KEY=...      # browser automation

# Media & generation
# FAL_KEY=...                  # image generation

# Voice / STT / TTS
# GROQ_API_KEY=...             # Groq Whisper STT (free tier)
# VOICE_TOOLS_OPENAI_KEY=...   # OpenAI TTS/STT
# ELEVENLABS_API_KEY=...       # ElevenLabs TTS
# FISH_AUDIO_API_KEY=...       # Fish Audio TTS

# Other integrations
# WANDB_API_KEY=...            # experiment tracking (W&B)
# HONCHO_API_KEY=...           # user modeling (Honcho)
# TINKER_API_KEY=...           # Tinker tool
```

## Security Best Practices

1. **Never commit `.env` files** — add to `.gitignore`
2. **Use restrictive permissions** — `chmod 600 $HERMES_HOME/.env`
3. **Rotate keys periodically** — especially after any suspected leak
4. **Use the pairing system** — add authorized Telegram numeric IDs to `$HERMES_HOME/pairing/telegram-approved.json` (see [telegram.md](telegram.md)); avoid relying solely on `TELEGRAM_ALLOWED_USERS`
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
- [skills.md](skills.md) — `CODOMYRMEX_SKILLS_REGISTRY` and project skill profile

## Navigation

- **Index**: [README.md](README.md)
- **Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/hermes/)
