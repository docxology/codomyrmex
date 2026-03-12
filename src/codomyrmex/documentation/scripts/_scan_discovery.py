"""Phase 1: Discovery and Inventory for Documentation Scan."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class DocumentationDiscoveryMixin:
    """Phase 1: Discovery and Inventory"""

    repo_root: "Path"
    results: "dict[str, Any]"

    def phase1_discovery(self):
        """Phase 1: Discovery and Inventory"""
        print("=" * 80)
        print("PHASE 1: DISCOVERY AND INVENTORY")
        print("=" * 80)
        print()

        # 1.1 File Discovery
        print("1.1 Scanning all markdown files...")
        all_md_files = list(self.repo_root.rglob("*.md"))
        agents_files = list(self.repo_root.rglob("AGENTS.md"))
        readme_files = list(self.repo_root.rglob("README.md"))

        self.results["phase1"]["files_found"] = {
            "total_markdown": len(all_md_files),
            "agents_files": len(agents_files),
            "readme_files": len(readme_files),
            "all_md_paths": [str(f.relative_to(self.repo_root)) for f in all_md_files],
            "agents_paths": [str(f.relative_to(self.repo_root)) for f in agents_files],
            "readme_paths": [str(f.relative_to(self.repo_root)) for f in readme_files],
        }

        print(f"  ✓ Found {len(all_md_files)} markdown files")
        print(f"  ✓ Found {len(agents_files)} AGENTS.md files")
        print(f"  ✓ Found {len(readme_files)} README.md files")
        print()

        # Identify configuration files
        print("1.1 Identifying configuration files...")
        config_files = []
        config_patterns = [
            "pyproject.toml",
            "pytest.ini",
            "Makefile",
            "package.json",
            "setup.py",
            "requirements.txt",
            "*.yaml",
            "*.yml",
            "*.json",
        ]

        for pattern in config_patterns:
            if "*" in pattern:
                config_files.extend(self.repo_root.rglob(pattern))
            else:
                config_path = self.repo_root / pattern
                if config_path.exists():
                    config_files.append(config_path)

        self.results["phase1"]["files_found"]["config_files"] = [  # type: ignore
            str(f.relative_to(self.repo_root)) for f in config_files
        ]
        print(f"  ✓ Found {len(config_files)} configuration files")
        print()

        # 1.2 Structure Mapping
        print("1.2 Mapping documentation structure...")
        structure = self._map_documentation_structure()
        self.results["phase1"]["structure_map"] = structure
        print(f"  ✓ Mapped {len(structure['categories'])} documentation categories")
        print()

        # 1.3 Existing Tools Inventory
        print("1.3 Cataloging existing validation tools...")
        tools = self._inventory_validation_tools()
        self.results["phase1"]["tools_inventory"] = tools
        print(f"  ✓ Found {len(tools['existing_tools'])} existing validation tools")
        print()

        print("✓ Phase 1 complete!")
        print()
        return self.results["phase1"]

    def _map_documentation_structure(self) -> dict:
        """Map the documentation hierarchy and categories."""
        structure = {
            "root_level": [],
            "directory_level": [],
            "categories": {
                "project_docs": [],
                "module_docs": [],
                "script_docs": [],
                "testing_docs": [],
                "tool_docs": [],
            },
            "hierarchy": {},
        }

        # Root level docs
        root_docs = ["README.md", "AGENTS.md", "LICENSE", "SECURITY.md"]
        for doc in root_docs:
            if (self.repo_root / doc).exists():
                structure["root_level"].append(doc)

        # Category mapping
        categories_map = {
            "project_docs": self.repo_root / "docs",
            "module_docs": self.repo_root / "src" / "codomyrmex",
            "script_docs": self.repo_root / "scripts",
            "testing_docs": self.repo_root / "testing",
            "tool_docs": self.repo_root / "tools",
        }

        for category, base_path in categories_map.items():
            if base_path.exists():
                md_files = list(base_path.rglob("*.md"))
                structure["categories"][category] = [
                    str(f.relative_to(self.repo_root)) for f in md_files
                ]

        return structure

    def _inventory_validation_tools(self) -> dict:
        """Inventory existing validation and documentation tools."""
        tools = {"existing_tools": [], "capabilities": {}, "gaps": []}

        tool_paths = {
            "comprehensive_audit": "scripts/documentation/comprehensive_audit.py",
            "module_docs_auditor": "scripts/documentation/module_docs_auditor.py",
            "check_doc_links": "scripts/documentation/check_doc_links.py",
            "validate_module_docs": "scripts/documentation/validate_module_docs.py",
            "validate_docs_quality": "src/codomyrmex/documentation/scripts/validate_docs_quality.py",
        }

        for tool_name, tool_path in tool_paths.items():
            full_path = self.repo_root / tool_path
            if full_path.exists():
                tools["existing_tools"].append(
                    {"name": tool_name, "path": tool_path, "exists": True}
                )
            else:
                tools["gaps"].append(f"Missing tool: {tool_path}")

        return tools
