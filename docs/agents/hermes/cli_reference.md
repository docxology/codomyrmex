# Hermes CLI Commands Reference

**Source**: [hermes-agent.nousresearch.com/docs/reference/cli-commands](https://hermes-agent.nousresearch.com/docs/reference/cli-commands)

> Verified against official Hermes docs, March 2026.

## Terminal Commands

### Core

```bash
hermes                              # Start interactive chat
hermes chat -q "prompt"             # One-shot query
hermes chat --continue              # Resume last session (-c)
hermes chat -c "project-name"       # Continue named session
hermes chat --resume <id>           # Resume by session ID (-r)
hermes chat --model <name>          # Override model
hermes chat --provider <name>       # Override provider (nous|openrouter|zai|kimi-coding|minimax|minimax-cn)
hermes chat --toolsets "web,term"   # Limit tool categories (-t)
hermes chat --verbose               # Verbose output
hermes --worktree                   # Git worktree isolation (-w)
hermes --checkpoints                # Enable checkpoints
```

### Provider & Model Management

```bash
hermes model                        # Interactive model selection
hermes login                        # Auth with Nous Portal (OAuth)
hermes logout                       # Clear Nous Portal auth
```

### Configuration

```bash
hermes setup                        # Full interactive wizard
hermes config                       # View current configuration
hermes config edit                  # Open config.yaml in $EDITOR
hermes config set KEY VAL           # Set a value (auto-routes keys→.env, rest→config.yaml)
hermes config check                 # Check for missing options after updates
hermes config migrate               # Interactively add missing options
hermes tools                        # Manage which toolsets are enabled
hermes status                       # Quick status overview
hermes doctor                       # Full system diagnostics
```

### Maintenance

```bash
hermes update                       # Self-update (git pull + pip install)
hermes version                      # Show version
hermes uninstall                    # Full uninstall
```

### Gateway (Messaging + Cron)

```bash
hermes gateway                      # Gateway status overview
hermes gateway setup                # Configure messaging platforms
hermes gateway install              # Install as system service (launchd/systemd)
hermes gateway start                # Start the service
hermes gateway stop                 # Stop the service
hermes gateway restart              # Restart the service
hermes gateway run                  # Run in foreground
hermes gateway run --replace        # Run, replacing stale PID
hermes gateway status               # Check running status
hermes gateway uninstall            # Remove system service
hermes whatsapp                     # WhatsApp QR pairing
```

### Skills

```bash
hermes skills browse                # Browse Skills Hub (agentskills.io)
hermes skills search <query>        # Search skills
hermes skills install <identifier>  # Install a skill
hermes skills inspect <identifier>  # Inspect skill details
hermes skills list                  # List installed skills
hermes skills list --source hub     # List Hub skills
hermes skills audit                 # Audit installed skills
hermes skills uninstall <name>      # Remove a skill
hermes skills publish <path> --to github --repo owner/repo
hermes skills snapshot export <file>   # Export skill snapshot
hermes skills snapshot import <file>   # Import skill snapshot
hermes skills tap add <repo>           # Add skill tap (custom registry)
hermes skills tap remove <repo>        # Remove skill tap
hermes skills tap list                 # List taps
```

### Cron & Pairing

```bash
hermes cron list                    # List scheduled jobs
hermes cron status                  # Cron system status
hermes cron tick                    # Manually trigger cron tick
hermes pairing list                 # List pending pairing requests
hermes pairing approve <platform> <code>    # Approve pairing
hermes pairing revoke <platform> <user_id>  # Revoke access
hermes pairing clear-pending        # Clear all pending requests
```

### Sessions

```bash
hermes sessions list                # List all sessions
hermes sessions rename <id> <title> # Rename a session
hermes sessions export <id>         # Export session JSON
hermes sessions delete <id>         # Delete a session
hermes sessions prune               # Clean old sessions
hermes sessions stats               # Session statistics
```

### Insights

```bash
hermes insights                     # Usage analytics overview
hermes insights --days 7            # Last N days
hermes insights --source telegram   # Platform-specific analytics
```

## Slash Commands (Inside Chat)

### Navigation & Control

| Command | Description |
|:---|:---|
| `/help` | Show all commands |
| `/exit` or `/quit` | End chat |
| `/new` | Start new session |
| `/save` | Save current session |
| `/load <id>` | Load a session |
| `/undo` | Undo last message |

### Tools & Configuration

| Command | Description |
|:---|:---|
| `/tools` | List available tools |
| `/toolsets` | Manage active tool categories |
| `/model <name>` | Switch model |
| `/provider <name>` | Switch provider |
| `/verbose` | Toggle verbose mode |
| `/reasoning <level>` | Set reasoning effort |

### Conversation

| Command | Description |
|:---|:---|
| `/clear` | Clear conversation history |
| `/summary` | Summarize current context |
| `/context` | Show context window usage |
| `/branch` | Branch conversation |

### Media & Input

| Command | Description |
|:---|:---|
| `/image <path>` | Send image for vision analysis |
| `/file <path>` | Attach file to context |
| `/voice` | Start voice input |
| `/speak` | Toggle TTS output |

### Skills & Scheduling

| Command | Description |
|:---|:---|
| `/skills` | List/manage skills |
| `/skill <name>` | Run a skill |
| `/cron` | Manage scheduled tasks |
| `/delegate <task>` | Spawn subagent |

### Gateway-Only

| Command | Description |
|:---|:---|
| `/pair` | Start pairing flow |
| `/unpair` | Remove pairing |
| `/status` | Bot status |

## Navigation

- [Setup Guide](setup_guide.md) — Complete installation
- [Configuration](configuration.md) — config.yaml reference
- [Gateway](gateway.md) — Messaging gateway
- [README](README.md) — Documentation index
