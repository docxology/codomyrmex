"""API surface analyzer.

Analyzes the public API surface: counts endpoints, modules,
coverage, and generates summary reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from codomyrmex.api.api_contract import APIContract, APIEndpoint


@dataclass
class APISurfaceReport:
    """Report on the public API surface.

    Attributes:
        total_endpoints: Total API endpoint count.
        frozen_endpoints: Number of frozen endpoints.
        modules: Unique module count.
        module_breakdown: Endpoints per module.
        coverage: Fraction of endpoints with signatures.
    """

    total_endpoints: int = 0
    frozen_endpoints: int = 0
    modules: int = 0
    module_breakdown: dict[str, int] = field(default_factory=dict)
    coverage: float = 0.0


class APISurface:
    """Analyze the public API surface.

    Example::

        surface = APISurface(contract)
        report = surface.analyze()
        md = surface.to_markdown()
    """

    def __init__(self, contract: APIContract) -> None:
        """Initialize this instance."""
        self._contract = contract

    def analyze(self) -> APISurfaceReport:
        """Analyze the API surface."""
        endpoints = self._contract.endpoints
        total = len(endpoints)
        frozen = sum(1 for ep in endpoints.values() if ep.frozen)

        # Module breakdown
        modules: dict[str, int] = {}
        has_sig = 0
        for ep in endpoints.values():
            mod = ep.module or "unknown"
            modules[mod] = modules.get(mod, 0) + 1
            if ep.signature:
                has_sig += 1

        coverage = has_sig / total if total > 0 else 0.0

        return APISurfaceReport(
            total_endpoints=total,
            frozen_endpoints=frozen,
            modules=len(modules),
            module_breakdown=modules,
            coverage=coverage,
        )

    def frozen_percentage(self) -> float:
        """Return percentage of frozen endpoints."""
        report = self.analyze()
        if report.total_endpoints == 0:
            return 0.0
        return report.frozen_endpoints / report.total_endpoints

    def unfrozen_endpoints(self) -> list[str]:
        """List endpoints that are not yet frozen."""
        return [
            name for name, ep in self._contract.endpoints.items()
            if not ep.frozen
        ]

    def by_module(self) -> dict[str, list[APIEndpoint]]:
        """Group endpoints by module."""
        grouped: dict[str, list[APIEndpoint]] = {}
        for ep in self._contract.endpoints.values():
            mod = ep.module or "unknown"
            grouped.setdefault(mod, []).append(ep)
        return grouped

    def to_markdown(self) -> str:
        """Generate an API surface summary as markdown."""
        report = self.analyze()
        lines = [
            "# API Surface Report",
            "",
            f"**Total Endpoints**: {report.total_endpoints} | "
            f"**Frozen**: {report.frozen_endpoints} | "
            f"**Modules**: {report.modules} | "
            f"**Coverage**: {report.coverage:.0%}",
            "",
            "## Module Breakdown",
            "",
            "| Module | Endpoints |",
            "|--------|-----------|",
        ]
        for mod, count in sorted(report.module_breakdown.items()):
            lines.append(f"| {mod} | {count} |")

        return "\n".join(lines)


__all__ = ["APISurface", "APISurfaceReport"]
