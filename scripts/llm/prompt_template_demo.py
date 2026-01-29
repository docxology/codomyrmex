#!/usr/bin/env python3
"""
Demonstrate prompt template loading and variable substitution.

Usage:
    python prompt_template_demo.py [--template TEMPLATE] [--vars KEY=VALUE...]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re


# Built-in demo templates
DEMO_TEMPLATES = {
    "code_review": """You are a code reviewer. Review the following code:

```{language}
{code}
```

Focus on:
- Code quality and best practices
- Potential bugs or issues
- Suggestions for improvement

Provide your review:""",

    "summarize": """Summarize the following text in {style} style:

{text}

Summary:""",

    "explain": """Explain the concept of {topic} to someone who is {audience}.

Use simple language and provide examples where helpful.

Explanation:""",

    "translate": """Translate the following {source_lang} text to {target_lang}:

{text}

Translation:""",
}


def load_template(template_path: str) -> str:
    """Load template from file or use built-in."""
    if template_path in DEMO_TEMPLATES:
        return DEMO_TEMPLATES[template_path]
    
    path = Path(template_path)
    if path.exists():
        return path.read_text()
    
    raise ValueError(f"Template not found: {template_path}")


def extract_variables(template: str) -> list:
    """Extract variable names from template."""
    return list(set(re.findall(r'\{(\w+)\}', template)))


def render_template(template: str, variables: dict) -> str:
    """Render template with variable substitution."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def parse_var_arg(var_str: str) -> tuple:
    """Parse KEY=VALUE argument."""
    if "=" not in var_str:
        raise ValueError(f"Invalid variable format: {var_str}. Use KEY=VALUE")
    key, value = var_str.split("=", 1)
    return key.strip(), value.strip()


def main():
    parser = argparse.ArgumentParser(description="Demonstrate prompt template usage")
    parser.add_argument("--template", "-t", default="explain",
                        help="Template name or file path (built-in: code_review, summarize, explain, translate)")
    parser.add_argument("--vars", "-v", nargs="*", default=[],
                        help="Template variables as KEY=VALUE pairs")
    parser.add_argument("--list", "-l", action="store_true",
                        help="List available built-in templates")
    parser.add_argument("--show", "-s", action="store_true",
                        help="Show template without rendering")
    args = parser.parse_args()
    
    if args.list:
        print("📋 Available built-in templates:\n")
        for name, template in DEMO_TEMPLATES.items():
            variables = extract_variables(template)
            print(f"  {name}")
            print(f"    Variables: {', '.join(variables)}")
            print()
        return 0
    
    try:
        template = load_template(args.template)
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    
    variables = extract_variables(template)
    
    if args.show:
        print(f"📄 Template: {args.template}\n")
        print("Variables:", ", ".join(variables))
        print("\n--- Template Content ---\n")
        print(template)
        return 0
    
    # Parse provided variables
    var_dict = {}
    for var_str in args.vars:
        try:
            key, value = parse_var_arg(var_str)
            var_dict[key] = value
        except ValueError as e:
            print(f"❌ Error: {e}")
            return 1
    
    # Check for missing variables
    missing = [v for v in variables if v not in var_dict]
    if missing:
        print(f"📝 Template: {args.template}")
        print(f"   Required variables: {', '.join(variables)}")
        print(f"\n⚠️  Missing variables: {', '.join(missing)}")
        print("\n   Example usage:")
        example_vars = " ".join(f'-v {v}="<value>"' for v in missing)
        print(f"   python prompt_template_demo.py -t {args.template} {example_vars}")
        return 1
    
    # Render template
    rendered = render_template(template, var_dict)
    
    print(f"📄 Template: {args.template}")
    print(f"   Variables: {var_dict}")
    print("\n--- Rendered Prompt ---\n")
    print(rendered)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
