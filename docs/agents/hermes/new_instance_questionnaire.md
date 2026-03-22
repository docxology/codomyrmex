# Hermes Instance Configuration — Required Inputs

Use this checklist when spawning a new Hermes instance. Items marked **[REQUIRED]** must be provided. Others have sensible defaults.

**Quick spawn**: `src/codomyrmex/agents/hermes/scripts/spawn_instance.sh <name> [personality] [model] [workdir]`

## 1. Instance Identity

- **[REQUIRED] Instance name**: Directory name (no spaces, lowercase)
  - Example: `research-bot`, `codomyrmex-watcher`, `civic-analyst`
  - Creates: `~/<name>/.hermes/`

- **[REQUIRED] Purpose/scope**: What this agent does
  - Example: "Monitor and analyze codomyrmex module health"
  - Used for personality and cron job design

## 2. Model & Provider

- **[REQUIRED] Model**: OpenRouter model ID
  - Free tier: `nvidia/nemotron-3-super-120b-a12b:free`
  - Best: `openrouter/hunter-alpha`, `anthropic/claude-sonnet-4`, `google/gemini-2.5-pro`
  - Format: `provider/model-name`

- **[REQUIRED] OPENROUTER_API_KEY**: From https://openrouter.ai/keys
  - Same key can be shared across instances (or separate for billing isolation)

## 3. Personality

- **[REQUIRED] Personality**: Built-in name or custom prompt
  - Built-in: `helpful`, `concise`, `technical`, `creative`, `teacher`, `kawaii`, `pirate`, `shakespeare`, `surfer`, `noir`, `uwu`, `philosopher`, `hype`
  - Custom: Provide a system prompt string (1-3 sentences describing behavior)

## 4. Telegram Integration (Optional)

- **TELEGRAM_BOT_TOKEN**: From @BotFather on Telegram
  - Create bot: Message @BotFather → /newbot → follow prompts
  - Required if you want Telegram connectivity

- **TELEGRAM_ALLOWED_USERS**: Who can interact with the bot
  - Single user: `docxology`
  - Multiple: `user1,user2,user3`
  - Open: `allow all`

- **TELEGRAM_HOME_CHANNEL**: Default outbound channel name
  - Example: `ActiveInference`, `Research`, `Monitoring`
  - Used for cron job delivery and unsolicited messages

- **require_mention**: Only respond when mentioned (@bot)
  - Default: `true` (recommended for group chats)
  - Set `false` for dedicated DM bots

## 5. Working Directory

- **terminal.cwd**: Where the agent operates
  - Default: `.` (current directory)
  - Example: `~/codomyrmex`, `~/research`, `~/my-project`

## 6. Toolsets

- **toolsets**: Which tools to enable
  - Default: `['all']` (everything)
  - Restricted: `['terminal', 'file', 'web', 'skills', 'delegation']`

## 7. Context Compression

- **compression.enabled**: Default `true`
- **compression.summary_model**: Default `google/gemini-3-flash-preview` (fast, cheap)
- **compression.threshold**: Default `0.9` (compress when 90% full)

## 8. Scheduling (Optional)

Define cron jobs for the agent:
- **Schedule**: Cron expression (`0 2 * * *` for 2 AM daily) or interval (`every 15m`)
- **Prompt**: Self-contained task description
- **Label**: Descriptive name
- **Repeat**: Number of times (omit for forever)
- **Delivery**: `origin` (back to source), `telegram`, `local`

## 9. Advanced (Optional)

- **agent.max_turns**: Max conversation turns (default: 300)
- **agent.reasoning_effort**: `low`, `medium`, `high` (default: high)
- **terminal.timeout**: Command timeout in seconds (default: 300)
- **human_delay.mode**: `off`, `typing`, `random` (default: off)
- **session_reset.idle_minutes**: Session reset after idle (default: 1440 = 24h)

## Navigation

- **Spawn script**: [scripts/spawn\_instance.sh](../../../src/codomyrmex/agents/hermes/scripts/spawn_instance.sh)
- **Config template**: [instance\_templates/config.template.yaml](../../../src/codomyrmex/agents/hermes/instance_templates/config.template.yaml)
- **Active instances**: [instances.md](instances.md)
