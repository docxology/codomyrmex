"""MCP tool definitions for the release module.

Exposes release validation, package building, and certification as MCP tools.
"""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


def _get_validator(version: str = "1.0.0"):
    """Lazy import of ReleaseValidator."""
    from codomyrmex.release.release_validator import ReleaseValidator

    return ReleaseValidator(version=version)


def _get_builder():
    """Lazy import of PackageBuilder and PackageMetadata."""
    from codomyrmex.release.package_builder import PackageBuilder, PackageMetadata

    return PackageBuilder, PackageMetadata


@mcp_tool(
    category="release",
    description="Validate release readiness by running certification checks on tests, coverage, security, and docs.",
)
def release_validate(
    version: str = "1.3.0",
    test_failures: int | None = None,
    test_total: int | None = None,
    coverage_overall: float | None = None,
    coverage_tier1: float = 0.0,
    type_errors: int | None = None,
    cve_count: int | None = None,
    secrets_found: int | None = None,
    docs_complete: bool | None = None,
    artifacts_verified: bool | None = None,
    artifact_count: int | None = None,
) -> dict[str, Any]:
    """Run release certification checks and return the certification report.

    Args:
        version: Release version string.
        test_failures: Number of test failures.
        test_total: Total number of tests.
        coverage_overall: Overall code coverage percentage.
        coverage_tier1: Tier-1 module coverage percentage.
        cve_count: Number of known CVEs.
        secrets_found: Number of secrets detected.
        docs_complete: Whether documentation is complete.

    Returns:
        dict with keys: status, certified, version, pass_rate, blockers, checks
    """
    try:
        validator = _get_validator(version)
        if test_failures is not None and test_total is not None:
            validator.check_tests(failures=test_failures, total=test_total)
        if coverage_overall is not None:
            validator.check_coverage(overall=coverage_overall, tier1=coverage_tier1)
        if type_errors is not None:
            validator.check_type_safety(errors=type_errors)
        if cve_count is not None and secrets_found is not None:
            validator.check_security(cve_count=cve_count, secrets_found=secrets_found)
        if docs_complete is not None:
            validator.check_documentation(complete=docs_complete)
        if artifacts_verified is not None and artifact_count is not None:
            validator.check_artifacts(
                verified=artifacts_verified,
                artifact_count=artifact_count,
            )

        cert = validator.certify()
        return {
            "status": "success",
            "certified": cert.certified,
            "version": cert.version,
            "pass_rate": cert.pass_rate,
            "blockers": cert.blockers,
            "checks": [
                {
                    "name": c.name,
                    "category": c.category,
                    "status": c.status.value,
                    "value": c.value,
                }
                for c in cert.checks
            ],
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="release",
    description="Build distribution packages (sdist and wheel) and validate metadata.",
)
def release_build(
    name: str = "codomyrmex",
    version: str = "1.3.0",
    python_requires: str = ">=3.11",
    source_dir: str = ".",
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Build distribution artifacts for a package.

    Args:
        name: Package name.
        version: Package version.
        python_requires: Python version requirement.

    Returns:
        dict with keys: status, success, artifacts, warnings
    """
    try:
        PackageBuilder, PackageMetadata = _get_builder()
        metadata = PackageMetadata(
            name=name,
            version=version,
            python_requires=python_requires,
        )
        builder = PackageBuilder(
            metadata,
            source_dir=source_dir,
            output_dir=output_dir,
        )
        report = builder.build()
        return {
            "status": "success",
            "success": report.success,
            "artifacts": [
                {
                    "filename": a.filename,
                    "path": str(a.path),
                    "format": a.format,
                    "media_type": a.media_type,
                    "size_bytes": a.size_bytes,
                    "sha256": a.sha256,
                    "sha512": a.sha512,
                }
                for a in report.artifacts
            ],
            "warnings": report.warnings,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


@mcp_tool(
    category="release",
    description="Generate a markdown-formatted release certification report.",
)
def release_certification_report(
    version: str = "1.3.0",
    test_failures: int | None = None,
    test_total: int | None = None,
    coverage_overall: float | None = None,
    type_errors: int | None = None,
    cve_count: int | None = None,
    secrets_found: int | None = None,
    docs_complete: bool | None = None,
    artifacts_verified: bool | None = None,
    artifact_count: int | None = None,
) -> dict[str, Any]:
    """Generate a markdown certification report for a release.

    Args:
        version: Release version.
        test_failures: Number of test failures.
        test_total: Total tests run.
        coverage_overall: Overall coverage percentage.

    Returns:
        dict with keys: status, markdown, certified
    """
    try:
        validator = _get_validator(version)
        if test_failures is not None and test_total is not None:
            validator.check_tests(failures=test_failures, total=test_total)
        if coverage_overall is not None:
            validator.check_coverage(overall=coverage_overall)
        if type_errors is not None:
            validator.check_type_safety(errors=type_errors)
        if cve_count is not None and secrets_found is not None:
            validator.check_security(cve_count=cve_count, secrets_found=secrets_found)
        if docs_complete is not None:
            validator.check_documentation(complete=docs_complete)
        if artifacts_verified is not None and artifact_count is not None:
            validator.check_artifacts(
                verified=artifacts_verified,
                artifact_count=artifact_count,
            )
        cert = validator.certify()
        md = validator.to_markdown(cert)
        return {
            "status": "success",
            "markdown": md,
            "certified": cert.certified,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
