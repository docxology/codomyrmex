#!/usr/bin/env python3
"""
Comprehensive demonstration of Git visualization capabilities.

This script demonstrates all the new Git visualization functions in both
data_visualization and git_operations modules, showing how to create:
- PNG Git tree visualizations
- Mermaid Git diagrams
- Commit activity charts
- Repository structure diagrams
- Comprehensive Git analysis reports

Usage:
    python3 examples/git_visualization_comprehensive_demo.py [repository_path]

If no repository path is provided, the script will use sample data for demonstration.
"""
import os
import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from codomyrmex.data_visualization import (
        GitVisualizer, MermaidDiagramGenerator,
        visualize_git_repository, create_git_tree_png, create_git_tree_mermaid,
        create_git_branch_diagram, create_git_workflow_diagram,
        create_repository_structure_diagram, create_commit_timeline_diagram
    )
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Data visualization module not available: {e}")
    VISUALIZATION_AVAILABLE = False

try:
    from codomyrmex.git_operations import (
        check_git_availability, is_git_repository, get_commit_history,
        get_current_branch, get_status
    )
    from codomyrmex.git_operations.visualization_integration import (
        create_git_analysis_report, visualize_git_branches, visualize_commit_activity,
        create_git_workflow_diagram as create_workflow_via_integration,
        analyze_repository_structure, get_repository_metadata
    )
    GIT_OPERATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Git operations module not available: {e}")
    GIT_OPERATIONS_AVAILABLE = False

try:
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    setup_logging()
    logger = get_logger(__name__)
    LOGGING_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    LOGGING_AVAILABLE = False
    print("Warning: Using standard logging instead of codomyrmex logging")


def create_output_directory(base_name="git_visualization_demo"):
    """Create output directory for demo files."""
    output_dir = Path.cwd() / "@output" / f"01_{base_name}"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir


def demo_sample_data_visualizations(output_dir):
    """Demonstrate Git visualizations with sample data."""
    logger.info("=== Demonstrating Git Visualizations with Sample Data ===")
    
    if not VISUALIZATION_AVAILABLE:
        logger.error("Data visualization module not available")
        return False
    
    # Sample data for demonstrations
    sample_branches = [
        {"name": "main", "commits": 10, "created_at": "2024-01-01"},
        {"name": "develop", "commits": 8, "created_at": "2024-01-02", "merged": False},
        {"name": "feature/user-auth", "commits": 5, "created_at": "2024-01-03", "merged": True},
        {"name": "feature/api-endpoints", "commits": 6, "created_at": "2024-01-05", "merged": True},
        {"name": "hotfix/security-fix", "commits": 2, "created_at": "2024-01-10", "merged": True}
    ]
    
    sample_commits = [
        {"hash": "a1b2c3d", "message": "Initial commit", "author_name": "Alice", "author_email": "alice@example.com", "date": "2024-01-01T10:00:00Z", "branch": "main"},
        {"hash": "e4f5g6h", "message": "Add project structure", "author_name": "Alice", "author_email": "alice@example.com", "date": "2024-01-01T14:30:00Z", "branch": "main"},
        {"hash": "i7j8k9l", "message": "Start user authentication", "author_name": "Bob", "author_email": "bob@example.com", "date": "2024-01-03T09:15:00Z", "branch": "feature/user-auth"},
        {"hash": "m1n2o3p", "message": "Implement login system", "author_name": "Bob", "author_email": "bob@example.com", "date": "2024-01-03T16:45:00Z", "branch": "feature/user-auth"},
        {"hash": "q4r5s6t", "message": "Add password validation", "author_name": "Bob", "author_email": "bob@example.com", "date": "2024-01-04T11:20:00Z", "branch": "feature/user-auth"},
        {"hash": "u7v8w9x", "message": "Create API endpoints", "author_name": "Charlie", "author_email": "charlie@example.com", "date": "2024-01-05T13:00:00Z", "branch": "feature/api-endpoints"},
        {"hash": "y1z2a3b", "message": "Add request validation", "author_name": "Charlie", "author_email": "charlie@example.com", "date": "2024-01-06T10:30:00Z", "branch": "feature/api-endpoints"},
        {"hash": "c4d5e6f", "message": "Fix security vulnerability", "author_name": "Alice", "author_email": "alice@example.com", "date": "2024-01-10T08:45:00Z", "branch": "hotfix/security-fix"},
        {"hash": "g7h8i9j", "message": "Update documentation", "author_name": "Alice", "author_email": "alice@example.com", "date": "2024-01-12T15:20:00Z", "branch": "develop"},
        {"hash": "k1l2m3n", "message": "Prepare release v1.0", "author_name": "Alice", "author_email": "alice@example.com", "date": "2024-01-15T12:00:00Z", "branch": "main"}
    ]
    
    sample_workflow_steps = [
        {"name": "Start", "type": "terminal", "description": "Start Development"},
        {"name": "Clone", "type": "process", "description": "git clone repository"},
        {"name": "Branch", "type": "process", "description": "git checkout -b feature/name"},
        {"name": "Code", "type": "process", "description": "Write code & tests"},
        {"name": "Test", "type": "decision", "description": "Tests pass?"},
        {"name": "Fix", "type": "process", "description": "Fix issues"},
        {"name": "Stage", "type": "process", "description": "git add ."},
        {"name": "Commit", "type": "process", "description": "git commit -m 'message'"},
        {"name": "Push", "type": "process", "description": "git push origin feature/name"},
        {"name": "PR", "type": "process", "description": "Create Pull Request"},
        {"name": "Review", "type": "decision", "description": "Code Review Pass?"},
        {"name": "Merge", "type": "process", "description": "Merge to main"},
        {"name": "Deploy", "type": "process", "description": "Deploy to production"},
        {"name": "End", "type": "terminal", "description": "Complete"}
    ]
    
    sample_repo_structure = {
        "src": {
            "codomyrmex": {
                "data_visualization": {
                    "__init__.py": "file",
                    "plotter.py": "file",
                    "git_visualizer.py": "file",
                    "mermaid_generator.py": "file",
                    "tests": {
                        "unit": {
                            "test_git_visualizer.py": "file",
                            "test_mermaid_generator.py": "file"
                        },
                        "integration": {
                            "test_git_visualization_integration.py": "file"
                        }
                    }
                },
                "git_operations": {
                    "__init__.py": "file",
                    "git_manager.py": "file",
                    "visualization_integration.py": "file",
                    "tests": {
                        "unit": {
                            "test_visualization_integration.py": "file"
                        }
                    }
                }
            }
        },
        "examples": {
            "git_visualization_comprehensive_demo.py": "file"
        },
        "docs": {
            "README.md": "file"
        },
        "requirements.txt": "file",
        "setup.py": "file"
    }
    
    # Initialize visualizer
    visualizer = GitVisualizer()
    mermaid_generator = MermaidDiagramGenerator()
    
    results = {}
    
    # 1. Create PNG Git tree visualization
    logger.info("Creating PNG Git tree visualization...")
    png_success = visualizer.visualize_git_tree_png(
        branches=sample_branches,
        commits=sample_commits,
        title="Sample Git Repository - Branch Tree",
        output_path=str(output_dir / "sample_git_tree.png"),
        max_commits=15
    )
    results['git_tree_png'] = png_success
    logger.info(f"PNG Git tree: {'Success' if png_success else 'Failed'}")
    
    # 2. Create Mermaid Git tree diagram
    logger.info("Creating Mermaid Git tree diagram...")
    mermaid_content = visualizer.visualize_git_tree_mermaid(
        branches=sample_branches,
        commits=sample_commits,
        title="Sample Git Repository - Branch Diagram",
        output_path=str(output_dir / "sample_git_tree.mmd")
    )
    results['git_tree_mermaid'] = bool(mermaid_content)
    logger.info(f"Mermaid Git tree: {'Success' if mermaid_content else 'Failed'}")
    
    # 3. Create commit activity visualization
    logger.info("Creating commit activity visualization...")
    activity_success = visualizer.visualize_commit_activity_png(
        commits=sample_commits,
        title="Sample Repository - Commit Activity",
        output_path=str(output_dir / "sample_commit_activity.png"),
        days_back=20
    )
    results['commit_activity'] = activity_success
    logger.info(f"Commit activity: {'Success' if activity_success else 'Failed'}")
    
    # 4. Create repository summary dashboard
    logger.info("Creating repository summary dashboard...")
    repo_data = {
        'status': {'clean': False, 'modified': ['file1.py', 'file2.py'], 'untracked': ['temp.txt']},
        'commits': sample_commits,
        'current_branch': 'main',
        'total_commits': len(sample_commits)
    }
    
    summary_success = visualizer.visualize_repository_summary_png(
        repo_data=repo_data,
        title="Sample Repository - Summary Dashboard",
        output_path=str(output_dir / "sample_repository_summary.png")
    )
    results['repository_summary'] = summary_success
    logger.info(f"Repository summary: {'Success' if summary_success else 'Failed'}")
    
    # 5. Create Mermaid workflow diagram
    logger.info("Creating Git workflow diagram...")
    workflow_content = mermaid_generator.create_git_workflow_diagram(
        workflow_steps=sample_workflow_steps,
        title="Feature Branch Development Workflow",
        output_path=str(output_dir / "sample_git_workflow.mmd")
    )
    results['workflow_diagram'] = bool(workflow_content)
    logger.info(f"Workflow diagram: {'Success' if workflow_content else 'Failed'}")
    
    # 6. Create repository structure diagram
    logger.info("Creating repository structure diagram...")
    structure_content = mermaid_generator.create_repository_structure_diagram(
        repo_structure=sample_repo_structure,
        title="Codomyrmex Project Structure",
        output_path=str(output_dir / "sample_repo_structure.mmd")
    )
    results['structure_diagram'] = bool(structure_content)
    logger.info(f"Structure diagram: {'Success' if structure_content else 'Failed'}")
    
    # 7. Create commit timeline diagram
    logger.info("Creating commit timeline diagram...")
    timeline_content = mermaid_generator.create_commit_timeline_diagram(
        commits=sample_commits,
        title="Development Timeline",
        output_path=str(output_dir / "sample_commit_timeline.mmd")
    )
    results['timeline_diagram'] = bool(timeline_content)
    logger.info(f"Timeline diagram: {'Success' if timeline_content else 'Failed'}")
    
    # 8. Test different workflow types
    logger.info("Creating different workflow type diagrams...")
    workflow_types = [
        ("feature_branch", "Feature Branch Workflow"),
        ("gitflow", "GitFlow Workflow"),
        ("github_flow", "GitHub Flow Workflow")
    ]
    
    for workflow_type, title in workflow_types:
        content = create_git_workflow_diagram(
            title=title,
            output_path=str(output_dir / f"workflow_{workflow_type}.mmd")
        )
        results[f'workflow_{workflow_type}'] = bool(content)
        logger.info(f"Workflow {workflow_type}: {'Success' if content else 'Failed'}")
    
    # Generate summary report
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    logger.info(f"Sample data visualization completed: {success_count}/{total_count} successful")
    
    # Create summary file
    summary_content = [
        "# Git Visualization Demo - Sample Data Results",
        "",
        f"**Total visualizations:** {total_count}",
        f"**Successful:** {success_count}",
        f"**Failed:** {total_count - success_count}",
        "",
        "## Results:",
        ""
    ]
    
    for result_name, success in results.items():
        status = "✅" if success else "❌"
        summary_content.append(f"- {result_name}: {status}")
    
    summary_content.extend([
        "",
        "## Generated Files:",
        "",
        "### PNG Visualizations:",
        "- `sample_git_tree.png`: Git branch tree visualization",
        "- `sample_commit_activity.png`: Commit activity chart",
        "- `sample_repository_summary.png`: Comprehensive repository dashboard",
        "",
        "### Mermaid Diagrams:",
        "- `sample_git_tree.mmd`: Git branch diagram",
        "- `sample_git_workflow.mmd`: Development workflow",
        "- `sample_repo_structure.mmd`: Repository structure",
        "- `sample_commit_timeline.mmd`: Commit timeline",
        "- `workflow_*.mmd`: Various workflow type diagrams",
        "",
        "## Usage:",
        "- PNG files can be viewed directly or embedded in documents",
        "- Mermaid files can be rendered using:",
        "  - Mermaid Live Editor (mermaid.live)",
        "  - GitHub/GitLab markdown rendering", 
        "  - VS Code Mermaid extensions",
        "  - Mermaid CLI tools"
    ])
    
    summary_path = output_dir / "sample_data_demo_README.md"
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_content))
    
    logger.info(f"Sample data demo summary saved to {summary_path}")
    
    return success_count > 0


def demo_real_repository_analysis(repository_path, output_dir):
    """Demonstrate Git visualizations with a real repository."""
    logger.info(f"=== Analyzing Real Git Repository: {repository_path} ===")
    
    if not VISUALIZATION_AVAILABLE:
        logger.error("Data visualization module not available")
        return False
    
    if not GIT_OPERATIONS_AVAILABLE:
        logger.error("Git operations module not available")
        return False
    
    # Check if Git is available
    if not check_git_availability():
        logger.error("Git is not available on this system")
        return False
    
    # Check if path is a Git repository
    if not is_git_repository(repository_path):
        logger.error(f"Path {repository_path} is not a Git repository")
        return False
    
    logger.info(f"Repository validation passed for: {repository_path}")
    
    # Method 1: Use comprehensive integration function
    logger.info("Creating comprehensive Git analysis report...")
    
    report_result = create_git_analysis_report(
        repository_path=repository_path,
        output_dir=str(output_dir / "comprehensive_report"),
        report_name="live_repo_analysis",
        include_png=True,
        include_mermaid=True
    )
    
    if report_result.get("success"):
        logger.info(f"Comprehensive report created successfully")
        logger.info(f"Files created: {len(report_result.get('files_created', []))}")
        for file_path in report_result.get('files_created', []):
            logger.info(f"  - {file_path}")
    else:
        logger.error(f"Comprehensive report failed: {report_result.get('error', 'Unknown error')}")
    
    # Method 2: Use individual visualization functions
    logger.info("Creating individual visualizations...")
    
    individual_results = {}
    
    # Git branch visualizations
    png_result = visualize_git_branches(
        repository_path=repository_path,
        output_path=str(output_dir / "live_branches.png"),
        format_type="png",
        title=f"Git Branches - {os.path.basename(repository_path)}"
    )
    individual_results['branches_png'] = png_result.get('success', False)
    
    mermaid_result = visualize_git_branches(
        repository_path=repository_path,
        output_path=str(output_dir / "live_branches.mmd"),
        format_type="mermaid",
        title=f"Git Branch Diagram - {os.path.basename(repository_path)}"
    )
    individual_results['branches_mermaid'] = mermaid_result.get('success', False)
    
    # Commit activity
    activity_result = visualize_commit_activity(
        repository_path=repository_path,
        output_path=str(output_dir / "live_commit_activity.png"),
        days_back=30,
        title=f"Commit Activity - {os.path.basename(repository_path)}"
    )
    individual_results['commit_activity'] = activity_result.get('success', False)
    
    # Repository structure analysis
    structure_result = analyze_repository_structure(
        repository_path=repository_path,
        output_path=str(output_dir / "live_repo_structure.mmd"),
        title=f"Repository Structure - {os.path.basename(repository_path)}"
    )
    individual_results['structure_analysis'] = structure_result.get('success', False)
    
    # Get repository metadata
    metadata = get_repository_metadata(repository_path)
    if "error" not in metadata:
        logger.info("Repository metadata retrieved successfully:")
        logger.info(f"  Current branch: {metadata.get('current_branch')}")
        logger.info(f"  Total recent commits: {metadata.get('commit_stats', {}).get('total_recent_commits', 0)}")
        logger.info(f"  Unique authors: {metadata.get('commit_stats', {}).get('unique_authors', 0)}")
        logger.info(f"  Repository clean: {metadata.get('status', {}).get('clean', False)}")
        
        # Save metadata to file
        import json
        metadata_path = output_dir / "live_repo_metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info(f"Metadata saved to: {metadata_path}")
        individual_results['metadata'] = True
    else:
        logger.error(f"Failed to get repository metadata: {metadata['error']}")
        individual_results['metadata'] = False
    
    # Method 3: Direct visualizer usage
    logger.info("Using GitVisualizer directly...")
    
    visualizer = GitVisualizer()
    direct_results = visualizer.create_comprehensive_git_report(
        repository_path=repository_path,
        output_dir=str(output_dir / "direct_visualizer"),
        report_name="direct_analysis"
    )
    
    direct_success_count = sum(1 for success in direct_results.values() if success)
    logger.info(f"Direct visualizer results: {direct_success_count}/{len(direct_results)} successful")
    
    # Generate comprehensive summary
    total_individual = sum(1 for success in individual_results.values() if success)
    
    summary_content = [
        f"# Git Repository Analysis - {os.path.basename(repository_path)}",
        "",
        f"**Repository Path:** {repository_path}",
        f"**Analysis Date:** {Path().cwd()}",
        "",
        "## Analysis Results:",
        "",
        f"### Comprehensive Report:",
        f"- Success: {'✅' if report_result.get('success') else '❌'}",
        f"- Files Created: {len(report_result.get('files_created', []))}",
        "",
        f"### Individual Visualizations: {total_individual}/{len(individual_results)}",
        ""
    ]
    
    for result_name, success in individual_results.items():
        status = "✅" if success else "❌"
        summary_content.append(f"- {result_name}: {status}")
    
    summary_content.extend([
        "",
        f"### Direct Visualizer: {direct_success_count}/{len(direct_results)}",
        ""
    ])
    
    for result_name, success in direct_results.items():
        status = "✅" if success else "❌"
        summary_content.append(f"- {result_name}: {status}")
    
    if "error" not in metadata:
        summary_content.extend([
            "",
            "## Repository Information:",
            f"- Current Branch: {metadata.get('current_branch')}",
            f"- Repository Status: {'Clean' if metadata.get('status', {}).get('clean') else 'Has Changes'}",
            f"- Recent Commits: {metadata.get('commit_stats', {}).get('total_recent_commits', 0)}",
            f"- Unique Authors: {metadata.get('commit_stats', {}).get('unique_authors', 0)}",
            f"- Directories: {metadata.get('structure_stats', {}).get('directories', 0)}",
            f"- Files: {metadata.get('structure_stats', {}).get('files', 0)}"
        ])
    
    summary_path = output_dir / "live_repo_analysis_README.md"
    with open(summary_path, 'w') as f:
        f.write('\n'.join(summary_content))
    
    logger.info(f"Live repository analysis summary saved to {summary_path}")
    
    overall_success = (
        report_result.get("success", False) or 
        total_individual > 0 or 
        direct_success_count > 0
    )
    
    return overall_success


def demo_workflow_diagrams(output_dir):
    """Demonstrate various Git workflow diagram generation."""
    logger.info("=== Demonstrating Git Workflow Diagrams ===")
    
    if not VISUALIZATION_AVAILABLE:
        logger.error("Data visualization module not available")
        return False
    
    workflow_types = [
        ("feature_branch", "Feature Branch Workflow", "Standard feature branch development process"),
        ("gitflow", "GitFlow Workflow", "GitFlow branching model with release branches"),
        ("github_flow", "GitHub Flow", "Simplified GitHub-style workflow"),
        ("custom", "Custom Team Workflow", "Example of a custom workflow definition")
    ]
    
    results = {}
    
    # Create workflow diagrams using integration module
    if GIT_OPERATIONS_AVAILABLE:
        for workflow_type, title, description in workflow_types:
            if workflow_type != "custom":  # Skip custom for integration module
                result = create_workflow_via_integration(
                    workflow_type=workflow_type,
                    output_path=str(output_dir / f"integration_workflow_{workflow_type}.mmd"),
                    title=title
                )
                results[f'integration_{workflow_type}'] = result.get('success', False)
                logger.info(f"Integration workflow {workflow_type}: {'Success' if result.get('success') else 'Failed'}")
    
    # Create workflow diagrams using direct Mermaid generator
    mermaid_generator = MermaidDiagramGenerator()
    
    # Custom workflow example
    custom_workflow_steps = [
        {"name": "Start", "type": "terminal", "description": "Begin Sprint"},
        {"name": "Planning", "type": "process", "description": "Sprint Planning"},
        {"name": "Ticket", "type": "process", "description": "Pick Ticket"},
        {"name": "Branch", "type": "process", "description": "git checkout -b ticket/PROJ-123"},
        {"name": "Develop", "type": "process", "description": "Implement Feature"},
        {"name": "Test", "type": "decision", "description": "Tests Pass?"},
        {"name": "Fix", "type": "process", "description": "Fix Issues"},
        {"name": "Commit", "type": "process", "description": "git commit"},
        {"name": "Push", "type": "process", "description": "git push origin ticket/PROJ-123"},
        {"name": "MR", "type": "process", "description": "Create Merge Request"},
        {"name": "Review", "type": "decision", "description": "Code Review Approved?"},
        {"name": "Deploy", "type": "process", "description": "Deploy to Staging"},
        {"name": "QA", "type": "decision", "description": "QA Testing Pass?"},
        {"name": "Merge", "type": "process", "description": "Merge to main"},
        {"name": "Production", "type": "process", "description": "Deploy to Production"},
        {"name": "Monitor", "type": "process", "description": "Monitor & Verify"},
        {"name": "End", "type": "terminal", "description": "Complete"}
    ]
    
    custom_content = mermaid_generator.create_git_workflow_diagram(
        workflow_steps=custom_workflow_steps,
        title="Custom Team Workflow with QA",
        output_path=str(output_dir / "custom_team_workflow.mmd")
    )
    results['custom_workflow'] = bool(custom_content)
    logger.info(f"Custom workflow: {'Success' if custom_content else 'Failed'}")
    
    # Create workflow comparison diagram
    comparison_content = [
        "# Git Workflow Comparison",
        "",
        "This document compares different Git workflow approaches:",
        "",
        "## 1. Feature Branch Workflow",
        "- Simple branching from main",
        "- Feature development in isolation", 
        "- Direct merge back to main",
        "- Suitable for small teams and continuous deployment",
        "",
        "## 2. GitFlow Workflow",
        "- Multiple branch types (main, develop, feature, release, hotfix)",
        "- Structured release process",
        "- Parallel development streams",
        "- Suitable for scheduled releases",
        "",
        "## 3. GitHub Flow",
        "- Single main branch",
        "- Feature branches with pull requests",
        "- Continuous deployment focus",
        "- Suitable for web applications",
        "",
        "## 4. Custom Team Workflow",
        "- Incorporates team-specific processes",
        "- Includes QA and staging steps",
        "- Formal review processes",
        "- Suitable for enterprise environments",
        "",
        f"Generated {len([r for r in results.values() if r])} workflow diagrams successfully."
    ]
    
    comparison_path = output_dir / "workflow_comparison.md"
    with open(comparison_path, 'w') as f:
        f.write('\n'.join(comparison_content))
    
    logger.info(f"Workflow comparison saved to {comparison_path}")
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    logger.info(f"Workflow diagram demo completed: {success_count}/{total_count} successful")
    
    return success_count > 0


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Comprehensive Git Visualization Demo")
    parser.add_argument("repository_path", nargs='?', help="Path to Git repository to analyze")
    parser.add_argument("--output-dir", help="Output directory for demo files")
    parser.add_argument("--skip-sample", action="store_true", help="Skip sample data demonstrations")
    parser.add_argument("--skip-workflows", action="store_true", help="Skip workflow diagram demonstrations")
    
    args = parser.parse_args()
    
    # Check module availability
    if not VISUALIZATION_AVAILABLE:
        logger.error("Data visualization module is not available. Cannot run demo.")
        return False
    
    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = create_output_directory("git_visualization_comprehensive_demo")
    
    logger.info(f"Git Visualization Comprehensive Demo")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Visualization module available: {VISUALIZATION_AVAILABLE}")
    logger.info(f"Git operations module available: {GIT_OPERATIONS_AVAILABLE}")
    
    demo_results = {}
    
    # 1. Sample data demonstrations
    if not args.skip_sample:
        sample_success = demo_sample_data_visualizations(output_dir / "sample_data")
        demo_results['sample_data'] = sample_success
    
    # 2. Real repository analysis (if path provided)
    if args.repository_path:
        repo_success = demo_real_repository_analysis(args.repository_path, output_dir / "real_repository")
        demo_results['real_repository'] = repo_success
    else:
        logger.info("No repository path provided. Skipping real repository analysis.")
        logger.info("To analyze a real repository, run: python3 examples/git_visualization_comprehensive_demo.py /path/to/repository")
    
    # 3. Workflow diagram demonstrations  
    if not args.skip_workflows:
        workflow_success = demo_workflow_diagrams(output_dir / "workflows")
        demo_results['workflows'] = workflow_success
    
    # Generate overall summary
    successful_demos = sum(1 for success in demo_results.values() if success)
    total_demos = len(demo_results)
    
    overall_summary = [
        "# Git Visualization Comprehensive Demo - Results",
        "",
        f"**Demo Date:** {Path().cwd()}",
        f"**Output Directory:** {output_dir}",
        f"**Successful Demos:** {successful_demos}/{total_demos}",
        "",
        "## Demo Results:",
        ""
    ]
    
    for demo_name, success in demo_results.items():
        status = "✅" if success else "❌"
        overall_summary.append(f"- {demo_name}: {status}")
    
    overall_summary.extend([
        "",
        "## Module Availability:",
        f"- Data Visualization: {'✅' if VISUALIZATION_AVAILABLE else '❌'}",
        f"- Git Operations: {'✅' if GIT_OPERATIONS_AVAILABLE else '❌'}",
        f"- Logging Monitoring: {'✅' if LOGGING_AVAILABLE else '❌'}",
        "",
        "## Capabilities Demonstrated:",
        "- PNG Git tree visualizations with matplotlib",
        "- Mermaid diagram generation (gitgraph, flowchart, timeline)",
        "- Commit activity analysis and charting",
        "- Repository structure analysis",
        "- Comprehensive Git repository reporting",
        "- Integration between data_visualization and git_operations modules",
        "- Support for both sample data and live Git repositories",
        "- Multiple workflow diagram types",
        "",
        "## Output Structure:",
        "```",
        f"{output_dir.name}/",
        "├── sample_data/          # Sample data visualizations",
        "├── real_repository/      # Real repository analysis (if provided)",
        "├── workflows/            # Git workflow diagrams",
        "└── comprehensive_demo_README.md",
        "```",
        "",
        "## Next Steps:",
        "1. Review generated visualizations in each subdirectory",
        "2. Open PNG files to view charts and dashboards",
        "3. Render Mermaid (.mmd) files using supported tools",
        "4. Use the integration functions in your own projects",
        "5. Customize visualizations for your team's needs"
    ])
    
    summary_path = output_dir / "comprehensive_demo_README.md"
    with open(summary_path, 'w') as f:
        f.write('\n'.join(overall_summary))
    
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE DEMO COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Overall Results: {successful_demos}/{total_demos} demos successful")
    logger.info(f"Output Directory: {output_dir}")
    logger.info(f"Summary Report: {summary_path}")
    
    if successful_demos > 0:
        logger.info("✅ Demo completed successfully! Check the output directory for results.")
        return True
    else:
        logger.error("❌ All demos failed. Check the logs for error details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
