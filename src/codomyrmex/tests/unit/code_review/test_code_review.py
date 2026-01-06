"""Unit tests for code.review module."""

import sys
import pytest
from pathlib import Path


class TestCodeReview:
    """Test cases for code review functionality."""

    def test_code_review_import(self, code_dir):
        """Test that we can import code_review module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import code
            assert code is not None
        except ImportError as e:
            pytest.fail(f"Failed to import code_review: {e}")

    def test_code_review_module_exists(self, code_dir):
        """Test that code_review module directory exists."""
        code_review_path = code_dir / "codomyrmex" / "code" / "review"
        assert code_review_path.exists()
        assert code_review_path.is_dir()

    def test_code_review_init_file(self, code_dir):
        """Test that code_review has __init__.py."""
        init_path = code_dir / "codomyrmex" / "code" / "review" / "__init__.py"
        assert init_path.exists()

    def test_code_review_main_module(self, code_dir):
        """Test that code_review has main module file."""
        main_path = code_dir / "codomyrmex" / "code" / "review" / "reviewer.py"
        assert main_path.exists()

    def test_code_reviewer_class_import(self, code_dir):
        """Test that CodeReviewer class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import CodeReviewer
            assert CodeReviewer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import CodeReviewer: {e}")

    def test_pyscn_analyzer_import(self, code_dir):
        """Test that PyscnAnalyzer class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import PyscnAnalyzer
            assert PyscnAnalyzer is not None
        except ImportError as e:
            pytest.fail(f"Failed to import PyscnAnalyzer: {e}")

    def test_analysis_types_import(self, code_dir):
        """Test that AnalysisType enum can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import AnalysisType, SeverityLevel, Language
            assert AnalysisType is not None
            assert SeverityLevel is not None
            assert Language is not None
        except ImportError as e:
            pytest.fail(f"Failed to import enums: {e}")

    def test_data_classes_import(self, code_dir):
        """Test that data classes can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import (
                AnalysisResult,
                AnalysisSummary,
                CodeMetrics,
                QualityGateResult,
            )
            assert AnalysisResult is not None
            assert AnalysisSummary is not None
            assert CodeMetrics is not None
            assert QualityGateResult is not None
        except ImportError as e:
            pytest.fail(f"Failed to import data classes: {e}")

    def test_exception_classes_import(self, code_dir):
        """Test that exception classes can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import (
                CodeReviewError,
                PyscnError,
                ToolNotFoundError,
                ConfigurationError,
            )
            assert CodeReviewError is not None
            assert PyscnError is not None
            assert ToolNotFoundError is not None
            assert ConfigurationError is not None
        except ImportError as e:
            pytest.fail(f"Failed to import exception classes: {e}")

    def test_analyze_functions_import(self, code_dir):
        """Test that analyze functions can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.code.review import (
                analyze_file,
                analyze_project,
                check_quality_gates,
                generate_report,
            )
            assert callable(analyze_file)
            assert callable(analyze_project)
            assert callable(check_quality_gates)
            assert callable(generate_report)
        except ImportError as e:
            pytest.fail(f"Failed to import analyze functions: {e}")

    def test_code_review_version(self, code_dir):
        """Test that code_review has version defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import code
        assert hasattr(code, "__version__")
        assert code.__version__ == "0.1.0"

    def test_code_review_all_exports(self, code_dir):
        """Test that code_review exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import code

        expected_exports = [
            "CodeReviewer",
            "PyscnAnalyzer",
            "AnalysisType",
            "SeverityLevel",
            "Language",
            "AnalysisResult",
            "AnalysisSummary",
            "CodeMetrics",
            "QualityGateResult",
            "analyze_file",
            "analyze_project",
            "check_quality_gates",
            "generate_report",
        ]

        for export in expected_exports:
            assert hasattr(code, export), f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for code_review module."""
        agents_path = code_dir / "codomyrmex" / "code" / "review" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for code_review module."""
        readme_path = code_dir / "codomyrmex" / "code" / "review" / "README.md"
        assert readme_path.exists()

    def test_security_md_exists(self, code_dir):
        """Test that SECURITY.md exists for code_review module."""
        security_path = code_dir / "codomyrmex" / "code" / "review" / "SECURITY.md"
        assert security_path.exists()



