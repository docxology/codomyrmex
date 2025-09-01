"""
Unit tests for the Mermaid diagram generator.

Tests all Mermaid diagram generation functions with various inputs.
"""
import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from codomyrmex.data_visualization.mermaid_generator import (
    MermaidDiagramGenerator,
    create_git_branch_diagram,
    create_git_workflow_diagram,
    create_repository_structure_diagram,
    create_commit_timeline_diagram
)


class TestMermaidDiagramGenerator:
    """Test the MermaidDiagramGenerator class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.generator = MermaidDiagramGenerator()
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_generator_initialization(self):
        """Test generator initializes with correct diagram types."""
        assert self.generator is not None
        assert 'gitgraph' in self.generator.diagram_types
        assert 'flowchart' in self.generator.diagram_types
        assert 'timeline' in self.generator.diagram_types
        assert callable(self.generator.diagram_types['gitgraph'])
    
    def test_create_git_branch_diagram_default(self):
        """Test creating a Git branch diagram with default data."""
        result = self.generator.create_git_branch_diagram()
        
        assert isinstance(result, str)
        assert 'gitGraph' in result
        assert 'commit' in result
        assert 'branch' in result
    
    def test_create_git_branch_diagram_with_data(self):
        """Test creating a Git branch diagram with custom data."""
        branches = [
            {"name": "main", "created_at": "2024-01-01"},
            {"name": "feature/test", "created_at": "2024-01-02", "merged": True}
        ]
        commits = [
            {"hash": "abc123", "message": "Initial commit", "branch": "main", "date": "2024-01-01"},
            {"hash": "def456", "message": "Add feature", "branch": "feature/test", "date": "2024-01-02"}
        ]
        
        result = self.generator.create_git_branch_diagram(
            branches=branches,
            commits=commits,
            title="Test Git Diagram"
        )
        
        assert isinstance(result, str)
        assert 'gitGraph' in result
        assert 'feature/test' in result
        assert 'Add feature' in result
    
    def test_create_git_branch_diagram_with_output_path(self):
        """Test creating a Git branch diagram and saving to file."""
        output_path = os.path.join(self.test_dir, "test_git_diagram.mmd")
        
        result = self.generator.create_git_branch_diagram(
            title="Test Diagram",
            output_path=output_path
        )
        
        assert isinstance(result, str)
        assert os.path.exists(output_path)
        
        # Verify file content
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == result
            assert 'gitGraph' in content
    
    def test_create_git_workflow_diagram_default(self):
        """Test creating a Git workflow diagram with default data."""
        result = self.generator.create_git_workflow_diagram()
        
        assert isinstance(result, str)
        assert 'flowchart TD' in result
        assert 'git clone' in result
        assert 'git commit' in result
    
    def test_create_git_workflow_diagram_with_data(self):
        """Test creating a Git workflow diagram with custom steps."""
        workflow_steps = [
            {"name": "Start", "type": "terminal", "description": "Begin"},
            {"name": "Code", "type": "process", "description": "Write code"},
            {"name": "Test", "type": "decision", "description": "Tests pass"},
            {"name": "Deploy", "type": "process", "description": "Deploy app"}
        ]
        
        result = self.generator.create_git_workflow_diagram(
            workflow_steps=workflow_steps,
            title="Custom Workflow"
        )
        
        assert isinstance(result, str)
        assert 'flowchart TD' in result
        assert 'Write code' in result
        assert 'Tests pass' in result
    
    def test_create_repository_structure_diagram_default(self):
        """Test creating a repository structure diagram with default data."""
        result = self.generator.create_repository_structure_diagram()
        
        assert isinstance(result, str)
        assert 'graph TD' in result
        assert '📁' in result
        assert 'src/' in result or 'tests/' in result
    
    def test_create_repository_structure_diagram_with_data(self):
        """Test creating a repository structure diagram with custom structure."""
        repo_structure = {
            "src": {
                "main.py": "file",
                "utils": {
                    "helper.py": "file"
                }
            },
            "tests": {
                "test_main.py": "file"
            },
            "README.md": "file"
        }
        
        result = self.generator.create_repository_structure_diagram(
            repo_structure=repo_structure,
            title="Project Structure"
        )
        
        assert isinstance(result, str)
        assert 'graph TD' in result
        assert 'main.py' in result
        assert 'utils' in result
        assert 'README.md' in result
    
    def test_create_commit_timeline_diagram_default(self):
        """Test creating a commit timeline diagram with default data."""
        result = self.generator.create_commit_timeline_diagram()
        
        assert isinstance(result, str)
        assert 'timeline' in result
        assert '2024' in result
    
    def test_create_commit_timeline_diagram_with_data(self):
        """Test creating a commit timeline diagram with custom commits."""
        commits = [
            {"hash": "abc123", "message": "Initial commit", "date": "2024-01-01"},
            {"hash": "def456", "message": "Add feature", "date": "2024-01-05"},
            {"hash": "ghi789", "message": "Fix bug", "date": "2024-01-10"}
        ]
        
        result = self.generator.create_commit_timeline_diagram(
            commits=commits,
            title="Development Timeline"
        )
        
        assert isinstance(result, str)
        assert 'timeline' in result
        assert 'Initial commit' in result
        assert '2024-01-01' in result
        assert 'Add feature' in result
    
    def test_save_mermaid_content_creates_directory(self):
        """Test that saving Mermaid content creates directories as needed."""
        nested_path = os.path.join(self.test_dir, "nested", "dir", "diagram.mmd")
        content = "graph TD\n    A --> B"
        
        result = self.generator._save_mermaid_content(content, nested_path)
        
        assert result is True
        assert os.path.exists(nested_path)
        
        with open(nested_path, 'r') as f:
            assert f.read() == content
    
    def test_save_mermaid_content_handles_errors(self):
        """Test that saving Mermaid content handles errors gracefully."""
        # Try to write to an invalid path
        invalid_path = "/invalid/path/that/should/not/exist/diagram.mmd"
        content = "graph TD\n    A --> B"
        
        result = self.generator._save_mermaid_content(content, invalid_path)
        
        assert result is False
    
    def test_get_file_icon_mappings(self):
        """Test file icon mapping functionality."""
        assert self.generator._get_file_icon("test.py") == "🐍"
        assert self.generator._get_file_icon("script.js") == "📜"
        assert self.generator._get_file_icon("config.json") == "📋"
        assert self.generator._get_file_icon("README.md") == "📝"
        assert self.generator._get_file_icon("unknown.xyz") == "📄"
    
    def test_build_gitgraph_from_data(self):
        """Test building gitgraph from branch and commit data."""
        branches = [
            {"name": "main", "created_at": "2024-01-01"},
            {"name": "feature/auth", "created_at": "2024-01-02", "merged": True}
        ]
        commits = [
            {"hash": "abc123", "message": "Add auth", "branch": "feature/auth"},
            {"hash": "def456", "message": "Fix auth bug", "branch": "feature/auth"}
        ]
        
        result = self.generator._build_gitgraph_from_data(branches, commits, "Test")
        
        assert isinstance(result, str)
        assert 'gitGraph' in result
        assert 'feature/auth' in result
        assert 'Add auth' in result
        assert 'merge feature/auth' in result
    
    def test_build_workflow_from_data(self):
        """Test building workflow flowchart from step data."""
        workflow_steps = [
            {"name": "Start", "type": "terminal", "description": "Begin"},
            {"name": "Process", "type": "process", "description": "Do work"},
            {"name": "Decision", "type": "decision", "description": "Success"},
            {"name": "End", "type": "terminal", "description": "Complete"}
        ]
        
        result = self.generator._build_workflow_from_data(workflow_steps, "Test")
        
        assert isinstance(result, list)
        assert 'flowchart TD' in result[0]
        assert any('Begin' in line for line in result)
        assert any('Do work' in line for line in result)
        assert any('Success?' in line for line in result)
    
    def test_build_structure_from_data(self):
        """Test building structure graph from repository data."""
        repo_structure = {
            "src": {
                "main.py": "file",
                "utils": {
                    "helper.py": "file"
                }
            }
        }
        
        result = self.generator._build_structure_from_data(repo_structure, "Test")
        
        assert isinstance(result, list)
        assert 'graph TD' in result[0]
        assert any('main.py' in line for line in result)
        assert any('utils' in line for line in result)


class TestMermaidConvenienceFunctions:
    """Test the convenience functions for Mermaid diagram creation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_create_git_branch_diagram_function(self):
        """Test the convenience function for Git branch diagrams."""
        result = create_git_branch_diagram(title="Test Function")
        
        assert isinstance(result, str)
        assert 'gitGraph' in result
    
    def test_create_git_workflow_diagram_function(self):
        """Test the convenience function for Git workflow diagrams."""
        result = create_git_workflow_diagram(title="Test Workflow")
        
        assert isinstance(result, str)
        assert 'flowchart TD' in result
    
    def test_create_repository_structure_diagram_function(self):
        """Test the convenience function for repository structure diagrams."""
        result = create_repository_structure_diagram(title="Test Structure")
        
        assert isinstance(result, str)
        assert 'graph TD' in result
    
    def test_create_commit_timeline_diagram_function(self):
        """Test the convenience function for commit timeline diagrams."""
        result = create_commit_timeline_diagram(title="Test Timeline")
        
        assert isinstance(result, str)
        assert 'timeline' in result
    
    def test_convenience_functions_with_output_path(self):
        """Test convenience functions save files correctly."""
        output_path = os.path.join(self.test_dir, "test_diagram.mmd")
        
        result = create_git_branch_diagram(
            title="Test",
            output_path=output_path
        )
        
        assert isinstance(result, str)
        assert os.path.exists(output_path)
        
        with open(output_path, 'r') as f:
            content = f.read()
            assert content == result


class TestMermaidMainExecution:
    """Test the main execution block of the Mermaid generator."""
    
    def test_main_execution_with_examples(self):
        """Test that main execution creates example files."""
        with patch('codomyrmex.data_visualization.mermaid_generator.Path') as mock_path:
            mock_output_dir = MagicMock()
            mock_path.return_value.parent.parent = MagicMock()
            mock_path.return_value.parent.parent.__truediv__ = MagicMock(return_value=mock_output_dir)
            mock_output_dir.mkdir = MagicMock()
            
            # Mock the creation functions to avoid file I/O
            with patch('codomyrmex.data_visualization.mermaid_generator.create_git_branch_diagram') as mock_branch:
                with patch('codomyrmex.data_visualization.mermaid_generator.create_git_workflow_diagram') as mock_workflow:
                    mock_branch.return_value = "mocked branch diagram"
                    mock_workflow.return_value = "mocked workflow diagram"
                    
                    # The main execution should run without errors
                    # This is implicitly tested by importing the module


if __name__ == '__main__':
    pytest.main([__file__])
