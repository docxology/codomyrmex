---
name: red-team
description: Adversarially test a design, implementation, agent workflow, or tool surface for realistic failure and abuse paths within authorized scope.
---

# Red-Team Review

Use this skill for security, reliability, permission, prompt-injection, data-loss, or operational-risk review. Work only within the explicitly authorized repository and systems.

1. Define the asset, trust boundaries, attacker or failure capabilities, and out-of-scope actions.
2. Enumerate plausible abuse and failure paths, including malformed input, confused-deputy behavior, excessive permissions, stale state, partial failure, and misleading success signals.
3. Exercise the highest-risk paths with the least invasive reproducible checks. Prefer real components and fixtures over mocks.
4. For every finding, capture evidence, preconditions, impact, likelihood, severity, and a narrowly scoped mitigation.
5. Re-test the mitigation and distinguish confirmed findings from hypotheses.

Report findings first, ordered by risk. Include “not exploitable under current scope” when a tempting path was checked and rejected. Never turn a red-team review into an unauthorized destructive action.
