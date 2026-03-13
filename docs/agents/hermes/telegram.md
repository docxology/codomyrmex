# Hermes Telegram Integration

**Version**: v0.2.0 | **Last Updated**: March 2026

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
TELEGRAM_ALLOWED_USERS=YourUsername    # comma-separated Telegram usernames
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

### `TELEGRAM_ALLOWED_USERS`

Comma-separated list of Telegram usernames authorized to interact with the bot. Messages from unlisted users are silently ignored.

### `TELEGRAM_HOME_CHANNEL`

The channel/user where cron job results and proactive messages are delivered.

## How Polling Works

The Telegram adapter uses the Bot API's `getUpdates` endpoint with long polling:

```
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

```
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

1. **Check allowed users**: Is your username in `TELEGRAM_ALLOWED_USERS`?
2. **Check require_mention**: Try @mentioning the bot in the message
3. **Check logs**: `tail -f $HERMES_HOME/logs/gateway.log`
4. **Check process**: `ps aux | grep hermes`
5. **Verify token**: Send a test with `curl`:
    ```bash
    curl https://api.telegram.org/bot<TOKEN>/getMe
    ```

### Bot Responds via Wrong Bot

If you have multiple bots on the same machine, verify each gateway is using the correct token. The gateway log shows the token prefix:

```
HTTP Request: POST https://api.telegram.org/bot8754235534:***/getUpdates
```

## User Pairing

Hermes supports a pairing system for authorized user management:

```bash
# Generate a pairing code
hermes pairing create

# List active pairings
hermes pairing list
```

Users can pair by sending the code to the bot in Telegram.

## Related Documents

- [Gateway](gateway.md) — Gateway architecture
- [Multi-Instance](multi_instance.md) — Running multiple bots
- [Troubleshooting](troubleshooting.md) — Error patterns and fixes
