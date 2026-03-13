# Hermes launchd Service Management (macOS)

**Version**: v0.2.0 | **Last Updated**: March 2026

## Overview

On macOS, Hermes gateway instances are best managed as launchd user agents. This provides automatic startup on login, crash recovery via `KeepAlive`, and proper environment variable isolation for multi-instance deployments.

## Primary Instance Plist

The default Hermes gateway plist installed by `hermes setup`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/mini/.hermes/hermes-agent/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>gateway</string>
        <string>run</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/mini/.hermes/hermes-agent</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/mini/.hermes/logs/gateway.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/mini/.hermes/logs/gateway.error.log</string>
</dict>
</plist>
```

## Additional Instance Plist Template

For running a second (or third, etc.) Hermes bot on the same machine:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>ai.hermes.gateway.YOUR-INSTANCE-NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/mini/.hermes/hermes-agent/venv/bin/python</string>
        <string>-m</string>
        <string>hermes_cli.main</string>
        <string>gateway</string>
        <string>run</string>
        <string>--replace</string>
    </array>

    <!-- CRITICAL: Set HERMES_HOME to the instance's data directory -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>HERMES_HOME</key>
        <string>/Users/mini/hermes-YOUR-INSTANCE/.hermes</string>
    </dict>

    <key>WorkingDirectory</key>
    <string>/Users/mini/.hermes/hermes-agent</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/mini/hermes-YOUR-INSTANCE/.hermes/logs/gateway.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/mini/hermes-YOUR-INSTANCE/.hermes/logs/gateway.error.log</string>
</dict>
</plist>
```

## Key Differences for Additional Instances

| Setting              | Primary                            | Additional Instance                               |
| :------------------- | :--------------------------------- | :------------------------------------------------ |
| **Label**            | `ai.hermes.gateway`                | `ai.hermes.gateway.instance-name`                 |
| **HERMES_HOME**      | Not set (defaults to `~/.hermes/`) | Must be explicitly set via `EnvironmentVariables` |
| **`--replace` flag** | Optional                           | **Recommended** — prevents stale PID deadlocks    |
| **Log paths**        | `~/.hermes/logs/`                  | Instance-specific log directory                   |

## Installing a Plist

```bash
# 1. Create the plist file
vim ~/Library/LaunchAgents/ai.hermes.gateway.my-bot.plist

# 2. Load (register) the service
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.my-bot.plist

# 3. Verify it's registered
launchctl list | grep hermes
```

## Service Operations

```bash
# Start the service
launchctl start ai.hermes.gateway.my-bot

# Stop the service
launchctl stop ai.hermes.gateway.my-bot

# Unload (unregister) the service
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.my-bot.plist

# Reload after plist changes
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.my-bot.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.my-bot.plist
```

## The `--replace` Flag

The `--replace` flag on `gateway run` is critical for service management:

- **Without `--replace`**: If the gateway crashes and leaves a stale `gateway.pid`, launchd restarts the process but the new process sees the stale PID and **refuses to start** (exits cleanly with code 0). Since KeepAlive only restarts on non-zero exits, the service is now permanently dead.

- **With `--replace`**: The new process automatically kills any existing process referenced by `gateway.pid` and takes over, regardless of whether the old PID is alive or stale.

## KeepAlive Behavior

```xml
<key>KeepAlive</key>
<dict>
    <key>SuccessfulExit</key>
    <false/>
</dict>
```

This means: **restart the process only if it exits with a non-zero exit code**. A clean exit (code 0) is treated as intentional shutdown and launchd will not restart it.

This interacts with the stale PID problem: if the gateway exits cleanly because it found a stale PID, KeepAlive won't retry. The `--replace` flag solves this.

## Debugging

```bash
# Check service status (- means not running, number is PID)
launchctl list | grep hermes

# Check exit code (second column: 0 = clean exit, other = error)
# PID    ExitCode  Label
# 6801   0         ai.hermes.gateway.crescent-city

# View logs
tail -f ~/path-to-instance/.hermes/logs/gateway.log
tail -f ~/path-to-instance/.hermes/logs/gateway.error.log

# Manual test (run interactively to see errors)
HERMES_HOME=/path/to/.hermes /Users/mini/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run 2>&1
```

## Related Documents

- [Multi-Instance](multi_instance.md) — Instance setup guide
- [Gateway](gateway.md) — Gateway architecture
- [Troubleshooting](troubleshooting.md) — Common issues
