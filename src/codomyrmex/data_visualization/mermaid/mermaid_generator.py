"""
Mermaid diagram generation for the Data Visualization module.

This module provides functions to generate Mermaid diagrams for various visualization types,
particularly focused on Git operations and workflow visualization.

- Uses logging_monitoring for logging.
- Recommend calling environment_setup.env_checker.ensure_dependencies_installed() at app startup.
"""

import logging
import os
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

from codomyrmex.model_context_protocol.decorators import mcp_tool


class MermaidDiagramGenerator:
    """Generator for Mermaid diagrams with Git visualization capabilities."""

    def __init__(self):
        """Initialize the Mermaid diagram generator."""
        self.diagram_types = {
            "flowchart": self._create_flowchart,
            "gitgraph": self._create_gitgraph,
            "timeline": self._create_timeline,
            "graph": self._create_graph,
            "sequence": self._create_sequence,
            "class": self._create_class,
            "state": self._create_state,
            "pie": self._create_pie_chart,
            "journey": self._create_user_journey,
        }

    def create_git_branch_diagram(
        self,
        branches: list[dict[str, Any]],
        commits: list[dict[str, Any]],
        title: str = "Git Branch Diagram",
        output_path: str = None,
    ) -> str:
        """
        Create a Git branch diagram using Mermaid gitgraph syntax.

        Args:
            branches: List of branch information dictionaries
            commits: List of commit information dictionaries
            title: Title for the diagram
            output_path: Optional file path to save the diagram

        Returns:
            Mermaid diagram content as string
        """
        logger.debug(f"Creating Git branch diagram: {title}")

        mermaid_content = """gitGraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Feature start"

    branch feature/auth
    checkout feature/auth
    commit id: "Add auth logic"
    commit id: "Add tests"

    checkout develop
    merge feature/auth
    commit id: "Merge feature"

    checkout main
    merge develop
    commit id: "Release v1.0"
    tag v1.0.0
"""

        if branches and commits:
            # Build custom gitgraph from provided data
            mermaid_content = self._build_gitgraph_from_data(branches, commits, title)

        if output_path:
            self._save_mermaid_content(mermaid_content, output_path)

        logger.info(f"Git branch diagram '{title}' generated successfully")
        return mermaid_content

    def create_git_workflow_diagram(
        self,
        workflow_steps: list[dict[str, Any]] | None = None,
        title: str = "Git Workflow",
        output_path: str = None,
    ) -> str:
        """
        Create a Git workflow diagram using Mermaid flowchart syntax.

        Args:
            workflow_steps: List of workflow step dictionaries
            title: Title for the diagram
            output_path: Optional file path to save the diagram

        Returns:
            Mermaid diagram content as string
        """
        logger.debug(f"Creating Git workflow diagram: {title}")

        flowchart_content = ["flowchart TD"]
        flowchart_content.append("    Start([Start]) --> Clone[git clone]")
        flowchart_content.append("    Clone --> Branch[git checkout -b feature]")
        flowchart_content.append("    Branch --> Code[Write Code]")
        flowchart_content.append("    Code --> Add[git add .]")
        flowchart_content.append("    Add --> Commit[git commit -m 'message']")
        flowchart_content.append("    Commit --> Push[git push origin feature]")
        flowchart_content.append("    Push --> PR[Create Pull Request]")
        flowchart_content.append("    PR --> Review[Code Review]")
        flowchart_content.append("    Review --> Merge[Merge to main]")
        flowchart_content.append("    Merge --> End([End])")

        if workflow_steps:
            # Build custom workflow from provided data
            flowchart_content = self._build_workflow_from_data(workflow_steps, title)

        mermaid_content = "\n".join(flowchart_content)

        if output_path:
            self._save_mermaid_content(mermaid_content, output_path)

        logger.info(f"Git workflow diagram '{title}' generated successfully")
        return mermaid_content

    def create_repository_structure_diagram(
        self,
        repo_structure: dict[str, Any],
        title: str = "Repository Structure",
        output_path: str = None,
    ) -> str:
        """
        Create a repository structure diagram using Mermaid graph syntax.

        Args:
            repo_structure: Dictionary representing repository structure
            title: Title for the diagram
            output_path: Optional file path to save the diagram

        Returns:
            Mermaid diagram content as string
        """
        logger.debug(f"Creating repository structure diagram: {title}")

        graph_content = ["graph TD"]
        graph_content.append("    Root[📁 Repository Root] --> SRC[📁 src/]")
        graph_content.append("    Root --> Tests[📁 tests/]")
        graph_content.append("    Root --> Docs[📁 docs/]")
        graph_content.append("    Root --> Config[⚙️ config files]")
        graph_content.append("    SRC --> Modules[📁 modules/]")
        graph_content.append("    SRC --> Utils[📁 utils/]")
        graph_content.append("    Tests --> Unit[📁 unit/]")
        graph_content.append("    Tests --> Integration[📁 integration/]")

        if repo_structure:
            # Build custom structure from provided data
            graph_content = self._build_structure_from_data(repo_structure, title)

        mermaid_content = "\n".join(graph_content)

        if output_path:
            self._save_mermaid_content(mermaid_content, output_path)

        logger.info(f"Repository structure diagram '{title}' generated successfully")
        return mermaid_content

    def create_commit_timeline_diagram(
        self,
        commits: list[dict[str, Any]],
        title: str = "Commit Timeline",
        output_path: str = None,
    ) -> str:
        """
        Create a commit timeline diagram using Mermaid timeline syntax.

        Args:
            commits: List of commit information dictionaries
            title: Title for the diagram
            output_path: Optional file path to save the diagram

        Returns:
            Mermaid diagram content as string
        """
        logger.debug(f"Creating commit timeline diagram: {title}")

        timeline_content = ["timeline"]
        timeline_content.append(f"    title {title}")
        timeline_content.append("    2024-01-01 : Initial commit")
        timeline_content.append("    2024-01-05 : Add authentication")
        timeline_content.append("    2024-01-10 : Add database layer")
        timeline_content.append("    2024-01-15 : Add API endpoints")
        timeline_content.append("    2024-01-20 : Add tests")
        timeline_content.append("    2024-01-25 : Release v1.0.0")

        if commits:
            # Build custom timeline from provided commit data
            timeline_content = self._build_timeline_from_commits(commits, title)

        mermaid_content = "\n".join(timeline_content)

        if output_path:
            self._save_mermaid_content(mermaid_content, output_path)

        logger.info(f"Commit timeline diagram '{title}' generated successfully")
        return mermaid_content

    def _build_gitgraph_from_data(
        self, branches: list[dict[str, Any]], commits: list[dict[str, Any]], title: str
    ) -> str:
        """Build gitgraph from branch and commit data."""
        lines = ["gitGraph"]

        # Sort branches by creation order
        branches_sorted = sorted(branches, key=lambda x: x.get("created_at", ""))

        # Add initial commit
        lines.append('    commit id: "Initial"')

        for branch in branches_sorted:
            branch_name = branch.get("name", "unknown")
            if branch_name != "main" and branch_name != "master":
                lines.append(f"    branch {branch_name}")
                lines.append(f"    checkout {branch_name}")

                # Add commits for this branch
                branch_commits = [c for c in commits if c.get("branch") == branch_name]
                for commit in branch_commits[:3]:  # Limit to 3 commits per branch
                    commit_msg = commit.get("message", "Commit")[:20]
                    commit.get("hash", "unknown")[:7]
                    lines.append(f'    commit id: "{commit_msg}"')

                # Merge back if specified
                if branch.get("merged", False):
                    lines.append("    checkout main")
                    lines.append(f"    merge {branch_name}")

        return "\n".join(lines)

    def _build_workflow_from_data(
        self, workflow_steps: list[dict[str, Any]], title: str
    ) -> list[str]:
        """Build workflow flowchart from step data."""
        lines = ["flowchart TD"]

        prev_step = "Start([Start])"

        for i, step in enumerate(workflow_steps):
            step_name = step.get("name", f"Step{i}")
            step_type = step.get("type", "process")
            step_description = step.get("description", step_name)

            # Format step based on type
            if step_type == "decision":
                current_step = f"{step_name}{{{step_description}?}}"
            elif step_type == "terminal":
                current_step = f"{step_name}([{step_description}])"
            else:
                current_step = f"{step_name}[{step_description}]"

            lines.append(f"    {prev_step} --> {current_step}")
            prev_step = current_step

        return lines

    def _build_structure_from_data(
        self, repo_structure: dict[str, Any], title: str
    ) -> list[str]:
        """Build structure graph from repository data."""
        lines = ["graph TD"]

        def add_structure_nodes(
            parent_id: str, parent_name: str, structure: dict[str, Any], level: int = 0
        ):
            """Recursively add nodes for directory structure."""
            if isinstance(structure, dict):
                for name, content in structure.items():
                    node_id = f"{parent_id}_{name}".replace(" ", "_").replace(".", "_")

                    if isinstance(content, dict):
                        # Directory
                        icon = "📁" if level < 2 else "📂"
                        lines.append(f"    {parent_id} --> {node_id}[{icon} {name}]")
                        add_structure_nodes(node_id, name, content, level + 1)
                    else:
                        # File
                        icon = self._get_file_icon(name)
                        lines.append(f"    {parent_id} --> {node_id}[{icon} {name}]")

        root_id = "Root"
        lines.append(f"    {root_id}[📁 {title}]")
        add_structure_nodes(root_id, title, repo_structure)

        return lines

    def _build_timeline_from_commits(
        self, commits: list[dict[str, Any]], title: str
    ) -> list[str]:
        """Build timeline from commit data."""
        lines = ["timeline"]
        lines.append(f"    title {title}")

        # Sort commits by date
        commits_sorted = sorted(commits, key=lambda x: x.get("date", ""))

        for commit in commits_sorted[:10]:  # Limit to 10 commits
            date = commit.get("date", "2024-01-01")[:10]  # Get date part only
            message = commit.get("message", "Commit")[:30]  # Truncate long messages
            hash_short = commit.get("hash", "unknown")[:7]

            lines.append(f"    {date} : {message} ({hash_short})")

        return lines

    def _get_file_icon(self, filename: str) -> str:
        """Get appropriate icon for file type."""
        extension = filename.split(".")[-1].lower() if "." in filename else ""

        icons = {
            "py": "🐍",
            "js": "📜",
            "ts": "📘",
            "json": "📋",
            "md": "📝",
            "yml": "⚙️",
            "yaml": "⚙️",
            "txt": "📄",
            "git": "🔧",
            "sh": "⚡",
        }

        return icons.get(extension, "📄")

    def _create_flowchart(self, **kwargs) -> str:
        """Create a generic flowchart."""
        return "flowchart TD\n    A[Start] --> B[Process] --> C[End]"

    def _create_gitgraph(self, **kwargs) -> str:
        """Create a generic gitgraph."""
        return (
            "gitGraph\n    commit\n    branch develop\n    checkout develop\n    commit"
        )

    def _create_timeline(self, **kwargs) -> str:
        """Create a generic timeline."""
        return "timeline\n    title Timeline\n    2024 : Event 1\n    2024 : Event 2"

    def _create_graph(self, **kwargs) -> str:
        """Create a generic graph."""
        return "graph TD\n    A --> B\n    B --> C"

    def _create_sequence(self, **kwargs) -> str:
        """Create a generic sequence diagram."""
        return "sequenceDiagram\n    A->>B: Message\n    B-->>A: Response"

    def _create_class(self, **kwargs) -> str:
        """Create a generic class diagram."""
        return "classDiagram\n    class Class1{\n        +method()\n    }"

    def _create_state(self, **kwargs) -> str:
        """Create a generic state diagram."""
        return "stateDiagram\n    [*] --> State1\n    State1 --> [*]"

    def _create_pie_chart(self, **kwargs) -> str:
        """Create a generic pie chart."""
        return 'pie title Data\n    "A" : 40\n    "B" : 60'

    def _create_user_journey(self, **kwargs) -> str:
        """Create a generic user journey."""
        return "journey\n    title User Journey\n    section Journey\n        Step1: 5: User"

    def _save_mermaid_content(self, content: str, output_path: str) -> bool:
        """Save Mermaid content to file."""
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Mermaid diagram saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving Mermaid content to {output_path}: {e}")
            return False


# Convenience functions for easy import
@mcp_tool()
def create_git_branch_diagram(
    branches: list[dict[str, Any]] = None,
    commits: list[dict[str, Any]] = None,
    title: str = "Git Branch Diagram",
    output_path: str = None,
) -> str:
    """Create a Git branch diagram using Mermaid syntax."""
    generator = MermaidDiagramGenerator()
    return generator.create_git_branch_diagram(branches, commits, title, output_path)


@mcp_tool()
def create_git_workflow_diagram(
    workflow_steps: list[dict[str, Any]] = None,
    title: str = "Git Workflow",
    output_path: str = None,
) -> str:
    """Create a Git workflow diagram using Mermaid syntax."""
    generator = MermaidDiagramGenerator()
    return generator.create_git_workflow_diagram(workflow_steps, title, output_path)


@mcp_tool()
def create_repository_structure_diagram(
    repo_structure: dict[str, Any] = None,
    title: str = "Repository Structure",
    output_path: str = None,
) -> str:
    """Create a repository structure diagram using Mermaid syntax."""
    generator = MermaidDiagramGenerator()
    return generator.create_repository_structure_diagram(
        repo_structure, title, output_path
    )


@mcp_tool()
def create_commit_timeline_diagram(
    commits: list[dict[str, Any]] = None,
    title: str = "Commit Timeline",
    output_path: str = None,
) -> str:
    """Create a commit timeline diagram using Mermaid syntax."""
    generator = MermaidDiagramGenerator()
    return generator.create_commit_timeline_diagram(commits, title, output_path)


if __name__ == "__main__":
    # Test the Mermaid generator
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output" / "mermaid_examples"
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("--- Testing Mermaid Diagram Generation ---")

    # Test Git branch diagram
    sample_branches = [
        {"name": "main", "created_at": "2024-01-01"},
        {"name": "develop", "created_at": "2024-01-02"},
        {"name": "feature/auth", "created_at": "2024-01-03", "merged": True},
    ]

    sample_commits = [
        {
            "hash": "a1b2c3d",
            "message": "Initial commit",
            "branch": "main",
            "date": "2024-01-01",
        },
        {
            "hash": "e4f5g6h",
            "message": "Add authentication",
            "branch": "feature/auth",
            "date": "2024-01-03",
        },
        {
            "hash": "i7j8k9l",
            "message": "Fix auth bug",
            "branch": "feature/auth",
            "date": "2024-01-04",
        },
    ]

    git_diagram = create_git_branch_diagram(
        branches=sample_branches,
        commits=sample_commits,
        title="Sample Git Workflow",
        output_path=str(output_dir / "git_branch_diagram.mmd"),
    )

    # Test workflow diagram
    workflow_steps = [
        {"name": "Start", "type": "terminal", "description": "Start Development"},
        {"name": "Clone", "type": "process", "description": "git clone repository"},
        {"name": "Branch", "type": "process", "description": "create feature branch"},
        {"name": "Code", "type": "process", "description": "write code"},
        {"name": "Test", "type": "decision", "description": "tests pass"},
        {"name": "Commit", "type": "process", "description": "commit changes"},
        {"name": "Push", "type": "process", "description": "push to remote"},
        {"name": "End", "type": "terminal", "description": "Complete"},
    ]

    workflow_diagram = create_git_workflow_diagram(
        workflow_steps=workflow_steps,
        title="Git Development Workflow",
        output_path=str(output_dir / "git_workflow_diagram.mmd"),
    )

    # Test structure diagram
    repo_structure = {
        "src": {
            "codomyrmex": {
                "data_visualization": {"__init__.py": "module", "plotter.py": "module"},
                "git_operations": {"__init__.py": "module", "git_manager.py": "module"},
            }
        },
        "tests": {"unit": {}, "integration": {}},
        "docs": {"README.md": "file"},
    }

    structure_diagram = create_repository_structure_diagram(
        repo_structure=repo_structure,
        title="Codomyrmex Project Structure",
        output_path=str(output_dir / "repo_structure_diagram.mmd"),
    )

    # Test timeline diagram
    timeline_diagram = create_commit_timeline_diagram(
        commits=sample_commits,
        title="Development Timeline",
        output_path=str(output_dir / "commit_timeline_diagram.mmd"),
    )

    logger.info(f"Mermaid diagram examples generated in {output_dir}")

    # Basic logging setup if running standalone
    if not logger.hasHandlers():
        import logging
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            "Basic logging configured for direct script execution of mermaid_generator.py."
        )

