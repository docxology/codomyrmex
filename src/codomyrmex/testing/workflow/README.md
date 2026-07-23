# workflow

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Module implementation, resources, and local coordination for Workflow. A non-passing
step stops the runner by default; use the explicit `continue_on_error=True` step
option only for workflows whose continuation policy is intentional. Script and
expression steps are trusted-workflow-only and are not a sandbox or remote shell.

## Directory Contents
- `PAI.md` – File
- `README.md` – File
- `SPEC.md` – File
- `__init__.py` – File
- `executors.py` – File
- `models.py` – File
- `py.typed` – File
- `runner.py` – File

## Navigation
- **Parent Directory**: [testing](../README.md)
- **Project Root**: ../../../../README.md

## Related Documents

- **Agents**: [AGENTS.md](AGENTS.md)
