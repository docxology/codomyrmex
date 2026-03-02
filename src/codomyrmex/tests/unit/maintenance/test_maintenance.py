"""Unit tests for tools module - comprehensive testing with real implementations.

Tests for DependencyAnalyzer, DependencyChecker, project analysis functions,
dependency consolidator, deprecation notice utilities, and validate_dependencies.
"""

import time
from pathlib import Path

import pytest

from codomyrmex.maintenance.analyze_project import (
    analyze_code_quality,
    analyze_dependencies,
    analyze_project_structure,
    generate_report,
)

# Test with real implementations
from codomyrmex.maintenance.deps.dependency_analyzer import DependencyAnalyzer
from codomyrmex.maintenance.deps.dependency_checker import (
    check_dependencies,
    check_python_version,
)

# ==================== Module Import Tests ====================


@pytest.mark.unit
class TestMaintenanceModuleImport:
    """Tests for maintenance module import."""

    def test_maintenance_module_import(self):
        """Test that maintenance module can be imported."""
        from codomyrmex import maintenance
        assert maintenance is not None

    def test_maintenance_module_has_path(self):
        """Test maintenance module has __path__ attribute."""
        from codomyrmex import maintenance
        assert hasattr(maintenance, "__path__")


# ==================== DependencyAnalyzer Tests ====================


@pytest.mark.unit
class TestDependencyAnalyzerInit:
    """Tests for DependencyAnalyzer initialization."""

    def test_initialization_with_path(self):
        """Test initializing with a path."""
        repo_root = Path(".")
        analyzer = DependencyAnalyzer(repo_root)

        assert analyzer is not None
        assert analyzer.project_root == repo_root.resolve()

    def test_initialization_with_string(self):
        """Test initializing with string path."""
        analyzer = DependencyAnalyzer(".")

        assert analyzer is not None
        assert isinstance(analyzer.project_root, Path)

    def test_initialization_sets_src_path(self):
        """Test that initialization sets src_path correctly."""
        analyzer = DependencyAnalyzer(".")

        assert "src" in str(analyzer.src_path)
        assert "codomyrmex" in str(analyzer.src_path)

    def test_initialization_empty_containers(self):
        """Test that initialization creates empty containers."""
        analyzer = DependencyAnalyzer(".")

        assert isinstance(analyzer.imports, dict)
        assert isinstance(analyzer.modules, set)
        assert isinstance(analyzer.circular_deps, list)
        assert isinstance(analyzer.violations, list)
        assert len(analyzer.modules) == 0
        assert len(analyzer.circular_deps) == 0
        assert len(analyzer.violations) == 0

    def test_allowed_dependencies_configured(self):
        """Test that allowed dependencies are configured."""
        analyzer = DependencyAnalyzer(".")

        assert isinstance(analyzer.allowed_dependencies, dict)
        assert "logging_monitoring" in analyzer.allowed_dependencies
        assert "environment_setup" in analyzer.allowed_dependencies


@pytest.mark.unit
class TestDependencyAnalyzerExtractImports:
    """Tests for extract_imports method."""

    def test_extract_imports_from_file(self, tmp_path):
        """Test extracting imports from a Python file."""
        # Create a test file with codomyrmex imports
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
from codomyrmex.logging_monitoring import get_logger
from codomyrmex.utils import helper
import codomyrmex.cache
""")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "logging_monitoring" in imports
        assert "utils" in imports
        assert "cache" in imports

    def test_extract_imports_no_codomyrmex(self, tmp_path):
        """Test extracting imports with no codomyrmex imports."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path
""")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert len(imports) == 0

    def test_extract_imports_syntax_error_handling(self, tmp_path):
        """Test handling of syntax errors in files."""
        test_file = tmp_path / "bad_syntax.py"
        test_file.write_text("def broken(:\n    pass")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        # Should return empty set, not raise exception
        assert isinstance(imports, set)

    def test_extract_imports_empty_file(self, tmp_path):
        """Test extracting imports from empty file."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert len(imports) == 0

    def test_extract_imports_import_from_statement(self, tmp_path):
        """Test extracting 'from X import Y' statements."""
        test_file = tmp_path / "test.py"
        test_file.write_text("from codomyrmex.encryption.core.encryptor import Encryptor")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "encryption" in imports

    def test_extract_imports_direct_import(self, tmp_path):
        """Test extracting 'import X' statements."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import codomyrmex.validation")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "validation" in imports

    def test_extract_imports_multiple_imports_same_module(self, tmp_path):
        """Test extracting multiple imports from same module."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
from codomyrmex.cache import Cache
from codomyrmex.cache import CacheManager
from codomyrmex.cache.backends import InMemoryCache
""")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "cache" in imports
        assert len([i for i in imports if i == "cache"]) == 1  # No duplicates

    def test_extract_imports_aliased_import(self, tmp_path):
        """Test extracting aliased imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text("import codomyrmex.validation as val")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "validation" in imports


@pytest.mark.unit
class TestDependencyAnalyzerScanModule:
    """Tests for scan_module method."""

    def test_scan_module_nonexistent(self):
        """Test scanning a nonexistent module."""
        analyzer = DependencyAnalyzer(".")

        # Should not raise an exception
        analyzer.scan_module("nonexistent_module_xyz")

        assert "nonexistent_module_xyz" not in analyzer.modules

    def test_scan_module_adds_to_modules(self):
        """Test that scanning adds module to modules set."""
        analyzer = DependencyAnalyzer(".")

        # Scan a real module
        analyzer.scan_module("logging_monitoring")

        assert "logging_monitoring" in analyzer.modules

    def test_scan_module_records_imports(self):
        """Test that scanning records module imports."""
        analyzer = DependencyAnalyzer(".")

        analyzer.scan_module("maintenance")

        assert "maintenance" in analyzer.imports

    def test_scan_module_idempotent(self):
        """Test that scanning same module twice is idempotent."""
        analyzer = DependencyAnalyzer(".")

        analyzer.scan_module("logging_monitoring")
        initial_count = len(analyzer.modules)

        analyzer.scan_module("logging_monitoring")
        assert len(analyzer.modules) == initial_count


@pytest.mark.unit
class TestDependencyAnalyzerScanAll:
    """Tests for scan_all_modules method."""

    def test_scan_all_modules(self):
        """Test scanning all modules."""
        analyzer = DependencyAnalyzer(".")

        analyzer.scan_all_modules()

        # Should have found multiple modules
        assert len(analyzer.modules) > 0
        # Should include known modules
        assert "logging_monitoring" in analyzer.modules or len(analyzer.modules) > 5

    def test_scan_all_modules_populates_imports(self):
        """Test scan_all_modules populates imports dict."""
        analyzer = DependencyAnalyzer(".")

        analyzer.scan_all_modules()

        assert len(analyzer.imports) > 0


@pytest.mark.unit
class TestDependencyAnalyzerCircularDeps:
    """Tests for circular dependency detection."""

    def test_detect_circular_dependencies_empty(self):
        """Test detection with no modules scanned."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.detect_circular_dependencies()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_detect_circular_dependencies_returns_list(self):
        """Test that detection returns a list of tuples."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()

        result = analyzer.detect_circular_dependencies()

        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_detect_circular_dependencies_stores_result(self):
        """Test that detection stores result in circular_deps."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()

        result = analyzer.detect_circular_dependencies()

        assert analyzer.circular_deps == result


@pytest.mark.unit
class TestDependencyAnalyzerValidateHierarchy:
    """Tests for dependency hierarchy validation."""

    def test_validate_hierarchy_returns_list(self):
        """Test that validation returns a list."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.validate_dependency_hierarchy()

        assert isinstance(result, list)

    def test_validate_hierarchy_violation_format(self):
        """Test violation dictionary format."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()

        violations = analyzer.validate_dependency_hierarchy()

        for violation in violations:
            assert "module" in violation
            assert "imported" in violation
            assert "allowed" in violation
            assert "severity" in violation

    def test_validate_hierarchy_stores_violations(self):
        """Test that validation stores violations."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()

        violations = analyzer.validate_dependency_hierarchy()

        assert analyzer.violations == violations


@pytest.mark.unit
class TestDependencyAnalyzerReports:
    """Tests for report generation."""

    def test_generate_report_format(self):
        """Test report generation format."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()
        analyzer.detect_circular_dependencies()
        analyzer.validate_dependency_hierarchy()

        report = analyzer.generate_report()

        assert isinstance(report, str)
        assert "# Dependency Analysis Report" in report
        assert "Circular Dependencies" in report
        assert "Hierarchy Violations" in report

    def test_generate_mermaid_graph(self):
        """Test Mermaid graph generation."""
        analyzer = DependencyAnalyzer(".")
        analyzer.scan_all_modules()

        graph = analyzer.generate_mermaid_graph()

        assert isinstance(graph, str)
        assert "```mermaid" in graph
        assert "graph TD" in graph
        assert "```" in graph

    def test_generate_report_with_no_issues(self):
        """Test report generation with no issues detected."""
        analyzer = DependencyAnalyzer(".")

        report = analyzer.generate_report()

        assert isinstance(report, str)
        assert "# Dependency Analysis Report" in report


@pytest.mark.unit
class TestDependencyAnalyzerAnalyze:
    """Tests for full analyze method."""

    def test_analyze_returns_dict(self):
        """Test that analyze returns a dictionary."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.analyze()

        assert isinstance(result, dict)

    def test_analyze_contains_expected_keys(self):
        """Test that analyze result contains expected keys."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.analyze()

        assert "modules" in result
        assert "imports" in result
        assert "circular_dependencies" in result
        assert "violations" in result
        assert "summary" in result

    def test_analyze_summary_structure(self):
        """Test analyze summary structure."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.analyze()

        summary = result["summary"]
        assert "total_modules" in summary
        assert "modules_with_imports" in summary
        assert "circular_count" in summary
        assert "violation_count" in summary

    def test_analyze_modules_is_list(self):
        """Test that modules in result is a list."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.analyze()

        assert isinstance(result["modules"], list)

    def test_analyze_imports_is_dict(self):
        """Test that imports in result is a dict."""
        analyzer = DependencyAnalyzer(".")

        result = analyzer.analyze()

        assert isinstance(result["imports"], dict)


# ==================== DependencyChecker Tests ====================


@pytest.mark.unit
class TestDependencyChecker:
    """Tests for dependency checking functionality."""

    def test_check_python_version_returns_dict(self):
        """Test check_python_version returns a dictionary."""
        result = check_python_version()

        assert isinstance(result, dict)

    def test_check_python_version_has_version(self):
        """Test that result contains version info."""
        result = check_python_version()

        assert "current_version" in result or "version" in result

    def test_check_python_version_meets_requirement(self):
        """Test that result indicates if requirement is met."""
        result = check_python_version()

        assert "meets_requirement" in result or "compatible" in result

    def test_check_dependencies_returns_dict(self):
        """Test check_dependencies returns a dictionary."""
        result = check_dependencies()

        assert isinstance(result, dict)

    def test_check_dependencies_has_status(self):
        """Test check_dependencies has status."""
        result = check_dependencies()

        # Should have some indication of status
        assert len(result) > 0


# ==================== Project Analysis Tests ====================


@pytest.mark.unit
class TestAnalyzeProjectStructure:
    """Tests for project structure analysis."""

    def test_returns_dict(self):
        """Test that analyze_project_structure returns a dict."""
        result = analyze_project_structure()

        assert isinstance(result, dict)

    def test_contains_directories(self):
        """Test result contains directories info."""
        result = analyze_project_structure()

        assert "directories" in result

    def test_contains_file_types(self):
        """Test result contains file types."""
        result = analyze_project_structure()

        assert "file_types" in result

    def test_contains_total_size(self):
        """Test result contains total size."""
        result = analyze_project_structure()

        assert "total_size" in result
        assert isinstance(result["total_size"], (int, float))

    def test_file_types_categorized(self):
        """Test that file types are categorized."""
        result = analyze_project_structure()

        file_types = result["file_types"]
        # Should have at least Python files
        assert ".py" in file_types or len(file_types) > 0

    def test_directories_is_dict(self):
        """Test directories is a dictionary."""
        result = analyze_project_structure()

        assert isinstance(result["directories"], dict)


@pytest.mark.unit
class TestAnalyzeDependencies:
    """Tests for dependency analysis."""

    def test_returns_dict(self):
        """Test analyze_dependencies returns a dict."""
        result = analyze_dependencies()

        assert isinstance(result, dict)

    def test_contains_python_requires(self):
        """Test result contains Python requirement."""
        result = analyze_dependencies()

        assert "python_requires" in result

    def test_contains_main_dependencies(self):
        """Test result contains main dependencies."""
        result = analyze_dependencies()

        assert "main_dependencies" in result
        assert isinstance(result["main_dependencies"], list)

    def test_contains_dev_dependencies(self):
        """Test result contains dev dependencies."""
        result = analyze_dependencies()

        assert "dev_dependencies" in result
        assert isinstance(result["dev_dependencies"], list)

    def test_total_count_computed(self):
        """Test total count is computed."""
        result = analyze_dependencies()

        assert "total_count" in result
        expected_total = len(result["main_dependencies"]) + len(result["dev_dependencies"])
        assert result["total_count"] == expected_total

    def test_main_dependencies_are_strings(self):
        """Test main dependencies are strings."""
        result = analyze_dependencies()

        for dep in result["main_dependencies"]:
            assert isinstance(dep, str)


@pytest.mark.unit
class TestAnalyzeCodeQuality:
    """Tests for code quality analysis."""

    def test_returns_dict(self):
        """Test analyze_code_quality returns a dict."""
        result = analyze_code_quality()

        assert isinstance(result, dict)

    def test_counts_python_files(self):
        """Test that Python files are counted."""
        result = analyze_code_quality()

        assert "total_python_files" in result
        assert result["total_python_files"] > 0

    def test_counts_test_files(self):
        """Test that test files are counted."""
        result = analyze_code_quality()

        assert "test_files" in result
        assert isinstance(result["test_files"], int)

    def test_counts_documentation_files(self):
        """Test that documentation files are counted."""
        result = analyze_code_quality()

        assert "documentation_files" in result
        assert isinstance(result["documentation_files"], int)

    def test_checks_for_tests(self):
        """Test that tests presence is checked."""
        result = analyze_code_quality()

        assert "has_tests" in result
        assert isinstance(result["has_tests"], bool)

    def test_checks_for_ci(self):
        """Test that CI presence is checked."""
        result = analyze_code_quality()

        assert "has_ci" in result
        assert isinstance(result["has_ci"], bool)

    def test_checks_for_linting(self):
        """Test that linting config is checked."""
        result = analyze_code_quality()

        assert "has_linting" in result
        assert isinstance(result["has_linting"], bool)

    def test_positive_file_counts(self):
        """Test file counts are non-negative."""
        result = analyze_code_quality()

        assert result["total_python_files"] >= 0
        assert result["test_files"] >= 0
        assert result["documentation_files"] >= 0


@pytest.mark.unit
class TestGenerateReport:
    """Tests for report generation."""

    def test_generates_string_report(self):
        """Test that generate_report returns a string."""
        structure = {"directories": {}, "file_types": {}, "total_size": 1000}
        deps = {"main_dependencies": [], "dev_dependencies": [], "total_count": 0}
        quality = {
            "total_python_files": 10,
            "test_files": 2,
            "documentation_files": 5,
            "has_tests": True,
            "has_ci": True,
            "has_linting": True,
        }

        report = generate_report(structure, deps, quality)

        assert isinstance(report, str)

    def test_report_contains_sections(self):
        """Test report contains expected sections."""
        structure = {"directories": {}, "file_types": {".py": []}, "total_size": 1000}
        deps = {"main_dependencies": ["pytest"], "dev_dependencies": [], "total_count": 1}
        quality = {
            "total_python_files": 10,
            "test_files": 2,
            "documentation_files": 5,
            "has_tests": True,
            "has_ci": True,
            "has_linting": True,
        }

        report = generate_report(structure, deps, quality)

        assert "Project Structure" in report
        assert "Dependencies" in report
        assert "Code Quality" in report

    def test_report_recommendations_when_missing(self):
        """Test report includes recommendations when features missing."""
        structure = {"directories": {}, "file_types": {}, "total_size": 1000}
        deps = {"main_dependencies": [], "dev_dependencies": [], "total_count": 0}
        quality = {
            "total_python_files": 10,
            "test_files": 2,
            "documentation_files": 5,
            "has_tests": False,
            "has_ci": False,
            "has_linting": False,
        }

        report = generate_report(structure, deps, quality)

        assert "Recommendations" in report

    def test_report_no_recommendations_when_complete(self):
        """Test report when all features present."""
        structure = {"directories": {}, "file_types": {".py": []}, "total_size": 1000}
        deps = {"main_dependencies": ["pytest"], "dev_dependencies": [], "total_count": 1}
        quality = {
            "total_python_files": 10,
            "test_files": 2,
            "documentation_files": 5,
            "has_tests": True,
            "has_ci": True,
            "has_linting": True,
        }

        report = generate_report(structure, deps, quality)

        assert isinstance(report, str)
        assert len(report) > 0


# ==================== Dependency Consolidator Tests ====================


@pytest.mark.unit
class TestDependencyConsolidator:
    """Tests for dependency consolidator functions."""

    def test_parse_requirements_file_empty(self, tmp_path):
        """Test parsing empty requirements file."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            parse_requirements_file,
        )

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("")

        result = parse_requirements_file(req_file)

        assert result == []

    def test_parse_requirements_file_nonexistent(self, tmp_path):
        """Test parsing nonexistent requirements file."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            parse_requirements_file,
        )

        req_file = tmp_path / "nonexistent.txt"

        result = parse_requirements_file(req_file)

        assert result == []

    def test_parse_requirements_file_with_packages(self, tmp_path):
        """Test parsing requirements file with packages."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            parse_requirements_file,
        )

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""pytest==7.0.0
requests>=2.28.0
# This is a comment
click
""")

        result = parse_requirements_file(req_file)

        assert len(result) == 3
        assert any(r[0] == "pytest" for r in result)
        assert any(r[0] == "requests" for r in result)
        assert any(r[0] == "click" for r in result)

    def test_parse_requirements_file_with_comments(self, tmp_path):
        """Test parsing requirements file skips comments."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            parse_requirements_file,
        )

        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""# Comment line
pytest==7.0.0  # inline comment
""")

        result = parse_requirements_file(req_file)

        assert len(result) == 1
        assert result[0][0] == "pytest"

    def test_find_all_requirements_files(self, tmp_path):
        """Test finding requirements files."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            find_all_requirements_files,
        )

        # Create directory structure
        src_dir = tmp_path / "src" / "codomyrmex"
        src_dir.mkdir(parents=True)

        module1 = src_dir / "module1"
        module1.mkdir()
        (module1 / "requirements.txt").write_text("pytest")

        module2 = src_dir / "module2"
        module2.mkdir()
        (module2 / "requirements.txt").write_text("requests")

        result = find_all_requirements_files(tmp_path)

        assert len(result) == 2

    def test_generate_deprecation_notice(self):
        """Test generating deprecation notice."""
        from codomyrmex.maintenance.deps.dependency_consolidator import (
            generate_deprecation_notice,
        )

        notice = generate_deprecation_notice("auth", "pyproject.toml")

        assert "DEPRECATED" in notice
        assert "auth" in notice
        assert "pyproject.toml" in notice


# ==================== Deprecation Notice Tests ====================


@pytest.mark.unit
class TestDeprecationNotice:
    """Tests for deprecation notice utilities."""

    def test_get_module_name_from_path(self):
        """Test extracting module name from path."""
        from codomyrmex.maintenance.add_deprecation_notices import get_module_name

        path = Path("/src/codomyrmex/auth/requirements.txt")
        result = get_module_name(path)

        assert result == "auth"

    def test_get_module_name_unknown(self):
        """Test get_module_name with unknown path."""
        from codomyrmex.maintenance.add_deprecation_notices import get_module_name

        path = Path("/some/other/path.txt")
        result = get_module_name(path)

        assert result == "unknown"

    def test_get_dependency_location_optional(self):
        """Test get_dependency_location for optional modules."""
        from codomyrmex.maintenance.add_deprecation_notices import (
            get_dependency_location,
        )

        result = get_dependency_location("code_review")

        assert "optional-dependencies" in result

    def test_get_dependency_location_main(self):
        """Test get_dependency_location for main modules."""
        from codomyrmex.maintenance.add_deprecation_notices import (
            get_dependency_location,
        )

        result = get_dependency_location("some_other_module")

        assert "project.dependencies" in result


# ==================== Integration Tests ====================


@pytest.mark.unit
class TestMaintenanceIntegration:
    """Integration tests for tools module."""

    def test_full_project_analysis_workflow(self):
        """Test complete project analysis workflow."""
        # Run all analyses
        structure = analyze_project_structure()
        deps = analyze_dependencies()
        quality = analyze_code_quality()

        # Generate report
        report = generate_report(structure, deps, quality)

        # All should complete without error
        assert structure is not None
        assert deps is not None
        assert quality is not None
        assert report is not None
        assert len(report) > 0

    def test_dependency_analyzer_full_workflow(self):
        """Test complete dependency analyzer workflow."""
        analyzer = DependencyAnalyzer(".")

        # Run full analysis
        result = analyzer.analyze()

        # Generate outputs
        report = analyzer.generate_report()
        graph = analyzer.generate_mermaid_graph()

        assert result is not None
        assert report is not None
        assert graph is not None

    def test_all_analysis_functions_return_consistent_types(self):
        """Test that all analysis functions return consistent types."""
        structure = analyze_project_structure()
        deps = analyze_dependencies()
        quality = analyze_code_quality()

        assert isinstance(structure, dict)
        assert isinstance(deps, dict)
        assert isinstance(quality, dict)


# ==================== Allowed Dependencies Tests ====================


@pytest.mark.unit
class TestAllowedDependencies:
    """Tests for allowed dependency configuration."""

    def test_foundation_layer_no_deps(self):
        """Test foundation layer modules have no dependencies."""
        analyzer = DependencyAnalyzer(".")

        # Foundation modules should have empty or minimal allowed deps
        assert analyzer.allowed_dependencies.get("environment_setup") == set()
        assert analyzer.allowed_dependencies.get("logging_monitoring") == set()

    def test_analysis_layer_deps(self):
        """Test analysis layer allowed dependencies."""
        analyzer = DependencyAnalyzer(".")

        static_analysis_deps = analyzer.allowed_dependencies.get("static_analysis", set())
        assert "logging_monitoring" in static_analysis_deps

    def test_build_layer_deps(self):
        """Test build layer allowed dependencies."""
        analyzer = DependencyAnalyzer(".")

        build_deps = analyzer.allowed_dependencies.get("build_synthesis", set())
        assert "logging_monitoring" in build_deps
        assert "static_analysis" in build_deps

    def test_allowed_dependencies_are_sets(self):
        """Test that all allowed dependencies are sets."""
        analyzer = DependencyAnalyzer(".")

        for module, deps in analyzer.allowed_dependencies.items():
            assert isinstance(deps, set), f"Dependencies for {module} should be a set"


# ==================== Edge Cases Tests ====================


@pytest.mark.unit
class TestMaintenanceEdgeCases:
    """Tests for edge cases in tools module."""

    def test_analyzer_with_empty_project(self, tmp_path):
        """Test analyzer with empty project directory."""
        # Create minimal structure
        src_dir = tmp_path / "src" / "codomyrmex"
        src_dir.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        result = analyzer.analyze()

        assert result is not None
        assert isinstance(result["modules"], list)

    def test_extract_imports_with_try_except(self, tmp_path):
        """Test extracting imports from file with try/except."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
try:
    from codomyrmex.cache import Cache
except ImportError:
    Cache = None
""")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "cache" in imports

    def test_extract_imports_conditional(self, tmp_path):
        """Test extracting conditional imports."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
if True:
    import codomyrmex.validation
else:
    import codomyrmex.cache
""")

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "validation" in imports
        assert "cache" in imports

    def test_generate_report_handles_empty_inputs(self):
        """Test generate_report handles empty inputs gracefully."""
        report = generate_report({}, {}, {})

        assert isinstance(report, str)


# From test_tier3_promotions.py
class TestMaintenanceScheduler:
    """Tests for MaintenanceScheduler."""

    def test_register_and_execute(self):
        """Test functionality: register and execute."""
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler,
            MaintenanceTask,
            ScheduleConfig,
            TaskStatus,
        )
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="test_task",
            description="Test task",
            action=lambda: "done",
            schedule=ScheduleConfig(max_retries=0),
        )
        scheduler.register(task)
        result = scheduler.execute("test_task")
        assert result.status == TaskStatus.COMPLETED
        assert result.output == "done"

    def test_due_tasks(self):
        """Test functionality: due tasks."""
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler,
            MaintenanceTask,
            ScheduleConfig,
        )
        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="due_task",
            description="Due task",
            action=lambda: None,
            schedule=ScheduleConfig(interval_seconds=10, run_on_startup=True),
        )
        scheduler.register(task)
        due = scheduler.get_due_tasks(time.time())
        assert len(due) == 1

    def test_failed_task_retries(self):
        """Test functionality: failed task retries."""
        from codomyrmex.maintenance.health.scheduler import (
            MaintenanceScheduler,
            MaintenanceTask,
            ScheduleConfig,
            TaskStatus,
        )
        call_count = 0
        def failing_action():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("fail")

        scheduler = MaintenanceScheduler()
        task = MaintenanceTask(
            name="fail_task",
            description="Failing task",
            action=failing_action,
            schedule=ScheduleConfig(max_retries=2, retry_delay_seconds=0.001),
        )
        scheduler.register(task)
        result = scheduler.execute("fail_task")
        assert result.status == TaskStatus.FAILED
        assert call_count == 3  # initial + 2 retries


# From test_tier3_promotions_pass2.py
class TestHealthChecker:
    """Tests for HealthChecker."""

    def test_healthy_check(self):
        """Test functionality: healthy check."""
        from codomyrmex.maintenance.health.health_check import (
            HealthCheck,
            HealthChecker,
            HealthStatus,
        )
        checker = HealthChecker()
        checker.register(HealthCheck(
            name="test",
            description="Always healthy",
            check_fn=lambda: (HealthStatus.HEALTHY, "OK", {}),
        ))
        report = checker.run_all()
        assert report.overall_status == HealthStatus.HEALTHY
        assert report.healthy_count == 1

    def test_unhealthy_check(self):
        """Test functionality: unhealthy check."""
        from codomyrmex.maintenance.health.health_check import (
            HealthCheck,
            HealthChecker,
            HealthStatus,
        )
        checker = HealthChecker()
        checker.register(HealthCheck(
            name="bad",
            description="Always fails",
            check_fn=lambda: (HealthStatus.UNHEALTHY, "Down", {}),
            critical=True,
        ))
        report = checker.run_all()
        assert report.overall_status == HealthStatus.UNHEALTHY

    def test_exception_handling(self):
        """Test functionality: exception handling."""
        from codomyrmex.maintenance.health.health_check import (
            HealthCheck,
            HealthChecker,
            HealthStatus,
        )
        def exploding():
            raise RuntimeError("boom")

        checker = HealthChecker()
        checker.register(HealthCheck(
            name="explode",
            description="Raises",
            check_fn=exploding,
        ))
        result = checker.run("explode")
        assert result.status == HealthStatus.UNHEALTHY
        assert "boom" in result.message
