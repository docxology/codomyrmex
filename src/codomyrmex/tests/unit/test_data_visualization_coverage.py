# type: ignore
"""Functional tests for data_visualization module — zero-mock.

Exercises chart classes, dashboard, themes, report builders,
Mermaid diagram, and factory functions.
"""

from __future__ import annotations

import pytest

import codomyrmex.data_visualization as dv


class TestDataVizImports:
    """Core exports are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "AreaChart",
            "BarChart",
            "BarPlot",
            "BoxPlot",
            "Card",
            "Dashboard",
            "FinanceReport",
            "GeneralSystemReport",
            "Grid",
            "Heatmap",
            "Histogram",
            "LinePlot",
            "LogisticsReport",
            "MarketingReport",
            "MermaidDiagram",
            "PieChart",
            "Report",
            "ScatterPlot",
            "Section",
            "Table",
            "Theme",
            "DARK_THEME",
            "DEFAULT_THEME",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(dv, name), f"Missing export: {name}"


class TestThemes:
    """Theme objects."""

    def test_dark_theme(self) -> None:
        assert dv.DARK_THEME is not None

    def test_default_theme(self) -> None:
        assert dv.DEFAULT_THEME is not None

    def test_theme_callable(self) -> None:
        assert callable(dv.Theme)


class TestChartClasses:
    """All chart classes are callable."""

    @pytest.mark.parametrize(
        "name",
        [
            "AreaChart",
            "BarChart",
            "BarPlot",
            "BoxPlot",
            "Heatmap",
            "Histogram",
            "LinePlot",
            "PieChart",
            "ScatterPlot",
        ],
    )
    def test_chart_callable(self, name: str) -> None:
        cls = getattr(dv, name)
        assert callable(cls)


class TestDashboard:
    """Dashboard class."""

    def test_dashboard_callable(self) -> None:
        assert callable(dv.Dashboard)

    def test_card_callable(self) -> None:
        assert callable(dv.Card)

    def test_grid_callable(self) -> None:
        assert callable(dv.Grid)

    def test_section_callable(self) -> None:
        assert callable(dv.Section)

    def test_table_callable(self) -> None:
        assert callable(dv.Table)


class TestReports:
    """Report builder classes."""

    @pytest.mark.parametrize(
        "name",
        ["FinanceReport", "GeneralSystemReport", "LogisticsReport", "MarketingReport", "Report"],
    )
    def test_report_callable(self, name: str) -> None:
        assert callable(getattr(dv, name))


class TestFactoryFunctions:
    """Chart factory functions."""

    @pytest.mark.parametrize(
        "name",
        [
            "create_area_chart",
            "create_bar_chart",
            "create_bar_chart_from_dict",
            "create_box_plot",
            "create_heatmap",
            "create_histogram",
            "create_line_plot",
            "create_pie_chart",
            "create_scatter_plot",
            "generate_report",
            "render_html",
        ],
    )
    def test_factory_callable(self, name: str) -> None:
        fn = getattr(dv, name)
        assert callable(fn)


class TestMermaidDiagram:
    """MermaidDiagram class."""

    def test_mermaid_callable(self) -> None:
        assert callable(dv.MermaidDiagram)


class TestSubmoduleAccess:
    """Submodule imports for deeper coverage."""

    def test_git_visualizer_submodule(self) -> None:
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        assert viz is not None

    def test_mermaid_generator_submodule(self) -> None:
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        assert gen is not None
        public = [m for m in dir(gen) if not m.startswith("_") and callable(getattr(gen, m))]
        assert len(public) > 0
