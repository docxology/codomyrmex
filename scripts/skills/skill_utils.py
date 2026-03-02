#!/usr/bin/env python3
"""
Skills system utilities.

Usage:
    python skill_utils.py <command> [options]
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


def find_skills(search_paths: list = None) -> list:
    """Find skill definitions."""
    paths = search_paths or [".agent/skills", "skills", ".codomyrmex/skills"]
    found = []
    
    for base in paths:
        p = Path(base)
        if p.exists():
            # Look for SKILL.md files
            for f in p.rglob("SKILL.md"):
                found.append(f)
            # Look for skill.yaml files
            for f in p.rglob("skill.yaml"):
                found.append(f)
    
    return found


def parse_skill_md(path: Path) -> dict:
    """Parse SKILL.md file."""
    with open(path) as f:
        content = f.read()
    
    info = {"path": str(path), "type": "markdown"}
    
    # Extract frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    info[key.strip()] = value.strip()
    
    # Extract first heading
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match and "name" not in info:
        info["name"] = match.group(1)
    
    info["size"] = len(content)
    
    return info


def create_skill_template(name: str, output_dir: str = ".agent/skills") -> Path:
    """Create a skill template."""
    skill_dir = Path(output_dir) / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    skill_md = f'''---
name: {name}
description: Description of what this skill does
version: 0.1.0
---

# {name.replace("_", " ").title()}

## Purpose

Describe the purpose of this skill here.

## Usage

Explain how to use this skill.

## Prerequisites

List any requirements or dependencies.

## Steps

1. First step
2. Second step
3. Third step

## Examples

```python
# Example code here
```
'''
    
    (skill_dir / "SKILL.md").write_text(skill_md)
    return skill_dir


def main():
    parser = argparse.ArgumentParser(description="Skills utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # List command
    subparsers.add_parser("list", help="List available skills")
    
    # Show command
    show = subparsers.add_parser("show", help="Show skill details")
    show.add_argument("name", help="Skill name or path")
    
    # Create command
    create = subparsers.add_parser("create", help="Create skill template")
    create.add_argument("name", help="Skill name")
    create.add_argument("--output", "-o", default=".agent/skills")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🎯 Skills Utilities\n")
        print("Commands:")
        print("  list   - List available skills")
        print("  show   - Show skill details")
        print("  create - Create skill template")
        return 0
    
    if args.command == "list":
        skills = find_skills()
        print(f"🎯 Skills ({len(skills)}):\n")
        for s in skills:
            if s.name == "SKILL.md":
                info = parse_skill_md(s)
                name = info.get("name", s.parent.name)
                desc = info.get("description", "")[:50]
                print(f"   📚 {name}")
                if desc:
                    print(f"      {desc}")
            else:
                print(f"   📄 {s}")
        if not skills:
            print("   No skills found")
            print("   Searched: .agent/skills/, skills/, .codomyrmex/skills/")
    
    elif args.command == "show":
        # Find the skill
        skills = find_skills()
        found = None
        for s in skills:
            if args.name in str(s) or (s.name == "SKILL.md" and args.name == s.parent.name):
                found = s
                break
        
        if not found:
            print(f"❌ Skill not found: {args.name}")
            return 1
        
        info = parse_skill_md(found)
        print(f"🎯 Skill: {info.get('name', found.parent.name)}\n")
        for key, val in info.items():
            if key not in ["path", "type"]:
                print(f"   {key}: {val}")
    
    elif args.command == "create":
        output = create_skill_template(args.name, args.output)
        print(f"✅ Created skill: {output}")
        print(f"   Edit: {output}/SKILL.md")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
