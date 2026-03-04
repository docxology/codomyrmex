"""Tests for data_visualization, documentation, coding, and agents modules.

Sprint 7 coverage push — batch 3: completing the remaining 4 modules.
"""

import os

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for CI

import pytest

# ===================================================================
# Data Visualization — Components
# ===================================================================

@pytest.mark.unit
class TestBaseComponent:
    """Test BaseComponent dataclass."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.data_visualization.components._base import BaseComponent
        c = BaseComponent()
        assert c.css_class == ""
        assert c.style == {}

    def test_render(self):
        """Verify render behavior."""
        from codomyrmex.data_visualization.components._base import BaseComponent
        c = BaseComponent(css_class="test-class")
        html = c.render()
        assert "test-class" in html
        assert "<div" in html

    def test_to_dict(self):
        """Verify to dict behavior."""
        from codomyrmex.data_visualization.components._base import BaseComponent
        c = BaseComponent()
        d = c.to_dict()
        assert d["type"] == "BaseComponent"

    def test_str(self):
        """Verify str behavior."""
        from codomyrmex.data_visualization.components._base import BaseComponent
        c = BaseComponent(css_class="x")
        assert str(c) == c.render()

    def test_repr(self):
        """Verify repr behavior."""
        from codomyrmex.data_visualization.components._base import BaseComponent
        c = BaseComponent(css_class="x")
        assert "BaseComponent" in repr(c)


@pytest.mark.unit
class TestBadge:
    """Test Badge component."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.data_visualization.components.badge import Badge
        b = Badge(label="OK", color="success")
        assert b.label == "OK"
        assert b.color == "success"

    def test_render_named_color(self):
        """Verify render named color behavior."""
        from codomyrmex.data_visualization.components.badge import Badge
        b = Badge(label="Pass", color="success")
        html = b.render()
        assert "#5cb85c" in html
        assert "Pass" in html

    def test_render_hex_color(self):
        """Verify render hex color behavior."""
        from codomyrmex.data_visualization.components.badge import Badge
        b = Badge(label="Custom", color="#FF0000")
        html = b.render()
        assert "#FF0000" in html

    def test_str(self):
        """Verify str behavior."""
        from codomyrmex.data_visualization.components.badge import Badge
        b = Badge(label="Test")
        assert "<span" in str(b)


@pytest.mark.unit
class TestAlert:
    """Test Alert component."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.data_visualization.components.alert import Alert
        a = Alert(message="Warning!", level="warning")
        assert a.message == "Warning!"
        assert a.level == "warning"

    def test_render_info(self):
        """Verify render info behavior."""
        from codomyrmex.data_visualization.components.alert import Alert
        a = Alert(message="Info message", level="info")
        html = a.render()
        assert "#d9edf7" in html
        assert "Info message" in html

    def test_render_danger(self):
        """Verify render danger behavior."""
        from codomyrmex.data_visualization.components.alert import Alert
        a = Alert(message="Error!", level="danger")
        html = a.render()
        assert "#f2dede" in html

    def test_render_unknown_level(self):
        """Verify render unknown level behavior."""
        from codomyrmex.data_visualization.components.alert import Alert
        a = Alert(message="x", level="custom")
        html = a.render()
        assert "#d9edf7" in html  # default fallback

    def test_str(self):
        """Verify str behavior."""
        from codomyrmex.data_visualization.components.alert import Alert
        a = Alert(message="Test")
        assert "<div" in str(a)


# ===================================================================
# Data Visualization — Charts
# ===================================================================

@pytest.mark.unit
class TestLinePlot:
    """Test LinePlot class and create_line_plot function."""

    def test_line_plot_class_init(self):
        """Verify line plot class init behavior."""
        from codomyrmex.data_visualization.charts.line_plot import LinePlot
        lp = LinePlot(x_data=[1, 2, 3], y_data=[4, 5, 6], title="Test")
        assert lp.title == "Test"
        assert lp.x_data == [1, 2, 3]

    def test_line_plot_render(self, tmp_path):
        """Verify line plot render behavior."""
        from codomyrmex.data_visualization.charts.line_plot import LinePlot
        lp = LinePlot(x_data=[1, 2, 3], y_data=[4, 5, 6], title="Test")
        out = str(tmp_path / "test_line.png")
        fig = lp.render(output_path=out)
        assert fig is not None
        assert os.path.exists(out)

    def test_create_line_plot_simple(self, tmp_path):
        """Verify create line plot simple behavior."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        out = str(tmp_path / "simple.png")
        fig = create_line_plot([1, 2, 3], [4, 5, 6], output_path=out)
        assert fig is not None
        assert os.path.exists(out)

    def test_create_line_plot_empty_data(self):
        """Verify create line plot empty data behavior."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        result = create_line_plot([], [], title="Empty")
        assert result is None

    def test_create_line_plot_multiple_lines(self, tmp_path):
        """Verify create line plot multiple lines behavior."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        x = [1, 2, 3]
        y = [[1, 2, 3], [3, 2, 1]]
        out = str(tmp_path / "multi.png")
        fig = create_line_plot(x, y, output_path=out, line_labels=["A", "B"])
        assert fig is not None

    def test_create_line_plot_length_mismatch(self):
        """Verify create line plot length mismatch behavior."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        result = create_line_plot([1, 2], [1, 2, 3])
        assert result is None

    def test_create_line_plot_with_markers(self, tmp_path):
        """Verify create line plot with markers behavior."""
        from codomyrmex.data_visualization.charts.line_plot import create_line_plot
        fig = create_line_plot([1, 2, 3], [1, 4, 9], markers=True,
                              output_path=str(tmp_path / "markers.png"))
        assert fig is not None

    def test_line_plot_save(self, tmp_path):
        """Verify line plot save behavior."""
        from codomyrmex.data_visualization.charts.line_plot import LinePlot
        lp = LinePlot(x_data=[1, 2], y_data=[3, 4])
        out = str(tmp_path / "saved.png")
        lp.save(out)
        assert os.path.exists(out)


# ===================================================================
# Documentation — Quality Assessment
# ===================================================================

@pytest.mark.unit
class TestDocumentationQualityAnalyzer:
    """Test DocumentationQualityAnalyzer."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        assert analyzer.quality_metrics is not None
        assert "completeness" in analyzer.quality_metrics

    def test_analyze_file_not_found(self, tmp_path):
        """Verify analyze file not found behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(tmp_path / "nonexistent.md")
        assert "error" in result

    def test_analyze_file_real(self, tmp_path):
        """Verify analyze file real behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        # Create a documentation file with standard sections
        doc = tmp_path / "README.md"
        doc.write_text("""# Overview

## Installation

```bash
pip install mypackage
```

## Usage

```python
import mypackage
```

## API

The `class MyClass` provides `method foo`.
Returns a `dict`.

## Examples

See the examples directory.

## Contributing

Please submit a PR.
""")
        analyzer = DocumentationQualityAnalyzer()
        result = analyzer.analyze_file(doc)
        assert "completeness" in result
        assert "consistency" in result
        assert "overall_score" in result
        assert result["completeness"] > 0
        assert result["overall_score"] > 0

    def test_assess_completeness_high(self):
        """Verify assess completeness high behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        content = "overview installation usage api examples ```code``` http://link"
        score = analyzer._assess_completeness(content)
        assert score >= 80.0

    def test_assess_completeness_low(self):
        """Verify assess completeness low behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        score = analyzer._assess_completeness("just some text")
        assert score < 50.0

    def test_assess_consistency_good(self):
        """Verify assess consistency good behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        content = "# H1\n## H2\n### H3\n```python\ncode\n```"
        score = analyzer._assess_consistency(content)
        assert score >= 80.0

    def test_assess_consistency_unclosed_code_block(self):
        """Verify assess consistency unclosed code block behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        content = "# Title\n```python\ncode\n"  # odd number of ```
        score = analyzer._assess_consistency(content)
        assert score < 100.0

    def test_assess_readability(self):
        """Verify assess readability behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        # Short, clear text
        score = analyzer._assess_readability("Simple clear text.")
        assert score >= 80.0

    def test_assess_structure_good(self):
        """Verify assess structure good behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        content = "# Title\n## Installation\n## Usage\n## API\n## Examples\n## Contributing"
        score = analyzer._assess_structure(content)
        assert score >= 50.0

    def test_assess_technical_accuracy(self):
        """Verify assess technical accuracy behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            DocumentationQualityAnalyzer,
        )
        analyzer = DocumentationQualityAnalyzer()
        content = "def foo(): pass\nclass Bar:\nimport os\nversion 1.0\nerror handling"
        score = analyzer._assess_technical_accuracy(content)
        assert score >= 50.0


@pytest.mark.unit
class TestGenerateQualityReport:
    """Test generate_quality_report function."""

    def test_report_with_readme(self, tmp_path):
        """Verify report with readme behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )
        readme = tmp_path / "README.md"
        readme.write_text("# Project\n\n## Installation\n\npip install it\n")
        report = generate_quality_report(tmp_path)
        assert "Documentation Quality Report" in report
        assert "README.md" in report

    def test_report_empty_project(self, tmp_path):
        """Verify report empty project behavior."""
        from codomyrmex.documentation.quality.quality_assessment import (
            generate_quality_report,
        )
        report = generate_quality_report(tmp_path)
        assert "Documentation Quality Report" in report


# ===================================================================
# Coding — Execution
# ===================================================================

@pytest.mark.unit
class TestValidateTimeout:
    """Test validate_timeout function."""

    def test_none_returns_default(self):
        """Verify none returns default behavior."""
        from codomyrmex.coding.execution.executor import (
            DEFAULT_TIMEOUT,
            validate_timeout,
        )
        assert validate_timeout(None) == DEFAULT_TIMEOUT

    def test_normal_value(self):
        """Verify normal value behavior."""
        from codomyrmex.coding.execution.executor import validate_timeout
        assert validate_timeout(60) == 60

    def test_too_high_clamped(self):
        """Verify too high clamped behavior."""
        from codomyrmex.coding.execution.executor import MAX_TIMEOUT, validate_timeout
        assert validate_timeout(999) == MAX_TIMEOUT

    def test_too_low_clamped(self):
        """Verify too low clamped behavior."""
        from codomyrmex.coding.execution.executor import MIN_TIMEOUT, validate_timeout
        assert validate_timeout(0) == MIN_TIMEOUT

    def test_negative_clamped(self):
        """Verify negative clamped behavior."""
        from codomyrmex.coding.execution.executor import MIN_TIMEOUT, validate_timeout
        assert validate_timeout(-10) == MIN_TIMEOUT


@pytest.mark.unit
class TestLanguageSupport:
    """Test language support functions."""

    def test_validate_python(self):
        """Verify validate python behavior."""
        from codomyrmex.coding.execution.language_support import validate_language
        assert validate_language("python") is True

    def test_validate_javascript(self):
        """Verify validate javascript behavior."""
        from codomyrmex.coding.execution.language_support import validate_language
        assert validate_language("javascript") is True

    def test_validate_unsupported(self):
        """Verify validate unsupported behavior."""
        from codomyrmex.coding.execution.language_support import validate_language
        assert validate_language("fortran") is False

    def test_supported_languages_dict(self):
        """Verify supported languages dict behavior."""
        from codomyrmex.coding.execution.language_support import SUPPORTED_LANGUAGES
        assert isinstance(SUPPORTED_LANGUAGES, dict)
        assert "python" in SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) >= 5


@pytest.mark.unit
class TestExecuteCodeValidation:
    """Test execute_code input validation (without Docker)."""

    def test_unsupported_language(self):
        """Verify unsupported language behavior."""
        from codomyrmex.coding.execution.executor import execute_code
        result = execute_code("cobol", "DISPLAY 'HELLO'")
        assert result["status"] == "setup_error"
        assert "not supported" in result["error_message"].lower() or "unsupported" in result["error_message"].lower()

    def test_empty_code(self):
        """Verify empty code behavior."""
        from codomyrmex.coding.execution.executor import execute_code
        result = execute_code("python", "")
        assert result["status"] == "setup_error"


# ===================================================================
# Agents — Registry
# ===================================================================

@pytest.mark.unit
class TestProbeResult:
    """Test ProbeResult dataclass."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.agents.agent_setup.registry import ProbeResult
        pr = ProbeResult(name="test", status="operative", detail="ok")
        assert pr.name == "test"
        assert pr.status == "operative"

    def test_is_operative_true(self):
        """Verify is operative true behavior."""
        from codomyrmex.agents.agent_setup.registry import ProbeResult
        pr = ProbeResult(name="test", status="operative", detail="ok")
        assert pr.is_operative is True

    def test_is_operative_false(self):
        """Verify is operative false behavior."""
        from codomyrmex.agents.agent_setup.registry import ProbeResult
        pr = ProbeResult(name="test", status="missing", detail="not found")
        assert pr.is_operative is False

    def test_latency(self):
        """Verify latency behavior."""
        from codomyrmex.agents.agent_setup.registry import ProbeResult
        pr = ProbeResult(name="test", status="operative", detail="ok", latency_ms=42.5)
        assert pr.latency_ms == 42.5


@pytest.mark.unit
class TestAgentDescriptor:
    """Test AgentDescriptor dataclass."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentDescriptor, ProbeResult
        desc = AgentDescriptor(
            name="test_agent",
            display_name="Test Agent",
            agent_type="api",
            env_var="TEST_KEY",
            config_key="test",
            default_model="gpt-4",
            probe=lambda: ProbeResult(name="test_agent", status="operative", detail="ok"),
        )
        assert desc.name == "test_agent"
        assert desc.agent_type == "api"

    def test_probe_callable(self):
        """Verify probe callable behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentDescriptor, ProbeResult
        desc = AgentDescriptor(
            name="test", display_name="Test", agent_type="api",
            env_var="X", config_key="x", default_model="m",
            probe=lambda: ProbeResult(name="test", status="operative", detail="ok"),
        )
        result = desc.probe()
        assert isinstance(result, ProbeResult)


@pytest.mark.unit
class TestAgentRegistry:
    """Test AgentRegistry."""

    def test_creation(self):
        """Verify creation behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentRegistry
        registry = AgentRegistry()
        assert registry is not None

    def test_list_agents(self):
        """Verify list agents behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentRegistry
        registry = AgentRegistry()
        agents = registry.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0

    def test_probe_all(self):
        """Verify probe all behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentRegistry
        registry = AgentRegistry()
        results = registry.probe_all()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_get_operative(self):
        """Verify get operative behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentRegistry
        registry = AgentRegistry()
        operative = registry.get_operative()
        assert isinstance(operative, list)

    def test_probe_unknown_agent(self):
        """Verify probe unknown agent behavior."""
        from codomyrmex.agents.agent_setup.registry import AgentRegistry
        registry = AgentRegistry()
        result = registry.probe_agent("nonexistent_agent_xyz")
        assert result is not None
        assert result.is_operative is False
