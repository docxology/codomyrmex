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
    version: str = "1.0.0",
    test_failures: int = 0,
    test_total: int = 0,
    coverage_overall: float = 0.0,
    coverage_tier1: float = 0.0,
    cve_count: int = 0,
    secrets_found: int = 0,
    docs_complete: bool = True,
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
        if test_total > 0:
            validator.check_tests(failures=test_failures, total=test_total)
        if coverage_overall > 0:
            validator.check_coverage(overall=coverage_overall, tier1=coverage_tier1)
        validator.check_security(cve_count=cve_count, secrets_found=secrets_found)
        validator.check_documentation(complete=docs_complete)

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
    version: str = "1.0.0",
    python_requires: str = ">=3.11",
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
        builder = PackageBuilder(metadata)
        report = builder.build()
        return {
            "status": "success",
            "success": report.success,
            "artifacts": [
                {
                    "filename": a.filename,
                    "format": a.format,
                    "size_bytes": a.size_bytes,
                    "checksum": a.checksum,
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
    version: str = "1.0.0",
    test_failures: int = 0,
    test_total: int = 100,
    coverage_overall: float = 70.0,
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
        validator.check_tests(failures=test_failures, total=test_total)
        validator.check_coverage(overall=coverage_overall)
        cert = validator.certify()
        md = validator.to_markdown(cert)
        return {
            "status": "success",
            "markdown": md,
            "certified": cert.certified,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}
