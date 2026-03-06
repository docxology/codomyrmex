# Email Module Demos Specification

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demonstrates usage of the email module including GmailProvider and AgentMailProvider for sending, receiving, and managing email messages.

## Functional Requirements

- **orchestrator.py**: Runs AgentMail and Gmail provider demos with message sending and inbox management


## Execution

**Prerequisites:**
```bash
uv sync (requires AGENTMAIL_API_KEY or GMAIL credentials)
```

**Run:**
```bash
uv run python scripts/email/orchestrator.py
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
