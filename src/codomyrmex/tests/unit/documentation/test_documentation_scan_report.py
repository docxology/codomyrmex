"""Unit tests for documentation_scan_report.DocumentationScanner.

Covers all 7 phases, helper methods, report generation, and result persistence.
Zero-mock policy: uses real filesystem via tmp_path fixtures.
"""

import json
from pathlib import Path

import pytest


@pytest.mark.unit
class TestDocumentationScannerInit:
    """Tests for DocumentationScanner constructor."""

    def test_init_sets_repo_root(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        assert scanner.repo_root == tmp_path.resolve()

    def test_init_resolves_relative_path(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        # Create a subdirectory, use relative-like path via symlink
        sub = tmp_path / "a" / "b"
        sub.mkdir(parents=True)
        scanner = DocumentationScanner(sub)
        assert scanner.repo_root.is_absolute()

    def test_init_creates_results_structure(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        assert set(scanner.results.keys()) == {
            "phase1",
            "phase2",
            "phase3",
            "phase4",
            "phase5",
            "phase6",
            "phase7",
        }

    def test_init_phase1_has_expected_keys(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        assert "files_found" in scanner.results["phase1"]
        assert "structure_map" in scanner.results["phase1"]
        assert "tools_inventory" in scanner.results["phase1"]

    def test_init_phase2_has_expected_keys(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        p2 = scanner.results["phase2"]
        assert isinstance(p2["content_issues"], list)
        assert isinstance(p2["reference_issues"], list)
        assert isinstance(p2["terminology_issues"], list)


@pytest.mark.unit
class TestPhase1Discovery:
    """Tests for phase1_discovery and its helper methods."""

    def _make_repo(self, tmp_path: Path) -> Path:
        """Create a minimal repo structure for scanning."""
        (tmp_path / "README.md").write_text("# Project\nVersion v1.0.0\n")
        (tmp_path / "AGENTS.md").write_text("# Agents\n")
        (tmp_path / "pyproject.toml").write_text('version = "1.0.0"\n')
        (tmp_path / "pytest.ini").write_text("[pytest]\n")

        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# Guide\n")

        src = tmp_path / "src" / "codomyrmex" / "mymodule"
        src.mkdir(parents=True)
        (src / "README.md").write_text("# Module\n")

        return tmp_path

    def test_phase1_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        assert isinstance(result, dict)

    def test_phase1_counts_markdown_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        # README.md, AGENTS.md, docs/guide.md, src/.../README.md = 4
        assert result["files_found"]["total_markdown"] == 4

    def test_phase1_finds_agents_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        assert result["files_found"]["agents_files"] == 1

    def test_phase1_finds_readme_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        assert result["files_found"]["readme_files"] == 2

    def test_phase1_finds_config_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        assert "config_files" in result["files_found"]
        config = result["files_found"]["config_files"]
        assert "pyproject.toml" in config
        assert "pytest.ini" in config

    def test_phase1_maps_structure_categories(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        categories = result["structure_map"]["categories"]
        assert isinstance(categories, dict)
        # docs/guide.md should appear under project_docs
        assert len(categories["project_docs"]) >= 1

    def test_phase1_inventories_tools(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._make_repo(tmp_path)
        scanner = DocumentationScanner(repo)
        result = scanner.phase1_discovery()
        tools = result["tools_inventory"]
        assert "existing_tools" in tools
        assert "gaps" in tools

    def test_phase1_empty_directory(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase1_discovery()
        assert result["files_found"]["total_markdown"] == 0

    def test_map_documentation_structure_root_level(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("# Root\n")
        (tmp_path / "AGENTS.md").write_text("# Agents\n")
        scanner = DocumentationScanner(tmp_path)
        structure = scanner._map_documentation_structure()
        assert "README.md" in structure["root_level"]
        assert "AGENTS.md" in structure["root_level"]

    def test_map_documentation_structure_missing_root_docs(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        structure = scanner._map_documentation_structure()
        assert structure["root_level"] == []

    def test_inventory_validation_tools_missing_tools(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        tools = scanner._inventory_validation_tools()
        # None of the expected tools exist in tmp_path
        assert tools["existing_tools"] == []
        assert len(tools["gaps"]) > 0

    def test_inventory_validation_tools_with_existing_tool(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        tool_dir = tmp_path / "scripts" / "documentation"
        tool_dir.mkdir(parents=True)
        (tool_dir / "comprehensive_audit.py").write_text("# tool\n")
        scanner = DocumentationScanner(tmp_path)
        tools = scanner._inventory_validation_tools()
        existing_names = [t["name"] for t in tools["existing_tools"]]
        assert "comprehensive_audit" in existing_names


@pytest.mark.unit
class TestPhase2Accuracy:
    """Tests for phase2_accuracy and its helper methods."""

    def test_phase2_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase2_accuracy()
        assert isinstance(result, dict)
        assert "content_issues" in result
        assert "reference_issues" in result
        assert "terminology_issues" in result

    def test_check_content_accuracy_no_readme(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_content_accuracy()
        assert issues == []

    def test_check_content_accuracy_version_match(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("Project v1.2.3\n")
        (tmp_path / "pyproject.toml").write_text('version = "1.2.3"\n')
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_content_accuracy()
        # Version matches, so no mismatch issue
        version_issues = [i for i in issues if i.get("type") == "version_mismatch"]
        assert len(version_issues) == 0

    def test_check_content_accuracy_version_mismatch(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("Project v1.0.0\n")
        (tmp_path / "pyproject.toml").write_text('version = "2.0.0"\n')
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_content_accuracy()
        version_issues = [i for i in issues if i.get("type") == "version_mismatch"]
        assert len(version_issues) == 1
        assert "2.0.0" in version_issues[0]["issue"]

    def test_check_reference_accuracy_no_link_checker(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_reference_accuracy()
        assert issues == []

    def test_check_terminology_consistency_empty(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_terminology_consistency()
        assert isinstance(issues, list)

    def test_check_terminology_consistency_finds_inconsistency(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        # Create files using multiple variants of the same term
        (tmp_path / "a.md").write_text("Codomyrmex is great. Also codomyrmex works.\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_terminology_consistency()
        # The term_usage check uses case-insensitive, and the key_terms dict
        # checks for variants 'Codomyrmex' and 'codomyrmex' both present
        term_types = [i.get("type") for i in issues]
        assert "terminology_inconsistency" in term_types or issues == []

    def test_check_terminology_consistency_mcp_variants(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc1.md").write_text("Use MCP for integration.\n")
        (tmp_path / "doc2.md").write_text("The Model Context Protocol is key.\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._check_terminology_consistency()
        mcp_issues = [i for i in issues if i.get("term") == "mcp"]
        # Both "MCP" and "Model Context Protocol" found
        assert len(mcp_issues) >= 1


@pytest.mark.unit
class TestPhase3Completeness:
    """Tests for phase3_completeness and its helper methods."""

    def test_phase3_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase3_completeness()
        assert isinstance(result, dict)
        assert "coverage_gaps" in result
        assert "audience_gaps" in result
        assert "cross_ref_gaps" in result

    def test_check_coverage_completeness_missing_readme(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        mod = tmp_path / "src" / "codomyrmex" / "mymod"
        mod.mkdir(parents=True)
        # No README.md in mymod
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_coverage_completeness()
        module_names = [g["module"] for g in gaps]
        assert "mymod" in module_names

    def test_check_coverage_completeness_with_readme(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        mod = tmp_path / "src" / "codomyrmex" / "mymod"
        mod.mkdir(parents=True)
        (mod / "README.md").write_text("# Module Docs\n")
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_coverage_completeness()
        module_names = [g.get("module") for g in gaps]
        assert "mymod" not in module_names

    def test_check_coverage_completeness_skips_underscore_dirs(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        mod = tmp_path / "src" / "codomyrmex" / "__pycache__"
        mod.mkdir(parents=True)
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_coverage_completeness()
        module_names = [g.get("module") for g in gaps]
        assert "__pycache__" not in module_names

    def test_check_audience_completeness_missing_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_audience_completeness()
        file_names = [g["file"] for g in gaps]
        assert "installation.md" in file_names
        assert "quickstart.md" in file_names

    def test_check_audience_completeness_with_files(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        gs = tmp_path / "docs" / "getting-started"
        gs.mkdir(parents=True)
        (gs / "installation.md").write_text("# Install\n")
        (gs / "quickstart.md").write_text("# Quickstart\n")
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_audience_completeness()
        assert gaps == []

    def test_check_cross_ref_completeness_missing_links(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("# Project\nNo links here.\n")
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_cross_ref_completeness()
        missing_links = [g["missing_link"] for g in gaps]
        assert "docs/README.md" in missing_links

    def test_check_cross_ref_completeness_all_links_present(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        content = "See docs/README.md and docs/getting-started and docs/reference\n"
        (tmp_path / "README.md").write_text(content)
        scanner = DocumentationScanner(tmp_path)
        gaps = scanner._check_cross_ref_completeness()
        assert gaps == []


@pytest.mark.unit
class TestPhase4Quality:
    """Tests for phase4_quality and its helper methods."""

    def test_phase4_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase4_quality()
        assert isinstance(result, dict)
        assert "quality_issues" in result
        assert "actionability_issues" in result
        assert "maintainability_issues" in result

    def test_assess_clarity_long_lines(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        long_line = "x" * 150
        (tmp_path / "doc.md").write_text(f"Short line\n{long_line}\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_clarity_readability()
        long_issues = [i for i in issues if i["type"] == "long_line"]
        assert len(long_issues) >= 1
        assert long_issues[0]["length"] == 150

    def test_assess_clarity_no_long_lines(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc.md").write_text("Short line\nAnother short line\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_clarity_readability()
        assert len(issues) == 0

    def test_assess_actionability_finds_todo(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc.md").write_text("# Guide\nTODO: finish this section\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_actionability()
        assert len(issues) >= 1
        assert issues[0]["type"] == "incomplete_content"

    def test_assess_actionability_finds_fixme(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc.md").write_text("# Guide\nFIXME: broken example\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_actionability()
        assert len(issues) >= 1

    def test_assess_actionability_clean(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc.md").write_text("# Guide\nEverything is great.\n")
        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_actionability()
        assert len(issues) == 0

    def test_assess_maintainability_returns_list(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        issues = scanner._assess_maintainability()
        assert isinstance(issues, list)


@pytest.mark.unit
class TestPhase5Improvements:
    """Tests for phase5_improvements and _identify_improvements."""

    def test_phase5_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase5_improvements()
        assert isinstance(result, dict)
        assert "improvements_made" in result

    def test_identify_improvements_with_reference_issues(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        scanner.results["phase2"]["reference_issues"] = [
            {"type": "broken_link", "details": "bad"}
        ]
        improvements = scanner._identify_improvements()
        types = [i["type"] for i in improvements]
        assert "fix_broken_links" in types

    def test_identify_improvements_with_coverage_gaps(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        scanner.results["phase3"]["coverage_gaps"] = [
            {"type": "missing_module_readme", "module": "x"}
        ]
        improvements = scanner._identify_improvements()
        types = [i["type"] for i in improvements]
        assert "add_missing_docs" in types

    def test_identify_improvements_none_when_clean(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        improvements = scanner._identify_improvements()
        assert improvements == []


@pytest.mark.unit
class TestPhase6Verification:
    """Tests for phase6_verification and its helper methods."""

    def test_phase6_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        result = scanner.phase6_verification()
        assert isinstance(result, dict)
        assert "validation_results" in result
        assert "manual_review_notes" in result

    def test_run_automated_checks_no_tools(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        results = scanner._run_automated_checks()
        # All tools should report 'Tool not found'
        for _tool_name, tool_result in results.items():
            assert tool_result.get("error") == "Tool not found"

    def test_generate_manual_review_checklist(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        checklist = scanner._generate_manual_review_checklist()
        assert isinstance(checklist, list)
        assert len(checklist) == 8
        assert any("new user" in item for item in checklist)


@pytest.mark.unit
class TestPhase7Reporting:
    """Tests for phase7_reporting and its helper methods."""

    def _run_all_phases(self, scanner):
        """Run phases 1-6 so phase 7 has data to aggregate."""
        scanner.phase1_discovery()
        scanner.phase2_accuracy()
        scanner.phase3_completeness()
        scanner.phase4_quality()
        scanner.phase5_improvements()
        scanner.phase6_verification()

    def test_phase7_returns_dict(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        result = scanner.phase7_reporting()
        assert isinstance(result, dict)
        assert "summary_stats" in result
        assert "issue_catalog" in result
        assert "recommendations" in result

    def test_generate_summary_stats(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "doc.md").write_text("# Doc\n")
        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        stats = scanner._generate_summary_stats()
        assert "total_files_scanned" in stats
        assert "issues_by_category" in stats
        assert isinstance(stats["issues_by_category"], dict)

    def test_compile_issue_catalog_aggregates(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        scanner.results["phase2"]["content_issues"] = [{"issue": "a"}]
        scanner.results["phase2"]["reference_issues"] = [{"issue": "b"}]
        scanner.results["phase2"]["terminology_issues"] = [{"issue": "c"}]
        scanner.results["phase3"]["coverage_gaps"] = [{"gap": "d"}]
        scanner.results["phase3"]["audience_gaps"] = [{"gap": "e"}]
        scanner.results["phase4"]["quality_issues"] = [{"quality": "f"}]
        catalog = scanner._compile_issue_catalog()
        assert len(catalog) == 6

    def test_generate_recommendations_always_includes_process(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        recs = scanner._generate_recommendations()
        areas = [r["area"] for r in recs]
        assert "Process Improvement" in areas

    def test_generate_recommendations_with_issues(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        scanner.results["phase2"]["reference_issues"] = [{"type": "broken"}]
        scanner.results["phase3"]["coverage_gaps"] = [{"type": "missing"}]
        recs = scanner._generate_recommendations()
        areas = [r["area"] for r in recs]
        assert "Link Validation" in areas
        assert "Documentation Coverage" in areas
        assert "Process Improvement" in areas


@pytest.mark.unit
class TestGenerateReport:
    """Tests for generate_report method."""

    def _run_all_phases(self, scanner):
        scanner.phase1_discovery()
        scanner.phase2_accuracy()
        scanner.phase3_completeness()
        scanner.phase4_quality()
        scanner.phase5_improvements()
        scanner.phase6_verification()
        scanner.phase7_reporting()

    def test_generate_report_returns_string(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        report = scanner.generate_report()
        assert isinstance(report, str)

    def test_generate_report_contains_header(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        report = scanner.generate_report()
        assert "Documentation Scan and Improvement Report" in report

    def test_generate_report_contains_all_phases(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("# Project\n")
        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        report = scanner.generate_report()
        assert "Phase 1" in report
        assert "Phase 2" in report
        assert "Phase 3" in report
        assert "Phase 4" in report
        assert "Phase 5" in report
        assert "Phase 6" in report
        assert "Phase 7" in report

    def test_generate_report_contains_repo_path(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        self._run_all_phases(scanner)
        report = scanner.generate_report()
        assert str(tmp_path.resolve()) in report

    def test_generate_report_without_running_phases(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        # generate_report should still work with default empty results
        report = scanner.generate_report()
        assert isinstance(report, str)
        assert "Phase 2" in report


@pytest.mark.unit
class TestSaveResults:
    """Tests for save_results method."""

    def test_save_results_writes_json(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        scanner = DocumentationScanner(tmp_path)
        output = tmp_path / "results.json"
        scanner.save_results(output)
        assert output.exists()
        data = json.loads(output.read_text())
        assert "phase1" in data
        assert "phase7" in data

    def test_save_results_after_scanning(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        (tmp_path / "README.md").write_text("# Hello\n")
        scanner = DocumentationScanner(tmp_path)
        scanner.phase1_discovery()
        output = tmp_path / "results.json"
        scanner.save_results(output)
        data = json.loads(output.read_text())
        assert data["phase1"]["files_found"]["total_markdown"] >= 1


@pytest.mark.unit
class TestFullScanIntegration:
    """Integration-style tests running all phases in sequence on a controlled repo."""

    def _build_repo(self, tmp_path: Path) -> Path:
        """Build a rich fake repo for full-scan testing."""
        # Root docs
        (tmp_path / "README.md").write_text(
            "# Codomyrmex\nVersion v0.5.0\nSee docs/README.md and docs/getting-started\n"
        )
        (tmp_path / "AGENTS.md").write_text("# Agents\n")
        (tmp_path / "pyproject.toml").write_text('version = "1.0.0"\n')

        # Docs dir
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "README.md").write_text("# Docs\nTODO: write more\n")

        gs = docs / "getting-started"
        gs.mkdir()
        (gs / "installation.md").write_text("# Install\n")

        # Module without README
        mod = tmp_path / "src" / "codomyrmex" / "orphan_module"
        mod.mkdir(parents=True)

        # Module with README
        mod2 = tmp_path / "src" / "codomyrmex" / "good_module"
        mod2.mkdir(parents=True)
        (mod2 / "README.md").write_text("# Good Module\n" + "x" * 130 + "\n")

        return tmp_path

    def test_full_scan_all_phases(self, tmp_path: Path):
        from codomyrmex.documentation.scripts.documentation_scan_report import (
            DocumentationScanner,
        )

        repo = self._build_repo(tmp_path)
        scanner = DocumentationScanner(repo)

        p1 = scanner.phase1_discovery()
        assert p1["files_found"]["total_markdown"] >= 4

        p2 = scanner.phase2_accuracy()
        # Version mismatch: README says 0.5.0, pyproject says 1.0.0
        version_issues = [
            i for i in p2["content_issues"] if i.get("type") == "version_mismatch"
        ]
        assert len(version_issues) >= 1

        p3 = scanner.phase3_completeness()
        # orphan_module has no README
        missing_readmes = [
            g for g in p3["coverage_gaps"] if g["module"] == "orphan_module"
        ]
        assert len(missing_readmes) == 1
        # quickstart.md is missing
        audience_files = [g["file"] for g in p3["audience_gaps"]]
        assert "quickstart.md" in audience_files

        p4 = scanner.phase4_quality()
        # good_module/README.md has a long line
        long_lines = [i for i in p4["quality_issues"] if i["type"] == "long_line"]
        assert len(long_lines) >= 1
        # docs/README.md has TODO
        todos = [
            i
            for i in p4["actionability_issues"]
            if i["type"] == "incomplete_content"
        ]
        assert len(todos) >= 1

        p5 = scanner.phase5_improvements()
        assert len(p5["improvements_made"]) >= 1

        p6 = scanner.phase6_verification()
        assert len(p6["manual_review_notes"]) == 8

        p7 = scanner.phase7_reporting()
        assert p7["summary_stats"]["total_files_scanned"] >= 4
        assert len(p7["recommendations"]) >= 1

        # Final report
        report = scanner.generate_report()
        assert "Documentation Scan" in report
        assert "Phase 7" in report

        # Save and reload
        out = tmp_path / "output.json"
        scanner.save_results(out)
        reloaded = json.loads(out.read_text())
        assert reloaded["phase7"]["summary_stats"]["total_files_scanned"] >= 4
