#!/usr/bin/env python3
"""
Template rendering utilities.

Usage:
    python template_utils.py <template> [--vars VARS]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
import json
from string import Template


def render_simple(template: str, variables: dict) -> str:
    """Render template with simple $var substitution."""
    t = Template(template)
    return t.safe_substitute(variables)


def render_jinja_like(template: str, variables: dict) -> str:
    """Render template with {{ var }} substitution."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{ {key} }}}}", str(value))
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def find_variables(template: str) -> list:
    """Find variables in a template."""
    dollar_vars = re.findall(r'\$(\w+)', template)
    jinja_vars = re.findall(r'\{\{\s*(\w+)\s*\}\}', template)
    return list(set(dollar_vars + jinja_vars))


def validate_template(template: str, variables: dict) -> list:
    """Validate that all variables are provided."""
    required = find_variables(template)
    missing = [v for v in required if v not in variables]
    return missing


def main():
    parser = argparse.ArgumentParser(description="Template utilities")
    parser.add_argument("template", nargs="?", help="Template file or string")
    parser.add_argument("--vars", "-v", help="Variables as JSON")
    parser.add_argument("--vars-file", "-f", help="Variables JSON file")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--list-vars", "-l", action="store_true", help="List template variables")
    args = parser.parse_args()
    
    if not args.template:
        print("📝 Template Utilities\n")
        print("Usage:")
        print('  python template_utils.py template.txt --vars \'{"name":"World"}\'')
        print("  python template_utils.py template.txt --vars-file vars.json")
        print("  python template_utils.py template.txt --list-vars")
        print("\nSupported syntax:")
        print("  $variable or ${variable}")
        print("  {{ variable }}")
        return 0
    
    # Load template
    template_path = Path(args.template)
    if template_path.exists():
        template_content = template_path.read_text()
        print(f"📄 Template: {template_path}\n")
    else:
        template_content = args.template
        print("📝 Template (inline)\n")
    
    # List variables
    if args.list_vars:
        variables = find_variables(template_content)
        print(f"📋 Variables ({len(variables)}):")
        for v in variables:
            print(f"   - {v}")
        return 0
    
    # Load variables
    variables = {}
    if args.vars:
        try:
            variables = json.loads(args.vars)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return 1
    elif args.vars_file:
        vars_path = Path(args.vars_file)
        if not vars_path.exists():
            print(f"❌ File not found: {args.vars_file}")
            return 1
        variables = json.loads(vars_path.read_text())
    
    # Validate
    missing = validate_template(template_content, variables)
    if missing:
        print(f"⚠️  Missing variables: {', '.join(missing)}")
    
    # Render
    result = render_simple(template_content, variables)
    result = render_jinja_like(result, variables)
    
    if args.output:
        Path(args.output).write_text(result)
        print(f"✅ Output saved to: {args.output}")
    else:
        print("📤 Result:\n")
        print(result[:2000])
        if len(result) > 2000:
            print(f"\n... ({len(result) - 2000} more characters)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
