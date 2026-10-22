#!/usr/bin/env python3
"""Fix Installation sections that got wrong content injected."""
import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "src", "codomyrmex")

fixed = 0
for d in sorted(os.listdir(SRC)):
    p = os.path.join(SRC, d)
    if not os.path.isdir(p) or d == "__pycache__":
        continue
    readme = os.path.join(p, "README.md")
    if not os.path.exists(readme):
        continue

    with open(readme) as f:
        lines = f.readlines()

    in_install = False
    install_start = -1
    install_end = -1
    has_python_in_install = False

    for i, line in enumerate(lines):
        if line.strip() == "## Installation":
            in_install = True
            install_start = i
            continue
        if in_install and line.startswith("## ") and "Installation" not in line:
            install_end = i
            in_install = False
            break
        if in_install and ("from codomyrmex" in line or "import codomyrmex" in line):
            has_python_in_install = True

    if has_python_in_install and install_start >= 0 and install_end > 0:
        correct = [
            "## Installation\n",
            "\n",
            "```bash\n",
            "pip install codomyrmex\n",
            "```\n",
            "\n",
            "Or for development:\n",
            "\n",
            "```bash\n",
            "uv sync\n",
            "```\n",
            "\n",
        ]
        new_lines = lines[:install_start] + correct + lines[install_end:]
        with open(readme, "w") as f:
            f.writelines(new_lines)
        fixed += 1

print(f"Fixed {fixed} Installation sections")
