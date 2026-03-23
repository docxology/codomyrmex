# Hermes Troubleshooting Guide

**Version**: v0.4.0 | **Last Updated**: March 2026 (73-commit update + v0.4.0)

## Quick Diagnostics

```bash
# Run the built-in doctor
hermes doctor

# Check gateway status
hermes status

# Check running processes
ps aux | grep hermes | grep -v grep

# Check launchd services
launchctl list | grep hermes
```

---

## Common Issues

### 1. Telegram 409 Conflict

**Error**:

```text
telegram.error.Conflict: Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

**Cause**: Two processes are polling `getUpdates` with the same bot token. Telegram only permits one consumer per token.

**Diagnosis**:

```bash
# Find all hermes processes
ps aux | grep hermes | grep -v grep

# Check which token each instance uses
grep TELEGRAM_BOT_TOKEN ~/.hermes/.env
grep TELEGRAM_BOT_TOKEN ~/other-instance/.hermes/.env

# Check gateway logs for token prefix
grep "bot[0-9]*:" ~/.hermes/logs/gateway.log | tail -1
```

**Fix**:

1. Ensure each bot token is used by exactly one process
2. Kill the duplicate: `kill <PID>`
3. If multi-instance, verify each instance has a unique HERMES_HOME with unique bot token

---

### 2. "Gateway Already Running" (Stale PID)

**Error**:

```text
Another gateway instance is already running (PID 5519, HERMES_HOME=...).
Use 'hermes gateway restart' to replace it, or 'hermes gateway stop' first.
```

**Cause**: `gateway.pid` contains a PID from a previous process that crashed without cleanup.

**Fix**:

```bash
# Option 1: Stop via hermes CLI
HERMES_HOME=/path/to/.hermes hermes gateway stop

# Option 2: Use --replace flag
HERMES_HOME=/path/to/.hermes hermes gateway run --replace

# Option 3: Manual cleanup
rm $HERMES_HOME/gateway.pid
hermes gateway run
```

**Prevention**: Always use `--replace` in launchd/systemd service definitions.

---

### 3. Invalid Command: `hermes telegram`

**Error**:

```text
hermes: error: argument command: invalid choice: 'telegram'
```

**Cause**: `hermes telegram` is not a valid subcommand. The correct command is `hermes gateway`, which starts all configured messaging platforms.

**Fix**: Use `hermes gateway run` instead.

**Valid commands**:

```text
chat, model, gateway, setup, whatsapp, copilot, login, logout, status,
cron, doctor, config, pairing, skills, tools, sessions, insights,
claw, version, update, uninstall
```

---

### 4. Duplicate YAML Keys (Silent Config Loss)

**Symptom**: Agent ignores `max_turns`, `personality`, or other settings despite them being in `config.yaml`.

**Cause**: YAML has duplicate top-level keys. The parser silently takes the last one and discards earlier ones.

**Diagnosis**:

```bash
python3 -c "
import yaml
with open('$HERMES_HOME/config.yaml') as f:
    data = yaml.safe_load(f)
print(yaml.dump(data, default_flow_style=False))
"
```

Compare the output against the raw file. Missing keys = they were in a duplicated block.

**Fix**: Merge all settings for a key into a single block. See [configuration.md](configuration.md).

---

### 5. launchd Service Won't Restart

**Symptom**: `launchctl list` shows the service with PID `-` and exit code `0`, but no process is running.

**Cause**: The KeepAlive config only restarts on non-zero exits. If the gateway exits cleanly (e.g., due to stale PID detection), launchd treats it as intentional.

**Fix**: Add `--replace` to the `ProgramArguments` in the plist. See [launchd.md](launchd.md).

---

### 6. Wrong Bot Token Being Used

**Symptom**: Bot doesn't respond, or logs show requests to the wrong bot token.

**Cause**: `HERMES_HOME` is not set correctly, causing the gateway to load `.env` from the default `~/.hermes/` path.

**Diagnosis**:

```bash
# Check which token is in the log
grep "api.telegram.org/bot" $HERMES_HOME/logs/gateway.log | tail -1
# Output: bot8754235534:*** ← is this the right token?
```

**Fix**: Ensure `HERMES_HOME` is set in the process environment (shell export, launchd plist, or systemd unit).

---

### 7. Bot Not Responding (Silent)

**Checklist**:

1. ✅ Is the gateway process running? (`ps aux | grep hermes`)
2. ✅ Is it polling successfully? (`grep getUpdates $HERMES_HOME/logs/gateway.log | tail -3`)
3. ✅ Is the user's **numeric Telegram ID** in `$HERMES_HOME/pairing/telegram-approved.json`? (Check for `Unauthorized user:` in log)
4. ✅ For groups: is BotFather privacy mode **OFF**? (`curl https://api.telegram.org/bot<TOKEN>/getMe` → `can_read_all_group_messages` must be `true`)
5. ✅ Is `require_mention: true`? Try @mentioning the bot
6. ✅ Is the bot using the correct token? Check log for `bot<TOKEN>:`
7. ✅ Are there errors? Check `$HERMES_HOME/logs/errors.log`

---

### 8. High Memory Usage

**Symptom**: Gateway process grows to several GB over time.

**Cause**: Large session histories and/or many concurrent sessions.

**Fix**:

- Enable compression: `compression.enabled: true`
- Lower threshold: `compression.threshold: 0.75`
- Periodically restart the gateway

---

### 9. API Key Errors

**Symptom**: `401 Unauthorized` or `403 Forbidden` in logs.

**Diagnosis**:

```bash
# Check configured keys
hermes status
# Shows: OpenRouter ✓ sk-o...1405
```

**Fix**:

1. Verify the key is valid: `curl -H "Authorization: Bearer $KEY" https://openrouter.ai/api/v1/models`
2. Check `.env` for typos or trailing whitespace
3. Ensure the key has sufficient credits

---

---

### 10. Copilot ACP Errors (v0.3.0)

**Symptom**: `Could not start Copilot ACP command 'copilot'` or `Copilot ACP did not return a sessionId`.

**Cause**: GitHub Copilot CLI is not installed or not authenticated.

**Fix**:

```bash
# 1. Install Copilot CLI extension
gh extension install github/gh-copilot

# 2. Authenticate Hermes with Copilot
hermes copilot login

# 3. Verify
copilot --version
```

> **Note**: Copilot ACP does not support structured tool calls. For agentic tasks, use OpenRouter instead.

---

### 11. Rate Limit Exceeded (429 from OpenRouter)

**Symptom**: `429 Too Many Requests` — free tier is 50 req/day with < $5 balance.

**Fix options**:

1. **Add $5 credits** → bumps free quota to 1,000 req/day and raises RPM from 20 → 200: [openrouter.ai/settings/credits](https://openrouter.ai/settings/credits)
2. **Enable smart model routing** to route simple messages to a different model:

   ```yaml
   smart_model_routing:
     enabled: true
     cheap_model:
       provider: openrouter
       model: google/gemini-2.0-flash-001
   ```

3. **Add fallback models** to `config.yaml`:

   ```yaml
   fallback_models:
     - google/gemini-2.0-flash-001
     - anthropic/claude-3-haiku
   ```

4. **Check current usage**: `curl https://openrouter.ai/api/v1/key -H "Authorization: Bearer $OPENROUTER_API_KEY"`

### 12. Codomyrmex skill profile not applied (wrong skills or none)

**Symptoms**: `HermesClient` / MCP runs without expected `hermes chat -s` skills, or profile seems ignored.

**Checks**:

1. **Working directory** — `.codomyrmex/hermes_skills_profile.yaml` is discovered from the process **cwd** (walking up to filesystem root). Running from a different directory than the repo root picks up a different profile or none.
2. **Disable flag** — `hermes_skill_profile_disable` on the client skips the project file.
3. **Ollama fallback** — skill packs are not loaded on the Ollama path (use Hermes CLI backend for preload).
4. **Validate** — call MCP `hermes_skills_validate_registry` and read [skills.md](skills.md) for merge order.

## Diagnostic Commands Reference

| Command           | Purpose                      |
| :---------------- | :--------------------------- |
| `hermes doctor`   | Full system diagnostics      |
| `hermes status`   | Quick service overview       |
| `hermes version`  | Version and Python info      |
| `hermes config`   | Show effective configuration |
| `hermes sessions` | List active sessions         |

## Related Documents

- [Configuration](configuration.md) — YAML pitfalls
- [Multi-Instance](multi_instance.md) — Token conflicts
- [launchd](launchd.md) — Service management
- [Environment](environment.md) — `.env` loading
- [Copilot ACP](copilot_acp.md) — Copilot backend issues
- [skills.md](skills.md) — Codomyrmex skill registry, profile, merge order

## Navigation

- **Index**: [README.md](README.md)
- **Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/hermes/](../../../src/codomyrmex/agents/hermes/)
