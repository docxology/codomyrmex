# Personal AI Infrastructure - Utils Context

## Why this exists

The `utils` module exists to enforce **standardization by default**. In early versions of Codomyrmex, every script reinvented logging, argument parsing, and error handling. This led to:

1. Inconsistent logs (some JSON, some text, some missing).
2. Uncatchable errors (scripts crashing without trace).
3. Configuration drift (hardcoded paths vs env vars).

`ScriptBase` solves this by forcing a "golden path".

## AI Context

As an AI, when you write code for Codomyrmex:

1. **Read `script_base.py`**: It is your best friend. It minimizes the code you need to generate.
2. **Use the Wrappers**: `utils.run_command` allows you to execute commands "safely" - meaning if they stall or fail, the system catches it and reports it structuredly, rather than hanging effectively forever or crashing silently.

## Key Decisions

- **Unified Config**: We merged CLI, Env, and File config into one `ScriptConfig` object to make "configuration precedence" explicit and debuggable.
- **Fail-Safe Logging**: The logging setup in `ScriptBase` includes a fallback if the main `logging_monitoring` module is broken, ensuring we *always* get output.

## Future Direction

- **Remote Execution**: We plan to extend `ScriptBase` to allow scripts to run remotely via the `orchestrator` without changing the script code.
