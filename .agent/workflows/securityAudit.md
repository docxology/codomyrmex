---
description: Run a Trail of Bits-style security audit using Claude Code skills. Covers audit context building, static analysis, sharp edges, variant analysis, and supply chain risk.
---

# Security Audit (Trail of Bits Methodology)

Crossover workflow bridging Trail of Bits Claude Code skills into Antigravity IDE. Read the relevant SKILL.md files on-demand for full instructions.

## Phase 1: Deep Context Building

Read the full skill before starting:

```
view_file ~/.claude/plugins/cache/trailofbits/audit-context-building/1.1.0/skills/audit-context-building/SKILL.md
```

1. Perform **line-by-line / block-by-block** code analysis
2. Apply **First Principles**, **5 Whys**, and **5 Hows** at micro scale
3. Map: modules → entrypoints → actors → state variables
4. Per-function: Purpose → Inputs → Outputs → Block-by-Block → Cross-Function Dependencies
5. Build global mental model: state invariants, trust boundaries, workflow reconstruction

**Quality thresholds**: Min 3 invariants/function, 5 assumptions documented, 3 risk considerations for external interactions.

## Phase 2: Static Analysis (Semgrep)

Read the full skill:

```
view_file ~/.claude/plugins/cache/trailofbits/static-analysis/1.2.0/skills/semgrep/SKILL.md
```

1. Detect languages with file counts
2. Check Semgrep Pro availability: `semgrep --pro --validate --config p/default 2>/dev/null`
3. Select scan mode: "run all" or "important only"
4. Include third-party rulesets (Trail of Bits, 0xdea, Decurity)
5. **Always use `--metrics=off`**
6. Merge SARIF output

## Phase 3: Sharp Edges Analysis

Read the full skill:

```
view_file ~/.claude/plugins/cache/trailofbits/sharp-edges/1.0.0/skills/sharp-edges/SKILL.md
```

Check for: algorithm/mode selection footguns, dangerous defaults, primitive vs semantic APIs, configuration cliffs, silent failures, stringly-typed security.

Model three adversaries: **The Scoundrel** (malicious), **The Lazy Developer** (copy-paste), **The Confused Developer** (misunderstands API).

## Phase 4: Variant Analysis

Read the full skill:

```
view_file ~/.claude/plugins/cache/trailofbits/variant-analysis/1.0.0/skills/variant-analysis/SKILL.md
```

Five-step process: Understand original → Exact match → Identify abstraction points → Iteratively generalize → Analyze and triage.

## Phase 5: Supply Chain Risk

Read the full skill:

```
view_file ~/.claude/plugins/cache/trailofbits/supply-chain-risk-auditor/1.0.0/skills/supply-chain-risk-auditor/SKILL.md
```

Evaluate: single maintainer, unmaintained, low popularity, high-risk features (FFI, deserialization), past CVEs, missing security contact.
