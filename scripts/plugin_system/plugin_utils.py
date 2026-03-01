#!/usr/bin/env python3
"""
Plugin system utilities.

Usage:
    python plugin_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse


def find_plugins(search_paths: list = None) -> list:
    """Find plugin files."""
    paths = search_paths or ["plugins", "src/plugins", ".codomyrmex/plugins"]
    found = []
    
    for base in paths:
        p = Path(base)
        if p.exists():
            for f in p.glob("*.py"):
                if not f.name.startswith("_"):
                    found.append(f)
            for f in p.glob("*/plugin.py"):
                found.append(f)
    
    return found


def analyze_plugin(path: Path) -> dict:
    """Analyze a plugin file."""
    info = {"path": str(path), "valid": False}
    
    try:
        with open(path) as f:
            content = f.read()
        
        info["lines"] = len(content.split("\n"))
        info["has_register"] = "register" in content or "setup" in content
        info["has_docstring"] = '"""' in content[:200] or "'''" in content[:200]
        info["valid"] = info["has_register"]
        
        # Try to extract metadata
        if "name = " in content or 'name = "' in content:
            import re
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                info["name"] = match.group(1)
        
        if "version = " in content:
            import re
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                info["version"] = match.group(1)
                
    except Exception as e:
        info["error"] = str(e)
    
    return info


def create_plugin_template(name: str, output_dir: str = "plugins") -> Path:
    """Create a plugin template."""
    template = f'''"""
{name.title()} Plugin

Description: Add your plugin description here.
"""

__name__ = "{name}"
__version__ = "0.1.0"
__author__ = "Your Name"


def register(app):
    """Register this plugin with the application."""
    print(f"Registering plugin: {__name__}")
    # Add your plugin registration logic here
    return True


def unregister(app):
    """Unregister this plugin."""
    print(f"Unregistering plugin: {__name__}")
    return True


# Optional: Plugin hooks
def on_startup():
    """Called when the application starts."""
    pass


def on_shutdown():
    """Called when the application shuts down."""
    pass
'''
    
    output = Path(output_dir) / f"{name}.py"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template)
    return output


def main():
    parser = argparse.ArgumentParser(description="Plugin utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    subparsers.add_parser("list", help="List installed plugins")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze a plugin")
    analyze.add_argument("path", help="Plugin file path")
    
    # Create command
    create = subparsers.add_parser("create", help="Create plugin template")
    create.add_argument("name", help="Plugin name")
    create.add_argument("--output", "-o", default="plugins")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔌 Plugin Utilities\n")
        print("Commands:")
        print("  list    - List installed plugins")
        print("  analyze - Analyze a plugin file")
        print("  create  - Create plugin template")
        return 0
    
    if args.command == "list":
        plugins = find_plugins()
        print(f"🔌 Plugins ({len(plugins)}):\n")
        for p in plugins:
            info = analyze_plugin(p)
            icon = "✅" if info["valid"] else "⚠️"
            name = info.get("name", p.stem)
            version = info.get("version", "")
            print(f"   {icon} {name} {version}")
            print(f"      {p}")
        if not plugins:
            print("   No plugins found")
            print("   Searched: plugins/, src/plugins/, .codomyrmex/plugins/")
    
    elif args.command == "analyze":
        path = Path(args.path)
        if not path.exists():
            print(f"❌ File not found: {args.path}")
            return 1
        
        info = analyze_plugin(path)
        print(f"🔍 Plugin Analysis: {path.name}\n")
        print(f"   Valid: {'Yes' if info['valid'] else 'No'}")
        print(f"   Lines: {info.get('lines', 'N/A')}")
        print(f"   Has register: {info.get('has_register', False)}")
        print(f"   Has docstring: {info.get('has_docstring', False)}")
    
    elif args.command == "create":
        output = create_plugin_template(args.name, args.output)
        print(f"✅ Created plugin template: {output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
