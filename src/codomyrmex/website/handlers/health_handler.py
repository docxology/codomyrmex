"""Health, status, telemetry, and security posture handlers for WebsiteServer.

Handles /api/health, /api/status, /api/telemetry, /api/security/posture,
and /api/awareness endpoints.
"""

from __future__ import annotations

import sys

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class HealthHandler:
    """Mixin providing health/status/telemetry endpoint handlers.

    Expects the host class to provide:
    - self.data_provider: DataProvider instance
    - self.send_json_response(data, status): JSON response sender
    - self.send_error(code, msg): error response sender
    """

    # Persistent telemetry collector shared across requests
    _telemetry_collector = None
    _telemetry_dm = None

    def handle_status(self) -> None:
        """Handle /api/status -- quick system status."""
        if self.data_provider:
            summary = self.data_provider.get_system_summary()
            self.send_json_response(summary)
        else:
            self.send_error(500, "Data provider missing")

    def handle_health(self) -> None:
        """Handle /api/health -- comprehensive health data."""
        if self.data_provider:
            health = self.data_provider.get_health_status()
            self.send_json_response(health)
        else:
            self.send_error(500, "Data provider missing")

    def handle_awareness(self) -> None:
        """Handle GET /api/awareness -- PAI ecosystem data."""
        if self.data_provider:
            data = self.data_provider.get_pai_awareness_data()
            self.send_json_response(data)
        else:
            self.send_json_response({"error": "Data provider missing"}, status=500)

    def handle_llm_config(self) -> None:
        """Handle GET /api/llm/config -- return LLM configuration."""
        if self.data_provider:
            config = self.data_provider.get_llm_config()
            self.send_json_response(config)
        else:
            self.send_json_response({"error": "Data provider missing"}, status=500)

    @classmethod
    def _ensure_telemetry(cls):
        """Lazily initialise the shared MetricCollector and DashboardManager.

        Returns:
            Tuple of (collector, dashboard_manager, MetricType) for callers.
        """
        from codomyrmex.telemetry.dashboard import (
            DashboardManager,
            MetricCollector,
            MetricType,
            Panel,
            PanelType,
        )

        if cls._telemetry_collector is None:
            cls._telemetry_collector = MetricCollector()
            cls._telemetry_dm = DashboardManager(cls._telemetry_collector)
            dash = cls._telemetry_dm.create(
                "System Overview",
                description="Baseline system metrics",
                tags=["system", "auto"],
            )
            dash.add_panel(Panel(
                id="modules", title="Module Count",
                panel_type=PanelType.STAT, metrics=["module_count"],
            ))
            dash.add_panel(Panel(
                id="tools", title="MCP Tool Count",
                panel_type=PanelType.STAT, metrics=["tool_count"],
            ))
            dash.add_panel(Panel(
                id="agents", title="Agent Count",
                panel_type=PanelType.STAT, metrics=["agent_count"],
            ))

        return cls._telemetry_collector, cls._telemetry_dm, MetricType

    def handle_telemetry(self) -> None:
        """Handle GET /api/telemetry -- metric series and dashboard registry.

        Uses a persistent MetricCollector that seeds baseline system
        metrics on first access and refreshes them on each request.
        """
        try:
            collector, dm, MetricType = self._ensure_telemetry()

            # Seed / refresh baseline metrics from DataProvider
            if self.data_provider:
                modules = self.data_provider.get_modules()
                collector.record("module_count", float(len(modules)),
                                metric_type=MetricType.GAUGE)
                agents = self.data_provider.get_actual_agents()
                collector.record("agent_count", float(len(agents)),
                                metric_type=MetricType.GAUGE)
                try:
                    tools_data = self.data_provider.get_mcp_tools()
                    collector.record("tool_count",
                                    float(len(tools_data.get("tools", []))),
                                    metric_type=MetricType.GAUGE)
                except Exception as e:
                    logger.debug("Failed to record tool_count metric: %s", e)
                    pass

            # Build latest_values dict for the frontend
            latest_values = {}
            for name in collector._metrics:
                latest = collector.get_latest(name)
                if latest is not None:
                    latest_values[name] = latest.value

            data = {
                "status": "ok",
                "dashboards": [d.to_dict() for d in dm.list()],
                "metric_names": list(collector._metrics.keys()),
                "total_metrics": sum(
                    len(v) for v in collector._metrics.values()
                ),
                "latest_values": latest_values,
            }
        except Exception as exc:
            data = {"status": "error", "error": str(exc)}
        self.send_json_response(data)

    def handle_telemetry_seed(self) -> None:
        """Handle POST /api/telemetry/seed -- seed baseline system metrics.

        Triggers a fresh telemetry snapshot capturing module count,
        tool count, agent count, and Python version.
        """
        try:
            collector, _dm, MetricType = self._ensure_telemetry()
            seeded = []

            if self.data_provider:
                modules = self.data_provider.get_modules()
                collector.record("module_count", float(len(modules)),
                                metric_type=MetricType.GAUGE)
                seeded.append("module_count")

                agents = self.data_provider.get_actual_agents()
                collector.record("agent_count", float(len(agents)),
                                metric_type=MetricType.GAUGE)
                seeded.append("agent_count")

                try:
                    tools_data = self.data_provider.get_mcp_tools()
                    collector.record("tool_count",
                                    float(len(tools_data.get("tools", []))),
                                    metric_type=MetricType.GAUGE)
                    seeded.append("tool_count")
                except Exception as e:
                    logger.debug("Failed to seed tool_count metric: %s", e)
                    pass

                # Additional useful metrics
                collector.record("python_version_minor",
                                float(sys.version_info.minor),
                                metric_type=MetricType.GAUGE)
                seeded.append("python_version_minor")

                scripts = self.data_provider.get_available_scripts()
                collector.record("script_count",
                                float(len(scripts)),
                                metric_type=MetricType.GAUGE)
                seeded.append("script_count")

            self.send_json_response({
                "status": "ok",
                "seeded_metrics": seeded,
                "count": len(seeded),
            })
        except Exception as exc:
            self.send_json_response(
                {"status": "error", "error": str(exc)}, status=500
            )

    def handle_security_posture(self) -> None:
        """Handle GET /api/security/posture -- aggregate security posture."""
        try:
            from codomyrmex.security.dashboard import SecurityDashboard
            sd = SecurityDashboard()
            posture = sd.posture()
            data = {
                "status": "ok",
                "risk_score": posture.risk_score,
                "compliance_rate": posture.compliance_pass_rate,
                "secret_findings_count": posture.secret_findings_count,
                "total_checks": posture.total_checks,
                "markdown": sd.to_markdown(),
            }
        except Exception as exc:
            data = {"status": "error", "error": str(exc)}
        self.send_json_response(data)
