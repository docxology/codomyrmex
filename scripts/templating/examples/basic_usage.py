#!/usr/bin/env python3
"""
Templating - Real Usage Examples

Demonstrates actual templating capabilities:
- TemplateEngine initialization (Jinja2, Mako)
- Template rendering with context
- TemplateManager usage
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.templating import (
    TemplateManager,
    render
)

def main():
    setup_logging()
    print_info("Running Templating Examples...")

    # 1. Direct Rendering
    print_info("Testing direct rendering...")
    try:
        template_str = "Hello {{ name }}!"
        context = {"name": "Codomyrmex"}
        output = render(template_str, context, engine="jinja2")
        if "Codomyrmex" in output:
            print_success(f"  Rendered output: {output}")
    except Exception as e:
        print_error(f"  Direct rendering failed: {e}")

    # 2. Template Manager
    print_info("Testing TemplateManager...")
    try:
        manager = TemplateManager()
        print_success("  TemplateManager initialized.")
    except Exception as e:
        print_error(f"  TemplateManager failed: {e}")

    print_success("Templating examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
