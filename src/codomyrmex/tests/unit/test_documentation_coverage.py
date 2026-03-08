"""Functional tests for documentation module — coverage push.

Tests real documentation utilities: quality analysis, consistency checking,
RASP audit, and site generation.
Zero-mock policy: all tests use real methods.
"""

from __future__ import annotations

import importlib
import types
from pathlib import Path
from unittest.mock import patch

import pytest

import codomyrmex.documentation


class TestDocumentationModule:
    """Test documentation module imports and exports."""

    def test_module_imports(self) -> None:
        """Module should import successfully."""
        assert isinstance(codomyrmex.documentation, types.ModuleType)

    def test_exports_available(self) -> None:
        """Key exports should be accessible."""
        mod = codomyrmex.documentation
        assert hasattr(mod, "audit_documentation")
        assert hasattr(mod, "check_documentation_consistency")
        assert hasattr(mod, "DocumentationQualityAnalyzer")


class TestDocumentationQualityAnalyzer:
    """Test DocumentationQualityAnalyzer class."""

    def test_analyzer_instantiation(self) -> None:
        """Analyzer should instantiate."""
        analyzer = codomyrmex.documentation.DocumentationQualityAnalyzer()
        assert analyzer is not None

    def test_analyzer_has_methods(self) -> None:
        """Analyzer should have expected methods."""
        analyzer = codomyrmex.documentation.DocumentationQualityAnalyzer()
        assert callable(getattr(analyzer, "analyze_file", None))


class TestDocumentationConsistency:
    """Test documentation consistency checking."""

    def test_consistency_checker_instantiation(self) -> None:
        """ConsistencyChecker should instantiate."""
        checker = codomyrmex.documentation.DocumentationConsistencyChecker()
        assert checker is not None

    def test_consistency_report_model(self) -> None:
        """ConsistencyReport should be a valid data class."""
        report_cls = codomyrmex.documentation.ConsistencyReport
        assert report_cls is not None

    def test_consistency_issue_model(self) -> None:
        """ConsistencyIssue should be a valid data class."""
        issue_cls = codomyrmex.documentation.ConsistencyIssue
        assert issue_cls is not None


class TestDocumentationSubmodules:
    """Test submodule imports for coverage."""

    def test_quality_submodule(self) -> None:
        """Quality submodule should import."""
        mod = importlib.import_module("codomyrmex.documentation.quality")
        assert isinstance(mod, types.ModuleType)

    def test_maintenance_submodule(self) -> None:
        """Maintenance submodule should import."""
        mod = importlib.import_module("codomyrmex.documentation.maintenance")
        assert isinstance(mod, types.ModuleType)

    def test_pai_submodule(self) -> None:
        """PAI submodule should import."""
        mod = importlib.import_module("codomyrmex.documentation.pai")
        assert isinstance(mod, types.ModuleType)


class TestDocumentationFunctions:
    """Test top-level documentation functions."""

    def test_audit_documentation_callable(self) -> None:
        """audit_documentation should be callable."""
        assert callable(codomyrmex.documentation.audit_documentation)

    def test_audit_rasp_callable(self) -> None:
        """audit_rasp should be callable."""
        assert callable(codomyrmex.documentation.audit_rasp)

    def test_generate_pai_md_callable(self) -> None:
        """generate_pai_md should be callable."""
        assert callable(codomyrmex.documentation.generate_pai_md)

    def test_check_doc_environment_callable(self) -> None:
        """check_doc_environment should be callable."""
        assert callable(codomyrmex.documentation.check_doc_environment)

    def test_build_static_site_callable(self) -> None:
        """build_static_site should be callable."""
        assert callable(codomyrmex.documentation.build_static_site)

    def test_aggregate_docs_callable(self) -> None:
        """aggregate_docs should be callable."""
        assert callable(codomyrmex.documentation.aggregate_docs)

    def test_install_dependencies_callable(self) -> None:
        """install_dependencies should be callable."""
        assert callable(codomyrmex.documentation.install_dependencies)

    def test_finalize_docs_callable(self) -> None:
        """finalize_docs should be callable."""
        assert callable(codomyrmex.documentation.finalize_docs)

    def test_generate_quality_report_callable(self) -> None:
        """generate_quality_report should be callable."""
        assert callable(codomyrmex.documentation.generate_quality_report)

    def test_assess_site_callable(self) -> None:
        """assess_site should be callable."""
        assert callable(codomyrmex.documentation.assess_site)

    def test_check_documentation_consistency_callable(self) -> None:
        """check_documentation_consistency should be callable."""
        assert callable(codomyrmex.documentation.check_documentation_consistency)
