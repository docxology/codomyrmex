# Hermes Sentinel Recommendations Hub

This directory is an autonomous staging ground for **Hermes Sentinel** findings. 

## Workflow

1.  **Sentinel** monitors the codebase and saves `REC_YYYYMMDD_HHMMSS.md` files here.
2.  **Collaborating Agents** (or the User) review these recommendations.
3.  Implementations are tracked via `hermes_create_task` or direct edits.
4.  Once implemented or triaged as invalid, the recommendation file is deleted.

---
*Self-Aware Remediation Loop v2.3.0*
