from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import os
import shutil

from codomyrmex.data_visualization import (
from codomyrmex.data_visualization.git_visualizer import (
from codomyrmex.git_operations import (
from codomyrmex.git_operations.visualization_integration import (
from codomyrmex.logging_monitoring import get_logger

























    BaseChartVisualizer,
    BaseNetworkVisualizer,
)
    check_git_availability,
    is_git_repository,
)
    generate_git_workflow_diagram,
)

logger = get_logger(__name__)


class GitVisualizationDemo:
    """
    Class to encapsulate the visualization demo logic.
    """

# Optional import for data visualization
try:
        GitVisualizer,
        MermaidDiagramGenerator,
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

logger = get_logger(__name__)


class GitVisualizationDemo:
    """Class to run git visualization demonstrations."""

    def __init__(self, output_dir: str = None):
        """Initialize the demo runner."""
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.cwd() / "@output" / "git_visualization_demo"
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized demo with output directory: {self.output_dir}")

    def run_all_demos(self, repository_path: str = None, skip_sample: bool = False, skip_workflows: bool = False) -> bool:
        """Run all enabled demonstrations."""
        if not VISUALIZATION_AVAILABLE:
            logger.error("Data visualization module not available. Cannot run demo.")
            return False

        results = {}

        # 1. Sample data demonstrations
        if not skip_sample:
            logger.info("Running sample data demonstration...")
            results['sample_data'] = self.demo_sample_data_visualizations()

        # 2. Real repository analysis
        if repository_path:
            logger.info(f"Running real repository analysis for: {repository_path}")
            results['real_repo'] = self.demo_real_repository_analysis(repository_path)
        else:
            logger.info("No repository path provided. Skipping real repository analysis.")

        # 3. Workflow diagrams
        if not skip_workflows:
            logger.info("Running workflow diagram demonstration...")
            results['workflows'] = self.demo_workflow_diagrams()

        # Generate summary
        self._generate_overall_summary(results, repository_path)
        
        success_count = sum(1 for r in results.values() if r)
        logger.info(f"Demo run completed. Successful: {success_count}/{len(results)}")
        
        return success_count > 0

    def demo_sample_data_visualizations(self) -> bool:
        """Demonstrate Git visualizations with sample data."""
        output_dir = self.output_dir / "sample_data"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("=== Demonstrating Git Visualizations with Sample Data ===")
        
        # Sample data definitions
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
                        "plotter.py": "file"
                    },
                    "git_operations": {
                        "__init__.py": "file",
                        "git_manager.py": "file"
                    }
                }
            },
            "docs": {"README.md": "file"},
            "setup.py": "file"
        }

        visualizer = GitVisualizer()
        mermaid_generator = MermaidDiagramGenerator()
        results = {}

        # 1. Create PNG Git tree visualization
        results['git_tree_png'] = visualizer.visualize_git_tree_png(
            branches=sample_branches,
            commits=sample_commits,
            title="Sample Git Repository - Branch Tree",
            output_path=str(output_dir / "sample_git_tree.png"),
            max_commits=15
        )

        # 2. Create Mermaid Git tree diagram
        results['git_tree_mermaid'] = bool(visualizer.visualize_git_tree_mermaid(
            branches=sample_branches,
            commits=sample_commits,
            title="Sample Git Repository - Branch Diagram",
            output_path=str(output_dir / "sample_git_tree.mmd")
        ))

        # 3. Create commit activity visualization
        results['commit_activity'] = visualizer.visualize_commit_activity_png(
            commits=sample_commits,
            title="Sample Repository - Commit Activity",
            output_path=str(output_dir / "sample_commit_activity.png"),
            days_back=20
        )

        # 4. Create repository summary dashboard
        repo_data = {
            'status': {'clean': False, 'modified': ['file1.py'], 'untracked': []},
            'commits': sample_commits,
            'current_branch': 'main',
            'total_commits': len(sample_commits)
        }
        results['repository_summary'] = visualizer.visualize_repository_summary_png(
            repo_data=repo_data,
            title="Sample Repository - Summary Dashboard",
            output_path=str(output_dir / "sample_repository_summary.png")
        )

        # 5. Create Mermaid workflow diagram
        results['workflow_diagram'] = bool(mermaid_generator.create_git_workflow_diagram(
            workflow_steps=sample_workflow_steps,
            title="Feature Branch Development Workflow",
            output_path=str(output_dir / "sample_git_workflow.mmd")
        ))

        # 6. Create repository structure diagram
        results['structure_diagram'] = bool(mermaid_generator.create_repository_structure_diagram(
            repo_structure=sample_repo_structure,
            title="Codomyrmex Project Structure",
            output_path=str(output_dir / "sample_repo_structure.mmd")
        ))

        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Sample data demo: {success_count}/{len(results)} successful")
        
        return success_count > 0

    def demo_real_repository_analysis(self, repository_path: str) -> bool:
        """Demonstrate Git visualizations with a real repository."""
        output_dir = self.output_dir / "real_repository"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"=== Analyzing Real Git Repository: {repository_path} ===")
        
        if not check_git_availability():
            logger.error("Git is not available on this system")
            return False
            
        if not is_git_repository(repository_path):
            logger.error(f"Path {repository_path} is not a Git repository")
            return False

        # 1. Comprehensive Report
        report_result = create_git_analysis_report(
            repository_path=repository_path,
            output_dir=str(output_dir / "comprehensive_report"),
            report_name="live_repo_analysis"
        )
        
        # 2. Individual Visualizations
        visualize_git_branches(
            repository_path=repository_path,
            output_path=str(output_dir / "live_branches.png"),
            format_type="png"
        )
        
        visualize_commit_activity(
            repository_path=repository_path,
            output_path=str(output_dir / "live_commit_activity.png"),
            days_back=30
        )
        
        analyze_repository_structure(
            repository_path=repository_path,
            output_path=str(output_dir / "live_repo_structure.mmd")
        )

        return report_result.get("success", False)

    def demo_workflow_diagrams(self) -> bool:
        """Demonstrate workflow diagram generation."""
        output_dir = self.output_dir / "workflows"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_types = ["feature_branch", "gitflow", "github_flow"]
        results = {}
        
        for workflow_type in workflow_types:
            result = create_git_workflow_diagram(
                workflow_type=workflow_type,
                output_path=str(output_dir / f"workflow_{workflow_type}.mmd"),
                title=f"{workflow_type.replace('_', ' ').title()} Workflow"
            )
            results[workflow_type] = result.get('success', False)
            
        return any(results.values())

    def _generate_overall_summary(self, results: Dict[str, bool], repository_path: Optional[str]):
        """Generate overall summary markdown file."""
        summary = [
            "# Git Visualization Demo Results",
            "",
            f"**Output Directory:** {self.output_dir}",
            "",
            "## Results",
            ""
        ]
        
        for name, success in results.items():
            summary.append(f"- {name}: {'✅' if success else '❌'}")
            
        if repository_path:
            summary.append(f"\nAnalyzed Repository: {repository_path}")
            
        summary_path = self.output_dir / "demo_summary.md"
        with open(summary_path, 'w') as f:
            f.write('\n'.join(summary))
