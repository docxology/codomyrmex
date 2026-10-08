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
codomyrmex workflow run <name> [--params JSON]
codomyrmex workflow create <name> [--template TEMPLATE]
```

Workflows live in `config/workflows/production/*.json` under the current
directory (see [config/workflows](../../config/workflows/README.md) for the
file format), so a workflow created by one command is listed and run by later
ones started in the same directory.

- `list` — show each workflow's step count, modules and definition file.
- `run` — run the workflow's steps through the task orchestrator and print each
  step's outcome. `--params` is a JSON object merged into every step's
  parameters.
- `create` — save a new workflow from a template: `basic` (default),
  `ai-analysis` or `build-and-test` (underscores are accepted). An existing
  workflow of the same name is not replaced; the name must be usable as a file
  name.

### `codomyrmex project`

Work with project definitions.

```bash
codomyrmex project list
codomyrmex project create <name> [--template TEMPLATE] [--description TEXT] [--path DIRECTORY]
```

- `create` — scaffold `./<name>/` (so the name must be a plain directory
  name) or `--path DIRECTORY` with `src/`, `tests/`,
  `config/`, `docs/` and generated README/AGENTS files, and save
  `project.json` in it. `--template` is a project type: `ai_analysis`
  (default), `web_application`, `data_pipeline`, `ml_model`, `documentation`,
  `research` or `custom`; hyphens are accepted.
- `list` — show the projects saved as `*/project.json` under the current
  directory. A project created with `--path` elsewhere is listed from its
  parent directory.

These commands print errors (unknown template, existing workflow or project,
failed step) but currently exit with status 0 either way.

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

Module names are single package identifiers (for example, `concurrency`),
not filesystem paths. Test execution is bounded to 120 seconds by default;
set `CODOMYRMEX_MODULE_TEST_TIMEOUT` to a positive value when a larger local
budget is needed (values above 900 seconds are capped).

---

**Version**: 0.1.0 |
**Last Updated**: Aligned with current CLI implementation |
**Support**: See [Troubleshooting Guide](troubleshooting.md) or [GitHub Issues](https://github.com/docxology/codomyrmex/issues)

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Repository Root](../../README.md)
