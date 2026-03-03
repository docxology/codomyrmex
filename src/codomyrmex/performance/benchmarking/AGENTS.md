# AGENTS.md

As an AI agent working in the `performance/benchmarking` module:
- Ensure that benchmarks are deterministic where possible.
- When creating new benchmarks, ensure they are designed not to conflict with local system environment limits.
- Adhere to zero-mock policies for tests added here, triggering failure states via explicit, invalid types or parameter choices instead of monkeypatching.
