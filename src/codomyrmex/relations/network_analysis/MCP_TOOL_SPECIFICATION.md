# relations/network_analysis — MCP Tool Specification

## Overview

In-memory social graph utilities. Auto-discovered from [`mcp_tools.py`](mcp_tools.py). Category: `relations_network_analysis`.

## Tool: `network_analysis_add_edge`

| Parameter | Type | Required | Default | Description |
|:----------|:-----|:---------|:--------|:------------|
| `source` | string | Yes | — | Entity id |
| `target` | string | Yes | — | Entity id |
| `weight` | float | No | `1.0` | Edge weight |

## Tool: `network_analysis_calculate_centrality`

No parameters. **Returns:** `centrality_scores` map.

## Tool: `network_analysis_find_communities`

No parameters. **Returns:** `communities` (lists of entity ids), `count`.

## Navigation

- **Parent**: [relations](../README.md)
- **Project root**: [README.md](../../../../README.md)
