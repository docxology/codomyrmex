# Active Hermes Instances

Full status of all running Hermes instances. Last updated: 2026-03-13 10:20 AM PDT

---

## Instance 1: MAIN

| Property | Value |
|----------|-------|
| HERMES_HOME | `~/.hermes` |
| Gateway PID | 7078 |
| Model | `openrouter/hunter-alpha` |
| Provider | OpenRouter |
| Telegram Bot | @hermes_tele_bot (ID: 8626408153) |
| Telegram Home | @ActiveInference |
| Sessions | 274 |
| Skills | 24 |
| Memories | 2 |
| Working Dir | `.` (current) |
| Reasoning | medium |
| Toolsets | all |

### Cron Jobs (5)
1. **Daily Self-Improvement Review** — `0 1 * * *` (1 AM) — Review interactions, save insights
2. **Daily Codomyrmex Analysis** — `0 2 * * *` (2 AM) — Repo health, git analysis, MCP tools
3. **Deep Codomyrmex Module Study** — `0 3 * * *` (3 AM) — Systematic module examination
4. **Codomyrmex Review Session** — `0 */6 * * *` (every 6h) — Module/skills/tools overview
5. **Codomyrmex Self-Improvement** — `0 1 * * *` (1 AM) — Repo summary, test status, changes

### Purpose
Primary assistant for Daniel (docxology). Full codomyrmex sidekick with all capabilities.

---

## Instance 2: CRESCENT CITY

| Property | Value |
|----------|-------|
| HERMES_HOME | `~/hermes-crescent-city/.hermes` |
| Gateway PID | 6801 |
| Model | `nvidia/nemotron-3-super-120b-a12b:free` (free tier) |
| Provider | OpenRouter |
| Telegram Bot | @another_cc_bot (ID: 8754235534) |
| Sessions | 10 |
| Skills | 23 |
| Memories | 1 |
| Personality | `civic_technical_analyst` |
| Reasoning | medium |
| Toolsets | all |

### Cron Jobs (5)
1. **Continuous Improvement (1)** — every 15m — Run work_iteration.py
2. **Continuous Improvement (2)** — every 15m — Run work_iteration.py
3. **Continuous Improvement (3)** — every 15m — Run work_iteration.py
4. **6-Hour Summary (1)** — every 360m — Run summary_job.py
5. **6-Hour Summary (2)** — every 360m — Run summary_job.py

### Purpose
Civic technical analysis with continuous improvement cycles. Free model tier for always-on operation.

---

## Instance 3: TEMPLATE BOT

| Property | Value |
|----------|-------|
| HERMES_HOME | `~/hermes-template-bot/.hermes` |
| Gateway PID | 26318 |
| Model | `openrouter/hunter-alpha` |
| Provider | OpenRouter |
| Telegram Bot | @a_template_bot (ID: 8340130112) |
| Telegram Home | @ActiveInference |
| Sessions | 2 |
| Skills | 22 |
| Memories | 1 |
| Personality | `template_architect` |
| Working Dir | `~/Documents/GitHub/codomyrmex/hermes-templates/` |
| Reasoning | medium |
| Toolsets | all |

### Cron Jobs
None yet.

### Purpose
Self-modifying template architect. Maintains hermes-templates/ as the reference for spawning new instances. Evolves templates based on learnings.

---

## Summary

| Instance | Model | PID | Sessions | Telegram | Status |
|----------|-------|-----|----------|----------|--------|
| Main | hunter-alpha | 7078 | 274 | @hermes_tele_bot | ✓ Running |
| Crescent City | nemotron-free | 6801 | 10 | @another_cc_bot | ✓ Running |
| Template Bot | hunter-alpha | 26318 | 2 | @a_template_bot | ✓ Running |

**Total:** 3 instances, 286 sessions, 3 unique Telegram bots, all non-overlapping via separate HERMES_HOME namespaces.

## Related Skills

- `devops/hermes-isolated-agent-setup` — Procedure for creating isolated instances
- `autonomous-ai-agents/hermes-agent` — Spawning hermes as subprocess (one-shot or interactive PTY)
- `codomyrmex/codomyrmex-hermes-best-practices` — Integration patterns for codomyrmex sidekick
- `mlops/training/hermes-atropos-environments` — RL environments for Hermes agent training
