# Hermes Telegram Integration

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Overview

Hermes connects to Telegram via the Bot API using long polling. The Telegram adapter is one of the most commonly used platform integrations and has well-documented patterns and pitfalls.

## Setup

### 1. Create a Bot via BotFather

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the bot token (e.g., `1234567890:AAxxxxxxxxxxxxxxxxx`)

### 2. Configure `.env`

```bash
# $HERMES_HOME/.env
TELEGRAM_BOT_TOKEN=1234567890:AAxxxxxxxxxxxxxxxxx
TELEGRAM_HOME_CHANNEL=YourUsername     # for cron/proactive messages
```

### 3. Configure `config.yaml`

```yaml
telegram:
    require_mention: true # only respond when @bot_name is mentioned
    free_response_channels: "" # channel IDs where bot responds without mention
```

### 4. Start the Gateway

```bash
hermes gateway run
```

## Configuration Options

### `require_mention`

When `true`, the bot only responds to messages that @mention it. This is recommended for group chats to avoid noise. In DMs, messages are always processed regardless of this setting.

### `free_response_channels`

Comma-separated channel/group IDs where the bot responds to all messages without requiring @mention. Leave empty (`""`) to disable.

### `TELEGRAM_ALLOWED_USERS` & `TELEGRAM_ALLOW_ALL_USERS`

Hermes supports three tiers of user authorization for Telegram:

1. **Global Open Access**: Setting `TELEGRAM_ALLOW_ALL_USERS=true` in `.env` disables the pairing wall completely. Anyone who messages the bot will be processed. This is highly recommended for public group chats where you want all members to interface fluidly.
2. **Explicit Allowlist**: Setting `TELEGRAM_ALLOWED_USERS=1234,4567` restricts access to only those numeric Telegram IDs.
3. **Dynamic Pairing**: The current runtime system uses `$HERMES_HOME/pairing/telegram-approved.json` — a JSON file mapping dynamic user IDs to approval timestamps. Manage it via:

```bash
# Create a pairing code (user sends it to the bot to self-authorize)
hermes pairing create

# Or directly add a known user ID
python3 -c "
import json, pathlib, time, os
p = pathlib.Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))) / 'pairing/telegram-approved.json'
d = json.loads(p.read_text())
d['123456789'] = {'user_name': 'alice', 'approved_at': time.time()}
p.write_text(json.dumps(d, indent=2))
"
```

Groups are technically authorized by adding the group's `chat_id` (e.g., `-5295181842`) as an entry in `telegram-approved.json`. **However**, this only authorizes the *group routing*; individual users within the group still must pass the pairing check unless `TELEGRAM_ALLOW_ALL_USERS=true` is activated.

### `TELEGRAM_HOME_CHANNEL`

The channel/user where cron job results and proactive messages are delivered.

## How Polling Works

The Telegram adapter uses the Bot API's `getUpdates` endpoint with long polling:

```text
┌─────────────┐         ┌──────────────────┐
│  Hermes     │  POST   │  Telegram API    │
│  telegram.py│────────▶│  /getUpdates     │
│             │◀────────│                  │
│  (10s poll) │  JSON   │  Returns updates │
└─────────────┘         └──────────────────┘
```

The adapter:

1. Calls `getUpdates` with a long-poll timeout (~10 seconds)
2. Receives any new messages since last offset
3. Routes each message to the gateway runner
4. Updates the offset to acknowledge processed messages

## Common Issues

### 409 Conflict Error

```text
telegram.error.Conflict: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**Cause**: Two processes are polling `getUpdates` with the same bot token. Telegram only allows **one** long-polling consumer per bot token.

**Diagnosis**:

```bash
# Check for multiple hermes processes
ps aux | grep hermes | grep -v grep

# Check which token each is using
grep -r "TELEGRAM_BOT_TOKEN" ~/.hermes/.env ~/other-hermes-dir/.env
```

**Fix**:

1. Ensure each bot token is used by exactly one gateway process
2. Kill duplicate processes: `kill <PID>`
3. If running multiple bots, use different `HERMES_HOME` directories with different bot tokens

### Bot Not Responding

1. **Check pairing**: Is the user's Telegram **numeric ID** in `$HERMES_HOME/pairing/telegram-approved.json`?
2. **Check require_mention**: In groups, try @mentioning the bot exactly — `@your_bot_name message`
3. **Check BotFather group privacy**: Run `curl https://api.telegram.org/bot<TOKEN>/getMe` and check `can_read_all_group_messages`. If `false`, go to BotFather → `/mybots` → Bot Settings → Group Privacy → **Turn OFF**.
4. **Check logs**: `tail -f $HERMES_HOME/logs/gateway.log` — look for `Unauthorized user:` lines showing the blocked numeric ID.
5. **Check process**: `ps aux | grep hermes`
6. **Verify token**: Send a test with `curl`:

    ```bash
    curl https://api.telegram.org/bot<TOKEN>/getMe
    ```

### Bot Responds via Wrong Bot

If you have multiple bots on the same machine, verify each gateway is using the correct token. The gateway log shows the token prefix:

```text
HTTP Request: POST https://api.telegram.org/bot8754235534:***/getUpdates
```

## User Authorization (Pairing System)

Hermes manages authorized users via `$HERMES_HOME/pairing/telegram-approved.json`:

```json
{
  "544419050": {"user_name": "docxology", "approved_at": 1773344648.328},
  "8634124613": {"user_name": "Matt", "approved_at": 1773957153.759},
  "-5295181842": {"user_name": "hermes_chat", "approved_at": 1773959234.1, "type": "group"}
}
```

- **DM users**: add their numeric Telegram user ID
- **Group chats**: add the group's numeric chat ID (negative number — get it from gateway.log after a message arrives)
- **Pairing codes**: let users self-authorize:

```bash
# Generate a one-time pairing code
hermes pairing create
# User sends this code to the bot in Telegram — they are then auto-added to approved list
```

## Group Chat Setup

1. Add the bot to the Telegram group
2. **Disable privacy mode** in BotFather: `/mybots` → select bot → Bot Settings → Group Privacy → **Turn OFF** (required for the bot to receive group messages)
3. Send any message in the group — the gateway log will show the group `chat_id`:

   ```bash
   grep -E "group:|Unauthorized" $HERMES_HOME/logs/gateway.log | tail -5
   ```

4. Add the group `chat_id` to the approved list in `telegram-approved.json` (see above).
5. Open `config.yaml` and set `free_response_channels: '-5295181842'` under the `telegram:` block to let the bot respond to casual chat without needing a strict `@mention`.
6. **Critical for groups:** Open `.env` and set `TELEGRAM_ALLOW_ALL_USERS=true` so that new group members aren't silently blocked by the pairing wall when they try to chat with the bot.

## Related Documents

- [Gateway](gateway.md) — Gateway architecture
- [Multi-Instance](multi_instance.md) — Running multiple bots
- [Troubleshooting](troubleshooting.md) — Error patterns and fixes
- [skills.md](skills.md) — Codomyrmex skill defaults for programmatic Hermes calls

## Navigation

- **Index**: [README.md](README.md)
- **Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/hermes/)
