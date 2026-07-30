# Release — PAI Integration

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Role

The release module supports evidence collection, local execution, verification,
and remote planning:

| Phase | Capability |
|---|---|
| OBSERVE | ingest explicit gate results |
| PLAN | surface blockers; generate non-mutating GitHub or Zenodo-sandbox plans |
| EXECUTE | build real local distributions; make verified local copies |
| VERIFY | validate package and publication hashes and manifests |
| LEARN | preserve portable receipts for comparison and audit |

Remote planning returns `dry_run: true` and `executed: false`. It is not
publication authority or evidence of external acceptance.

## Access

- Python: `from codomyrmex.release import ...`
- CLI: `python -m codomyrmex.release publication prepare|verify|plan`
- MCP: `release_validate`, `release_build`,
  `release_certification_report`

## Navigation

- [README](README.md)
- [Specification](SPEC.md)
- [Source PAI documentation](../../../src/codomyrmex/release/PAI.md)
