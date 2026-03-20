# Hermes Security Guide

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

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

## Codomyrmex skill registry files

If you use **`CODOMYRMEX_SKILLS_REGISTRY`** or commit **`.codomyrmex/hermes_skills_profile.yaml`**, treat those YAML files like config: they can reference skill names and project policy. Do not embed secrets; keep registry paths readable only by intended users. See [skills.md](skills.md).

## Access Control

### TELEGRAM_ALLOWED_USERS

> **Legacy**: `TELEGRAM_ALLOWED_USERS` remains supported but the current primary mechanism
> is `$HERMES_HOME/pairing/telegram-approved.json`. Use `hermes pairing create` or edit the
> file directly. See [telegram.md](telegram.md) for the full pairing workflow.

The legacy env var:

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

## DM Security — Unauthorized DM Behavior (v0.3.0)

The 73-commit update hardened gateway DM handling. By default, Hermes **ignores unsolicited DMs** from users not in the allow-list rather than responding with an error that could leak agent info.

### Pairing System

Authorized users can be added dynamically without restarting the gateway via the pairing system:

```bash
hermes pairing list                           # list pending pairing codes
hermes pairing approve telegram <code>        # approve a pending pairing request
hermes pairing revoke telegram <user_id>      # revoke access
hermes pairing clear-pending                  # clear all pending codes
```

Users self-pair by sending `/pair <code>` to the bot. Codes are time-limited (15 minutes by default).

### `TELEGRAM_ALLOWED_USERS` vs. Pairing

| Method | Use Case | Persistence |
| :--- | :--- | :--- |
| `TELEGRAM_ALLOWED_USERS` in `.env` | Static admin allow-list | Survives restarts |
| `hermes pairing approve` | Dynamic user onboarding | Stored in `state.db` |

## Tirith Security Policy Engine

Hermes integrates the Tirith policy engine for fine-grained command approval:

```yaml
# config.yaml
security:
  redact_secrets: true        # mask API keys in logs/responses
  tirith_enabled: true        # enable Tirith policy engine
  tirith_path: tirith         # path to tirith binary
  tirith_timeout: 5           # seconds before fail-open
  tirith_fail_open: true      # allow if Tirith times out
  website_blocklist:
    enabled: false
    domains: []
```

Tirith evaluates tool calls against policies before execution. If `tirith_fail_open: true`, commands proceed if Tirith is unreachable.

## Audit Checklist

- [ ] `.env` files have `600` permissions
- [ ] `.env` not in version control
- [ ] `TELEGRAM_ALLOWED_USERS` restricts access
- [ ] `verbose: false` in production config
- [ ] `security.redact_secrets: true` in config
- [ ] Log files have appropriate permissions
- [ ] API keys rotated if any suspected leak
- [ ] Each bot instance uses unique tokens
- [ ] Pairing codes reviewed periodically (`hermes pairing list`)
- [ ] `tirith_enabled: true` for production deployments

## Related Documents

- [Environment](environment.md) — API key configuration
- [Configuration](configuration.md) — Security-relevant settings
- [Multi-Instance](multi_instance.md) — Instance isolation
- [Telegram](telegram.md) — DM access control and pairing
- [skills.md](skills.md) — Skill registry / profile files (Codomyrmex)
