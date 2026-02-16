"""
MCP Tool Discovery Module

Provides mechanisms for automatically discovering and registering MCP tools
from modules, files, and external servers.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set
from pathlib import Path
import importlib
import importlib.util
import json
import ast

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class DiscoveredTool:
    """Represents a discovered MCP tool."""
    name: str
    description: str
    source: str  # "module", "file", "external"
    source_path: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ModuleScanner:
    """
    Scans Python modules for MCP tool definitions.
    
    Looks for:
    - Functions decorated with @tool
    - Classes that inherit from Tool
    - MCP_TOOLS dictionaries
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()
        self._discovered: List[DiscoveredTool] = []
    
    def scan_module(self, module_path: str) -> List[DiscoveredTool]:
        """Scan a Python module for tools."""
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            logger.warning(f"Could not import module {module_path}: {e}")
            return []
        
        tools = []
        
        # Look for MCP_TOOLS dict
        if hasattr(module, "MCP_TOOLS"):
            mcp_tools = getattr(module, "MCP_TOOLS")
            if isinstance(mcp_tools, dict):
                for name, spec in mcp_tools.items():
                    tools.append(DiscoveredTool(
                        name=name,
                        description=spec.get("description", ""),
                        source="module",
                        source_path=module_path,
                        input_schema=self._build_schema(spec.get("parameters", {})),
                    ))
        
        # Look for decorated functions
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and hasattr(attr, "_mcp_tool"):
                tool_meta = attr._mcp_tool
                tools.append(DiscoveredTool(
                    name=tool_meta.get("name", attr_name),
                    description=tool_meta.get("description", attr.__doc__ or ""),
                    source="module",
                    source_path=module_path,
                    input_schema=tool_meta.get("schema", {}),
                    handler=attr,
                ))
        
        self._discovered.extend(tools)
        return tools
    
    def scan_directory(
        self,
        directory: Path,
        pattern: str = "*.py",
        recursive: bool = True,
    ) -> List[DiscoveredTool]:
        """Scan a directory for tools."""
        tools = []
        
        glob_method = directory.rglob if recursive else directory.glob
        
        for py_file in glob_method(pattern):
            if py_file.name.startswith("_"):
                continue
            
            try:
                # Convert file path to module path
                rel_path = py_file.relative_to(self.base_path)
                module_path = str(rel_path.with_suffix("")).replace("/", ".")
                
                file_tools = self.scan_module(module_path)
                tools.extend(file_tools)
            except Exception as e:
                logger.debug(f"Skipping {py_file}: {e}")
        
        return tools
    
    def _build_schema(self, params: Dict) -> Dict[str, Any]:
        """Build JSON Schema from parameter spec."""
        properties = {}
        required = []
        
        for name, spec in params.items():
            properties[name] = {
                "type": spec.get("type", "string"),
            }
            if "description" in spec:
                properties[name]["description"] = spec["description"]
            if "default" in spec:
                properties[name]["default"] = spec["default"]
            if spec.get("required"):
                required.append(name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


class SpecificationScanner:
    """
    Scans MCP_TOOL_SPECIFICATION.md files for tool definitions.
    """
    
    def scan_spec_file(self, spec_path: Path) -> List[DiscoveredTool]:
        """Parse an MCP_TOOL_SPECIFICATION.md file."""
        tools = []
        
        if not spec_path.exists():
            return tools
        
        content = spec_path.read_text()
        
        # Simple parsing - look for tool sections
        current_tool = None
        current_section = None
        
        for line in content.split("\n"):
            # Tool header (## Tool: name)
            if line.startswith("## ") and "tool" in line.lower():
                if current_tool:
                    tools.append(current_tool)
                
                name = line.replace("##", "").strip()
                name = name.split(":")[-1].strip() if ":" in name else name
                
                current_tool = DiscoveredTool(
                    name=name,
                    description="",
                    source="specification",
                    source_path=str(spec_path),
                    input_schema={},
                )
            
            # Section headers
            elif line.startswith("### "):
                current_section = line.replace("###", "").strip().lower()
            
            # Content
            elif current_tool and current_section:
                if "description" in current_section and not current_tool.description:
                    current_tool.description = line.strip()
                elif "invocation" in current_section:
                    current_tool.name = line.strip().strip("`")
        
        if current_tool:
            tools.append(current_tool)
        
        return tools


class ExternalServerDiscovery:
    """
    Discovers tools from external MCP servers.
    """
    
    def __init__(self):
        self._servers: Dict[str, Dict[str, Any]] = {}
    
    def register_server(
        self,
        name: str,
        transport: str,
        endpoint: str,
    ) -> None:
        """Register an external MCP server."""
        self._servers[name] = {
            "name": name,
            "transport": transport,
            "endpoint": endpoint,
        }
    
    async def discover_from_server(self, server_name: str) -> List[DiscoveredTool]:
        """Discover tools from a registered server."""
        if server_name not in self._servers:
            return []
        
        server = self._servers[server_name]
        tools = []
        
        # For now, return empty - would need actual server connection
        # This is a placeholder for HTTP/stdio transport implementation
        logger.info(f"Would discover from {server['endpoint']}")
        
        return tools


class ToolCatalog:
    """
    Central catalog of all discovered MCP tools.
    """
    
    def __init__(self):
        self._tools: Dict[str, DiscoveredTool] = {}
        self._tags: Dict[str, Set[str]] = {}  # tag -> tool names
        self._sources: Dict[str, Set[str]] = {}  # source -> tool names
    
    def add(self, tool: DiscoveredTool) -> None:
        """Add a tool to the catalog."""
        self._tools[tool.name] = tool
        
        for tag in tool.tags:
            if tag not in self._tags:
                self._tags[tag] = set()
            self._tags[tag].add(tool.name)
        
        if tool.source not in self._sources:
            self._sources[tool.source] = set()
        self._sources[tool.source].add(tool.name)
    
    def get(self, name: str) -> Optional[DiscoveredTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_all(self) -> List[DiscoveredTool]:
        """List all tools."""
        return list(self._tools.values())
    
    def search(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
    ) -> List[DiscoveredTool]:
        """Search for tools."""
        results = list(self._tools.values())
        
        if query:
            query_lower = query.lower()
            results = [
                t for t in results
                if query_lower in t.name.lower() or query_lower in t.description.lower()
            ]
        
        if tags:
            matching_names = set()
            for tag in tags:
                matching_names.update(self._tags.get(tag, set()))
            results = [t for t in results if t.name in matching_names]
        
        if source:
            source_names = self._sources.get(source, set())
            results = [t for t in results if t.name in source_names]
        
        return results
    
    def to_json(self) -> str:
        """Export catalog as JSON."""
        return json.dumps([
            {
                "name": t.name,
                "description": t.description,
                "source": t.source,
                "source_path": t.source_path,
                "input_schema": t.input_schema,
                "version": t.version,
                "tags": t.tags,
            }
            for t in self._tools.values()
        ], indent=2)


# Convenience function
def discover_tools(
    module_paths: Optional[List[str]] = None,
    directories: Optional[List[Path]] = None,
    spec_files: Optional[List[Path]] = None,
) -> ToolCatalog:
    """
    Discover tools from multiple sources.
    
    Args:
        module_paths: Python module paths to scan
        directories: Directories to scan for Python files
        spec_files: MCP_TOOL_SPECIFICATION.md files to parse
    
    Returns:
        ToolCatalog with all discovered tools
    """
    catalog = ToolCatalog()
    
    module_scanner = ModuleScanner()
    spec_scanner = SpecificationScanner()
    
    if module_paths:
        for path in module_paths:
            for tool in module_scanner.scan_module(path):
                catalog.add(tool)
    
    if directories:
        for directory in directories:
            for tool in module_scanner.scan_directory(Path(directory)):
                catalog.add(tool)
    
    if spec_files:
        for spec_file in spec_files:
            for tool in spec_scanner.scan_spec_file(Path(spec_file)):
                catalog.add(tool)
    
    return catalog


def discover_all_public_tools(
    *,
    include_classes: bool = False,
    excluded_modules: Optional[Set[str]] = None,
) -> List[DiscoveredTool]:
    """Discover ALL public functions from every codomyrmex module.

    Scans all top-level packages under ``codomyrmex.*``, imports each one,
    and introspects public functions to build MCP-ready tool descriptors
    with auto-generated JSON schemas from type annotations.

    Args:
        include_classes: If True, also register class constructors.
        excluded_modules: Module names to skip (e.g. ``{"tests", "examples"}``).

    Returns:
        List of :class:`DiscoveredTool` objects with handlers attached.
    """
    import inspect
    import os

    from codomyrmex.model_context_protocol.decorators import _generate_schema_from_signature

    if excluded_modules is None:
        excluded_modules = {"tests", "examples", "module_template"}

    # Find the codomyrmex source root
    codomyrmex_pkg = importlib.import_module("codomyrmex")
    src_root = Path(codomyrmex_pkg.__file__).parent

    # Enumerate all top-level sub-packages
    module_dirs = []
    for entry in sorted(os.listdir(src_root)):
        entry_path = src_root / entry
        if (
            entry_path.is_dir()
            and not entry.startswith(("_", "."))
            and (entry_path / "__init__.py").exists()
            and entry not in excluded_modules
        ):
            module_dirs.append(entry)

    tools: List[DiscoveredTool] = []
    seen_names: Set[str] = set()

    for module_name in module_dirs:
        fqn = f"codomyrmex.{module_name}"
        try:
            mod = importlib.import_module(fqn)
        except Exception as exc:
            logger.debug(f"Skipping {fqn}: {exc}")
            continue

        for attr_name in sorted(dir(mod)):
            if attr_name.startswith("_"):
                continue

            obj = getattr(mod, attr_name, None)
            if obj is None:
                continue

            # Skip objects not defined in this module
            obj_module = getattr(obj, "__module__", "") or ""
            if not obj_module.startswith(fqn):
                continue

            # Skip already-decorated @mcp_tool functions (discovered elsewhere)
            if hasattr(obj, "_mcp_tool"):
                continue

            is_function = inspect.isfunction(obj)
            is_class = inspect.isclass(obj) and include_classes

            if not (is_function or is_class):
                continue

            tool_name = f"codomyrmex.{module_name}.{attr_name}"
            if tool_name in seen_names:
                continue
            seen_names.add(tool_name)

            # Build description from docstring
            doc = inspect.getdoc(obj) or f"Call {module_name}.{attr_name}"
            # Truncate long docstrings for the MCP description
            first_line = doc.split("\n")[0].strip()
            if len(first_line) > 200:
                first_line = first_line[:197] + "..."

            # Auto-generate schema
            try:
                if is_function:
                    schema = _generate_schema_from_signature(obj)
                else:
                    # For classes, generate schema from __init__
                    schema = _generate_schema_from_signature(obj.__init__)
            except Exception:
                schema = {"type": "object", "properties": {}}

            # Create a handler closure that calls the real function
            def _make_handler(fn, mod_name, fn_name):
                """Create a handler closure bound to the specific function."""
                def handler(**kwargs):
                    try:
                        result = fn(**kwargs)
                        return {"result": result}
                    except Exception as e:
                        return {"error": f"{type(e).__name__}: {e}"}
                handler.__name__ = f"_auto_{mod_name}_{fn_name}"
                handler.__doc__ = f"Auto-generated handler for {mod_name}.{fn_name}"
                return handler

            tools.append(DiscoveredTool(
                name=tool_name,
                description=first_line,
                source="auto_discovery",
                source_path=fqn,
                input_schema=schema,
                handler=_make_handler(obj, module_name, attr_name),
                tags=[module_name, "auto_discovered"],
            ))

    logger.info(
        f"Auto-discovered {len(tools)} public tools from "
        f"{len(module_dirs)} modules"
    )
    return tools


__all__ = [
    "DiscoveredTool",
    "ModuleScanner",
    "SpecificationScanner",
    "ExternalServerDiscovery",
    "ToolCatalog",
    "discover_tools",
    "discover_all_public_tools",
]

