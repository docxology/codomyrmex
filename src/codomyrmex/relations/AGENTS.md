# Relations Agents

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agents for managing public relations, customer support, and networking.

## Agents

### `PRManager` (Social Media)

- **Role**: Manages public image and outreach.
- **Capabilities**: `draft_press_release`, `schedule_post`, `analyze_sentiment`.

### `SalesAgent` (CRM)

- **Role**: Manages leads and deals.
- **Capabilities**: `qualify_lead`, `update_deal`, `track_interaction`.

### `NetworkerAgent` (Network Analysis)

- **Role**: Identifies strategic connections.
- **Capabilities**: `find_path_to_contact`, `recommend_introduction`.

## Tools

| Tool | Agent | Description |
| :--- | :--- | :--- |
| `search_contacts` | SalesAgent | Find CRM entry |
| `publish_tweet` | PRManager | Post to X (Twitter) |

## Integration

These agents integrate with `codomyrmex.agents.core` and use the MCP protocol for tool access.

## Navigation

- [README](README.md) | [SPEC](SPEC.md)
