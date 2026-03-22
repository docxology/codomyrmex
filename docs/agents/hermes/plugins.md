# Hermes Plugin System

**Version**: v2.5.0 | **Last Updated**: March 2026

## Overview

The Hermes plugin system allows anyone to extend Hermes with third-party tools, custom skills, and gateway hooks — installed directly from Git repositories.

**Plugin directory**: `~/.hermes/plugins/` (respects `HERMES_HOME` env var)

---

## Commands

```bash
# Install from GitHub shorthand (owner/repo)
hermes plugins install owner/repo

# Install from full Git URL
hermes plugins install https://github.com/owner/repo.git
hermes plugins install git@github.com:owner/repo.git

# Update an installed plugin (git pull --ff-only)
hermes plugins update my-plugin

# Remove a plugin
hermes plugins remove my-plugin
hermes plugins rm my-plugin        # alias
hermes plugins uninstall my-plugin # alias

# List all installed plugins
hermes plugins list
hermes plugins ls                  # alias
```

After any install or remove, **restart the gateway** for changes to take effect:

```bash
hermes gateway restart
```

---

## Plugin Manifest (`plugin.yaml`)

Every plugin should ship a `plugin.yaml` at its repository root:

```yaml
name: my-plugin           # Used as the install directory name
version: 1.0.0
description: One-line description of what this plugin does
manifest_version: 1       # Schema version (currently always 1)
```

**`manifest_version`**: If a plugin declares a `manifest_version` higher than the installer supports, the install is aborted with an error suggesting `hermes update`.

If `plugin.yaml` is missing, the repo name is used as the plugin name.

---

## Install Flow

```
git clone --depth 1 <url> /tmp/plugin
    ↓
Read plugin.yaml → determine name
    ↓
Validate name (no path traversal)
    ↓
Check manifest_version compatibility
    ↓
Check for existing install (error unless --force)
    ↓
Move to ~/.hermes/plugins/<name>/
    ↓
Copy *.example → real filenames (skip existing)
    ↓
Render after-install.md (if present) via Rich
    ↓
Print: "hermes gateway restart"
```

### `--force` Flag

```bash
hermes plugins install owner/repo --force
```

If the plugin is already installed, `--force` removes and reinstalls it. Without `--force`, an existing plugin causes an error with a suggestion to use `hermes plugins update` instead.

---

## `after-install.md`

A plugin can ship an `after-install.md` file that is rendered as rich Markdown after a successful install. Use this to document:
- Required API keys or configuration
- How to enable the plugin in `config.yaml`
- First-run examples

If `after-install.md` is missing, a default confirmation panel is shown.

---

## Example Files (`*.example`)

Plugin config files ending in `.example` are automatically copied to their real names during install:

| Source | Destination |
|--------|-------------|
| `config.yaml.example` | `config.yaml` |
| `settings.json.example` | `settings.json` |

Files that already exist are **not overwritten** — safe to reinstall without losing customizations.

---

## Security

Plugin names are sanitized before use:
- Rejects names containing `/`, `\`, `..`
- Validates resolved path stays inside `~/.hermes/plugins/`
- `http://` and `file://` URL schemes trigger a security warning

---

## Update Flow

```bash
hermes plugins update my-plugin
```

Runs `git pull --ff-only` inside `~/.hermes/plugins/my-plugin/`. Requires the plugin to have been installed via `hermes plugins install` (`.git` directory must exist). Manual copies cannot be updated this way.

Also copies any new `.example` files added by the update.

---

## Plugin Directory Structure

```
~/.hermes/plugins/
└── my-plugin/
    ├── .git/               ← present if installed via hermes plugins install
    ├── plugin.yaml         ← manifest
    ├── after-install.md    ← post-install instructions (optional)
    ├── config.yaml         ← generated from config.yaml.example on install
    ├── config.yaml.example ← template
    └── __init__.py         ← plugin entry (optional)
```

---

## `HERMES_HOME` Override

By default, plugins are installed to `~/.hermes/plugins/`. Override via:

```bash
export HERMES_HOME=/path/to/custom/hermes
hermes plugins install owner/repo     # installs to /path/to/custom/hermes/plugins/
```

---

## Navigation

- [← Hermes README](../../../src/codomyrmex/agents/hermes/README.md)
- [@ Context References →](context-references.md)
- [Agent Cache →](agent-cache.md)
