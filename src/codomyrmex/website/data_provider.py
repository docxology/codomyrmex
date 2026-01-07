import os
from typing import Any, Dict, List
from pathlib import Path

class DataProvider:
    """
    Aggregates data from various system modules to populate the website.
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir

    def get_system_summary(self) -> Dict[str, Any]:
        """Returns high-level system metrics."""
        return {
            "status": "Operational",
            "version": "0.1.0",
            "environment": os.getenv("CODOMYRMEX_ENV", "Development"),
            "module_count": len(self.get_modules()),
            "agent_count": len(self.get_actual_agents()),
            "last_build": "N/A"  # Placeholder
        }

    def get_modules(self) -> List[Dict[str, Any]]:
        """
        Scans the `src/codomyrmex` directory for all modules (packages).
        This returns all Codomyrmex packages, not agents.
        """
        modules = []
        src_path = self.root_dir / "src/codomyrmex"
        
        if not src_path.exists():
            return []

        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                modules.append({
                    "name": item.name,
                    "status": "Active",
                    "path": str(item.relative_to(self.root_dir)),
                    "description": self._get_description(item),
                    "submodules": self._get_submodules(item)
                })
        
        return sorted(modules, key=lambda x: x["name"])

    def _get_submodules(self, module_path: Path) -> List[Dict[str, Any]]:
        """Get submodules of a module for hierarchical navigation."""
        submodules = []
        for item in module_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                submodules.append({
                    "name": item.name,
                    "path": str(item.relative_to(self.root_dir)),
                    "description": self._get_description(item)
                })
        return sorted(submodules, key=lambda x: x["name"])

    def get_actual_agents(self) -> List[Dict[str, Any]]:
        """
        Returns actual AI agent integrations from `src/codomyrmex/agents/`.
        These are the real agent frameworks (jules, claude, codex, etc.).
        """
        agents = []
        agents_path = self.root_dir / "src/codomyrmex/agents"
        
        if not agents_path.exists():
            return []

        # Known agent integration directories
        for item in agents_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                # Skip non-agent directories like 'tests'
                if item.name in ["tests", "__pycache__"]:
                    continue
                agents.append({
                    "name": item.name,
                    "status": "Available",
                    "path": str(item.relative_to(self.root_dir)),
                    "description": self._get_description(item),
                    "type": self._get_agent_type(item.name)
                })
        
        return sorted(agents, key=lambda x: x["name"])

    def _get_agent_type(self, agent_name: str) -> str:
        """Categorize agent by type."""
        cli_agents = ["jules", "opencode", "gemini", "mistral_vibe", "droid"]
        api_agents = ["claude", "codex"]
        framework_agents = ["generic", "theory", "every_code", "ai_code_editing"]
        
        if agent_name in cli_agents:
            return "CLI Integration"
        elif agent_name in api_agents:
            return "API Integration"
        elif agent_name in framework_agents:
            return "Framework"
        return "Agent"

    def get_agents_status(self) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Use get_modules() instead.
        Kept for backwards compatibility.
        """
        return self.get_modules()

    def _count_agents(self) -> int:
        return len(self.get_actual_agents())

    
    def get_available_scripts(self) -> List[Dict[str, Any]]:
        """
        Scans the `scripts` directory for executable scripts.
        """
        scripts = []
        scripts_dir = self.root_dir / "scripts"
        
        if not scripts_dir.exists():
            return []
            
        # Recursive search for .py files
        for path in scripts_dir.rglob("*.py"):
            # Skip hidden files, __init__.py, and output directories
            if path.name.startswith(("_", ".")) or "output" in path.parts:
                continue
                
            rel_path = path.relative_to(scripts_dir)
            
            scripts.append({
                "name": str(rel_path),
                "path": str(rel_path),
                "full_path": str(path),
                "description": self._get_script_docstring(path)
            })
            
        return sorted(scripts, key=lambda x: x["name"])

    def _get_description(self, path: Path) -> str:
        """Extracts description from __init__.py docstring."""
        init_file = path / "__init__.py"
        if init_file.exists():
            try:
                content = init_file.read_text(encoding="utf-8")
                # Very basic parsing
                if '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end != -1:
                        return content[start:end].strip()
            except Exception:
                pass
        return "No description available"

    def _get_script_docstring(self, script_path: Path) -> str:
        """Extracts the docstring from a python script."""
        try:
            content = script_path.read_text(encoding="utf-8")
            # Very basic parsing
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end != -1:
                    return content[start:end].strip()
            if "'''" in content:
                start = content.find("'''") + 3
                end = content.find("'''", start)
                if end != -1:
                    return content[start:end].strip()
        except Exception:
            pass
        return "No description available"

    def _get_description_from_markdown(self, agent_dir: Path) -> str:
        """Attempts to read the description from AGENTS.md or README.md."""
        for filename in ["AGENTS.md", "README.md"]:
            file_path = agent_dir / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    # Simple markdown extraction: find first non-empty line that isn't a header
                    lines = content.splitlines()
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            return line if len(line) < 100 else line[:97] + "..."
                    return "Documented" 
                except Exception:
                    continue
        return "No description available"


    def get_config_files(self) -> List[Dict[str, str]]:
        """Scans for configuration files."""
        configs = []
        # Look for typical config files in root
        patterns = ["*.toml", "*.yaml", "*.yml", "*.json", "requirements.txt"]
        
        for pattern in patterns:
            for path in self.root_dir.glob(pattern):
                if path.is_file():
                    configs.append({
                        "name": path.name,
                        "path": path.name, # Relative to root
                        "type": path.suffix.lstrip(".")
                    })
        
        # Also look in config/ dir if it exists
        config_dir = self.root_dir / "config"
        if config_dir.exists():
             for pattern in patterns:
                for path in config_dir.glob(pattern):
                    if path.is_file():
                         configs.append({
                            "name": f"config/{path.name}",
                            "path": str(path.relative_to(self.root_dir)),
                            "type": path.suffix.lstrip(".")
                        })
                        
        return sorted(configs, key=lambda x: x["name"])

    def get_config_content(self, filename: str) -> str:
        """Reads content of a config file."""
        # Security: prevent traversal
        if ".." in filename or filename.startswith("/"):
             raise ValueError("Invalid filename")
             
        file_path = self.root_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
            
        return file_path.read_text(encoding="utf-8")

    def save_config_content(self, filename: str, content: str) -> None:
        """Saves content to a config file."""
        # Security: prevent traversal
        if ".." in filename or filename.startswith("/"):
             raise ValueError("Invalid filename")
             
        file_path = self.root_dir / filename
        
        # Only allow updating existing files for safety in MVP? 
        # Or allow creating known config types?
        # Let's simple check it's in the allowed list from get_config_files roughly
        # For now, just write.
        
        file_path.write_text(content, encoding="utf-8")

    def get_doc_tree(self) -> Dict[str, Any]:
        """Builds a tree of documentation files."""
        docs_root = self.root_dir / "docs"
        src_root = self.root_dir / "src"
        
        tree = {"name": "Documentation", "children": []}
        
        # Add docs/ folder
        if docs_root.exists():
            tree["children"].append(self._scan_directory_for_docs(docs_root))
            
        # Add src/ READMEs
        src_docs = {"name": "Modules", "children": []}
        if src_root.exists():
             for path in src_root.rglob("README.md"):
                  src_docs["children"].append({
                      "name": str(path.relative_to(src_root).parent),
                      "path": str(path.relative_to(self.root_dir)),
                      "type": "file"
                  })
        if src_docs["children"]:
            tree["children"].append(src_docs)
            
        return tree

    def _scan_directory_for_docs(self, path: Path) -> Dict[str, Any]:
        node = {"name": path.name, "children": []}
        
        # Files first, then dirs
        for item in sorted(path.iterdir()):
            if item.name.startswith("."): continue
            
            if item.is_file() and item.suffix == ".md":
                node["children"].append({
                     "name": item.name,
                     "path": str(item.relative_to(self.root_dir)),
                     "type": "file"
                })
            elif item.is_dir():
                child_node = self._scan_directory_for_docs(item)
                # Only add if it has content
                if child_node["children"]:
                    node["children"].append(child_node)
                    
        return node
        
    def get_pipeline_status(self) -> List[Dict[str, Any]]:
        """
        Retrieves CI/CD pipeline status.
        Currently mocks data until state persistence is implemented.
        """
        # Feature: Integration with actual state would go here.
        # For now, we return a simulated list of recent pipelines.
        return [
            {
                "id": "pl-1024",
                "name": "Build & Test",
                "status": "success",
                "started_at": "2026-01-07T08:00:00Z",
                "duration": "4m 20s",
                "stages": [
                    {"name": "Lint", "status": "success"},
                    {"name": "Test", "status": "success"},
                    {"name": "Build", "status": "success"}
                ]
            },
             {
                "id": "pl-1025",
                "name": "Deploy Staging",
                "status": "running",
                "started_at": "2026-01-07T09:15:00Z",
                "duration": "1m 15s",
                "stages": [
                    {"name": "Build", "status": "success"},
                    {"name": "Deploy", "status": "running"},
                    {"name": "verify", "status": "pending"}
                ]
            }
        ]

