# Release Module API Specification

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: July 2026

## Overview

`codomyrmex.release` exposes immutable receipts for release evidence, real
wheel/sdist builds, verified local distribution, and portable technical-report
publication bundles. Remote operations are deliberately planning-only.

## Validation API

### Immutable types

| Type | Important fields |
|---|---|
| `ReleasePolicy` | `strict`, `required_categories`, `coverage_floor`, `tier1_coverage_floor` |
| `CertificationCheck` | `name`, `category`, `status`, `value`, `threshold`, `message` |
| `ReleaseCertification` | `version`, `checks`, `certified`, `certified_at`, `blockers`, `policy` |

`CertificationStatus` values are `PASS`, `FAIL`, `SKIP`, and `WARN`.

### `ReleaseValidator`

```python
ReleaseValidator(
    version: str = "1.3.0",
    *,
    policy: ReleasePolicy | None = None,
)
```

| Method | Result |
|---|---|
| `check_tests(failures, total, max_skips=50)` | requires at least one executed test and zero failures |
| `check_coverage(overall, tier1=0)` | enforces policy coverage floors |
| `check_type_safety(errors)` | blocking in strict mode; warning otherwise |
| `check_security(cve_count, secrets_found)` | blocks any supplied CVE or secret |
| `check_documentation(complete)` | blocking in strict mode; warning otherwise |
| `check_artifacts(verified, artifact_count)` | requires at least one verified artifact |
| `add_custom_check(check)` | appends caller evidence without changing policy |
| `certify()` | fails for any blocking check or missing required category |
| `to_markdown(certification)` | renders the receipt |

The default strict policy requires categories `testing`, `coverage`, `typing`,
`security`, `documentation`, and `artifacts`.

## Package-Build API

### `PackageMetadata`

Frozen expected metadata: `name`, `version`, `description`, `author`,
`license`, `python_requires`, `dependencies`, and `entry_points`.

### `BuildArtifact`

```python
BuildArtifact(
    filename: str,
    path: pathlib.Path,
    format: str,
    media_type: str,
    size_bytes: int,
    sha256: str,
    sha512: str,
    built_at: float,
)
```

`checksum` is a compatibility property returning the full `sha256`.

### `PackageBuilder`

```python
PackageBuilder(
    metadata: PackageMetadata | None = None,
    *,
    source_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    uv_executable: str = "uv",
    source_date_epoch: int | None = None,
)
```

`build()` executes `uv build --out-dir <isolated-stage> <source_dir>`. Success
requires exactly one wheel and one sdist, readable embedded metadata matching
the expected normalized name and version, and safe archive members. Absolute
or traversing members and private-worktree/cache components such as `.git`,
`.env`, and `__pycache__`, plus file contents embedding the active source or
user-home path, fail closed before files are copied to `output_dir`.
`BuildReport` records artifacts, warnings, success, command, stdout, and stderr.

## Distribution API

`DistributionTarget` values are `PYPI`, `TEST_PYPI`, `GITHUB`, and `LOCAL`.

```python
DistributionManager(build: BuildReport | None = None)
```

| Method | Contract |
|---|---|
| `preflight(target)` | verifies build success, artifact presence, metadata, file sizes, SHA-256, and SHA-512 |
| `publish(target, *, dry_run=None, destination=None)` | plans remote publication or executes a verified local copy |
| `publish_history()` | returns an isolated copy of in-memory results |

`PublishResult` contains `target`, `artifacts_published`, `url`, `success`,
`executed`, `dry_run`, `receipt`, and `error`. Remote targets default to
`dry_run=True`; remote `dry_run=False` fails. Local targets default to
execution, require `destination`, and verify all copied bytes.

## Publication API

All publication records are frozen dataclasses:

- `PublicationMetadata`
- `PublicationArtifact`
- `PublicationManifest`
- `PublicationBundle`
- `PublicationVerification`
- `PublicationPlan`

`PublicationMetadata.publication_type` must be `technical-report`; an unassigned
DOI is `None`.

```python
prepare_publication_bundle(
    *,
    metadata: PublicationMetadata,
    content_pdf: str | Path,
    distribution_pdf: str | Path,
    semantic_html: str | Path,
    output_dir: str | Path,
    project_root: str | Path = ".",
    reproducibility_inputs: Iterable[str | Path] = (),
    validation_receipts: Iterable[str | Path] = (),
    validation_outcomes: Iterable[tuple[str, bool, str]] = (),
    source_date_epoch: int = 0,
) -> PublicationBundle
```

The function copies required rendered artifacts, generates shared citation and
Zenodo metadata, records source state and producers, writes manifest v1 and both
checksum files, and performs no remote operation.

```python
verify_publication_bundle(
    bundle: PublicationBundle | str | Path,
) -> PublicationVerification
```

Verification checks schema version, required roles, portable paths, sizes,
SHA-256, SHA-512, checksum files, and—when `pdftotext` is available—the visible
content hash in the distribution PDF.

```python
plan_publication(
    bundle: PublicationBundle | str | Path,
    *,
    target: str,
    dry_run: bool = True,
    receipt_path: str | Path | None = None,
) -> PublicationPlan
```

Supported targets are `github` and `zenodo-sandbox`. `dry_run=False` raises
`ValueError`; a plan is written only after bundle verification passes.

## CLI

```text
python -m codomyrmex.release publication prepare [options]
python -m codomyrmex.release publication verify BUNDLE
python -m codomyrmex.release publication plan BUNDLE \
  --target {github,zenodo-sandbox} [--receipt PATH]
```

`plan` always calls the API with `dry_run=True`.

## Behavioral Compatibility Changes

- Certification is now evidence-complete and fail closed by default.
- Build records now identify real files with complete SHA-256 and SHA-512
  digests; `checksum` remains a SHA-256 alias.
- Remote distribution no longer reports simulated publication as executed.
- Publication bundle APIs are additive and never perform remote writes.
