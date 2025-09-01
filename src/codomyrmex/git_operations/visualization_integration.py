"""
Integration module between git_operations and data_visualization.

This module provides convenient functions that bridge git_operations data 
with data_visualization capabilities, specifically for Git-related visualizations.

- Uses logging_monitoring for logging.
- Integrates git_operations data with visualization functions.
- Supports both PNG and Mermaid output formats.
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .git_manager import (
    get_commit_history, get_current_branch, get_status, list_stashes,
    is_git_repository, check_git_availability
)

try:
    from ..data_visualization import (
        GitVisualizer, create_git_tree_png, create_git_tree_mermaid,
        create_git_branch_diagram, create_git_workflow_diagram
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

try:
    from ..logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def create_git_analysis_report(
    repository_path: str,
    output_dir: str = "./git_analysis",
    report_name: str = None,
    include_png: bool = True,
    include_mermaid: bool = True
) -> Dict[str, Any]:
    """
    Create a comprehensive Git analysis report with visualizations.
    
    Args:
        repository_path: Path to the Git repository
        output_dir: Directory to save the report files
        report_name: Base name for report files (defaults to repo name)
        include_png: Whether to generate PNG visualizations
        include_mermaid: Whether to generate Mermaid diagrams
        
    Returns:
        Dictionary with report status and file paths
    """
    logger.info(f"Creating Git analysis report for {repository_path}")
    
    if not VISUALIZATION_AVAILABLE:
        logger.error("Data visualization module not available")
        return {"error": "Visualization module not available"}
    
    if not check_git_availability():
        logger.error("Git is not available on this system")
        return {"error": "Git not available"}
    
    if not is_git_repository(repository_path):
        logger.error(f"Path {repository_path} is not a Git repository")
        return {"error": "Not a Git repository"}
    
    # Set default report name
    if not report_name:
        report_name = os.path.basename(os.path.abspath(repository_path))
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize visualizer
    visualizer = GitVisualizer()
    
    # Create comprehensive report
    try:
        results = visualizer.create_comprehensive_git_report(
            repository_path=repository_path,
            output_dir=output_dir,
            report_name=report_name
        )
        
        # Filter results based on user preferences
        if not include_png:
            results = {k: v for k, v in results.items() if 'png' not in k}
        if not include_mermaid:
            results = {k: v for k, v in results.items() if 'mermaid' not in k}
        
        return {
            "success": True,
            "repository_path": repository_path,
            "output_dir": output_dir,
            "report_name": report_name,
            "results": results,
            "files_created": _get_created_files(output_dir, report_name, results)
        }
        
    except Exception as e:
        logger.error(f"Error creating Git analysis report: {e}", exc_info=True)
        return {"error": str(e)}


def visualize_git_branches(
    repository_path: str,
    output_path: str = None,
    format_type: str = "png",
    title: str = None,
    max_commits: int = 20
) -> Dict[str, Any]:
    """
    Create a Git branch visualization.
    
    Args:
        repository_path: Path to the Git repository
        output_path: Path to save the visualization
        format_type: Output format ("png" or "mermaid")
        title: Title for the visualization
        max_commits: Maximum number of commits to include
        
    Returns:
        Dictionary with visualization status and details
    """
    logger.debug(f"Creating Git branch visualization for {repository_path}")
    
    if not VISUALIZATION_AVAILABLE:
        return {"error": "Visualization module not available"}
    
    if not is_git_repository(repository_path):
        return {"error": "Not a Git repository"}
    
    # Set defaults
    if not title:
        title = f"Git Branches - {os.path.basename(repository_path)}"
    
    if not output_path:
        base_name = os.path.basename(repository_path)
        extension = "png" if format_type == "png" else "mmd"
        output_path = f"./git_branches_{base_name}.{extension}"
    
    try:
        if format_type == "png":
            visualizer = GitVisualizer()
            success = visualizer.visualize_git_tree_png(
                repository_path=repository_path,
                title=title,
                output_path=output_path,
                max_commits=max_commits
            )
            
            return {
                "success": success,
                "format": "png",
                "output_path": output_path,
                "title": title
            }
            
        elif format_type == "mermaid":
            visualizer = GitVisualizer()
            content = visualizer.visualize_git_tree_mermaid(
                repository_path=repository_path,
                title=title,
                output_path=output_path
            )
            
            return {
                "success": bool(content),
                "format": "mermaid",
                "output_path": output_path,
                "content": content,
                "title": title
            }
        else:
            return {"error": f"Unsupported format: {format_type}"}
            
    except Exception as e:
        logger.error(f"Error creating Git branch visualization: {e}", exc_info=True)
        return {"error": str(e)}


def visualize_commit_activity(
    repository_path: str,
    output_path: str = None,
    days_back: int = 30,
    title: str = None
) -> Dict[str, Any]:
    """
    Create a commit activity visualization.
    
    Args:
        repository_path: Path to the Git repository
        output_path: Path to save the PNG visualization
        days_back: Number of days back to analyze
        title: Title for the visualization
        
    Returns:
        Dictionary with visualization status and details
    """
    logger.debug(f"Creating commit activity visualization for {repository_path}")
    
    if not VISUALIZATION_AVAILABLE:
        return {"error": "Visualization module not available"}
    
    if not is_git_repository(repository_path):
        return {"error": "Not a Git repository"}
    
    # Set defaults
    if not title:
        title = f"Commit Activity - {os.path.basename(repository_path)}"
    
    if not output_path:
        base_name = os.path.basename(repository_path)
        output_path = f"./commit_activity_{base_name}.png"
    
    try:
        visualizer = GitVisualizer()
        success = visualizer.visualize_commit_activity_png(
            repository_path=repository_path,
            title=title,
            output_path=output_path,
            days_back=days_back
        )
        
        return {
            "success": success,
            "output_path": output_path,
            "title": title,
            "days_analyzed": days_back
        }
        
    except Exception as e:
        logger.error(f"Error creating commit activity visualization: {e}", exc_info=True)
        return {"error": str(e)}


def create_git_workflow_diagram(
    workflow_type: str = "feature_branch",
    output_path: str = "./git_workflow.mmd",
    title: str = "Git Workflow"
) -> Dict[str, Any]:
    """
    Create a Git workflow diagram.
    
    Args:
        workflow_type: Type of workflow ("feature_branch", "gitflow", "github_flow")
        output_path: Path to save the Mermaid diagram
        title: Title for the diagram
        
    Returns:
        Dictionary with diagram creation status and content
    """
    logger.debug(f"Creating Git workflow diagram: {workflow_type}")
    
    if not VISUALIZATION_AVAILABLE:
        return {"error": "Visualization module not available"}
    
    # Define workflow steps for different types
    workflow_steps = {
        "feature_branch": [
            {"name": "Start", "type": "terminal", "description": "Start Development"},
            {"name": "Clone", "type": "process", "description": "git clone repository"},
            {"name": "Branch", "type": "process", "description": "git checkout -b feature/name"},
            {"name": "Develop", "type": "process", "description": "Write code & tests"},
            {"name": "Stage", "type": "process", "description": "git add ."},
            {"name": "Commit", "type": "process", "description": "git commit -m 'message'"},
            {"name": "Push", "type": "process", "description": "git push origin feature/name"},
            {"name": "PR", "type": "process", "description": "Create Pull Request"},
            {"name": "Review", "type": "decision", "description": "Code Review Pass"},
            {"name": "Merge", "type": "process", "description": "Merge to main"},
            {"name": "Deploy", "type": "process", "description": "Deploy to production"},
            {"name": "End", "type": "terminal", "description": "Complete"}
        ],
        "gitflow": [
            {"name": "Start", "type": "terminal", "description": "Initialize Repository"},
            {"name": "Main", "type": "process", "description": "main branch (production)"},
            {"name": "Develop", "type": "process", "description": "develop branch"},
            {"name": "Feature", "type": "process", "description": "feature/* branches"},
            {"name": "Release", "type": "process", "description": "release/* branch"},
            {"name": "Hotfix", "type": "process", "description": "hotfix/* branch"},
            {"name": "MergeDev", "type": "process", "description": "Merge to develop"},
            {"name": "MergeMain", "type": "process", "description": "Merge to main"},
            {"name": "Tag", "type": "process", "description": "Tag release"},
            {"name": "Deploy", "type": "process", "description": "Deploy"},
        ],
        "github_flow": [
            {"name": "Start", "type": "terminal", "description": "Start"},
            {"name": "Main", "type": "process", "description": "main branch"},
            {"name": "Branch", "type": "process", "description": "Create topic branch"},
            {"name": "Commit", "type": "process", "description": "Add commits"},
            {"name": "PR", "type": "process", "description": "Open Pull Request"},
            {"name": "Discuss", "type": "process", "description": "Discuss & review"},
            {"name": "Test", "type": "decision", "description": "Tests pass"},
            {"name": "Merge", "type": "process", "description": "Merge & deploy"},
            {"name": "End", "type": "terminal", "description": "Complete"}
        ]
    }
    
    steps = workflow_steps.get(workflow_type, workflow_steps["feature_branch"])
    
    try:
        content = create_git_workflow_diagram(
            workflow_steps=steps,
            title=title,
            output_path=output_path
        )
        
        return {
            "success": bool(content),
            "workflow_type": workflow_type,
            "output_path": output_path,
            "content": content,
            "title": title
        }
        
    except Exception as e:
        logger.error(f"Error creating Git workflow diagram: {e}", exc_info=True)
        return {"error": str(e)}


def analyze_repository_structure(
    repository_path: str,
    output_path: str = None,
    title: str = None,
    max_depth: int = 3
) -> Dict[str, Any]:
    """
    Analyze and visualize repository structure.
    
    Args:
        repository_path: Path to the Git repository
        output_path: Path to save the Mermaid diagram
        title: Title for the diagram
        max_depth: Maximum directory depth to analyze
        
    Returns:
        Dictionary with analysis results and diagram
    """
    logger.debug(f"Analyzing repository structure for {repository_path}")
    
    if not VISUALIZATION_AVAILABLE:
        return {"error": "Visualization module not available"}
    
    if not is_git_repository(repository_path):
        return {"error": "Not a Git repository"}
    
    # Set defaults
    if not title:
        title = f"Repository Structure - {os.path.basename(repository_path)}"
    
    if not output_path:
        base_name = os.path.basename(repository_path)
        output_path = f"./repo_structure_{base_name}.mmd"
    
    try:
        # Analyze repository structure
        structure = _analyze_directory_structure(repository_path, max_depth)
        
        # Create visualization
        from ..data_visualization import create_repository_structure_diagram
        
        content = create_repository_structure_diagram(
            repo_structure=structure,
            title=title,
            output_path=output_path
        )
        
        return {
            "success": bool(content),
            "output_path": output_path,
            "content": content,
            "structure": structure,
            "title": title,
            "stats": _get_structure_stats(structure)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing repository structure: {e}", exc_info=True)
        return {"error": str(e)}


def get_repository_metadata(repository_path: str) -> Dict[str, Any]:
    """
    Get comprehensive repository metadata for visualization.
    
    Args:
        repository_path: Path to the Git repository
        
    Returns:
        Dictionary with repository metadata
    """
    logger.debug(f"Getting repository metadata for {repository_path}")
    
    if not is_git_repository(repository_path):
        return {"error": "Not a Git repository"}
    
    try:
        metadata = {
            "path": repository_path,
            "name": os.path.basename(os.path.abspath(repository_path)),
            "is_git_repo": True,
            "current_branch": get_current_branch(repository_path),
            "status": get_status(repository_path),
            "recent_commits": get_commit_history(10, repository_path),
            "stashes": list_stashes(repository_path),
            "structure_stats": {}
        }
        
        # Add structure analysis
        structure = _analyze_directory_structure(repository_path, 2)
        metadata["structure_stats"] = _get_structure_stats(structure)
        
        # Add commit statistics
        commits = get_commit_history(100, repository_path)
        if commits:
            authors = {}
            for commit in commits:
                author = commit.get("author_name", "Unknown")
                authors[author] = authors.get(author, 0) + 1
            
            metadata["commit_stats"] = {
                "total_recent_commits": len(commits),
                "unique_authors": len(authors),
                "top_authors": sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]
            }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting repository metadata: {e}", exc_info=True)
        return {"error": str(e)}


def _analyze_directory_structure(path: str, max_depth: int = 3) -> Dict[str, Any]:
    """Analyze directory structure up to max_depth."""
    structure = {}
    path_obj = Path(path)
    
    def scan_directory(current_path: Path, current_depth: int = 0) -> Dict[str, Any]:
        if current_depth >= max_depth:
            return {}
        
        items = {}
        try:
            for item in current_path.iterdir():
                # Skip hidden files and git directory
                if item.name.startswith('.'):
                    continue
                
                if item.is_dir():
                    items[item.name] = scan_directory(item, current_depth + 1)
                else:
                    items[item.name] = "file"
        except PermissionError:
            pass
        
        return items
    
    return scan_directory(path_obj)


def _get_structure_stats(structure: Dict[str, Any]) -> Dict[str, int]:
    """Get statistics from directory structure."""
    stats = {"directories": 0, "files": 0}
    
    def count_items(items: Dict[str, Any]):
        for name, content in items.items():
            if isinstance(content, dict):
                stats["directories"] += 1
                count_items(content)
            else:
                stats["files"] += 1
    
    count_items(structure)
    return stats


def _get_created_files(output_dir: str, report_name: str, results: Dict[str, bool]) -> List[str]:
    """Get list of successfully created files."""
    files = []
    
    # Map result keys to file patterns
    file_patterns = {
        "git_tree_png": f"{report_name}_git_tree.png",
        "git_tree_mermaid": f"{report_name}_git_tree.mmd",
        "commit_activity": f"{report_name}_commit_activity.png", 
        "repo_summary": f"{report_name}_summary_dashboard.png",
        "workflow_mermaid": f"{report_name}_workflow.mmd",
        "structure_mermaid": f"{report_name}_structure.mmd"
    }
    
    for key, success in results.items():
        if success and key in file_patterns:
            files.append(os.path.join(output_dir, file_patterns[key]))
    
    # Always include README if it exists
    readme_path = os.path.join(output_dir, f"{report_name}_README.md")
    if os.path.exists(readme_path):
        files.append(readme_path)
    
    return files


if __name__ == '__main__':
    # Test the integration functions
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        
        logger.info(f"Testing Git visualization integration with: {repo_path}")
        
        # Test comprehensive report
        report_result = create_git_analysis_report(
            repository_path=repo_path,
            output_dir="./test_git_analysis",
            report_name="integration_test"
        )
        
        print(f"Report result: {report_result}")
        
        # Test branch visualization
        branch_result = visualize_git_branches(
            repository_path=repo_path,
            output_path="./test_branches.png"
        )
        
        print(f"Branch visualization result: {branch_result}")
        
        # Test commit activity
        activity_result = visualize_commit_activity(
            repository_path=repo_path,
            output_path="./test_activity.png"
        )
        
        print(f"Activity visualization result: {activity_result}")
        
    else:
        logger.info("Please provide a repository path as argument")
        
    # Basic logging setup if running standalone
    import logging
    if not logger.hasHandlers():
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.info("Basic logging configured for direct script execution of visualization_integration.py.")
