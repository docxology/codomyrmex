# Agent Memory Script

## Purpose

`run_memory.py` is a small local probe for the `codomyrmex.agents.memory`
subpackage. It configures project logging, imports the package, reports the
number of public exports, and prints a bounded sample for interactive diagnosis.

## Usage

From the repository root:

```bash
uv run python scripts/agents/memory/run_memory.py
```

The probe does not persist memory, contact external providers, or validate the
semantic quality of stored memories.

## Navigation

- [Agent guidance](AGENTS.md)
- [Parent scripts/agents directory](../README.md)
