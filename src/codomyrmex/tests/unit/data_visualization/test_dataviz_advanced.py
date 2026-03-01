"""Unit tests for advanced/specialized visualization types."""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pytest

# Use non-interactive backend for testing
matplotlib.use('Agg')


# ============================================================================
# TestThemes
# ============================================================================
@pytest.mark.unit
class TestThemes:
    """Test theme system."""

    def test_get_all_themes(self):
        """Test functionality: get all themes."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        for name in ThemeName:
            theme = get_theme(name)
            assert hasattr(theme, 'colors')
            assert theme.name == name

    def test_default_theme(self):
        """Test functionality: default theme."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        assert theme.colors.primary == "#1f77b4"

    def test_dark_theme(self):
        """Test functionality: dark theme."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DARK)
        assert theme.figure_facecolor == "#1a1a2e"

    def test_theme_to_rcparams(self):
        """Test functionality: theme to rcparams."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        params = theme.to_matplotlib_rcparams()
        assert isinstance(params, dict)
        assert 'figure.facecolor' in params
        assert 'axes.facecolor' in params
        assert 'font.family' in params

    def test_apply_theme(self):
        """Test functionality: apply theme."""
        from codomyrmex.data_visualization.themes import (
            ThemeName,
            apply_theme,
            get_theme,
        )
        theme = get_theme(ThemeName.LIGHT)
        apply_theme(theme)
        assert plt.rcParams['figure.facecolor'] == theme.figure_facecolor

    def test_list_themes(self):
        """Test functionality: list themes."""
        from codomyrmex.data_visualization.themes import list_themes
        themes = list_themes()
        assert isinstance(themes, list)
        assert len(themes) == 6
        assert "default" in themes
        assert "dark" in themes

    def test_color_palette_cycling(self):
        """Test functionality: color palette cycling."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.DEFAULT)
        palette = theme.colors
        # Should cycle
        color0 = palette.get_series_color(0)
        color_cycle = palette.get_series_color(len(palette.series))
        assert color0 == color_cycle

    def test_minimal_theme_no_grid(self):
        """Test functionality: minimal theme no grid."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.MINIMAL)
        assert theme.grid.show is False

    def test_scientific_theme_serif(self):
        """Test functionality: scientific theme serif."""
        from codomyrmex.data_visualization.themes import ThemeName, get_theme
        theme = get_theme(ThemeName.SCIENTIFIC)
        assert theme.fonts.family == "serif"


# ============================================================================
# TestAdvancedPlotter
# ============================================================================
@pytest.mark.unit
class TestAdvancedPlotter:
    """Test the AdvancedPlotter class."""

    def test_create_figure(self):
        """Test functionality: create figure."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        fig, ax = plotter.create_figure()
        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plotter.clear_figures()

    def test_plot_line(self):
        """Test functionality: plot line."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        line = plotter.plot_line([1, 2, 3], [4, 5, 6], label="test")
        assert hasattr(line, 'get_xdata')
        plotter.clear_figures()

    def test_plot_scatter(self):
        """Test functionality: plot scatter."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        scatter = plotter.plot_scatter([1, 2, 3], [4, 5, 6])
        assert hasattr(scatter, 'get_offsets')
        plotter.clear_figures()

    def test_plot_bar(self):
        """Test functionality: plot bar."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        bars = plotter.plot_bar(['A', 'B'], [10, 20])
        assert isinstance(bars, matplotlib.container.BarContainer)
        plotter.clear_figures()

    def test_plot_histogram(self):
        """Test functionality: plot histogram."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        result = plotter.plot_histogram([1, 2, 2, 3, 3, 3])
        assert isinstance(result, tuple)  # (n, bins, patches)
        plotter.clear_figures()

    def test_plot_heatmap(self):
        """Test functionality: plot heatmap."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        try:
            hm = plotter.plot_heatmap([[1, 2], [3, 4]])
            assert isinstance(hm, plt.Axes)
        except TypeError:
            # seaborn version incompatibility with xticklabels
            pytest.skip("seaborn heatmap incompatible with current version")
        finally:
            plotter.clear_figures()

    def test_plot_box(self):
        """Test functionality: plot box."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        bp = plotter.plot_box({"A": [1, 2, 3], "B": [4, 5, 6]})
        assert isinstance(bp, dict)  # boxplot returns dict of artists
        plotter.clear_figures()

    def test_save_plot(self, tmp_path):
        """Test functionality: save plot."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        plotter.plot_line([1, 2, 3], [1, 4, 9])
        output = str(tmp_path / "adv_plot.png")
        result = plotter.save_plot(output)
        assert result is True
        assert Path(output).exists()
        plotter.clear_figures()

    def test_clear_figures(self):
        """Test functionality: clear figures."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            AdvancedPlotter,
        )
        plotter = AdvancedPlotter()
        plotter.create_figure()
        plotter.create_figure()
        assert len(plotter.figures) == 2
        plotter.clear_figures()
        assert len(plotter.figures) == 0
        assert plotter.current_figure is None

    def test_convenience_functions(self):
        """Test functionality: convenience functions."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            create_advanced_bar_chart,
            create_advanced_line_plot,
            create_advanced_scatter_plot,
            get_available_palettes,
            get_available_plot_types,
            get_available_styles,
        )
        assert callable(create_advanced_line_plot)
        assert callable(create_advanced_scatter_plot)
        assert callable(create_advanced_bar_chart)
        assert len(get_available_styles()) > 0
        assert len(get_available_palettes()) > 0
        assert len(get_available_plot_types()) > 0

    def test_plot_config_dataclass(self):
        """Test functionality: plot config dataclass."""
        from codomyrmex.data_visualization.engines.advanced_plotter import PlotConfig
        config = PlotConfig(title="Test", figsize=(8, 5), dpi=150)
        assert config.title == "Test"
        assert config.figsize == (8, 5)
        assert config.dpi == 150

    def test_enums(self):
        """Test functionality: enums."""
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            ChartStyle,
            ColorPalette,
            PlotType,
        )
        assert PlotType.LINE.value == "line"
        assert ChartStyle.DARK.value == "dark"
        assert ColorPalette.VIRIDIS.value == "viridis"


# ============================================================================
# TestMermaidBuilders
# ============================================================================
@pytest.mark.unit
class TestMermaidBuilders:
    """Test Mermaid diagram builder classes."""

    def test_flowchart_creation(self):
        """Test functionality: flowchart creation."""
        from codomyrmex.data_visualization.mermaid import (
            Flowchart,
            FlowDirection,
            NodeShape,
        )
        fc = Flowchart(direction=FlowDirection.TOP_DOWN)
        fc.add_node("A", "Start", NodeShape.ROUND)
        fc.add_node("B", "End", NodeShape.ROUND)
        fc.add_link("A", "B", "goes to")
        content = fc.render()
        assert "flowchart TD" in content
        assert "A" in content
        assert "B" in content

    def test_sequence_diagram(self):
        """Test functionality: sequence diagram."""
        from codomyrmex.data_visualization.mermaid import SequenceDiagram
        sd = SequenceDiagram()
        sd.add_participant("Alice")
        sd.add_participant("Bob")
        sd.add_message("Alice", "Bob", "Hello")
        content = sd.render()
        assert "sequenceDiagram" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_class_diagram(self):
        """Test functionality: class diagram."""
        from codomyrmex.data_visualization.mermaid import ClassDiagram
        cd = ClassDiagram()
        cd.add_class("Animal", attributes=["name: str"], methods=["speak()"])
        content = cd.render()
        assert "classDiagram" in content
        assert "Animal" in content

    def test_flowchart_subgraph(self):
        """Test functionality: flowchart subgraph."""
        from codomyrmex.data_visualization.mermaid import (
            Flowchart,
            FlowDirection,
            NodeShape,
        )
        fc = Flowchart(direction=FlowDirection.LEFT_RIGHT)
        fc.add_node("A", "Node A", NodeShape.RECTANGLE)
        fc.add_node("B", "Node B", NodeShape.RECTANGLE)
        fc.add_subgraph("Sub1", "My Subgraph", ["B"])
        content = fc.render()
        assert "subgraph" in content

    def test_to_markdown(self):
        """Test functionality: to markdown."""
        from codomyrmex.data_visualization.mermaid import Flowchart, FlowDirection
        fc = Flowchart(direction=FlowDirection.TOP_DOWN)
        md = fc.to_markdown()
        assert "```mermaid" in md
        assert "```" in md


# ============================================================================
# TestMermaidGenerator
# ============================================================================
@pytest.mark.unit
class TestMermaidGenerator:
    """Test MermaidDiagramGenerator."""

    def test_git_branch_diagram(self):
        """Test functionality: git branch diagram."""
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        branches = [{"name": "main", "created_at": "2024-01-01"}]
        commits = [
            {"hash": "abc123", "message": "Init", "branch": "main", "date": "2024-01-01"},
        ]
        content = gen.create_git_branch_diagram(branches=branches, commits=commits)
        assert content  # non-empty

    def test_git_workflow_diagram(self):
        """Test functionality: git workflow diagram."""
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        workflow_steps = [
            {"name": "checkout", "description": "Checkout code"},
            {"name": "build", "description": "Build project"},
        ]
        content = gen.create_git_workflow_diagram(workflow_steps=workflow_steps, title="Test Workflow")
        assert content
        assert len(content) > 0

    def test_commit_timeline_diagram(self):
        """Test functionality: commit timeline diagram."""
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            create_commit_timeline_diagram,
        )
        commits = [
            {"hash": "abc", "message": "First", "date": "2024-01-01"},
            {"hash": "def", "message": "Second", "date": "2024-01-02"},
        ]
        content = create_commit_timeline_diagram(commits=commits)
        assert content

    def test_repository_structure_diagram(self):
        """Test functionality: repository structure diagram."""
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        structure = {"src": {"main.py": "file"}, "README.md": "file"}
        content = gen.create_repository_structure_diagram(repo_structure=structure)
        assert content

    def test_save_mermaid_to_file(self, tmp_path):
        """Test functionality: save mermaid to file."""
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        output = str(tmp_path / "test.mmd")
        workflow_steps = [
            {"name": "checkout", "description": "Checkout code"},
        ]
        content = gen.create_git_workflow_diagram(
            workflow_steps=workflow_steps, title="Save Test", output_path=output
        )
        assert content
        assert Path(output).exists()


# ============================================================================
# TestGitVisualizer
# ============================================================================
@pytest.mark.unit
class TestGitVisualizer:
    """Test GitVisualizer class."""

    def test_instantiation(self):
        """Test functionality: instantiation."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        assert isinstance(viz, GitVisualizer)
        assert hasattr(viz.mermaid_generator, 'create_git_branch_diagram')
        assert "main" in viz.colors

    def test_git_tree_png_with_sample_data(self, tmp_path):
        """Test functionality: git tree png with sample data."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "git_tree.png")
        result = viz.visualize_git_tree_png(title="Test Tree", output_path=output)
        assert result is True
        assert Path(output).exists()

    def test_git_tree_mermaid_with_sample_data(self, tmp_path):
        """Test functionality: git tree mermaid with sample data."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "git_tree.mmd")
        content = viz.visualize_git_tree_mermaid(title="Test Mermaid", output_path=output)
        assert content  # non-empty string

    def test_commit_activity_png(self, tmp_path):
        """Test functionality: commit activity png."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "activity.png")
        result = viz.visualize_commit_activity_png(title="Activity", output_path=output)
        assert result is True
        assert Path(output).exists()

    def test_repository_summary_png(self, tmp_path):
        """Test functionality: repository summary png."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        output = str(tmp_path / "summary.png")
        result = viz.visualize_repository_summary_png(
            title="Summary", output_path=output
        )
        assert result is True
        assert Path(output).exists()

    def test_branch_color_mapping(self):
        """Test functionality: branch color mapping."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        assert viz._get_branch_color("main") == viz.colors["main"]
        assert viz._get_branch_color("develop") == viz.colors["develop"]
        assert viz._get_branch_color("feature/auth") == viz.colors["feature"]
        assert viz._get_branch_color("hotfix/urgent") == viz.colors["hotfix"]
        assert viz._get_branch_color("release/1.0") == viz.colors["release"]
        assert viz._get_branch_color("other") == viz.colors["commit"]

    def test_sample_commits_generation(self):
        """Test functionality: sample commits generation."""
        from codomyrmex.data_visualization.git.git_visualizer import GitVisualizer
        viz = GitVisualizer()
        commits = viz._generate_sample_commits(10)
        assert len(commits) == 10
        assert all("hash" in c and "message" in c for c in commits)

    def test_convenience_functions(self, tmp_path):
        """Test functionality: convenience functions."""
        from codomyrmex.data_visualization.git.git_visualizer import (
            create_git_tree_mermaid,
            create_git_tree_png,
        )
        png_output = str(tmp_path / "conv_tree.png")
        result = create_git_tree_png(output_path=png_output, title="Conv PNG")
        assert result is True

        mmd_output = str(tmp_path / "conv_tree.mmd")
        content = create_git_tree_mermaid(output_path=mmd_output, title="Conv Mermaid")
        assert content


# ============================================================================
# TestExceptions
# ============================================================================
@pytest.mark.unit
class TestExceptions:
    """Test exception hierarchy."""

    def test_exception_hierarchy(self):
        """Test functionality: exception hierarchy."""
        from codomyrmex.data_visualization.exceptions import (
            ChartCreationError,
            DataVisualizationError,
            GitVisualizationError,
            InvalidDataError,
            MermaidGenerationError,
            PlotSaveError,
            ThemeError,
        )
        from codomyrmex.exceptions import PlottingError, VisualizationError

        # DataVisualizationError inherits from VisualizationError
        assert issubclass(DataVisualizationError, VisualizationError)

        # ChartCreationError inherits from PlottingError
        assert issubclass(ChartCreationError, PlottingError)

        # All custom exceptions inherit from DataVisualizationError
        assert issubclass(InvalidDataError, DataVisualizationError)
        assert issubclass(ThemeError, DataVisualizationError)
        assert issubclass(MermaidGenerationError, DataVisualizationError)
        assert issubclass(GitVisualizationError, DataVisualizationError)
        assert issubclass(PlotSaveError, DataVisualizationError)

    def test_exceptions_are_raisable(self):
        """Test functionality: exceptions are raisable."""
        from codomyrmex.data_visualization.exceptions import (
            ChartCreationError,
            DataVisualizationError,
            InvalidDataError,
        )

        with pytest.raises(DataVisualizationError):
            raise DataVisualizationError("test error")

        with pytest.raises(ChartCreationError):
            raise ChartCreationError("chart error")

        with pytest.raises(InvalidDataError):
            raise InvalidDataError("bad data")

    def test_exception_message(self):
        """Test functionality: exception message."""
        from codomyrmex.data_visualization.exceptions import DataVisualizationError
        err = DataVisualizationError("something went wrong")
        assert "something went wrong" in str(err)


# ============================================================================
# TestPlotter (engines.plotter.Plotter)
# ============================================================================
@pytest.mark.unit
class TestPlotter:
    """Test the Plotter wrapper class."""

    def test_plotter_bar_chart(self, tmp_path):
        """Test functionality: plotter bar chart."""
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.bar_chart(['A', 'B'], [1, 2], output_path=str(tmp_path / "p_bar.png"))
        assert isinstance(fig, plt.Figure)

    def test_plotter_line_plot(self, tmp_path):
        """Test functionality: plotter line plot."""
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.line_plot([1, 2, 3], [4, 5, 6], output_path=str(tmp_path / "p_line.png"))
        assert isinstance(fig, plt.Figure)

    def test_plotter_heatmap(self, tmp_path):
        """Test functionality: plotter heatmap."""
        from codomyrmex.data_visualization.engines.plotter import Plotter
        p = Plotter()
        fig = p.heatmap([[1, 2], [3, 4]], output_path=str(tmp_path / "p_hm.png"))
        assert isinstance(fig, plt.Figure)

    def test_plotter_default_figure_size(self):
        """Test functionality: plotter default figure size."""
        from codomyrmex.data_visualization.engines.plotter import (
            DEFAULT_FIGURE_SIZE,
            Plotter,
        )
        p = Plotter()
        assert p.figure_size == DEFAULT_FIGURE_SIZE


# Coverage push -- data_visualization
class TestAdvancedPlotterCoverage:
    """Coverage tests for AdvancedPlotter."""

    def test_chart_style_enum(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import ChartStyle
        assert len(list(ChartStyle)) > 0

    def test_plot_config(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import PlotConfig
        cfg = PlotConfig()
        assert isinstance(cfg, PlotConfig)

    def test_create_bar_chart(self, tmp_path):
        import matplotlib

        from codomyrmex.data_visualization.engines.advanced_plotter import (
            create_advanced_bar_chart,
        )
        matplotlib.use("Agg")
        fig = create_advanced_bar_chart(["A", "B", "C"], [10, 20, 30], title="Test")
        assert isinstance(fig, plt.Figure)

    def test_dataset_dataclass(self):
        from codomyrmex.data_visualization.engines.advanced_plotter import (
            DataPoint,
            Dataset,
            PlotType,
        )
        dp1 = DataPoint(x=1.0, y=2.0)
        dp2 = DataPoint(x=2.0, y=3.0)
        ds = Dataset(name="test", data=[dp1, dp2], plot_type=list(PlotType)[0], label="test")
        assert ds.label == "test"


class TestMermaidGeneratorExtended:
    """Extended tests for Mermaid diagram generation."""

    def test_create_git_branch_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            create_git_branch_diagram,
        )
        result = create_git_branch_diagram()
        assert isinstance(result, str)

    def test_create_commit_timeline(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            create_commit_timeline_diagram,
        )
        result = create_commit_timeline_diagram()
        assert isinstance(result, str)


class TestMermaidDeep:
    """Deep tests for mermaid diagram generation."""

    def test_create_git_workflow(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            create_git_workflow_diagram,
        )
        result = create_git_workflow_diagram()
        assert isinstance(result, str)

    def test_create_repo_structure(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            create_repository_structure_diagram,
        )
        result = create_repository_structure_diagram()
        assert isinstance(result, str)

    def test_generator_branch_diagram(self):
        from codomyrmex.data_visualization.mermaid.mermaid_generator import (
            MermaidDiagramGenerator,
        )
        gen = MermaidDiagramGenerator()
        branches = [{"name": "main", "commits": ["abc", "def"]}]
        commits = [{"hash": "abc", "message": "init"}, {"hash": "def", "message": "feat"}]
        diagram = gen.create_git_branch_diagram(branches=branches, commits=commits)
        assert isinstance(diagram, str)
