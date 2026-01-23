"""Test configuration and fixtures for test_project."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def test_project_root() -> Path:
    """Get the test_project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_python_file(tmp_path: Path) -> Path:
    """Create a sample Python file for testing."""
    content = '''"""Sample module for testing."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class SampleClass:
    """A sample dataclass."""
    
    name: str
    value: int = 0
    
    def process(self) -> str:
        """Process and return formatted value."""
        return f"{self.name}: {self.value}"


async def async_function(items: List[str]) -> List[str]:
    """An async function example."""
    return [item.upper() for item in items]


def sync_function(x: int, y: int) -> int:
    """A sync function with type hints."""
    return x + y


# TODO: Add more functionality
'''
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_directory(tmp_path: Path) -> Path:
    """Create a sample directory structure for testing."""
    # Create main.py
    (tmp_path / "main.py").write_text('''"""Main module."""

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
    
    # Create utils.py
    (tmp_path / "utils.py").write_text('''"""Utility functions."""

def helper(x):
    return x * 2
''')
    
    # Create subdir
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "module.py").write_text('''"""Submodule."""

class SubClass:
    pass
''')
    
    return tmp_path


@pytest.fixture
def output_directory(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_analysis_results() -> dict:
    """Create sample analysis results for testing."""
    return {
        "target": "/test/path",
        "files": [
            {
                "file": "main.py",
                "metrics": {
                    "lines_of_code": 50,
                    "functions": 3,
                    "classes": 1,
                },
                "patterns": ["type_hints", "docstrings"],
                "issues": [],
            },
            {
                "file": "utils.py",
                "metrics": {
                    "lines_of_code": 30,
                    "functions": 2,
                    "classes": 0,
                },
                "patterns": ["type_hints"],
                "issues": [
                    {"type": "todo", "severity": "info", "message": "TODO comment", "line": 10}
                ],
            },
        ],
        "summary": {
            "total_files": 2,
            "total_lines": 80,
            "total_non_empty_lines": 60,
            "total_functions": 5,
            "total_classes": 1,
            "total_issues": 1,
            "average_lines_per_file": 40.0,
            "patterns_found": {
                "type_hints": 2,
                "docstrings": 1,
            },
            "files_with_issues": 1,
        },
    }
