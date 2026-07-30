<!-- readme: curated -->

# Package-native documentation scripts

This package contains reusable scanners, validators, and historical repair
utilities. Repository-level entry points and the canonical MkDocs composition
live in [`scripts/documentation/`](../../../../scripts/documentation/).

## Supported validation

```bash
uv run --locked python \
  src/codomyrmex/documentation/scripts/triple_check.py \
  --repo-root . --fail-on-issues
```

The triple-check produces `output/triple_check_report.md`. It analyzes
documentation completeness and consistency without rewriting source.

## Mutation classes

| Class | Examples | Rule |
| :--- | :--- | :--- |
| Read-only analysis | `triple_check.py`, `audit_structure.py`, `validate_links.py` | Safe only within documented scope; receipts may be written |
| Previewable repair | `placeholder_check.py`, `repair_triple_check_completeness.py` | Use explicit `--dry-run` first |
| Broad generation | `bootstrap_agents_readmes.py`, `generate_missing_readmes.py` | Do not run during the hand-pass freeze |
| Marker management | `apply_curated_markers.py` | Preview the complete path set; never use as a substitute for review |
| Legacy maintenance | `fix*.py`, `clean*.py`, `remove_placeholders.py` | Inspect source and current tests before use; CLI behavior varies |

`placeholder_check.py` requires `--dry-run` or `--apply` and skips configured
submodules unless explicitly told otherwise. Its replacement logic guarantees
a single terminal period for the generic source-system placeholder.

## Safe placeholder preview

```bash
uv run --locked python \
  -m codomyrmex.documentation.scripts.placeholder_check \
  --repo-root . --dry-run
```

Do not switch this command to `--apply` while the README/AGENTS hand-pass
freeze is active.

## Navigation

- [Agent instructions](AGENTS.md)
- [Documentation package](../README.md)
- [Repository tooling](../../../../scripts/documentation/README.md)
- [Maintenance guide](../../../../docs/development/documentation.md)
- [Repository root](../../../../README.md)
