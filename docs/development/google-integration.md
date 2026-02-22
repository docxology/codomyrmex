# Google Integration

As part of our effort to adopt best practices from Google, we have integrated several Google libraries and tools into our development workflow. This document provides an overview of these integrations and how to use them.

## `absl-py`

We have integrated `absl-py` for command-line flag parsing. However, we have since transitioned to `python-fire` for our main CLI, so `absl-py` is no longer in use.

## `python-fire`

We use `python-fire` to automatically generate our command-line interface (CLI). The main CLI is defined in `src/codomyrmex/cli/core.py`. The `fire.Fire(Cli)` call at the end of the file exposes the `Cli` class as a CLI.

Each method in the `Cli` class corresponds to a command. For example, the `check` method can be called from the command line like this:

```bash
codomyrmex check
```

`python-fire` automatically generates help messages for the commands and their arguments. To see the help message for a command, you can use the `--help` flag:

```bash
codomyrmex check --help
```

## Pre-commit Hooks

We have refactored our pre-commit hooks to use `ruff` exclusively for linting and import sorting. This has simplified our toolchain and improved performance. `flake8` and `isort` have been removed from the pre-commit configuration and the project's dependencies.
