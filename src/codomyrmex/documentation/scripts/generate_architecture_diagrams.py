from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import argparse
import json
import logging
import os
import re
import sys

from dataclasses import dataclass, field

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.logger_config import get_logger








































"""
except ImportError:
    logger = logging.getLogger(__name__)


@dataclass
class ModuleInfo:
    """



    #!/usr/bin/env python3
    """

Architecture Diagram Generation Tool

This script generates Mermaid diagrams for Codomyrmex architecture visualization,
including module dependency graphs, workflow diagrams, and system architecture.
"""


# Add project root to path
SCRIPT_DIR = Path(__file__).parent.parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

try:


logger = get_logger(__name__)

Information about a module."""
    name: str
    path: str
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    category: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "dependencies": self.dependencies,
            "description": self.description,
            "category": self.category
        }


@dataclass
class WorkflowStep:
    """Represents a step in a workflow."""
    name: str
    module: str
    action: str
    dependencies: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "module": self.module,
            "action": self.action,
            "dependencies": self.dependencies,
            "description": self.description
        }


class ArchitectureDiagramGenerator:
    """
    Generates Mermaid diagrams for Codomyrmex architecture visualization.

    Creates various types of diagrams including dependency graphs,
    workflow diagrams, and system architecture diagrams.
    """

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize the diagram generator.

            project_root: Root path of the project
        """
        self.project_root = Path(project_root or SCRIPT_DIR)
        self.src_path = self.project_root / "src" / "codomyrmex"

        # Define module categories
        self.module_categories = {
            "foundation": ["logging_monitoring", "environment_setup", "model_context_protocol", "terminal_interface"],
            "core": ["ai_code_editing", "static_analysis", "code_execution_sandbox", "data_visualization",
                    "pattern_matching", "git_operations", "code_review", "security_audit",
                    "ollama_integration", "language_models"],
            "service": ["build_synthesis", "documentation", "api_documentation", "ci_cd_automation",
                       "containerization", "config_management", "database_management",
                       "project_orchestration", "physical_management"],
            "specialized": ["system_discovery", "module_template", "modeling_3d"]
        }

    def generate_module_diagram(self, module_name: str) -> str:
        """
        Generate a diagram for a specific module's internal structure.

            module_name: Name of the module

        Returns:
            Mermaid diagram string
        """
        module_path = self.src_path / module_name
        if not module_path.exists():
            return f"graph TD\n    A[\"Module '{module_name}' not found\"]"

        # Analyze module structure
        files = []
        for file_path in module_path.rglob("*.py"):
            if not file_path.name.startswith('_'):
                rel_path = file_path.relative_to(module_path)
                files.append(str(rel_path))

        # Create simple module structure diagram
        lines = ["graph TD"]

        # Add main module node
        lines.append(f"    {module_name}[\"{module_name}<br/>Module\"]")

        # Add file nodes
        for i, file in enumerate(files[:10]):  # Limit to 10 files
            file_id = f"file_{i}"
            file_name = Path(file).stem
            lines.append(f"    {file_id}[\"{file_name}.py\"]")
            lines.append(f"    {module_name} --> {file_id}")

        if len(files) > 10:
            lines.append(f"    more[\"... and {len(files) - 10} more files\"]")
            lines.append(f"    {module_name} --> more")

        return "\n".join(lines)

    def generate_dependency_graph(self) -> str:
        """
        Generate a dependency graph for all modules.

        Returns:
            Mermaid diagram string
        """
        modules = self._analyze_module_dependencies()

        lines = ["graph TD"]

        # Group modules by category
        for category, category_modules in self.module_categories.items():
            # Add subgraph for category
            category_modules_present = [m for m in category_modules if m in modules]

            if category_modules_present:
                lines.append(f"    subgraph {category} [\"{category.title()} Layer\"]")

                for module_name in category_modules_present:
                    module_info = modules.get(module_name)
                    if module_info:
                        # Clean module name for Mermaid
                        clean_name = module_name.replace('_', '')
                        description = module_info.description[:30] + "..." if len(module_info.description) > 30 else module_info.description
                        lines.append(f"        {clean_name}[\"{module_name}<br/>{description}\"]")

                lines.append("    end")
                lines.append("")

        # Add dependency edges
        added_edges = set()
        for module_name, module_info in modules.items():
            clean_source = module_name.replace('_', '')

            for dep in module_info.dependencies:
                if dep in modules:
                    clean_target = dep.replace('_', '')
                    edge_key = (clean_source, clean_target)

                    if edge_key not in added_edges:
                        lines.append(f"    {clean_source} --> {clean_target}")
                        added_edges.add(edge_key)

        return "\n".join(lines)

    def generate_workflow_diagram(self, workflow: Dict[str, Any]) -> str:
        """
        Generate a diagram for a workflow.

            workflow: Workflow definition dictionary

        Returns:
            Mermaid diagram string
        """
        lines = ["graph TD"]

        # Extract tasks from workflow
        tasks = workflow.get("tasks", [])

        # Add task nodes
        for task in tasks:
            task_name = task["name"]
            module = task.get("module", "")
            action = task.get("action", "")

            # Create clean IDs
            task_id = task_name.replace(' ', '_').replace('-', '_')

            label = f"{task_name}<br/>{module}:{action}"
            lines.append(f"    {task_id}[\"{label}\"]")

        # Add dependency edges
        for task in tasks:
            task_name = task["name"]
            task_id = task_name.replace(' ', '_').replace('-', '_')
            dependencies = task.get("dependencies", [])

            for dep in dependencies:
                dep_id = dep.replace(' ', '_').replace('-', '_')
                lines.append(f"    {dep_id} --> {task_id}")

        return "\n".join(lines)

    def generate_system_architecture(self) -> str:
        """
        Generate a high-level system architecture diagram.

        Returns:
            Mermaid diagram string
        """
        lines = ["graph TB"]

        # Define main components
        lines.append("    User[\"👤 User\"]")
        lines.append("    CLI[\"💻 CLI Interface\"]")
        lines.append("    API[\"🔌 REST/GraphQL API\"]")
        lines.append("    Orchestrator[\"🎯 Project Orchestrator\"]")
        lines.append("    Modules[\"📦 Codomyrmex Modules\"]")
        lines.append("    Storage[\"💾 Configuration & Results\"]")
        lines.append("    External[\"🌐 External Services\"]")

        # Add connections
        lines.append("    User --> CLI")
        lines.append("    User --> API")
        lines.append("    CLI --> Orchestrator")
        lines.append("    API --> Orchestrator")
        lines.append("    Orchestrator --> Modules")
        lines.append("    Modules --> Storage")
        lines.append("    Modules --> External")

        # Add sub-components for modules
        lines.append("")
        lines.append("    subgraph modules [\"Codomyrmex Modules\"]")
        lines.append("        Foundation[\"🏗️ Foundation<br/>Logging, Environment, MCP\"]")
        lines.append("        Core[\"⚙️ Core<br/>AI, Analysis, Security\"]")
        lines.append("        Service[\"🔧 Service<br/>Build, CI/CD, Container\"]")
        lines.append("        Specialized[\"🎨 Specialized<br/>3D, Discovery, Templates\"]")
        lines.append("    end")

        lines.append("    Modules --> Foundation")
        lines.append("    Modules --> Core")
        lines.append("    Modules --> Service")
        lines.append("    Modules --> Specialized")

        return "\n".join(lines)

    def add_diagrams_to_readme(self, readme_path: str, diagrams: Dict[str, str]) -> None:
        """
        Add generated diagrams to a README file.

            readme_path: Path to the README file
            diagrams: Dictionary mapping diagram names to diagram content
        """
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find or create Architecture section
            architecture_pattern = r'(?i)^## Architecture'
            architecture_match = re.search(architecture_pattern, content, re.MULTILINE)

            diagram_section = "\n### Architecture Diagrams\n\n"

            for name, diagram in diagrams.items():
                diagram_section += f"#### {name.replace('_', ' ').title()}\n\n"
                diagram_section += "```mermaid\n"
                diagram_section += diagram
                diagram_section += "\n```\n\n"

            if architecture_match:
                # Insert after Architecture section
                insert_pos = architecture_match.end()
                content = content[:insert_pos] + diagram_section + content[insert_pos:]
            else:
                # Add at the end
                content += "\n## Architecture\n" + diagram_section

            # Write back
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Added architecture diagrams to {readme_path}")

        except Exception as e:
            logger.error(f"Error adding diagrams to README: {e}")

    def _analyze_module_dependencies(self) -> Dict[str, ModuleInfo]:
        """Analyze dependencies between modules."""
        modules = {}

        # Get all module directories
        if not self.src_path.exists():
            return modules

        for module_path in self.src_path.iterdir():
            if module_path.is_dir() and not module_path.name.startswith('_'):
                module_name = module_path.name
                module_info = ModuleInfo(
                    name=module_name,
                    path=str(module_path),
                    category=self._get_module_category(module_name)
                )

                # Try to read description from README
                readme_path = module_path / "README.md"
                if readme_path.exists():
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract first paragraph as description
                            paragraphs = content.split('\n\n')
                            for para in paragraphs:
                                if para.strip() and not para.startswith('#'):
                                    module_info.description = para.strip()[:100]
                                    break
                    except Exception:
                        pass

                # Analyze imports to determine dependencies
                module_info.dependencies = self._analyze_module_imports(module_path)

                modules[module_name] = module_info

        return modules

    def _get_module_category(self, module_name: str) -> str:
        """Get the category for a module."""
        for category, category_modules in self.module_categories.items():
            if module_name in category_modules:
                return category
        return "unknown"

    def _analyze_module_imports(self, module_path: Path) -> List[str]:
        """Analyze imports in a module to determine dependencies."""
        dependencies = set()

        # Look for Python files
        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Find imports from other codomyrmex modules
                import_patterns = [
                    r'from codomyrmex\.([a-zA-Z_]+)',
                    r'import codomyrmex\.([a-zA-Z_]+)'
                ]

                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match != module_path.name:  # Don't depend on self
                            dependencies.add(match)

            except Exception:
                continue

        return list(dependencies)


def generate_module_diagram(module_name: str) -> str:
    """
    Convenience function to generate a module diagram.

        module_name: Name of the module

    Returns:
        Mermaid diagram string
    """
    generator = ArchitectureDiagramGenerator()
    return generator.generate_module_diagram(module_name)


def generate_dependency_graph() -> str:
    """
    Convenience function to generate a dependency graph.

    Returns:
        Mermaid diagram string
    """
    generator = ArchitectureDiagramGenerator()
    return generator.generate_dependency_graph()


def generate_workflow_diagram(workflow: Dict[str, Any]) -> str:
    """
    Convenience function to generate a workflow diagram.

        workflow: Workflow definition

    Returns:
        Mermaid diagram string
    """
    generator = ArchitectureDiagramGenerator()
    return generator.generate_workflow_diagram(workflow)


def generate_system_architecture() -> str:
    """
    Convenience function to generate system architecture diagram.

    Returns:
        Mermaid diagram string
    """
    generator = ArchitectureDiagramGenerator()
    return generator.generate_system_architecture()


def add_diagrams_to_readme(readme_path: str, diagrams: Dict[str, str]) -> None:
    """
    Convenience function to add diagrams to README.

        readme_path: Path to README file
        diagrams: Dictionary of diagram names to content
    """
    generator = ArchitectureDiagramGenerator()
    generator.add_diagrams_to_readme(readme_path, diagrams)


def main():
    """Main CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Generate architecture diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --module logging_monitoring
  %(prog)s --dependency-graph
  %(prog)s --system-architecture
  %(prog)s --workflow workflow.json
  %(prog)s --add-to-readme docs/README.md
        """
    )

    parser.add_argument(
        '--module', '-m',
        help='Generate diagram for a specific module'
    )

    parser.add_argument(
        '--dependency-graph',
        action='store_true',
        help='Generate module dependency graph'
    )

    parser.add_argument(
        '--system-architecture',
        action='store_true',
        help='Generate system architecture diagram'
    )

    parser.add_argument(
        '--workflow',
        help='Path to workflow JSON file to diagram'
    )

    parser.add_argument(
        '--add-to-readme',
        help='Add generated diagrams to specified README file'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file for diagram (default: stdout)'
    )

    args = parser.parse_args()

    generator = ArchitectureDiagramGenerator()
    diagrams = {}

    try:
        if args.module:
            print(f"🔍 Generating diagram for module: {args.module}")
            diagram = generator.generate_module_diagram(args.module)
            diagrams[f"{args.module}_module"] = diagram

        if args.dependency_graph:
            print("🔗 Generating dependency graph...")
            diagram = generator.generate_dependency_graph()
            diagrams["dependency_graph"] = diagram

        if args.system_architecture:
            print("🏗️ Generating system architecture...")
            diagram = generator.generate_system_architecture()
            diagrams["system_architecture"] = diagram

        if args.workflow:
            print(f"📋 Generating workflow diagram from {args.workflow}...")
            try:
                with open(args.workflow, 'r') as f:
                    workflow = json.load(f)
                diagram = generator.generate_workflow_diagram(workflow)
                diagrams["workflow_diagram"] = diagram
            except Exception as e:
                print(f"❌ Error reading workflow file: {e}")
                return 1

        # Output or add to README
        if diagrams:
            if args.add_to_readme:
                print(f"📝 Adding diagrams to README: {args.add_to_readme}")
                generator.add_diagrams_to_readme(args.add_to_readme, diagrams)
                print("✅ Diagrams added to README")
            elif args.output:
                # Save all diagrams to output file
                with open(args.output, 'w') as f:
                    for name, diagram in diagrams.items():
                        f.write(f"## {name.replace('_', ' ').title()}\n\n")
                        f.write("```mermaid\n")
                        f.write(diagram)
                        f.write("\n```\n\n")
                print(f"✅ Diagrams saved to {args.output}")
            else:
                # Print to stdout
                for name, diagram in diagrams.items():
                    print(f"## {name.replace('_', ' ').title()}")
                    print("")
                    print("```mermaid")
                    print(diagram)
                    print("```")
                    print("")
        else:
            print("❌ No diagrams generated. Use --help for options.")
            return 1

    except Exception as e:
        logger.error(f"Error generating diagrams: {e}")
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
