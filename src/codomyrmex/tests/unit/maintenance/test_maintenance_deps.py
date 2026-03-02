"""Unit tests for maintenance/deps subpackage.

Comprehensive tests for dependency_analyzer, dependency_consolidator,
dependency_checker, and validate_dependencies — covering graph analysis,
consolidation, conflict detection, requirement parsing, circular dependency
detection, and pyproject.toml validation.

Zero-mock policy: all tests use real data structures, tmp_path fixtures,
and in-memory strings. No mocks, stubs, or fakes.
"""


import pytest

from codomyrmex.maintenance.deps.dependency_analyzer import DependencyAnalyzer
from codomyrmex.maintenance.deps.dependency_checker import (
    check_python_version,
)
from codomyrmex.maintenance.deps.dependency_checker import (
    generate_report as checker_generate_report,
)
from codomyrmex.maintenance.deps.dependency_consolidator import (
    find_all_requirements_files,
    generate_deprecation_notice,
    generate_pyproject_additions,
    parse_requirements_file,
)
from codomyrmex.maintenance.deps.validate_dependencies import (
    check_duplicates,
    check_requirements_txt_deprecated,
    check_version_constraints,
    parse_pyproject_dependencies,
)

# ---------------------------------------------------------------------------
# 1. Requirement string parsing (dependency_consolidator.parse_requirements_file)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestParseRequirementsFile:
    """Tests for requirement string parsing from files."""

    @pytest.mark.parametrize(
        "line,expected_name,expected_version",
        [
            ("requests==2.28.0", "requests", "==2.28.0"),
            ("flask>=2.0", "flask", ">=2.0"),
            ("click~=8.1", "click", "~=8.1"),
            ("numpy!=1.21.0", "numpy", "!=1.21.0"),
            ("pandas<2.0", "pandas", "<2.0"),
            ("scipy", "scipy", ""),
            ("black>=22.0,<24.0", "black", ">=22.0"),  # parser captures first operator+version
        ],
        ids=[
            "pinned-exact",
            "gte-version",
            "compatible-release",
            "not-equal",
            "less-than",
            "bare-name",
            "compound-constraint",
        ],
    )
    def test_parse_various_requirement_formats(
        self, tmp_path, line, expected_name, expected_version
    ):
        """Parametrized: parse different requirement string formats."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(line + "\n")

        result = parse_requirements_file(req_file)

        assert len(result) >= 1
        assert result[0][0] == expected_name
        assert result[0][1] == expected_version

    def test_parse_skips_blank_lines_and_comments(self, tmp_path):
        """Blank lines and comment-only lines are skipped."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(
            "# full-line comment\n"
            "\n"
            "   \n"
            "requests==2.0\n"
            "# another comment\n"
        )

        result = parse_requirements_file(req_file)

        assert len(result) == 1
        assert result[0][0] == "requests"

    def test_parse_strips_inline_comments(self, tmp_path):
        """Inline comments after the package spec are removed."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests>=2.0  # HTTP library\n")

        result = parse_requirements_file(req_file)

        assert len(result) == 1
        assert result[0][0] == "requests"
        assert "HTTP" not in result[0][1]

    def test_parse_lowercases_package_names(self, tmp_path):
        """Package names are normalized to lowercase."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("Flask==2.0\nDjango>=3.0\n")

        result = parse_requirements_file(req_file)

        names = [r[0] for r in result]
        assert "flask" in names
        assert "django" in names

    def test_parse_records_source_file(self, tmp_path):
        """Each parsed dependency records the source file path."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.0\n")

        result = parse_requirements_file(req_file)

        assert result[0][2] == str(req_file)

    def test_parse_nonexistent_file(self, tmp_path):
        """Parsing a nonexistent file returns an empty list."""
        result = parse_requirements_file(tmp_path / "missing.txt")

        assert result == []


# ---------------------------------------------------------------------------
# 2. Version conflict detection (validate_dependencies.check_version_constraints)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestVersionConflictDetection:
    """Tests for version constraint and conflict checking."""

    def test_detects_missing_version_constraint(self):
        """Packages without version constraints are flagged."""
        deps = {
            "dependencies": [("requests", ">=2.0"), ("click", "")],
        }

        errors = check_version_constraints(deps)

        assert len(errors) == 1
        assert "click" in errors[0]

    def test_all_constrained_no_errors(self):
        """When all packages have version constraints, no errors."""
        deps = {
            "dependencies": [
                ("requests", ">=2.0"),
                ("flask", "==2.3.0"),
            ],
        }

        errors = check_version_constraints(deps)

        assert errors == []

    def test_multiple_sections_checked(self):
        """Constraints are checked across all sections."""
        deps = {
            "dependencies": [("requests", ">=2.0")],
            "optional-dev": [("pytest", ""), ("black", ">=22.0")],
        }

        errors = check_version_constraints(deps)

        assert len(errors) == 1
        assert "pytest" in errors[0]

    def test_duplicate_detection_across_sections(self):
        """Packages appearing in multiple sections are reported."""
        deps = {
            "dependencies": [("requests", ">=2.0")],
            "optional-http": [("requests", ">=2.28")],
        }

        warnings = check_duplicates(deps)

        assert len(warnings) == 1
        assert "requests" in warnings[0]

    def test_no_duplicates_no_warnings(self):
        """No warnings when all packages are unique across sections."""
        deps = {
            "dependencies": [("requests", ">=2.0")],
            "optional-http": [("httpx", ">=0.24")],
        }

        warnings = check_duplicates(deps)

        assert warnings == []


# ---------------------------------------------------------------------------
# 3. Pyproject.toml parsing (validate_dependencies.parse_pyproject_dependencies)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestParsePyprojectDependencies:
    """Tests for parsing pyproject.toml dependency sections."""

    def test_parse_main_dependencies_section(self):
        """Parse [project.dependencies] section."""
        content = (
            '[project.dependencies]\n'
            '"requests>=2.28"\n'
            '"click>=8.0"\n'
        )

        result = parse_pyproject_dependencies(content)

        assert "dependencies" in result
        names = [pkg for pkg, _ in result["dependencies"]]
        assert "requests" in names
        assert "click" in names

    def test_parse_optional_dependencies_section(self):
        """Parse [project.optional-dependencies] section."""
        content = (
            '[project.optional-dependencies]\n'
            '"httpx>=0.24"\n'
        )

        result = parse_pyproject_dependencies(content)

        assert "optional-dependencies" in result

    def test_section_reset_on_new_header(self):
        """Parser resets current section on non-dependency header."""
        content = (
            '[project.dependencies]\n'
            '"requests>=2.28"\n'
            '\n'
            '[tool.pytest.ini_options]\n'
            '"not-a-dep>=1.0"\n'
        )

        result = parse_pyproject_dependencies(content)

        all_names = []
        for section_deps in result.values():
            all_names.extend(pkg for pkg, _ in section_deps)
        assert "not-a-dep" not in all_names

    def test_empty_content_returns_empty_dict(self):
        """Empty content yields empty dictionary."""
        result = parse_pyproject_dependencies("")

        assert result == {}

    def test_comments_are_skipped(self):
        """Lines starting with # inside sections are skipped."""
        content = (
            '[project.dependencies]\n'
            '# This is a comment\n'
            '"requests>=2.28"\n'
        )

        result = parse_pyproject_dependencies(content)

        names = [pkg for pkg, _ in result.get("dependencies", [])]
        assert "requests" in names
        assert len(names) == 1


# ---------------------------------------------------------------------------
# 4. Circular dependency detection (DependencyAnalyzer)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCircularDependencyDetection:
    """Tests for DependencyAnalyzer circular dependency detection with synthetic graphs."""

    def test_no_cycles_in_linear_graph(self, tmp_path):
        """A -> B -> C has no circular dependencies."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"a", "b", "c"}
        analyzer.imports = {
            "a": {"b"},
            "b": {"c"},
            "c": set(),
        }

        circular = analyzer.detect_circular_dependencies()

        assert circular == []

    def test_detects_direct_cycle(self, tmp_path):
        """A -> B -> A is a direct circular dependency."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"a", "b"}
        analyzer.imports = {
            "a": {"b"},
            "b": {"a"},
        }

        circular = analyzer.detect_circular_dependencies()

        assert len(circular) >= 1
        # Both directions should appear (a,b) and/or (b,a)
        flat = set()
        for pair in circular:
            flat.add(pair[0])
            flat.add(pair[1])
        assert "a" in flat
        assert "b" in flat

    def test_no_cycle_with_isolated_nodes(self, tmp_path):
        """Isolated nodes (no imports) produce no cycles."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"x", "y", "z"}
        analyzer.imports = {
            "x": set(),
            "y": set(),
            "z": set(),
        }

        circular = analyzer.detect_circular_dependencies()

        assert circular == []

    def test_stores_circular_deps_on_instance(self, tmp_path):
        """detect_circular_dependencies stores result on self.circular_deps."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"a", "b"}
        analyzer.imports = {"a": {"b"}, "b": {"a"}}

        result = analyzer.detect_circular_dependencies()

        assert analyzer.circular_deps is result


# ---------------------------------------------------------------------------
# 5. Dependency hierarchy validation (DependencyAnalyzer)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDependencyHierarchyValidation:
    """Tests for dependency hierarchy validation with synthetic data."""

    def test_no_violations_for_allowed_imports(self, tmp_path):
        """No violations when imports respect allowed dependencies."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"static_analysis", "logging_monitoring"}
        analyzer.imports = {
            "static_analysis": {"logging_monitoring"},
            "logging_monitoring": set(),
        }

        violations = analyzer.validate_dependency_hierarchy()

        assert violations == []

    def test_violation_for_disallowed_import(self, tmp_path):
        """Importing a disallowed module produces a violation."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"environment_setup", "static_analysis"}
        analyzer.imports = {
            "environment_setup": {"static_analysis"},
            "static_analysis": set(),
        }

        violations = analyzer.validate_dependency_hierarchy()

        assert len(violations) == 1
        assert violations[0]["module"] == "environment_setup"
        assert violations[0]["imported"] == "static_analysis"
        assert violations[0]["severity"] == "error"

    def test_documentation_module_exempt(self, tmp_path):
        """documentation module is exempt from hierarchy validation."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"documentation", "security"}
        analyzer.imports = {
            "documentation": {"security"},
            "security": set(),
        }

        violations = analyzer.validate_dependency_hierarchy()

        # documentation can import from all modules
        assert violations == []

    def test_unknown_modules_skipped(self, tmp_path):
        """Modules not in allowed_dependencies map are skipped."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"unknown_module_xyz", "logging_monitoring"}
        analyzer.imports = {
            "unknown_module_xyz": {"logging_monitoring"},
            "logging_monitoring": set(),
        }

        violations = analyzer.validate_dependency_hierarchy()

        assert violations == []


# ---------------------------------------------------------------------------
# 6. Dependency tree / graph generation (DependencyAnalyzer report+mermaid)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDependencyTreeGeneration:
    """Tests for report and mermaid graph generation from synthetic data."""

    def test_report_includes_module_count(self, tmp_path):
        """Report header includes the count of analyzed modules."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"alpha", "beta", "gamma"}
        analyzer.imports = {"alpha": {"beta"}, "beta": set(), "gamma": set()}
        analyzer.circular_deps = []
        analyzer.violations = []

        report = analyzer.generate_report()

        assert "3 modules" in report

    def test_report_shows_circular_deps_when_present(self, tmp_path):
        """Report lists circular dependencies when they exist."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"a", "b"}
        analyzer.imports = {"a": {"b"}, "b": {"a"}}
        analyzer.circular_deps = [("a", "b")]
        analyzer.violations = []

        report = analyzer.generate_report()

        assert "circular" in report.lower()
        assert "a" in report
        assert "b" in report

    def test_report_shows_no_issues_message(self, tmp_path):
        """Report shows success message when no circular deps or violations."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"alpha"}
        analyzer.imports = {"alpha": set()}
        analyzer.circular_deps = []
        analyzer.violations = []

        report = analyzer.generate_report()

        assert "No circular dependencies detected" in report
        assert "No hierarchy violations detected" in report

    def test_mermaid_graph_contains_nodes(self, tmp_path):
        """Mermaid graph includes nodes for all modules."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"alpha", "beta"}
        analyzer.imports = {"alpha": {"beta"}, "beta": set()}
        analyzer.violations = []
        analyzer.circular_deps = []

        graph = analyzer.generate_mermaid_graph()

        assert "```mermaid" in graph
        assert "graph TD" in graph
        assert "alpha" in graph
        assert "beta" in graph

    def test_mermaid_graph_shows_violations(self, tmp_path):
        """Mermaid graph edges include violation markers."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)

        analyzer = DependencyAnalyzer(tmp_path)
        analyzer.modules = {"alpha", "beta"}
        analyzer.imports = {"alpha": {"beta"}, "beta": set()}
        analyzer.violations = [
            {"module": "alpha", "imported": "beta", "allowed": "none", "severity": "error"}
        ]
        analyzer.circular_deps = []

        graph = analyzer.generate_mermaid_graph()

        assert "violation" in graph


# ---------------------------------------------------------------------------
# 7. Consolidation and deduplication (dependency_consolidator)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDependencyConsolidation:
    """Tests for merging, deduplicating, and consolidating dependency lists."""

    def test_find_requirements_files_in_structure(self, tmp_path):
        """Finds all requirements.txt files under src/codomyrmex/*/."""
        src = tmp_path / "src" / "codomyrmex"
        for name in ["auth", "cache", "api"]:
            mod = src / name
            mod.mkdir(parents=True)
            (mod / "requirements.txt").write_text(f"{name}-lib==1.0\n")

        result = find_all_requirements_files(tmp_path)

        assert len(result) == 3

    def test_find_requirements_files_empty_tree(self, tmp_path):
        """Returns empty list when no src/codomyrmex exists."""
        result = find_all_requirements_files(tmp_path)

        assert result == []

    def test_generate_pyproject_additions_filters_existing(self):
        """Packages already in pyproject.toml are excluded from additions."""
        deps = {
            "requests": {
                "versions": {">=2.28"},
                "sources": [("mod1/requirements.txt", ">=2.28")],
                "conflicts": [],
            },
        }
        pyproject_content = '"requests>=2.28"\n'

        section, mapping = generate_pyproject_additions(deps, pyproject_content)

        # requests is already in pyproject, so it should not appear in mapping
        all_pkgs = []
        for pkgs in mapping.values():
            all_pkgs.extend(pkgs)
        assert not any("requests" in p for p in all_pkgs)

    def test_generate_pyproject_additions_includes_new_packages(self):
        """New packages not in pyproject.toml are included."""
        deps = {
            "httpx": {
                "versions": {">=0.24"},
                "sources": [
                    ("src/codomyrmex/api/requirements.txt", ">=0.24"),
                ],
                "conflicts": [],
            },
        }
        pyproject_content = '"requests>=2.28"\n'

        section, mapping = generate_pyproject_additions(deps, pyproject_content)

        assert "api" in mapping
        assert any("httpx" in pkg for pkg in mapping["api"])

    def test_generate_deprecation_notice_contains_module_name(self):
        """Deprecation notice references the correct module name."""
        notice = generate_deprecation_notice("encryption", "pyproject.toml")

        assert "DEPRECATED" in notice
        assert "encryption" in notice
        assert "uv sync --extra encryption" in notice

    def test_generate_deprecation_notice_contains_new_location(self):
        """Deprecation notice references the migration target."""
        notice = generate_deprecation_notice("cache", "pyproject.toml [optional-dependencies.cache]")

        assert "pyproject.toml" in notice


# ---------------------------------------------------------------------------
# 8. Unused dependency detection / requirements.txt deprecation
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRequirementsTxtDeprecation:
    """Tests for checking requirements.txt deprecation status."""

    def test_detects_missing_deprecation_notice(self, tmp_path):
        """Files without DEPRECATED header are flagged."""
        src = tmp_path / "src" / "codomyrmex"
        mod = src / "some_module"
        mod.mkdir(parents=True)
        (mod / "requirements.txt").write_text("requests>=2.0\n")

        errors = check_requirements_txt_deprecated(tmp_path)

        assert len(errors) == 1
        assert "missing deprecation notice" in errors[0].lower() or "DEPRECATED" in errors[0]

    def test_passes_with_deprecation_notice(self, tmp_path):
        """Files starting with '# DEPRECATED' pass the check."""
        src = tmp_path / "src" / "codomyrmex"
        mod = src / "some_module"
        mod.mkdir(parents=True)
        (mod / "requirements.txt").write_text(
            "# DEPRECATED: use pyproject.toml\nrequests>=2.0\n"
        )

        errors = check_requirements_txt_deprecated(tmp_path)

        assert errors == []

    def test_no_requirements_files_no_errors(self, tmp_path):
        """When no requirements.txt files exist, no errors."""
        src = tmp_path / "src" / "codomyrmex"
        mod = src / "clean_module"
        mod.mkdir(parents=True)
        (mod / "__init__.py").write_text("")

        errors = check_requirements_txt_deprecated(tmp_path)

        assert errors == []

    def test_nonexistent_src_dir_no_errors(self, tmp_path):
        """When src/codomyrmex does not exist, returns empty list."""
        errors = check_requirements_txt_deprecated(tmp_path)

        assert errors == []


# ---------------------------------------------------------------------------
# 9. Dependency checker report generation
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCheckerReportGeneration:
    """Tests for dependency_checker.generate_report with synthetic data."""

    def test_report_contains_python_version_section(self):
        """Report includes Python Version section."""
        py_version = {"current_version": "3.11.5", "meets_requirement": True, "status": "ok"}
        deps = {"core": {"click": {"installed": True, "status": "ok"}}}
        security = {"pip_audit_available": False, "safety_available": False, "vulnerabilities": []}
        env = {"virtual_env": True, "uv_available": True, "git_available": True, "docker_available": False}

        report = checker_generate_report(py_version, deps, security, env)

        assert "Python Version" in report
        assert "3.11.5" in report

    def test_report_flags_missing_dependencies(self):
        """Report marks missing dependencies."""
        py_version = {"current_version": "3.11.0", "meets_requirement": True, "status": "ok"}
        deps = {
            "core": {
                "installed_pkg": {"installed": True, "status": "ok"},
                "missing_pkg": {"installed": False, "status": "missing"},
            }
        }
        security = {"pip_audit_available": False, "safety_available": False, "vulnerabilities": []}
        env = {"virtual_env": True, "uv_available": True, "git_available": True, "docker_available": False}

        report = checker_generate_report(py_version, deps, security, env)

        assert "missing_pkg" in report
        assert "Missing" in report

    def test_report_security_section(self):
        """Report includes Security section."""
        py_version = {"current_version": "3.11.0", "meets_requirement": True, "status": "ok"}
        deps = {}
        security = {"pip_audit_available": True, "safety_available": False, "vulnerabilities": []}
        env = {"virtual_env": False, "uv_available": False, "git_available": False, "docker_available": False}

        report = checker_generate_report(py_version, deps, security, env)

        assert "Security" in report

    def test_report_environment_section(self):
        """Report includes Development Environment section."""
        py_version = {"current_version": "3.11.0", "meets_requirement": True, "status": "ok"}
        deps = {}
        security = {"pip_audit_available": False, "safety_available": False, "vulnerabilities": []}
        env = {"virtual_env": True, "uv_available": True, "git_available": True, "docker_available": True}

        report = checker_generate_report(py_version, deps, security, env)

        assert "Development Environment" in report


# ---------------------------------------------------------------------------
# 10. Python version checking (dependency_checker)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCheckPythonVersion:
    """Tests for check_python_version real execution."""

    def test_returns_dict_with_expected_keys(self):
        """check_python_version returns dict with required keys."""
        result = check_python_version()

        assert isinstance(result, dict)
        assert "current_version" in result
        assert "meets_requirement" in result
        assert "status" in result

    def test_version_is_string(self):
        """Reported version is a string."""
        result = check_python_version()

        assert isinstance(result["current_version"], str)
        assert "." in result["current_version"]

    def test_meets_requirement_for_current_python(self):
        """Current Python (3.10+) should meet the requirement."""
        import sys
        if sys.version_info < (3, 10):
            pytest.skip("Test requires Python 3.10+")

        result = check_python_version()

        assert result["meets_requirement"] is True
        assert result["status"] == "ok"


# ---------------------------------------------------------------------------
# 11. DependencyAnalyzer.extract_imports edge cases
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestExtractImportsEdgeCases:
    """Additional edge case tests for extract_imports."""

    def test_extract_imports_deeply_nested_package(self, tmp_path):
        """Deeply nested codomyrmex imports still extract the top module."""
        test_file = tmp_path / "deep.py"
        test_file.write_text(
            "from codomyrmex.security.secrets.vault import SecretVault\n"
        )

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert "security" in imports

    def test_extract_imports_mixed_codomyrmex_and_stdlib(self, tmp_path):
        """Only codomyrmex imports are extracted, stdlib is ignored."""
        test_file = tmp_path / "mixed.py"
        test_file.write_text(
            "import os\n"
            "import sys\n"
            "from pathlib import Path\n"
            "from codomyrmex.llm import provider\n"
            "import json\n"
        )

        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(test_file)

        assert imports == {"llm"}

    def test_extract_imports_nonexistent_file(self, tmp_path):
        """Extracting from a nonexistent file returns empty set (logged error)."""
        analyzer = DependencyAnalyzer(tmp_path)
        imports = analyzer.extract_imports(tmp_path / "ghost.py")

        assert imports == set()


# ---------------------------------------------------------------------------
# 12. Full analyze() pipeline with synthetic project
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAnalyzePipelineSynthetic:
    """Tests for the full analyze() pipeline on a synthetic project."""

    def _make_project(self, tmp_path):
        """Create a minimal synthetic project tree."""
        src = tmp_path / "src" / "codomyrmex"
        for mod_name, code in [
            ("alpha", "from codomyrmex.beta import something\n"),
            ("beta", "from codomyrmex.gamma import other\n"),
            ("gamma", "import os\n"),
        ]:
            mod = src / mod_name
            mod.mkdir(parents=True)
            (mod / "core.py").write_text(code)
        return tmp_path

    def test_analyze_finds_all_synthetic_modules(self, tmp_path):
        """analyze() discovers all modules in the synthetic project."""
        root = self._make_project(tmp_path)
        analyzer = DependencyAnalyzer(root)

        result = analyzer.analyze()

        assert "alpha" in result["modules"]
        assert "beta" in result["modules"]
        assert "gamma" in result["modules"]

    def test_analyze_records_imports_correctly(self, tmp_path):
        """analyze() correctly records import relationships."""
        root = self._make_project(tmp_path)
        analyzer = DependencyAnalyzer(root)

        result = analyzer.analyze()

        assert "beta" in result["imports"].get("alpha", [])
        assert "gamma" in result["imports"].get("beta", [])

    def test_analyze_summary_counts_match(self, tmp_path):
        """analyze() summary counts are consistent."""
        root = self._make_project(tmp_path)
        analyzer = DependencyAnalyzer(root)

        result = analyzer.analyze()

        assert result["summary"]["total_modules"] == len(result["modules"])
        assert result["summary"]["circular_count"] == len(result["circular_dependencies"])
        assert result["summary"]["violation_count"] == len(result["violations"])
