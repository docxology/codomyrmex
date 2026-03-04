---
description: Use when needing to run GitNexus CLI commands to analyze/index a repo, build a knowledge graph, trace execution flows, and understand project architecture.
---

# GitNexus

Crossover workflow from the `gitnexus` Claude Code skill ecosystem. GitNexus builds and queries an intelligent codebase knowledge graph.

Read the full CLI skill:
`view_file /Users/mini/Documents/GitHub/codomyrmex/.claude/skills/gitnexus/gitnexus-cli/SKILL.md`

## 1. Local CLI Commands

All commands work via `npx` (no global install required).

```bash
npx gitnexus analyze     # Build or refresh the index. Run this first or after major changes.
npx gitnexus status      # Check index freshness and symbol counts.
npx gitnexus clean       # Delete the index to start fresh.
npx gitnexus wiki        # Generate repository documentation from the graph.
npx gitnexus list        # List all indexed repos.
```

## 2. Exploring Codebases (MCP Tools)

Use these MCP tools and resources after indexing to understand the codebase.

- **Resources:**
  - `gitnexus://repo/{name}/context` (overview)
  - `gitnexus://repo/{name}/clusters` (functional areas)
  - `gitnexus://repo/{name}/process/{name}` (step-by-step trace)

- **Tools:**
  - `gitnexus_query({query: "payment flow"})` → Find execution flows related to a concept.
  - `gitnexus_context({name: "functionName"})` → 360-degree view (callers, callees, processes).

## 3. Workflow Checklist

1. Run `npx gitnexus analyze` if the repository isn't indexed or is terribly stale.
2. `READ gitnexus://repo/{name}/context` for the broad overview.
3. Use `gitnexus_query` to find execution flows for the domain you care about.
4. Use `gitnexus_context` on the critical symbols discovered.
5. Trace step-by-step logic by reading `process` resources.
6. Verify and read the actual source implementation files.
