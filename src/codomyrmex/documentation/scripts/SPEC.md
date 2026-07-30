# Package-native documentation scripts specification

## Purpose

This directory contains reusable documentation scanners and historical
generators. It is not a uniform CLI framework: each maintained mutator must
declare and test its own safety contract.

## Maintained contracts

### `triple_check.py`

- analyzes the selected repository without rewriting editorial source;
- writes the documented report path;
- returns nonzero with `--fail-on-issues` when blocking findings remain.

### `placeholder_check.py`

- requires exactly one of `--dry-run` or `--apply`;
- excludes configured Git submodules by default;
- preserves bytes in dry-run;
- consumes optional terminal punctuation before inserting a single-period
  replacement;
- returns nonzero when a file cannot be processed.

### `bootstrap_agents_readmes.py`

- supports preview mode and curated markers;
- owns only configured first-party surfaces;
- excludes vendor, generated, submodule, and protected module-mirror paths;
- must not run in apply mode during the hand-pass freeze.

## Legacy commands

Other fix, clean, enhancement, marker, and missing-file scripts retain
historical behavior. They are not safe merely because they live in this
package. Before use, inspect source, CLI defaults, exclusions, symlink behavior,
and tests. Add fail-closed modes before promoting a legacy mutator into an
authoritative workflow.

## Reports

Durable receipts must use deterministic ordering and repository-relative paths
and must not contain credentials or absolute home paths.

## Testing

Use real temporary files and subprocesses. Verify help/no-mode/dry-run are
read-only, apply scope is bounded, failures are nonzero, and submodule and
curated boundaries are preserved.

## Navigation

- [README](README.md)
- [Agent guidance](AGENTS.md)
- [Parent package](../SPEC.md)
- [Repository tooling specification](../../../../scripts/documentation/SPEC.md)
