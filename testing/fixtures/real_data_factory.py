"""Real data factory for generating test fixtures without mocks.

This module provides utilities for creating real test data, files, and structures
that can be used in place of mocked objects. Following the repository's TDD principle
of "no mock methods, always do real data analysis."
"""

import json
import os
import sqlite3
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class RealDataFactory:
    """Factory for creating real test data fixtures."""

    @staticmethod
    def create_python_module(project_path: Path, module_name: str, content: str) -> Path:
        """Create a real Python module file."""
        module_file = project_path / f"{module_name}.py"
        module_file.write_text(content)
        return module_file

    @staticmethod
    def create_package_structure(project_path: Path, package_name: str,
                               modules: Dict[str, str]) -> Path:
        """Create a real Python package with multiple modules."""
        package_dir = project_path / package_name
        package_dir.mkdir()

        # Create __init__.py
        (package_dir / "__init__.py").write_text("")

        # Create module files
        for module_name, content in modules.items():
            RealDataFactory.create_python_module(package_dir, module_name, content)

        return package_dir

    @staticmethod
    def create_config_file(project_path: Path, filename: str,
                          config_data: Dict[str, Any], format_type: str = "json") -> Path:
        """Create a real configuration file."""
        config_file = project_path / filename

        if format_type == "json":
            config_file.write_text(json.dumps(config_data, indent=2))
        elif format_type == "yaml":
            try:
                import yaml
                config_file.write_text(yaml.dump(config_data, default_flow_style=False))
            except ImportError:
                # Fallback to JSON if yaml not available
                config_file.write_text(json.dumps(config_data, indent=2))
        elif format_type == "env":
            env_content = "\n".join([f"{k}={v}" for k, v in config_data.items()])
            config_file.write_text(env_content)

        return config_file

    @staticmethod
    def create_git_repository(repo_path: Path) -> Path:
        """Create a real git repository with initial commit."""
        # Initialize repository
        subprocess.run(["git", "init"], cwd=repo_path, check=True,
                      capture_output=True)

        # Configure git
        subprocess.run(["git", "config", "user.name", "Test User"],
                      cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                      cwd=repo_path, check=True)

        # Create README and commit
        readme = repo_path / "README.md"
        readme.write_text("# Test Repository\n\nCreated for testing purposes.")
        subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"],
                      cwd=repo_path, check=True)

        return repo_path

    @staticmethod
    def create_sqlite_database(db_path: Path, schema: str,
                              sample_data: Optional[List[str]] = None) -> Path:
        """Create a real SQLite database with schema and data."""
        conn = sqlite3.connect(str(db_path))

        try:
            # Create schema
            conn.executescript(schema)
            conn.commit()

            # Insert sample data
            if sample_data:
                for query in sample_data:
                    conn.execute(query)
                conn.commit()

        finally:
            conn.close()

        return db_path

    @staticmethod
    def create_docker_compose_file(project_path: Path, services: Dict[str, Any]) -> Path:
        """Create a real docker-compose.yml file."""
        compose_data = {"version": "3.8", "services": services}
        return RealDataFactory.create_config_file(project_path, "docker-compose.yml",
                                                compose_data, "yaml")

    @staticmethod
    def create_code_with_issues(project_path: Path, issue_type: str) -> Path:
        """Create Python code with specific types of issues for testing."""
        issue_files = {
            "syntax_error": '''
def broken_function():
    print("Missing closing parenthesis"
    return "This won't execute"
''',
            "undefined_variable": '''
def problematic_function():
    result = undefined_variable + 1
    return result
''',
            "import_error": '''
import nonexistent_module
from missing_package import something

def function_with_missing_imports():
    return nonexistent_module.do_something()
''',
            "type_error": '''
def type_mismatch():
    x = "string"
    y = 5
    return x + y  # Type error: can't concatenate str and int
''',
            "indentation_error": '''
def bad_indentation():
    x = 1
  y = 2  # Inconsistent indentation
    return x + y
'''
        }

        if issue_type not in issue_files:
            raise ValueError(f"Unknown issue type: {issue_type}")

        filename = f"code_with_{issue_type}.py"
        return RealDataFactory.create_python_module(project_path, filename,
                                                   issue_files[issue_type])

    @staticmethod
    def create_test_project_structure(project_path: Path) -> Dict[str, Path]:
        """Create a complete test project structure."""
        structure = {}

        # Create main package
        main_package = RealDataFactory.create_package_structure(
            project_path, "mypackage",
            {
                "__init__": '',
                "core": '''
def core_function():
    """Core functionality."""
    return "core result"
''',
                "utils": '''
def helper_function():
    """Helper utility."""
    return "helper result"
'''
            }
        )
        structure["package"] = main_package

        # Create tests
        tests_dir = project_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("")

        test_core = tests_dir / "test_core.py"
        test_core.write_text('''
import pytest
from mypackage.core import core_function

def test_core_function():
    result = core_function()
    assert result == "core result"
''')
        structure["test_core"] = test_core

        # Create configuration files
        pyproject = project_path / "pyproject.toml"
        pyproject.write_text('''
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
''')
        structure["pyproject"] = pyproject

        # Create README
        readme = project_path / "README.md"
        readme.write_text("# Test Project\n\nA test project for Codomyrmex.")
        structure["readme"] = readme

        return structure


# Convenience functions for common test data patterns

def create_valid_python_code() -> str:
    """Return valid Python code for testing."""
    return '''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    """Mathematical utilities."""

    @staticmethod
    def is_even(number):
        """Check if a number is even."""
        return number % 2 == 0

    @staticmethod
    def factorial(n):
        """Calculate factorial of n."""
        if n == 0:
            return 1
        return n * MathUtils.factorial(n - 1)
'''


def create_invalid_python_code(error_type: str) -> str:
    """Return Python code with specific errors for testing."""
    error_codes = {
        "indentation": '''
def bad_function():
    x = 1
  y = 2  # Bad indentation
    return x + y
''',
        "syntax": '''
def syntax_error():
    print("Missing parenthesis"
    return "error"
''',
        "name": '''
def name_error():
    return undefined_variable
'''
    }
    return error_codes.get(error_type, "# No error")


def create_sample_config() -> Dict[str, Any]:
    """Return sample configuration data."""
    return {
        "app": {
            "name": "test_app",
            "version": "1.0.0",
            "debug": True
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db"
        },
        "logging": {
            "level": "INFO",
            "file": "/tmp/test.log"
        }
    }


def create_sample_workflow_config() -> Dict[str, Any]:
    """Return sample workflow configuration."""
    return {
        "name": "test_workflow",
        "description": "A test workflow",
        "steps": [
            {
                "name": "setup",
                "module": "environment_setup",
                "action": "validate_environment"
            },
            {
                "name": "analyze",
                "module": "static_analysis",
                "action": "analyze_code",
                "parameters": {"target": "src/"}
            },
            {
                "name": "test",
                "module": "testing",
                "action": "run_tests"
            }
        ]
    }
