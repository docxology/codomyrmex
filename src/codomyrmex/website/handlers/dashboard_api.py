"""Dashboard API endpoints for v1.1.10 telemetry and cost data.

Provides JSON API endpoints for the dashboard frontend:
- ``/api/modules`` — Module health overview
- ``/api/costs/summary`` — Cost accounting summary
- ``/api/mcp-call-graph`` — MCP tool call graph
- ``/api/tokens`` — Token consumption stats
- ``/api/agents/status`` — Agent status grid

Example::

    handler = DashboardAPIHandler()
    response = handler.handle_modules()
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class DashboardAPIHandler:
    """Handles dashboard API requests.

    Lazily initializes providers to avoid import-time overhead.
    """

    def __init__(self) -> None:
        self._module_provider = None
        self._cost_tracker = None
        self._call_collector = None
        self._token_tracker = None

    def _get_module_provider(self) -> Any:
        if self._module_provider is None:
            from codomyrmex.website.module_health import ModuleHealthProvider

            self._module_provider = ModuleHealthProvider()
        return self._module_provider

    def _get_call_collector(self) -> Any:
        if self._call_collector is None:
            from codomyrmex.telemetry.tracing.call_graph import get_collector

            self._call_collector = get_collector()
        return self._call_collector

    def _get_token_tracker(self) -> Any:
        if self._token_tracker is None:
            from codomyrmex.telemetry.metrics.token_tracker import get_token_tracker

            self._token_tracker = get_token_tracker()
        return self._token_tracker

    def handle_modules(self, module_name: str = "") -> dict[str, Any]:
        """Handle ``/api/modules`` — module health data.

        Args:
            module_name: Optional specific module name. If empty, returns all.

        Returns:
            JSON-serializable response dict.
        """
        provider = self._get_module_provider()
        if module_name:
            health = provider.get_module(module_name)
            if health is None:
                return {"error": f"Module '{module_name}' not found", "status": 404}
            return {"module": health.to_dict(), "status": 200}

        modules = provider.get_all_modules()
        return {
            "modules": [m.to_dict() for m in modules],
            "summary": provider.get_summary(),
            "timestamp": time.time(),
            "status": 200,
        }

    def handle_costs_summary(
        self,
        period: str = "daily",
    ) -> dict[str, Any]:
        """Handle ``/api/costs/summary`` — cost accounting summary.

        Args:
            period: Budget period (``"daily"``, ``"weekly"``, ``"monthly"``).

        Returns:
            JSON-serializable cost summary.
        """
        try:
            from codomyrmex.cost_management.models import BudgetPeriod
            from codomyrmex.cost_management.tracker import CostTracker

            period_map = {
                "daily": BudgetPeriod.DAILY,
                "weekly": BudgetPeriod.WEEKLY,
                "monthly": BudgetPeriod.MONTHLY,
            }
            budget_period = period_map.get(period)

            tracker = CostTracker()
            summary = tracker.get_summary(period=budget_period)
            return {
                "summary": summary.to_dict(),
                "period": period,
                "timestamp": time.time(),
                "status": 200,
            }
        except ImportError:
            return {"error": "Cost management module not available", "status": 503}

    def handle_mcp_call_graph(self) -> dict[str, Any]:
        """Handle ``/api/mcp-call-graph`` — MCP tool call graph DAG.

        Returns:
            JSON-serializable call graph with nodes and edges.
        """
        collector = self._get_call_collector()
        graph = collector.get_call_graph()
        stats = collector.get_stats()
        return {
            "graph": graph,
            "stats": stats,
            "timestamp": time.time(),
            "status": 200,
        }

    def handle_tokens(self) -> dict[str, Any]:
        """Handle ``/api/tokens`` — token consumption statistics.

        Returns:
            JSON-serializable token usage stats.
        """
        tracker = self._get_token_tracker()
        stats = tracker.get_stats()
        recent = tracker.get_recent(limit=20)
        return {
            "stats": stats,
            "recent": recent,
            "timestamp": time.time(),
            "status": 200,
        }

    def handle_agents_status(self) -> dict[str, Any]:
        """Handle ``/api/agents/status`` — agent status grid.

        Returns:
            JSON-serializable agent status list.
        """
        # Collect known agent types and their availability
        agents: list[dict[str, Any]] = []

        agent_defs = [
            ("hermes", "codomyrmex.agents.hermes"),
            ("claude", "codomyrmex.agents.claude"),
            ("codex", "codomyrmex.agents.codex"),
            ("jules", "codomyrmex.agents.jules"),
        ]

        for name, module_path in agent_defs:
            try:
                __import__(module_path)
                agents.append(
                    {
                        "name": name,
                        "status": "available",
                        "last_heartbeat": time.time(),
                        "module": module_path,
                    }
                )
            except ImportError:
                agents.append(
                    {
                        "name": name,
                        "status": "unavailable",
                        "last_heartbeat": 0,
                        "module": module_path,
                    }
                )

        return {
            "agents": agents,
            "total": len(agents),
            "available": sum(1 for a in agents if a["status"] == "available"),
            "timestamp": time.time(),
            "status": 200,
        }

    def route(self, path: str, params: dict[str, str] | None = None) -> str:
        """Route an API request and return JSON response.

        Args:
            path: API path (e.g., ``"/api/modules"``).
            params: Query parameters.

        Returns:
            JSON string response.
        """
        params = params or {}

        routes: dict[str, Any] = {
            "/api/modules": lambda: self.handle_modules(params.get("name", "")),
            "/api/costs/summary": lambda: self.handle_costs_summary(
                params.get("period", "daily")
            ),
            "/api/mcp-call-graph": self.handle_mcp_call_graph,
            "/api/tokens": self.handle_tokens,
            "/api/agents/status": self.handle_agents_status,
        }

        handler = routes.get(path)
        if handler is None:
            return json.dumps({"error": f"Unknown path: {path}", "status": 404})

        try:
            result = handler()
            return json.dumps(result, indent=2, default=str)
        except Exception as exc:
            logger.error("API error on %s: %s", path, exc, exc_info=True)
            return json.dumps({"error": str(exc), "status": 500})


__all__ = ["DashboardAPIHandler"]
