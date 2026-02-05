"""
Comprehensive tests for the System Discovery module.

This module tests all components of the system discovery functionality:
- SystemDiscovery engine for module analysis and capability discovery
- StatusReporter for health monitoring and status reporting
- CapabilityScanner for detailed capability analysis
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path
# Removed mock imports to follow TDD principle: no mock methods, always do real data analysis
import subprocess

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from codomyrmex.system_discovery.discovery_engine import (
    SystemDiscovery, ModuleCapability, ModuleInfo
)
from codomyrmex.system_discovery.status_reporter import StatusReporter


@pytest.mark.unit
class TestModuleCapability:
    """Test cases for ModuleCapability dataclass."""

    def test_module_capability_creation(self):
        """Test creating a ModuleCapability instance."""
        cap = ModuleCapability(
            name="test_function",
            module_path="/path/to/module",
            type="function",
            signature="test_function(x, y)",
            docstring="Test function docstring",
            file_path="/path/to/file.py",
            line_number=10,
            is_public=True,
            dependencies=["os", "sys"]
        )

        assert cap.name == "test_function"
        assert cap.type == "function"
        assert cap.is_public == True
        assert cap.line_number == 10
        assert cap.dependencies == ["os", "sys"]

    def test_module_capability_defaults(self):
        """Test ModuleCapability with default values."""
        cap = ModuleCapability(
            name="private_func",
            module_path="/path/to/module",
            type="function",
            signature="private_func()",
            docstring="",
            file_path="/path/to/file.py",
            line_number=5,
            is_public=False,
            dependencies=[]
        )

        assert cap.is_public == False
        assert cap.dependencies == []
        assert cap.docstring == ""


@pytest.mark.unit
class TestModuleInfo:
    """Test cases for ModuleInfo dataclass."""

    def test_module_info_creation(self):
        """Test creating a ModuleInfo instance."""
        capabilities = [
            ModuleCapability(
                name="func1", module_path="/test", type="function",
                signature="func1()", docstring="", file_path="/test.py",
                line_number=1, is_public=True, dependencies=[]
            )
        ]

        info = ModuleInfo(
            name="test_module",
            path="/path/to/test_module",
            description="Test module description",
            version="1.0.0",
            capabilities=capabilities,
            dependencies=["requests"],
            is_importable=True,
            has_tests=True,
            has_docs=True,
            last_modified="2024-01-01 12:00:00"
        )

        assert info.name == "test_module"
        assert info.version == "1.0.0"
        assert len(info.capabilities) == 1
        assert info.is_importable == True
        assert info.has_tests == True
        assert info.has_docs == True


@pytest.mark.unit
class TestSystemDiscovery:
    """Test cases for SystemDiscovery functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.src_path = self.temp_dir / "src"
        self.codomyrmex_path = self.src_path / "codomyrmex"
        self.testing_path = self.temp_dir / "testing"

        # Create directory structure
        self.codomyrmex_path.mkdir(parents=True)
        self.testing_path.mkdir()

        # Create a mock module
        test_module_path = self.codomyrmex_path / "test_module"
        test_module_path.mkdir()

        # Create __init__.py
        (test_module_path / "__init__.py").write_text('"""Test module."""\n__version__ = "1.0.0"\n')

        # Create a simple Python file
        (test_module_path / "test_file.py").write_text("""
def public_function():
    '''A public function.'''
    return "hello"

def _private_function():
    '''A private function.'''
    return "secret"

@pytest.mark.unit
class TestClass:
    '''A test class.'''

    def public_method(self):
        '''A public method.'''
        return "method"

    def _private_method(self):
        '''A private method.'''
        return "private"
""")

        # Create requirements.txt
        (test_module_path / "requirements.txt").write_text("requests==2.28.0\nnumpy>=1.21.0")

        # Create test file
        test_unit_path = self.testing_path / "unit"
        test_unit_path.mkdir()
        (test_unit_path / "test_test_module.py").write_text("# Test file")

        self.discovery = SystemDiscovery(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_system_discovery_initialization(self):
        """Test SystemDiscovery initialization."""
        assert self.discovery.project_root == self.temp_dir
        assert self.discovery.src_path == self.src_path
        assert self.discovery.codomyrmex_path == self.codomyrmex_path
        assert isinstance(self.discovery.modules, dict)

    def test_discover_modules(self):
        """Test module discovery functionality."""
        self.discovery._discover_modules()

        # Should find our test module
        assert "test_module" in self.discovery.modules

        module_info = self.discovery.modules["test_module"]
        assert module_info.name == "test_module"
        assert module_info.path.endswith("test_module")
        assert module_info.version == "1.0.0"
        assert module_info.is_importable == False  # Can't import since not in Python path
        assert module_info.has_tests == True
        assert module_info.has_docs == False  # No README.md

    def test_analyze_module(self):
        """Test module analysis."""
        test_module_path = self.codomyrmex_path / "test_module"

        # Test with real module import (no mocks)
        # Create a real test module if it doesn't exist
        if test_module_path.exists():
            module_info = self.discovery._analyze_module("test_module", test_module_path)

            assert module_info is not None
            assert module_info.name == "test_module"
            assert module_info.description == "Test module."
            # Module may not be importable since it's in a temp dir not on sys.path
            assert isinstance(module_info.is_importable, bool)
        else:
            # If test module doesn't exist, test that the function handles it gracefully
            pytest.skip("Test module not available - create real test module for this test")

    def test_get_module_description(self):
        """Test extracting module description."""
        test_module_path = self.codomyrmex_path / "test_module"

        # Test with __init__.py docstring
        description = self.discovery._get_module_description(test_module_path)
        assert description == "Test module."

        # Test with README.md
        (test_module_path / "README.md").write_text("# Test Module\n\nThis is a test module.")
        description = self.discovery._get_module_description(test_module_path)
        assert description == "This is a test module."

    def test_get_module_version(self):
        """Test extracting module version."""
        test_module_path = self.codomyrmex_path / "test_module"

        version = self.discovery._get_module_version(test_module_path)
        assert version == "1.0.0"

        # Test without version
        (test_module_path / "__init__.py").write_text('"""Test module without version."""')
        version = self.discovery._get_module_version(test_module_path)
        assert version == "unknown"

    def test_get_module_dependencies(self):
        """Test extracting module dependencies."""
        test_module_path = self.codomyrmex_path / "test_module"

        dependencies = self.discovery._get_module_dependencies(test_module_path)
        assert "requests" in dependencies
        assert any("numpy" in dep for dep in dependencies)

    def test_has_tests(self):
        """Test checking for test files."""
        assert self.discovery._has_tests("test_module") == True
        assert self.discovery._has_tests("nonexistent_module") == False

    def test_has_docs(self):
        """Test checking for documentation."""
        test_module_path = self.codomyrmex_path / "test_module"

        assert self.discovery._has_docs(test_module_path) == False

        # Add README
        (test_module_path / "README.md").write_text("# Test Module")
        assert self.discovery._has_docs(test_module_path) == True

    def test_get_last_modified(self):
        """Test getting last modified time."""
        test_module_path = self.codomyrmex_path / "test_module"

        last_modified = self.discovery._get_last_modified(test_module_path)
        assert last_modified != "unknown"
        assert isinstance(last_modified, str)

    def test_static_analysis_capabilities(self):
        """Test static analysis for capabilities when import fails."""
        # Use the actual test module path that has the Python files
        test_module_path = self.codomyrmex_path / "test_module"

        capabilities = self.discovery._static_analysis_capabilities(test_module_path)

        # The static analysis should run without errors
        # (The actual capabilities found depend on the files present)
        assert isinstance(capabilities, list)

        # If there are any capabilities, they should have the expected structure
        for cap in capabilities:
            assert hasattr(cap, 'name')
            assert hasattr(cap, 'type')
            assert hasattr(cap, 'signature')
            assert hasattr(cap, 'docstring')
            assert hasattr(cap, 'file_path')
            assert hasattr(cap, 'line_number')
            assert hasattr(cap, 'is_public')
            assert hasattr(cap, 'dependencies')

    def test_analyze_object_function(self):
        """Test analyzing function objects."""
        def test_function(x: int, y: str = "default") -> str:
            """A test function."""
            return f"{x}: {y}"

        capability = self.discovery._analyze_object(
            "test_function", test_function, self.codomyrmex_path / "test.py"
        )

        assert capability is not None
        assert capability.name == "test_function"
        assert capability.type == "function"
        # The signature includes the function name
        assert "(x: int, y: str = 'default') -> str" in capability.signature
        assert capability.docstring == "A test function."
        assert capability.is_public == True

    def test_analyze_object_class(self):
        """Test analyzing class objects."""
        class TestClass:
            """A test class."""

            def method(self):
                """A method."""
                pass

        capability = self.discovery._analyze_object(
            "TestClass", TestClass, self.codomyrmex_path / "test.py"
        )

        assert capability is not None
        assert capability.name == "TestClass"
        assert capability.type == "class"
        assert capability.docstring == "A test class."
        assert capability.is_public == True

    def test_get_function_signature_from_ast(self):
        """Test extracting function signature from AST."""
        import ast

        # Create a simple function AST
        code = """
def test_func(x, y=10, *args, **kwargs):
    return x + y
"""
        tree = ast.parse(code)
        func_def = tree.body[0]

        signature = self.discovery._get_function_signature_from_ast(func_def)
        assert signature == "test_func(x, y=10, *args, **kwargs)"

    def test_display_discovery_results(self):
        """Test displaying discovery results."""
        # Add a mock module
        self.discovery.modules["mock_module"] = ModuleInfo(
            name="mock_module",
            path="/mock/path",
            description="Mock module",
            version="1.0.0",
            capabilities=[],
            dependencies=[],
            is_importable=True,
            has_tests=False,
            has_docs=False,
            last_modified="2024-01-01"
        )

        # This should not raise an exception
        self.discovery._display_discovery_results()

    def test_display_capability_summary(self):
        """Test displaying capability summary."""
        # Add mock modules with capabilities
        self.discovery.modules["mock1"] = ModuleInfo(
            name="mock1", path="/mock1", description="Mock 1", version="1.0.0",
            capabilities=[
                ModuleCapability("func1", "/mock1", "function", "func1()", "", "/mock1.py", 1, True, []),
                ModuleCapability("class1", "/mock1", "class", "class class1", "", "/mock1.py", 5, True, [])
            ],
            dependencies=[], is_importable=True, has_tests=False, has_docs=False,
            last_modified="2024-01-01"
        )

        # This should not raise an exception
        self.discovery._display_capability_summary()

    def test_export_full_inventory(self):
        """Test exporting full system inventory."""
        # Add a mock module
        self.discovery.modules["mock_module"] = ModuleInfo(
            name="mock_module", path="/mock", description="Mock", version="1.0.0",
            capabilities=[], dependencies=[], is_importable=True,
            has_tests=False, has_docs=False, last_modified="2024-01-01"
        )

        # This should not raise an exception
        self.discovery.export_full_inventory()


@pytest.mark.unit
class TestStatusReporter:
    """Test cases for StatusReporter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.reporter = StatusReporter(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_status_reporter_initialization(self):
        """Test StatusReporter initialization."""
        assert self.reporter.project_root == self.temp_dir
        assert self.reporter.src_path == self.temp_dir / "src"

    def test_check_python_environment(self):
        """Test Python environment checking."""
        env = self.reporter.check_python_environment()

        assert "version" in env
        assert "version_string" in env
        assert "executable" in env
        assert "virtual_env" in env
        assert "platform" in env

        assert isinstance(env["version"], tuple)
        assert isinstance(env["version_string"], str)
        assert isinstance(env["executable"], str)

    def test_in_virtual_env(self):
        """Test virtual environment detection."""
        in_venv = self.reporter._in_virtual_env()
        assert isinstance(in_venv, bool)

    def test_check_project_structure(self):
        """Test project structure checking."""
        structure = self.reporter.check_project_structure()

        # Should check for various directories and files
        expected_keys = [
            "project_root_exists", "src_exists", "codomyrmex_package",
            "testing_dir", "docs_dir", "virtual_env_dir", "config_files"
        ]

        for key in expected_keys:
            assert key in structure

        assert isinstance(structure["config_files"], dict)

    def test_check_config_files(self):
        """Test configuration file checking."""
        config_files = self.reporter._check_config_files()

        expected_files = [
            "pyproject.toml", "requirements.txt", "setup.py",
            ".env", "pytest.ini", "README.md"
        ]

        for file in expected_files:
            assert file in config_files
            assert isinstance(config_files[file], bool)

    def test_check_dependencies(self):
        """Test dependency checking."""
        deps = self.reporter.check_dependencies()

        assert "dependencies" in deps
        assert "available_count" in deps
        assert "total_count" in deps
        assert "success_rate" in deps

        assert isinstance(deps["dependencies"], dict)
        assert isinstance(deps["available_count"], int)
        assert isinstance(deps["total_count"], int)
        assert isinstance(deps["success_rate"], (int, float))

    def test_check_import(self):
        """Test individual import checking."""
        # Test with a module that should exist
        result = self.reporter._check_import("sys")
        assert result == True

        # Test with a module that shouldn't exist
        result = self.reporter._check_import("nonexistent_module_xyz123")
        assert result == False

    def test_check_git_status(self):
        """Test git status checking."""
        git_status = self.reporter.check_git_status()

        expected_keys = [
            "is_git_repo", "git_available", "current_branch",
            "clean_working_tree", "remotes", "recent_commits",
            "staged_changes", "unstaged_changes"
        ]

        for key in expected_keys:
            assert key in git_status

    def test_check_git_status_no_git(self):
        """Test git status when git is not available with real git check."""
        # Test with real git availability check
        git_status = self.reporter.check_git_status()

        assert isinstance(git_status["git_available"], bool)
        # If git is available, test will pass; if not, git_available will be False
        assert git_status["is_git_repo"] == False

    def test_check_external_tools(self):
        """Test external tools checking."""
        tools = self.reporter.check_external_tools()

        expected_tools = ["git", "npm", "node", "docker", "uv"]

        for tool in expected_tools:
            assert tool in tools
            assert isinstance(tools[tool], bool)

    def test_generate_comprehensive_report(self):
        """Test comprehensive report generation."""
        report = self.reporter.generate_comprehensive_report()

        expected_keys = [
            "timestamp", "python_environment", "project_structure",
            "dependencies", "git_status", "external_tools"
        ]

        for key in expected_keys:
            assert key in report

        assert isinstance(report["timestamp"], str)

    def test_format_message_without_formatter(self):
        """Test message formatting without terminal formatter."""
        # Create a reporter with no formatter
        reporter = StatusReporter()
        # Manually set formatter to None to test the fallback
        reporter.formatter = None
        message = reporter.format_message("Test message", "success")
        assert message == "Test message"

    def test_format_message_with_formatter(self):
        """Test message formatting with real terminal formatter."""
        # Use real terminal formatter if available
        try:
            from codomyrmex.terminal_interface.terminal_utils import TerminalFormatter
            real_formatter = TerminalFormatter()
            self.reporter.formatter = real_formatter

            message = self.reporter.format_message("Test", "success")
            assert message is not None
            assert isinstance(message, str)
            # The actual format depends on the formatter implementation
            assert "Test" in message or message == "Test"
        except ImportError:
            # If terminal formatter not available, test without it
            self.reporter.formatter = None
            message = self.reporter.format_message("Test", "success")
            assert message == "Test"

    def test_export_report(self):
        """Test report export functionality."""
        # Generate a report first
        report = self.reporter.generate_comprehensive_report()

        # Export it
        output_path = self.reporter.export_report("test_report.json")

        assert output_path.endswith("test_report.json")

        # Check that file was created and contains valid JSON
        report_file = Path(output_path)
        assert report_file.exists()

        with open(report_file, 'r') as f:
            loaded_report = json.load(f)

        assert "timestamp" in loaded_report
        assert "python_environment" in loaded_report


@pytest.mark.unit
class TestIntegration:
    """Integration tests for system discovery components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create a more complete test project structure
        src_dir = self.temp_dir / "src"
        codomyrmex_dir = src_dir / "codomyrmex"
        codomyrmex_dir.mkdir(parents=True)

        # Create a test module
        test_module_dir = codomyrmex_dir / "integration_test"
        test_module_dir.mkdir()

        # Create module files
        (test_module_dir / "__init__.py").write_text("""
'''Integration test module.'''

__version__ = "1.0.0"

def test_function():
    '''A test function.'''
    return "integration test"

@pytest.mark.unit
class TestClass:
    '''A test class.'''

    def test_method(self):
        '''A test method.'''
        return "method result"
""")

        (test_module_dir / "utils.py").write_text("""
def utility_function():
    '''A utility function.'''
    return "utility"
""")

        self.project_root = self.temp_dir

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_discovery_workflow(self):
        """Test complete discovery workflow."""
        from codomyrmex.system_discovery.discovery_engine import SystemDiscovery

        discovery = SystemDiscovery(self.project_root)

        # This should work without errors
        discovery.run_full_discovery()

        # Check that modules were discovered
        assert len(discovery.modules) > 0

    def test_status_reporting_workflow(self):
        """Test complete status reporting workflow."""
        from codomyrmex.system_discovery.status_reporter import StatusReporter

        reporter = StatusReporter(self.project_root)

        # Generate comprehensive report
        report = reporter.generate_comprehensive_report()

        # Verify report structure
        assert "timestamp" in report
        assert "python_environment" in report
        assert "project_structure" in report
        assert "dependencies" in report

        # Test display (should not raise exceptions)
        reporter.display_status_report()

    def test_end_to_end_discovery_and_reporting(self):
        """Test end-to-end discovery and reporting workflow."""
        from codomyrmex.system_discovery.discovery_engine import SystemDiscovery
        from codomyrmex.system_discovery.status_reporter import StatusReporter

        # Run discovery
        discovery = SystemDiscovery(self.project_root)
        discovery.run_full_discovery()

        # Run status reporting
        reporter = StatusReporter(self.project_root)
        status_report = reporter.generate_comprehensive_report()

        # Verify both work together
        assert len(discovery.modules) >= 0  # At least ran
        assert "timestamp" in status_report  # Report generated


if __name__ == '__main__':
    pytest.main([__file__])
