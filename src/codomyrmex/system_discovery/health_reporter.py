"""Codebase health report generator.

Produces a comprehensive health report combining module introspection,
dependency analysis, and cross-cutting quality metrics into a
structured JSON/markdown report.

Example::

    reporter = HealthReporter()
    report = reporter.generate()
    reporter.write_markdown(report, "health_report.md")
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class HealthMetrics:
    """Aggregated health metrics.

    Attributes:
        total_modules: Module count.
        total_loc: Total lines of code.
        healthy_count: Modules at "healthy" health.
        partial_count: Modules at "partial" health.
        minimal_count: Modules at "minimal" health.
        cycle_count: Number of circular dependencies.
        modules_without_tests: Modules >100 LOC with no tests.
        top_imported: Most-imported modules.
        largest_modules: Biggest modules by LOC.
    """

    total_modules: int = 0
    total_loc: int = 0
    healthy_count: int = 0
    partial_count: int = 0
    minimal_count: int = 0
    cycle_count: int = 0
    modules_without_tests: int = 0
    top_imported: list[tuple[str, int]] = field(default_factory=list)
    largest_modules: list[tuple[str, int]] = field(default_factory=list)
    mcp_tool_count: int = 0
    total_classes: int = 0
    total_functions: int = 0

    @property
    def health_score(self) -> float:
        """Overall health score (0.0–100.0)."""
        if self.total_modules == 0:
            return 0.0
        doc_score = (
            self.healthy_count * 100 + self.partial_count * 50
        ) / self.total_modules
        test_penalty = min(30, self.modules_without_tests * 0.3)
        cycle_penalty = min(20, self.cycle_count * 2)
        return max(0.0, min(100.0, doc_score - test_penalty - cycle_penalty))


class HealthReporter:
    """Generate comprehensive codebase health reports.

    Args:
        repo_root: Repository root path.

    Example::

        reporter = HealthReporter()
        report = reporter.generate()
        print(f"Health score: {report['health_score']:.1f}/100")
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self._root = repo_root or _REPO_ROOT
        self._src_root = self._root / "src" / "codomyrmex"

    def generate(self) -> dict[str, Any]:
        """Generate a full health report.

        Returns:
            Comprehensive dict with metrics, recommendations, and details.
        """
        from codomyrmex.system_discovery.dependency_mapper import DependencyMapper
        from codomyrmex.system_discovery.module_introspector import ModuleIntrospector

        start = time.monotonic()

        # Module introspection
        intro = ModuleIntrospector(self._src_root)
        intro_report = intro.scan_all()

        # Dependency analysis
        mapper = DependencyMapper(self._src_root)
        dep_report = mapper.build_graph()

        # Build metrics
        health_dist = intro_report["health_distribution"]
        modules_no_tests = [
            m for m in intro_report["modules"] if not m["has_tests"] and m["loc"] > 100
        ]

        metrics = HealthMetrics(
            total_modules=intro_report["total_modules"],
            total_loc=intro_report["total_loc"],
            healthy_count=health_dist.get("healthy", 0),
            partial_count=health_dist.get("partial", 0),
            minimal_count=health_dist.get("minimal", 0),
            cycle_count=dep_report["cycle_count"],
            modules_without_tests=len(modules_no_tests),
            top_imported=dep_report["top_imported"][:5],
            largest_modules=[
                (m["name"], m["loc"])
                for m in sorted(
                    intro_report["modules"], key=lambda x: x["loc"], reverse=True
                )[:10]
            ],
            mcp_tool_count=intro_report["total_mcp_tools"],
            total_classes=intro_report["total_classes"],
            total_functions=intro_report["total_functions"],
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, modules_no_tests)

        elapsed = (time.monotonic() - start) * 1000
        return {
            "health_score": round(metrics.health_score, 1),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "metrics": {
                "total_modules": metrics.total_modules,
                "total_loc": metrics.total_loc,
                "total_classes": metrics.total_classes,
                "total_functions": metrics.total_functions,
                "mcp_tools": metrics.mcp_tool_count,
                "health_distribution": {
                    "healthy": metrics.healthy_count,
                    "partial": metrics.partial_count,
                    "minimal": metrics.minimal_count,
                },
                "circular_dependencies": metrics.cycle_count,
                "modules_without_tests": metrics.modules_without_tests,
            },
            "top_imported": metrics.top_imported,
            "largest_modules": metrics.largest_modules,
            "recommendations": recommendations,
            "scan_duration_ms": round(elapsed, 1),
        }

    def _generate_recommendations(
        self,
        metrics: HealthMetrics,
        modules_no_tests: list[dict],
    ) -> list[dict[str, str]]:
        """Generate actionable recommendations."""
        recs: list[dict[str, str]] = []

        if metrics.cycle_count > 0:
            recs.append(
                {
                    "severity": "warning",
                    "category": "architecture",
                    "message": f"{metrics.cycle_count} circular dependencies detected. "
                    "Consider extracting shared interfaces.",
                }
            )

        if metrics.modules_without_tests > 50:
            top_untested = sorted(
                modules_no_tests, key=lambda m: m["loc"], reverse=True
            )[:5]
            names = ", ".join(m["name"] for m in top_untested)
            recs.append(
                {
                    "severity": "info",
                    "category": "testing",
                    "message": f"{metrics.modules_without_tests} modules >100 LOC lack tests. "
                    f"Priority: {names}",
                }
            )

        if metrics.healthy_count < metrics.total_modules * 0.1:
            recs.append(
                {
                    "severity": "info",
                    "category": "documentation",
                    "message": f"Only {metrics.healthy_count}/{metrics.total_modules} modules at "
                    "'healthy' doc status. Add SPEC.md to boost health scores.",
                }
            )

        return recs

    def write_markdown(self, report: dict, output: str = "health_report.md") -> Path:
        """Write a markdown health report.

        Args:
            report: Report dict from :meth:`generate`.
            output: Output file path.

        Returns:
            Path to the written file.
        """
        lines = [
            "# Codebase Health Report",
            "",
            f"**Score**: {report['health_score']}/100 · "
            f"**Generated**: {report['timestamp']}",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Modules | {report['metrics']['total_modules']} |",
            f"| LOC | {report['metrics']['total_loc']:,} |",
            f"| Classes | {report['metrics']['total_classes']:,} |",
            f"| Functions | {report['metrics']['total_functions']:,} |",
            f"| MCP Tools | {report['metrics']['mcp_tools']} |",
            f"| Circular Deps | {report['metrics']['circular_dependencies']} |",
            f"| Untested (>100 LOC) | {report['metrics']['modules_without_tests']} |",
            "",
            "## Health Distribution",
            "",
        ]

        dist = report["metrics"]["health_distribution"]
        for status, count in dist.items():
            lines.append(f"- **{status}**: {count}")

        if report["recommendations"]:
            lines.extend(["", "## Recommendations", ""])
            for rec in report["recommendations"]:
                icon = "⚠️" if rec["severity"] == "warning" else "ℹ️"
                lines.append(f"- {icon} [{rec['category']}] {rec['message']}")

        lines.append("")
        out = Path(output)
        out.write_text("\n".join(lines))
        return out

    def write_json(self, report: dict, output: str = "health_report.json") -> Path:
        """Write a JSON health report."""
        out = Path(output)
        out.write_text(json.dumps(report, indent=2, default=str) + "\n")
        return out


__all__ = [
    "HealthMetrics",
    "HealthReporter",
]
