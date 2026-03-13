# External Skills & Slash Commands

**Version**: v1.2.2 | **Last Updated**: March 2026

> This document covers **external Claude Code skills** — markdown-prompt-based capabilities that extend Claude Code sessions. These are distinct from [Codomyrmex MCP tools](tools-reference.md) (Python modules exposed over the Model Context Protocol).

---

## What Are External Skills?

### Two Extension Mechanisms

PAI uses two separate extension mechanisms:

| Mechanism | Language | Discovery | Consumer | Examples |
|-----------|----------|-----------|----------|---------|
| **MCP Tools** | Python (`@mcp_tool`) | Auto-discovered via pkgutil | Any MCP client | `data_visualization`, `git_analysis`, `search` |
| **External Skills** | Markdown (SKILL.md) | Auto-loaded from `~/.claude/skills/` | Claude Code only | `visual-explainer`, `Codomyrmex`, `Research` |

**External skills** are installed as directories under `~/.claude/skills/`, each containing a `SKILL.md` file. Claude Code reads `SKILL.md` automatically when skills are listed, making the skill available via the `Skill` tool. They carry zero Python dependencies and require no MCP server.

### Slash Commands vs Skills

External skills may optionally ship **slash commands** — `.md` files placed in `~/.claude/commands/`. These become `/command-name` invocations in Claude Code sessions.

| Feature | Skill (SKILL.md) | Slash Command (commands/*.md) |
|---------|-----------------|-------------------------------|
| Activation | Immediate (current session) | Requires `/clear` or new session |
| Invocation | `Skill tool` or PAI auto-selects | `/command-name` typed in chat |
| Output | In-conversation | In-conversation |
| File type | Markdown (full instructions) | Markdown (focused prompt) |

---

## Installed Skills

### visual-explainer

**Source**: [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) · **Version**: v0.4.4 · **Stars**: 5.2k · **License**: MIT
**Installed**: March 3, 2026 · **Location**: `~/.claude/skills/visual-explainer/`

**Purpose**: Converts complex terminal output and structured data into styled, self-contained HTML pages — architecture diagrams, data tables, diff reviews, implementation plans, slide decks. Never falls back to ASCII art.

**Core Technology**:

| Library | Role | CDN |
|---------|------|-----|
| Mermaid.js v11 | Flowcharts, ER diagrams, state machines, sequences | `cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs` |
| Chart.js v4 | Bar/line/pie charts, dashboards | `cdn.jsdelivr.net/npm/chart.js` |
| CSS Grid + custom properties | Architecture cards, timelines | (inline CSS, no CDN) |
| anime.js v4 (optional) | Animated slide transitions | `cdn.jsdelivr.net/npm/animejs/dist/bundles/anime.umd.min.js` |
| Google Fonts | Typography pairs | `fonts.googleapis.com` |

**Output directory**: `~/.agent/diagrams/` (all HTML files written here, auto-opened in browser)

#### Slash Commands

All 7 commands are installed in `~/.claude/commands/`:

| Command | Purpose | Output |
|---------|---------|--------|
| `/generate-web-diagram` | Create an HTML diagram for any topic — flowchart, architecture, ER diagram, state machine, mind map | Self-contained `.html` |
| `/generate-visual-plan` | Visual implementation plan with state machines, code snippets, edge cases, test requirements | Self-contained `.html` |
| `/generate-slides` | Magazine-quality slide deck — 10 slide types, 100dvh per slide, no scroll | Self-contained `.html` |
| `/diff-review` | Before/after architecture comparison with code review analysis | Self-contained `.html` |
| `/plan-review` | Current codebase state vs. proposed implementation plan audit | Self-contained `.html` |
| `/project-recap` | Project mental model snapshot — recent decisions, key files, current state | Self-contained `.html` |
| `/fact-check` | Validate factual accuracy of a document against source code, correct inaccuracies | Edits source `.md` |

#### Aesthetic Directions

The skill follows strict anti-slop rules. Each diagram uses a **constrained aesthetic**:

| Aesthetic | Feel | Palette | Typography |
|-----------|------|---------|------------|
| **Blueprint** | Technical drawing | Deep slate/blue, grid background | IBM Plex Sans + IBM Plex Mono |
| **Editorial** | Serif, generous whitespace | Earth tones or deep navy + gold | Instrument Serif + JetBrains Mono |
| **Paper/ink** | Warm, informal | Cream `#faf7f5`, terracotta/sage | Plus Jakarta Sans + Azeret Mono |
| **IDE-inspired** | Named color schemes | Dracula, Nord, Catppuccin, Gruvbox | DM Sans + Fira Code |

**Forbidden patterns** (AI slop signals): Inter font + indigo/violet accents, gradient text on headings, emoji section headers, animated glowing box-shadows.

#### Content Routing Rules

| Content type | Rendered with | Reason |
|-------------|---------------|--------|
| Architecture (topology) | Mermaid `graph TD` | Automatic edge routing |
| Architecture (text-heavy, 15+ nodes) | CSS Grid cards + Mermaid overview | Mermaid unreadable at scale |
| Data tables (4+ rows or 3+ cols) | HTML `<table>` | Accessibility, copy-paste |
| Flowcharts, sequences | Mermaid | Automatic positioning |
| Dashboards, KPIs | Chart.js + CSS Grid | Canvas charts |

**Node limit**: Mermaid diagrams cap at 10–12 nodes. Use hybrid pattern (Mermaid overview + CSS Grid cards) for 15+ elements.

#### Known Limitations (v0.4.4)

- Mermaid rendering is fully client-side — requires internet for CDN fonts/libraries
- `surf-cli` (AI image generation) is optional; without it, hero images are omitted
- Special characters (`&`, `<`, `>`) in Mermaid node labels can silently break rendering — use HTML entities or avoid
- No server-side rendering; a browser is required to view output

#### Re-install Commands

```bash
# Install
git clone https://github.com/nicobailon/visual-explainer.git ~/.claude/skills/visual-explainer
mkdir -p ~/.claude/commands ~/.agent/diagrams
cp ~/.claude/skills/visual-explainer/prompts/*.md ~/.claude/commands/

# Update to latest
cd ~/.claude/skills/visual-explainer && git pull
cp prompts/*.md ~/.claude/commands/

# Register in skill-index.json (edit directly — no generator script exists)
# Edit ~/.claude/skills/skill-index.json and add entry under "skills" key
```

---

## Skill Installation Pattern

To add any `SKILL.md`-based external skill:

```bash
# 1. Clone to ~/.claude/skills/<skill-name>
git clone <repo-url> ~/.claude/skills/<skill-name>

# 2. (Optional) Copy slash command prompts
#    Only if the skill ships a prompts/ directory
cp ~/.claude/skills/<skill-name>/prompts/*.md ~/.claude/commands/

# 3. Create output directory (if needed)
mkdir -p ~/.agent/diagrams   # or whatever the skill uses

# 4. Update skill-index.json
#    Edit ~/.claude/skills/skill-index.json
#    Add entry to the "skills" dict with: name, path, fullDescription, triggers[], workflows[], tier
#    Note: GenerateSkillIndex.ts does NOT exist in PAI/Tools/ — edit JSON directly

# 5. Reload
#    Skill (SKILL.md) is active immediately in the current session
#    Slash commands require /clear or a new Claude Code session
```

### skill-index.json Entry Format

```json
"skill-name": {
  "name": "skill-name",
  "path": "skill-name/SKILL.md",
  "fullDescription": "One sentence: what it does and when to use it.",
  "triggers": ["keyword1", "keyword2", "..."],
  "workflows": ["workflow1", "workflow2"],
  "tier": "deferred"
}
```

`tier: "deferred"` means the skill loads on demand (when triggered). Use `tier: "alwaysLoaded"` only for skills needed on every prompt (e.g., PAI core).

---

## Notable Alternatives

Community skills in the same visual/diagram space:

| Skill | Approach | Key Differentiator |
|-------|----------|-------------------|
| [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) | HTML + Mermaid + Chart.js | Routes to right tech per content type; anti-slop aesthetic rules |
| [Anthropic frontend-design](https://github.com/anthropics/claude-code) | Brand-aware UI design | Anthropic official; 42 lines; production UI focus |
| [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill) | Excalidraw + Playwright | Self-inspects output via headless browser; fixes layout issues in a loop |
| [axtonliu/obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills) | Mermaid + Excalidraw + Obsidian canvas | 3-skill pack for Obsidian-centric workflows |
| [zolkos mermaid-validation-skill](https://www.zolkos.com/2025/11/26/mermaid-validation-skill-for-claude-code) | Mermaid syntax checking | Narrow validator; pairs with any diagramming skill as a gate |

---

## Navigation

- **Index**: [README.md](README.md)
- **Tools Reference**: [tools-reference.md](tools-reference.md)
- **Workflows**: [workflows.md](workflows.md)
- **On Ramp**: [on-ramp.md](on-ramp.md)
- **Root Bridge Doc**: [/PAI.md](../../PAI.md)
