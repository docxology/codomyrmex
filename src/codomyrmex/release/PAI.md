# Personal AI Infrastructure — Release Module

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Role

The release module turns measured local evidence into verifiable artifacts
while keeping external publication behind a separate authorization boundary.
It supports OBSERVE/VERIFY work directly and produces plans for later EXECUTE
work; it does not upload or reserve identifiers.

| PAI phase | Release contribution |
|---|---|
| OBSERVE | collect explicit test, coverage, typing, security, docs, and artifact evidence |
| PLAN | inspect certification blockers or produce GitHub/Zenodo-sandbox dry-run receipts |
| EXECUTE | run real local `uv build`; optionally make a verified local copy |
| VERIFY | re-hash package artifacts and publication bundles |
| LEARN | retain detached, machine-readable receipts for later comparison |

## Safe Workflow

```python
from codomyrmex.release import ReleaseValidator

validator = ReleaseValidator(version="1.3.0")
# Supply every measured category explicitly.
certification = validator.certify()
assert not certification.certified  # missing evidence fails closed
```

For publication planning:

```bash
uv run --locked python -m codomyrmex.release publication verify \
  output/release/codomyrmex-1.3.0
uv run --locked python -m codomyrmex.release publication plan \
  output/release/codomyrmex-1.3.0 --target github
```

The resulting plan is a receipt, not proof that GitHub or Zenodo accepted an
upload. An authorized external workflow must separately execute and verify any
real publication.

## Public Interface

- Validation: `ReleasePolicy`, `CertificationCheck`,
  `ReleaseCertification`, `ReleaseValidator`
- Package: `PackageMetadata`, `BuildArtifact`, `BuildReport`, `PackageBuilder`
- Distribution: `DistributionTarget`, `PreflightResult`, `PublishResult`,
  `DistributionManager`
- Publication: `PublicationMetadata`, `PublicationArtifact`,
  `PublicationManifest`, `PublicationBundle`, `PublicationVerification`,
  `PublicationPlan`, `prepare_publication_bundle()`,
  `verify_publication_bundle()`, `plan_publication()`

## MCP Surface

The module exposes `release_validate`, `release_build`, and
`release_certification_report`. These tools inherit the same strict and
real-artifact behavior. Publication preparation and planning are available
through the Python API and `python -m codomyrmex.release`.

## Boundaries

- `success=True, dry_run=True, executed=False` means a valid plan, never a
  publication.
- A valid bundle proves internal byte identity and stated provenance; it does
  not prove independent archival acceptance, DOI registration, or deployment
  safety.
- Dirty source state is disclosed in the source receipt, not hidden.

## Navigation

- [README](README.md)
- [API specification](API_SPECIFICATION.md)
- [MCP specification](MCP_TOOL_SPECIFICATION.md)
- [Functional specification](SPEC.md)
