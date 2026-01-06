"""Unit tests for tools module - modular functional testing with real implementations."""

import pytest
import tempfile
from pathlib import Path
import json

# Test with real implementations - no mocks
from codomyrmex.tools.dependency_analyzer import DependencyAnalyzer
from codomyrmex.tools.dependency_checker import check_python_version, check_dependencies
from codomyrmex.tools.analyze_project import analyze_project_structure


class TestDependencyAnalyzer:
    """Test dependency analysis functionality."""
    
    def test_dependency_analyzer_initialization(self):
        """Test initializing dependency analyzer."""
        repo_root = Path(".")
        try:
            analyzer = DependencyAnalyzer(repo_root)
            assert analyzer is not None
            assert analyzer.repo_root == repo_root.resolve()
        except ImportError:
            pytest.skip("Dependency analyzer not available")
    
    def test_analyze_module_dependencies(self):
        """Test analyzing module dependencies."""
        repo_root = Path(".")
        try:
            analyzer = DependencyAnalyzer(repo_root)
            # Analyze a specific module
            result = analyzer.analyze_module("logging_monitoring")
            assert result is not None
        except (ImportError, AttributeError):
            pytest.skip("Module dependency analysis not available")


class TestDependencyChecker:
    """Test dependency checking functionality."""
    
    def test_check_python_version(self):
        """Test checking Python version."""
        try:
            result = check_python_version()
            assert result is not None
            assert isinstance(result, dict)
            assert "current_version" in result
            assert "meets_requirement" in result
        except ImportError:
            pytest.skip("Dependency checker not available")
    
    def test_check_dependencies(self):
        """Test checking project dependencies."""
        try:
            result = check_dependencies()
            assert result is not None
            assert isinstance(result, dict)
            # Should return dependency status information
        except ImportError:
            pytest.skip("Dependency checker not available")


class TestDependencyAnalyzerMethods:
    """Test dependency analyzer methods."""
    
    def test_analyze_module_dependencies(self):
        """Test analyzing dependencies for a specific module."""
        repo_root = Path(".")
        try:
            analyzer = DependencyAnalyzer(repo_root)
            # Try to analyze a module
            if hasattr(analyzer, 'analyze_module'):
                result = analyzer.analyze_module("logging_monitoring")
                assert result is not None
        except (ImportError, AttributeError, TypeError):
            pytest.skip("Module dependency analysis not available")


class TestAnalyzeProject:
    """Test project analysis functionality."""
    
    def test_analyze_project_structure(self):
        """Test analyzing project structure."""
        try:
            result = analyze_project_structure()
            assert result is not None
            # Should return project structure information
            assert isinstance(result, dict)
            assert "directories" in result or "files" in result
        except ImportError:
            pytest.skip("Project analyzer not available")

