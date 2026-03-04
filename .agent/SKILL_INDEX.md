# Claude Code Skills → Antigravity IDE Crossover Index

All 32 Claude Code plugins and their SKILL.md paths. **Antigravity can read any skill on demand with `view_file`.**

## Workflow Bridges (Auto-Loaded)

These workflows in `.agent/workflows/` are auto-detected by Antigravity:

| Slash Command | Source | Description |
|:---|:---|:---|
| `/securityAudit` | Trail of Bits | Full security audit: context-building → static analysis → sharp edges → variant analysis → supply chain |
| `/modernPython` | Trail of Bits | Modern Python with uv, ruff, ty |
| `/tdd` | Superpowers | Test-Driven Development: red-green-refactor |
| `/systematicDebugging` | Superpowers | Root cause investigation before fixes |
| `/propertyBasedTesting` | Trail of Bits | Hypothesis-style property testing |

---

## Full Plugin → SKILL.md Path Map

### 🏛️ Anthropics Official

**document-skills** — PDF, DOCX, PPTX, XLSX extraction:

```
~/.claude/plugins/cache/anthropic-agent-skills/document-skills/3d5951151859/skills/*/SKILL.md
```

**example-skills** — Creative, design, technical demos:

```
~/.claude/plugins/cache/anthropic-agent-skills/example-skills/3d5951151859/skills/*/SKILL.md
```

---

### 🏗️ Superpowers (v4.3.1)

| Skill | Path |
|:---|:---|
| brainstorming | `~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1/skills/brainstorming/SKILL.md` |
| dispatching-parallel-agents | `…/skills/dispatching-parallel-agents/SKILL.md` |
| executing-plans | `…/skills/executing-plans/SKILL.md` |
| finishing-a-development-branch | `…/skills/finishing-a-development-branch/SKILL.md` |
| receiving-code-review | `…/skills/receiving-code-review/SKILL.md` |
| requesting-code-review | `…/skills/requesting-code-review/SKILL.md` |
| subagent-driven-development | `…/skills/subagent-driven-development/SKILL.md` |
| **systematic-debugging** | `…/skills/systematic-debugging/SKILL.md` |
| **test-driven-development** | `…/skills/test-driven-development/SKILL.md` |
| using-git-worktrees | `…/skills/using-git-worktrees/SKILL.md` |
| using-superpowers | `…/skills/using-superpowers/SKILL.md` |
| verification-before-completion | `…/skills/verification-before-completion/SKILL.md` |
| writing-plans | `…/skills/writing-plans/SKILL.md` |
| writing-skills | `…/skills/writing-skills/SKILL.md` |

Base: `~/.claude/plugins/cache/superpowers-marketplace/superpowers/4.3.1`

**elements-of-style**: `…/elements-of-style/1.0.0/skills/writing-clearly-and-concisely/SKILL.md`

**developing-for-claude-code**: `…/superpowers-developing-for-claude-code/0.3.1/skills/*/SKILL.md`

---

### 🔐 Trail of Bits

| Plugin | Skill(s) | Key Path |
|:---|:---|:---|
| audit-context-building | 1 | `…/trailofbits/audit-context-building/1.1.0/skills/audit-context-building/SKILL.md` |
| static-analysis | codeql, semgrep, sarif-parsing | `…/trailofbits/static-analysis/1.2.0/skills/{codeql,semgrep,sarif-parsing}/SKILL.md` |
| variant-analysis | 1 | `…/trailofbits/variant-analysis/1.0.0/skills/variant-analysis/SKILL.md` |
| supply-chain-risk-auditor | 1 | `…/trailofbits/supply-chain-risk-auditor/1.0.0/skills/supply-chain-risk-auditor/SKILL.md` |
| sharp-edges | 1 | `…/trailofbits/sharp-edges/1.0.0/skills/sharp-edges/SKILL.md` |
| differential-review | 1 | `…/trailofbits/differential-review/1.0.0/skills/differential-review/SKILL.md` |
| testing-handbook-skills | 15 | `…/trailofbits/testing-handbook-skills/1.0.1/skills/*/SKILL.md` |
| semgrep-rule-creator | 1 | `…/trailofbits/semgrep-rule-creator/1.1.0/skills/semgrep-rule-creator/SKILL.md` |
| modern-python | 1 | `…/trailofbits/modern-python/1.5.0/skills/modern-python/SKILL.md` |
| property-based-testing | 1 | `…/trailofbits/property-based-testing/1.1.0/skills/property-based-testing/SKILL.md` |
| insecure-defaults | 1 | `…/trailofbits/insecure-defaults/1.0.0/skills/insecure-defaults/SKILL.md` |
| agentic-actions-auditor | 1 | `…/trailofbits/agentic-actions-auditor/1.2.0/skills/agentic-actions-auditor/SKILL.md` |
| skill-improver | 1 | `…/trailofbits/skill-improver/1.0.0/skills/skill-improver/SKILL.md` |
| second-opinion | 1 | `…/trailofbits/second-opinion/1.6.0/skills/second-opinion/SKILL.md` |
| gh-cli | hooks-only | No SKILL.md (hooks-based plugin) |

Base: `~/.claude/plugins/cache/trailofbits`

---

### 🔄 Levnikolaevich (108 skills each)

**full-development-workflow-skills**: `~/.claude/plugins/cache/levnikolaevich-skills-marketplace/full-development-workflow-skills/cf48cc94b99b/`

Key skills: `ln-100-documents-pipeline`, `ln-200-scope-decomposer`, `ln-400-story-executor`, `ln-620-codebase-auditor`, `ln-700-project-bootstrap`, `ln-760-security-setup`

**claude-code-bootstrap**: Same base path under `claude-code-bootstrap/cf48cc94b99b/`

---

### 🧩 Alirezarezvani

**engineering-advanced-skills** (26): `~/.claude/plugins/cache/claude-code-skills/engineering-advanced-skills/1.1.0/*/SKILL.md`

Key: `tech-debt-tracker`, `performance-profiler`, `rag-architect`, `mcp-server-builder`, `dependency-auditor`, `ci-cd-pipeline-builder`, `skill-security-auditor`

**engineering-skills** (21): `…/engineering-skills/1.0.0/*/SKILL.md`

Key: `senior-architect`, `senior-backend`, `senior-security`, `code-reviewer`, `incident-commander`

**c-level-skills** (2): `…/c-level-skills/1.0.0/*/SKILL.md`

---

### 🧰 Daymade

Base: `~/.claude/plugins/cache/daymade-skills`

| Plugin | Path |
|:---|:---|
| skill-creator | `…/skill-creator/1.4.1/skills/skill-creator/SKILL.md` |
| github-ops | `…/github-ops/1.0.0/skills/github-ops/SKILL.md` |
| qa-expert | `…/qa-expert/1.0.0/skills/qa-expert/SKILL.md` |
| prompt-optimizer | `…/prompt-optimizer/1.1.0/skills/prompt-optimizer/SKILL.md` |
| capture-screen | `…/capture-screen/1.0.0/skills/capture-screen/SKILL.md` |
| deep-research | `…/deep-research/1.0.0/skills/deep-research/SKILL.md` |
| mermaid-tools | `…/mermaid-tools/1.0.0/skills/mermaid-tools/SKILL.md` |

---

## How Antigravity Uses These Skills

1. **Auto-triggered workflows**: `/securityAudit`, `/modernPython`, `/tdd`, `/systematicDebugging`, `/propertyBasedTesting` — summarized instructions with `view_file` references to full SKILL.md
2. **On-demand full instructions**: Use `view_file <path>` on any SKILL.md above to load the complete skill into context
3. **Keyword match**: Ask Antigravity to "do a security audit" or "use TDD" and it will find the matching workflow
