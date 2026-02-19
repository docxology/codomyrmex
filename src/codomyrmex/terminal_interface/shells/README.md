# Shells

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Terminal shell management utilities. Provides abstractions for executing commands in various shells (bash, zsh, fish, etc.), interactive shell sessions with bidirectional I/O, and a fluent command builder with piping and redirection support.

## Key Exports

### Enums

- **`ShellType`** -- Supported shell types: BASH, ZSH, SH, FISH, POWERSHELL, CMD

### Configuration and Results

- **`ShellConfig`** -- Shell configuration with type, executable path, args, environment, working directory, and timeout; includes `detect()` class method to auto-detect the system default shell
- **`CommandResult`** -- Result of command execution with exit code, stdout, stderr, duration, and `success` property

### Shell Implementations

- **`Shell`** -- Standard shell for executing commands synchronously or in background:
  - `run(command, timeout, env, cwd)` -- Execute and wait for completion
  - `run_background(command, env, cwd)` -- Launch a background process
  - `get_history()` / `clear_history()` -- Command execution audit trail
- **`InteractiveShell`** -- Persistent interactive shell session with:
  - `start()` / `stop()` -- Lifecycle management
  - `send(command)` -- Send command to stdin
  - `read_output(timeout)` -- Read available stdout
  - `execute(command, timeout)` -- Send and read in one call
  - Background reader thread for non-blocking output collection

### Command Builder

- **`CommandBuilder`** -- Fluent builder for constructing shell commands with:
  - `add(*args)` / `flag(name, value)` -- Append arguments and flags
  - `env(key, value)` -- Prepend environment variables
  - `pipe(command)` -- Pipe output to another command
  - `redirect_stdout(path)` / `redirect_stderr(path)` -- I/O redirection
  - `background()` -- Append background operator
  - `build()` -- Produce the final command string with proper quoting

### Factory

- **`create_shell()`** -- Factory to create a Shell instance, optionally for a specific ShellType

## Directory Contents

- `__init__.py` - All shell classes, builder, and factory (378 lines)
- `interactive_shell.py` - Additional interactive shell utilities
- `py.typed` - PEP 561 type stub marker

## Usage

```python
from codomyrmex.terminal_interface.shells import Shell, CommandBuilder, create_shell

# Quick command execution
shell = create_shell()
result = shell.run("ls -la /tmp", timeout=5.0)
print(result.stdout if result.success else result.stderr)

# Build complex commands
cmd = (CommandBuilder("grep")
    .flag("-r", "TODO")
    .add("src/")
    .pipe("wc -l")
    .build())
# => "grep -r TODO src/ | wc -l"
result = shell.run(cmd)
```

## Navigation

- **Parent Module**: [terminal_interface](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
