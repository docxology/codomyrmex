# Formal Verification — Security Considerations

## Model evaluation

The Z3 backend interprets a restricted Python AST; it does not execute items
with Python `exec()`. Model expressions may use explicitly approved Z3
constructors, symbolic operators, quantifiers, arrays and bitvectors. Solver
and optimizer objects expose only model-building methods. Calls through aliases
must meet the same capability checks.

Module traversal, private attributes, native handles, low-level `Z3_*`
bindings, filesystem parsers, Z3 log files and global configuration are rejected.
The full Z3 package is not a general callable namespace. New model capabilities
require explicit review and positive and negative regression tests.

## Isolation and resource limits

The solver timeout (default 30 seconds) bounds the solver's check operation.
It does not bound AST parsing, Python arithmetic, expression construction,
memory use, or native-library failures. This evaluator is not a process or
operating-system sandbox. Large expressions can exhaust resources before the
solver starts.

Do not expose the stateful MCP model tools to untrusted external inputs without
separate process isolation, memory and execution limits, and access control.
Review constraint strings in security-sensitive workflows. A SAT result is a
statement about the supplied constraints, not proof of their origin or intent.

## Dependencies

- `z3-solver`: Native solver wheels from PyPI (Microsoft Research, MIT licensed).
- Z3 vendor material: Reference only, not used at runtime by default.
