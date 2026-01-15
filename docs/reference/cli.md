# CLI Reference

This document provides a complete reference for all Codomyrmex command-line interface (CLI) commands and options.

## 📋 Overview

The Codomyrmex CLI provides convenient access to all major functionality through the `codomyrmex` command. The CLI is organized into logical subcommands for different operations.

### Installation Verification

```bash
# Check if CLI is properly installed
codomyrmex --version

# Get basic help
codomyrmex --help
```
 

## 🔧 Global Options

All commands accept the following global flags:

```bash
--verbose, -v     Enable verbose logging
--performance, -p Enable performance monitoring output where supported
```

## 🧭 Command Reference

### `codomyrmex check`
Run environment validation checks.

```bash
codomyrmex check
```

### `codomyrmex info`
Display high-level project information.

```bash
codomyrmex info
```

### `codomyrmex modules`
List available modules and their summaries.

```bash
codomyrmex modules
```

### `codomyrmex status`
Show the system status dashboard. Use the global `--performance` flag to include performance statistics.

```bash
codomyrmex status
codomyrmex --performance status
```

### `codomyrmex shell`
Launch the interactive Codomyrmex shell.

```bash
codomyrmex shell
```

### `codomyrmex workflow`
Manage orchestration workflows.

```bash
codomyrmex workflow list
codomyrmex workflow run <name> [--params JSON] [--async]
codomyrmex workflow create <name> [--template TEMPLATE]
```

- `list` — display registered workflows.
- `run` — execute a workflow with optional JSON parameters and asynchronous execution.
- `create` — create a workflow, optionally based on an existing template.

### `codomyrmex project`
Work with project definitions.

```bash
codomyrmex project list
codomyrmex project create <name> [--template TEMPLATE] [--description TEXT] [--path DIRECTORY]
```

### `codomyrmex orchestration`
Inspect orchestration engine status.

```bash
codomyrmex orchestration status
codomyrmex orchestration health
```

### `codomyrmex ai`
Access AI-powered helpers.

```bash
codomyrmex ai generate <prompt> [--language LANG] [--provider PROVIDER]
codomyrmex ai refactor <file> <instruction>
```

- `generate` — produce code for the supplied prompt, optionally selecting language and provider.
- `refactor` — request AI-driven refactoring for the given file and instruction.

### `codomyrmex analyze`
Run analysis tasks.

```bash
codomyrmex analyze code <path> [--output DIRECTORY]
codomyrmex analyze git [--repo PATH]
```

- `code` — run code-quality analysis for the specified path, optionally writing reports to `--output`.
- `git` — analyze a repository (defaults to the current directory unless `--repo` is provided).

### `codomyrmex build`
Execute build automation.

```bash
codomyrmex build project [--config FILE]
```

### `codomyrmex module`
Operate on individual modules.

```bash
codomyrmex module test <module_name>
codomyrmex module demo <module_name>
```

- `test` — run the module's tests.
- `demo` — execute the module's demo routine when available.

---

**Version**: 0.1.0  
**Last Updated**: Aligned with current CLI implementation  
**Support**: See [Troubleshooting Guide](troubleshooting.md) or [GitHub Issues](https://github.com/codomyrmex/codomyrmex/issues)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
