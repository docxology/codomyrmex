# Hermes Instance Gotchas & Lessons Learned

Hard-won knowledge from running multiple Hermes instances. Documented to prevent repeat failures.

**Source in Codomyrmex**: moved from `hermes-templates/GOTCHAS.md` → `docs/agents/hermes/gotchas.md`

---

## 1. Gateway Working Directory (CWD) — CRITICAL

**Symptom:** Messages return "Sorry, I encountered an unexpected error" even though gateway shows as running.

**Error in logs:**

```
FileNotFoundError: [Errno 2] No such file or directory
  cwd = os.getcwd()
```

**Root cause:** Gateway process inherited a temp directory (e.g., from cron job sandbox) that was cleaned up. When `prompt_builder.py` calls `os.getcwd()`, the directory no longer exists → crash.

**Fix:** Always set explicit `cwd` when spawning gateway:

```bash
# WRONG — inherits whatever CWD the parent has
hermes gateway run

# RIGHT — explicit working directory
cd ~/my-project && hermes gateway run

# Or programmatically:
subprocess.Popen([hermes, "gateway", "run"], cwd=workdir, ...)
```

**Validation:** After starting gateway, check logs for "Connected and polling" and test a message immediately.

---

## 2. launchd Services Are Shared

**Symptom:** `hermes gateway start` on a new instance uses the MAIN instance's HERMES_HOME.

**Root cause:** The launchd service (`ai.hermes.gateway`) points to `~/.hermes` and is shared across all `hermes gateway start` calls. Setting `HERMES_HOME` env var doesn't affect the installed service.

**Fix:** For non-main instances, run gateway as a background process:

```bash
HERMES_HOME=~/my-agent/.hermes hermes gateway run &
```

Or use `subprocess.Popen()` with explicit env and cwd.

---

## 3. Telegram Polling Conflict Kills Gateway

**Symptom:** Gateway was running but stopped responding. `gateway_state.json` shows `telegram_polling_conflict`.

**Root cause:** Two gateway processes for the same bot token are running simultaneously (e.g., stale process from launchd restart + direct launch, or two instances sharing the same `TELEGRAM_BOT_TOKEN`).

**Fix:**

```bash
# Check for stale hermes processes
ps aux | grep hermes_cli.main | grep -v grep

# Kill stale PIDs
kill <PID1> <PID2>

# Restart via launchd
launchctl start ai.hermes.gateway

# Verify
tail -10 ~/.hermes/logs/gateway.log  # should show "Connected and polling"
```

---

## 4. .env Must Include OpenRouter Key

**Symptom:** Gateway starts but API calls fail with auth errors.

**Fix:** Copy `OPENROUTER_API_KEY` from main instance. Can share same key across instances (or use separate keys for billing isolation).

---

## 5. Telegram Bot Must Be Started

**Symptom:** Bot token valid but messages never arrive.

**Fix:** Message the bot on Telegram first (send /start). This activates the bot with Telegram's servers.

---

## 6. Session Persistence Across Restarts

**Note:** Sessions persist in `state.db`. If gateway crashes and restarts, conversations resume. For clean slate, delete `state.db` or use `/reset` command.

---

## 7. Port Conflicts

**Note:** Multiple gateway instances don't conflict (each polls Telegram independently). But local tool servers (MCP, etc.) may conflict if using same ports. Use different tool configurations per instance.
