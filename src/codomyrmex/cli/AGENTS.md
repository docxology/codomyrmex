# Agent Guidelines - CLI

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Command-line interface framework with argument parsing and subcommands.

## Key Classes

- **CLI** — Main CLI application
- **Command** — Command definition
- **Option** — Command-line options
- **Argument** — Positional arguments

## Agent Instructions

1. **Use subcommands** — Group related commands
2. **Add help text** — Describe every option
3. **Exit codes** — Return proper exit codes
4. **Progress output** — Show progress for long ops
5. **Configuration** — Support config files

## Common Patterns

```python
from codomyrmex.cli import CLI, Command, Option, Argument

cli = CLI(name="myapp", version="1.0.0")

@cli.command()
@Option("--verbose", "-v", is_flag=True)
@Argument("name")
def greet(name: str, verbose: bool):
    \"\"\"Greet a user.\"\"\"
    if verbose:
        print(f"Verbose mode enabled")
    print(f"Hello, {name}!")

@cli.group()
def users():
    \"\"\"User management commands.\"\"\"
    pass

@users.command()
def list():
    \"\"\"List all users.\"\"\"
    for user in get_users():
        print(user.name)

if __name__ == "__main__":
    cli.run()
```

## Testing Patterns

```python
from codomyrmex.cli.testing import CliRunner

runner = CliRunner()

result = runner.invoke(cli, ["greet", "World"])
assert result.exit_code == 0
assert "Hello, World!" in result.output

result = runner.invoke(cli, ["--help"])
assert "Usage:" in result.output
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | Direct Python import, class instantiation, full API access | TRUSTED |
| **Architect** | Read + Design | API review, command structure design, dependency analysis | OBSERVED |
| **QATester** | Validation | Integration testing via pytest, CLI behavior validation | OBSERVED |

### Engineer Agent
**Use Cases**: Build CLI commands and subcommands, implement argument parsing, full implementation access during BUILD/EXECUTE phases

### Architect Agent
**Use Cases**: Review command hierarchy structure, validate CLI UX patterns, design subcommand grouping

### QATester Agent
**Use Cases**: Validate CLI exit codes, verify help text output, test argument parsing edge cases via CliRunner

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
