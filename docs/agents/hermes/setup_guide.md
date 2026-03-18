# Hermes Setup Guide — Complete New Instance

**Version**: v0.2.0 | **Last Updated**: March 2026

> **Official Docs**: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)
> **GitHub**: [github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)

## Prerequisites

- macOS, Linux, or WSL2 (native Windows not supported)
- Python 3.11+ (installed automatically by the installer)
- Node.js (optional, for WhatsApp/browser tools)
- An OpenRouter API key (or other LLM provider key)

## Part 1: Fresh Installation

### Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

This handles **everything**: Python, uv, Node.js, ripgrep, ffmpeg, repo clone, venv, global `hermes` command, and provider config.

After completion:

```bash
source ~/.zshrc   # or ~/.bashrc
hermes             # start chatting
```

### Manual Installation

```bash
# Step 1: Clone
git clone --recurse-submodules https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# Step 2: Create venv
uv venv venv --python 3.11
source venv/bin/activate

# Step 3: Install Python deps
uv pip install -e ".[all]"

# Step 4: Install submodules
uv pip install -e "./mini-swe-agent"
uv pip install -e "./tinker-atropos"

# Step 5: (Optional) Node.js deps for WhatsApp/browser
npm install

# Step 6: Create config directory
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}
cp cli-config.yaml.example ~/.hermes/config.yaml
touch ~/.hermes/.env

# Step 7: Add API keys
cat >> ~/.hermes/.env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
EOF

# Step 8: Add to PATH
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Step 9: Configure provider
hermes model

# Step 10: Verify
hermes version
hermes doctor
hermes status
hermes chat -q "Hello! What tools do you have available?"
```

## Part 2: Directory Structure

After setup, `~/.hermes/` contains:

```text
~/.hermes/
├── config.yaml       # Settings (model, terminal, TTS, compression, etc.)
├── .env              # API keys and secrets
├── auth.json         # OAuth provider credentials (Nous Portal)
├── SOUL.md           # Optional: global persona definition
├── gateway.pid       # Gateway process ID (when running)
├── state.db          # SQLite + FTS5 session/memory database
├── memories/         # Persistent memory (MEMORY.md, USER.md)
├── skills/           # Agent-created and installed skills
├── cron/             # Scheduled job definitions
├── sessions/         # Gateway session backups (JSON)
├── pairing/          # User pairing codes
├── hooks/            # Lifecycle hooks
├── logs/             # Logs (secrets auto-redacted)
│   ├── gateway.log
│   ├── gateway.error.log
│   └── errors.log
├── image_cache/      # Generated image cache
├── audio_cache/      # TTS audio cache
└── whatsapp/         # WhatsApp session data
    └── session/
```

## Part 3: Configuration

### config.yaml Essentials

```yaml
# Model (OpenRouter format: provider/model-name)
model: nousresearch/hermes-3-llama-3.1-405b:free

# Tool categories
toolsets:
    - all

# Agent behavior
agent:
    max_turns: 150
    reasoning_effort: medium
    personality: helpful
    personalities:
        helpful: You are a helpful, friendly AI assistant.

# Context compression
compression:
    enabled: true
    threshold: 0.85
    summary_model: google/gemini-3-flash-preview

# Terminal backend
terminal:
    backend: local
    timeout: 180

# Telegram (fill in after gateway setup)
telegram:
    require_mention: true
    free_response_channels: ""
```

### .env API Keys

```bash
# Required: at least one LLM provider
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Telegram (from @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:AAxxxxxxxxxxxxxxxxx
TELEGRAM_ALLOWED_USERS=YourUsername
TELEGRAM_HOME_CHANNEL=YourUsername

# Optional tool enhancements
# FIRECRAWL_API_KEY=fc-...     # Web search & scraping
# FAL_KEY=...                   # Image generation (FLUX)
# ELEVENLABS_API_KEY=...        # Premium TTS
# BROWSERBASE_API_KEY=...       # Browser automation
# BROWSERBASE_PROJECT_ID=...
# VOICE_TOOLS_OPENAI_KEY=...    # OpenAI TTS/STT
# HONCHO_API_KEY=...             # User modeling
# TINKER_API_KEY=...             # Tinker console
# WANDB_API_KEY=...              # Experiment tracking
```

### Configuration Precedence

1. **CLI arguments** — `hermes chat --model anthropic/claude-opus-4`
2. **`~/.hermes/config.yaml`** — primary settings
3. **`~/.hermes/.env`** — secrets (API keys, tokens)
4. **Built-in defaults** — hardcoded safe fallbacks

**Rule**: Secrets go in `.env`. Everything else goes in `config.yaml`.

## Part 4: Telegram Gateway Setup

```bash
# Interactive setup
hermes gateway setup

# Or manual:
# 1. Create bot via @BotFather → get token
# 2. Add token to .env: TELEGRAM_BOT_TOKEN=...
# 3. Add your username: TELEGRAM_ALLOWED_USERS=YourUsername
# 4. Start gateway
hermes gateway run
```

### Install as System Service (macOS)

```bash
hermes gateway install   # creates launchd plist automatically
```

Or manual plist — see [launchd.md](launchd.md).

## Part 5: New Instance (Multi-Bot)

To create a second bot with its own identity (e.g., `crescent-city`):

```bash
# 1. Create instance directory
export INSTANCE_NAME="crescent-city"
mkdir -p ~/hermes-${INSTANCE_NAME}/.hermes/{cron,sessions,logs,memories,skills,pairing,hooks,image_cache,audio_cache,whatsapp/session}

# 2. Create .env with unique bot token
cat > ~/hermes-${INSTANCE_NAME}/.hermes/.env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your-key-here
TELEGRAM_BOT_TOKEN=UNIQUE-BOT-TOKEN-HERE
TELEGRAM_ALLOWED_USERS=YourUsername
TELEGRAM_HOME_CHANNEL=YourUsername
EOF
chmod 600 ~/hermes-${INSTANCE_NAME}/.hermes/.env

# 3. Create config.yaml (customize personality)
cat > ~/hermes-${INSTANCE_NAME}/.hermes/config.yaml << 'EOF'
model: meta-llama/llama-3.3-70b-instruct:free
fallback_models:
  - "google/gemini-2.0-flash-exp:free"
  - "microsoft/phi-4-reasoning:free"
  - "openrouter/hunter-alpha"
toolsets:
  - all
agent:
  max_turns: 150
  reasoning_effort: medium
  personality: civic_technical_analyst
  personalities:
    civic_technical_analyst: "You are a technical expert with strong civic awareness and intelligence-analyst skills. Provide detailed, accurate technical information while considering societal implications and applying analytical rigor."
terminal:
  backend: local
  timeout: 180
compression:
  enabled: true
telegram:
  require_mention: true
  free_response_channels: ""
EOF

# 4. Test
HERMES_HOME=~/hermes-${INSTANCE_NAME}/.hermes hermes status
HERMES_HOME=~/hermes-${INSTANCE_NAME}/.hermes hermes gateway run

# 5. Create launchd service (see launchd.md for plist template)
```

See [multi_instance.md](multi_instance.md) and [launchd.md](launchd.md) for complete details.

## Part 6: CLI Command Reference

### Core

| Command                                 | Description             |
| :-------------------------------------- | :---------------------- |
| `hermes`                                | Start interactive chat  |
| `hermes chat -q "..."`                  | One-shot query          |
| `hermes chat --continue`                | Resume last session     |
| `hermes chat --resume <id>`             | Resume specific session |
| `hermes chat --model <name>`            | Override model          |
| `hermes chat --provider <name>`         | Override provider       |
| `hermes chat --toolsets "web,terminal"` | Limit tools             |

### Provider & Model

| Command         | Description                 |
| :-------------- | :-------------------------- |
| `hermes model`  | Interactive model selection |
| `hermes login`  | Auth with Nous Portal       |
| `hermes logout` | Clear Nous Portal auth      |

### Configuration

| Command                     | Description               |
| :-------------------------- | :------------------------ |
| `hermes setup`              | Full interactive wizard   |
| `hermes config`             | View current config       |
| `hermes config edit`        | Open config in editor     |
| `hermes config set KEY VAL` | Set a value               |
| `hermes config check`       | Check for missing options |
| `hermes config migrate`     | Add missing options       |
| `hermes tools`              | Manage toolsets           |
| `hermes status`             | Quick status summary      |
| `hermes doctor`             | Full diagnostics          |

### Gateway

| Command                    | Description               |
| :------------------------- | :------------------------ |
| `hermes gateway`           | Gateway status            |
| `hermes gateway setup`     | Configure platforms       |
| `hermes gateway install`   | Install as system service |
| `hermes gateway start`     | Start the service         |
| `hermes gateway stop`      | Stop the service          |
| `hermes gateway restart`   | Restart the service       |
| `hermes gateway uninstall` | Remove system service     |
| `hermes whatsapp`          | WhatsApp pairing          |

### Skills

| Command                           | Description            |
| :-------------------------------- | :--------------------- |
| `hermes skills browse`            | Browse Skills Hub      |
| `hermes skills search <q>`        | Search skills          |
| `hermes skills install <id>`      | Install a skill        |
| `hermes skills list`              | List installed skills  |
| `hermes skills list --source hub` | List Hub skills        |
| `hermes skills audit`             | Audit installed skills |
| `hermes skills uninstall <name>`  | Remove a skill         |
| `hermes skills publish <path>`    | Publish to GitHub      |
| `hermes skills tap add <repo>`    | Add skill tap          |

### Sessions & Insights

| Command                             | Description        |
| :---------------------------------- | :----------------- |
| `hermes sessions list`              | List sessions      |
| `hermes sessions stats`             | Session statistics |
| `hermes sessions export <id>`       | Export a session   |
| `hermes sessions delete <id>`       | Delete a session   |
| `hermes sessions prune`             | Clean old sessions |
| `hermes insights`                   | Usage analytics    |
| `hermes insights --days 7`          | Last 7 days        |
| `hermes insights --source telegram` | Platform filter    |

### Maintenance

| Command            | Description    |
| :----------------- | :------------- |
| `hermes update`    | Self-update    |
| `hermes version`   | Show version   |
| `hermes uninstall` | Full uninstall |

## Part 7: Codomyrmex Scripts

Thin orchestrator scripts in [`scripts/agents/hermes/`](../../../scripts/agents/hermes/):

| Script                      | Purpose                                            |
| :-------------------------- | :------------------------------------------------- |
| `setup_hermes.py`           | Validate environment, config, backends             |
| `run_hermes.py`             | Send prompt, get response (CLI or Ollama fallback) |
| `dispatch_hermes.py`        | Sweep-and-dispatch improvement orchestrator        |
| `observe_hermes.py`         | Session observability and telemetry viewer         |
| `prompt_context.py`         | Project-aware context builder for prompts          |
| `evaluate_orchestrators.py` | Evaluate scripts against thin orchestrator pattern |
| `new_instance.py`           | Create and configure a new Hermes instance         |

## Related Documents

- [Architecture](architecture.md) — Core agent loop
- [Configuration](configuration.md) — YAML reference & pitfalls
- [Environment](environment.md) — HERMES_HOME & API keys
- [Telegram](telegram.md) — Bot setup
- [Multi-Instance](multi_instance.md) — Multiple bots
- [launchd](launchd.md) — macOS services
- [Troubleshooting](troubleshooting.md) — Common issues

## External Links

- 📖 [Official Documentation](https://hermes-agent.nousresearch.com/docs/)
- 💻 [GitHub Repository](https://github.com/NousResearch/hermes-agent)
- 🤖 [Skills Hub](https://agentskills.io)
- 💬 [Discord](https://discord.gg/NousResearch)
- 🏢 [Nous Research](https://nousresearch.com)
