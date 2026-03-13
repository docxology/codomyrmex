# Hermes Security Guide

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

Hermes handles sensitive authentication tokens, API keys, and user conversations. This guide covers best practices for securing your Hermes deployment.

## API Key Management

### Storage

All secrets are stored in `$HERMES_HOME/.env`:

```bash
# Set restrictive permissions
chmod 600 $HERMES_HOME/.env
```

### Never Commit Secrets

Ensure `.env` files are excluded from version control:

```gitignore
# .gitignore
.env
*.env
.hermes/
```

### Key Rotation

Rotate keys immediately if:
- A key appears in logs, error messages, or git history
- The `.env` file was accidentally committed
- A team member's access is revoked

### Separate Keys Per Instance

Each Hermes instance should use unique API keys where possible:
- **OpenRouter**: Use separate API keys for budgeting and isolation
- **Telegram**: Each bot requires its own unique token from @BotFather
- **Other services**: Shared keys are acceptable if usage tracking isn't needed

## Access Control

### TELEGRAM_ALLOWED_USERS

The primary access control mechanism for Telegram bots:

```bash
# .env
TELEGRAM_ALLOWED_USERS=username1,username2
```

- Only listed usernames can interact with the bot
- Messages from unlisted users are **silently ignored**
- Use Telegram usernames, not display names

### require_mention

```yaml
# config.yaml
telegram:
  require_mention: true
```

When `true`, the bot only processes messages that @mention it. This prevents accidental responses in group chats.

### Bot Visibility

Consider setting your bot's privacy mode via @BotFather:
- **Privacy mode ON** (default): Bot only sees messages that @mention it in groups
- **Privacy mode OFF**: Bot sees all messages in groups it's added to

## Operational Security

### Log Hygiene

Gateway logs may contain:
- Bot token prefixes (not full tokens)
- User IDs and usernames
- Message content summaries

**Best practices**:
- Set `verbose: false` in production
- Restrict log file permissions: `chmod 600 $HERMES_HOME/logs/*.log`
- Rotate logs periodically

### Process Isolation

When running multiple instances:
- Each instance has its own `state.db` with conversation history
- Session files contain full message content
- Restrict directory permissions per instance

### Network Security

- All API calls use HTTPS
- Telegram Bot API connections are TLS-encrypted
- OpenRouter connections are TLS-encrypted
- No local ports are opened by default (long polling, not webhooks)

## Audit Checklist

- [ ] `.env` files have `600` permissions
- [ ] `.env` not in version control
- [ ] `TELEGRAM_ALLOWED_USERS` restricts access
- [ ] `verbose: false` in production config
- [ ] Log files have appropriate permissions
- [ ] API keys rotated if any suspected leak
- [ ] Each bot instance uses unique tokens

## Related Documents

- [Environment](environment.md) — API key configuration
- [Configuration](configuration.md) — Security-relevant settings
- [Multi-Instance](multi_instance.md) — Instance isolation
