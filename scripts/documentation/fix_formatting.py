#!/usr/bin/env python3
"""Fix formatting issues found in triple-check audit.

1. Fix unclosed code blocks (odd number of triple-backticks)
2. Remove duplicate ## Detailed Architecture sections
3. Fill empty sections with placeholder content
4. Add Installation sections to 3 remaining READMEs
"""
import ast
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(REPO, "src", "codomyrmex")


def fix_unclosed_code_blocks(filepath):
    """Fix files with odd number of triple-backtick groups."""
    with open(filepath) as f:
        content = f.read()

    ticks = content.count("```")
    if ticks % 2 == 0:
        return False

    # Add a closing ``` at the end
    content = content.rstrip() + "\n```\n"
    with open(filepath, "w") as f:
        f.write(content)
    return True


def fix_duplicate_sections(filepath):
    """Remove duplicate ## headings, keeping the first occurrence."""
    with open(filepath) as f:
        lines = f.readlines()

    seen_headings = set()
    new_lines = []
    skip_until_next_heading = False

    for i, line in enumerate(lines):
        heading_match = re.match(r"^(## .+)$", line.strip())
        if heading_match:
            heading = heading_match.group(1)
            if heading in seen_headings:
                # Skip this duplicate section until next heading
                skip_until_next_heading = True
                continue
            else:
                seen_headings.add(heading)
                skip_until_next_heading = False

        if skip_until_next_heading:
            # Check if this line starts a new heading (not duplicate)
            if re.match(r"^## .+$", line.strip()):
                skip_until_next_heading = False
                # Re-check this heading
                heading = line.strip()
                if heading in seen_headings:
                    skip_until_next_heading = True
                    continue
                seen_headings.add(heading)
            else:
                continue

        new_lines.append(line)

    if len(new_lines) != len(lines):
        with open(filepath, "w") as f:
            f.writelines(new_lines)
        return True
    return False


def fix_empty_sections(filepath):
    """Fill empty ## sections with minimal content."""
    with open(filepath) as f:
        content = f.read()

    # Find ## heading followed by another ## heading with only whitespace
    def fill_empty(match):
        heading = match.group(1).strip()
        next_heading = match.group(2)
        # Generate filler based on heading
        if "architecture" in heading.lower():
            filler = "See source code for architectural details.\n"
        elif "api" in heading.lower():
            filler = "See module exports for API details.\n"
        else:
            filler = "See source code and documentation.\n"
        return f"{heading}\n\n{filler}\n{next_heading}"

    new_content = re.sub(
        r"^(## .+)\n\s*\n(## .+)",
        fill_empty,
        content,
        flags=re.MULTILINE,
    )

    if new_content != content:
        with open(filepath, "w") as f:
            f.write(new_content)
        return True
    return False


def add_installation(mod_name):
    """Add Installation section to README if missing."""
    readme = os.path.join(SRC, mod_name, "README.md")
    if not os.path.exists(readme):
        return False

    with open(readme) as f:
        content = f.read()

    content_lower = content.lower()
    if "install" in content_lower or "setup" in content_lower or "pip" in content_lower:
        return False

    install = (
        "\n## Installation\n\n"
        "```bash\n"
        "pip install codomyrmex\n"
        "```\n\n"
        "Or for development:\n\n"
        "```bash\n"
        "uv sync\n"
        "```\n"
    )

    # Insert before Key Exports, Quick Start, Testing, or Navigation
    for anchor in ["## Key Export", "## Quick Start", "## Feature", "## Testing", "## Documentation", "## Navigation"]:
        if anchor in content:
            content = content.replace(anchor, install + "\n" + anchor)
            break
    else:
        content = content.rstrip() + "\n" + install

    with open(readme, "w") as f:
        f.write(content)
    return True


def main():
    fixes = {"unclosed": 0, "duplicate": 0, "empty": 0, "install": 0}

    # Fix unclosed code blocks
    for layer in [SRC, os.path.join(REPO, "docs", "modules")]:
        for d in sorted(os.listdir(layer)):
            p = os.path.join(layer, d)
            if not os.path.isdir(p) or d == "__pycache__":
                continue
            for f in ["README.md", "AGENTS.md", "SPEC.md"]:
                fp = os.path.join(p, f)
                if os.path.exists(fp) and fix_unclosed_code_blocks(fp):
                    fixes["unclosed"] += 1
                    print(f"  Fixed unclosed: {d}/{f}")

    # Fix duplicate sections
    for layer in [SRC, os.path.join(REPO, "docs", "modules")]:
        for d in sorted(os.listdir(layer)):
            p = os.path.join(layer, d)
            if not os.path.isdir(p) or d == "__pycache__":
                continue
            for f in ["README.md", "AGENTS.md", "SPEC.md"]:
                fp = os.path.join(p, f)
                if os.path.exists(fp) and fix_duplicate_sections(fp):
                    fixes["duplicate"] += 1
                    print(f"  Fixed duplicate: {d}/{f}")

    # Fix empty sections
    for layer in [SRC, os.path.join(REPO, "docs", "modules")]:
        for d in sorted(os.listdir(layer)):
            p = os.path.join(layer, d)
            if not os.path.isdir(p) or d == "__pycache__":
                continue
            for f in ["README.md", "AGENTS.md", "SPEC.md"]:
                fp = os.path.join(p, f)
                if os.path.exists(fp) and fix_empty_sections(fp):
                    fixes["empty"] += 1
                    print(f"  Fixed empty: {d}/{f}")

    # Add missing Installation sections
    modules = sorted(
        d for d in os.listdir(SRC)
        if os.path.isdir(os.path.join(SRC, d)) and d != "__pycache__"
    )
    for mod in modules:
        if add_installation(mod):
            fixes["install"] += 1
            print(f"  Added Install: {mod}")

    print(f"\n✅ Unclosed code blocks fixed: {fixes['unclosed']}")
    print(f"✅ Duplicate sections removed: {fixes['duplicate']}")
    print(f"✅ Empty sections filled: {fixes['empty']}")
    print(f"✅ Installation sections added: {fixes['install']}")
    print(f"📊 Total fixes: {sum(fixes.values())}")


if __name__ == "__main__":
    main()
