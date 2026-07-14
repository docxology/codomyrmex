---
name: first-principles
description: Reduce an ambiguous technical problem to verified facts, constraints, and explicit decisions before proposing a solution.
---

# First-Principles Reasoning

Use this skill when a request is ambiguous, a design has accumulated assumptions, or a proposed fix feels like precedent rather than necessity.

1. State the desired outcome and the decision that must be made.
2. Separate observations, requirements, constraints, assumptions, and preferences.
3. Decompose the system into actors, inputs, transformations, outputs, and failure states.
4. Identify the smallest facts that would change the decision; verify those facts from the repository, tests, or authoritative sources.
5. Rebuild the solution from the verified facts. Preserve real constraints, but discard inherited process and terminology that do not serve the outcome.
6. Record trade-offs, unresolved uncertainty, and the cheapest useful next experiment.

Output a compact decision record with: objective, facts, constraints, assumptions, options considered, chosen design, risks, and verification evidence. Do not present an assumption as a fact.
