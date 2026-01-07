#!/usr/bin/env python3
"""Fix security/digital/README.md navigation section."""

from pathlib import Path

def main():
    """Fix the README.md file."""
    file_path = Path("/Users/mini/Documents/GitHub/codomyrmex/src/codomyrmex/security/digital/README.md")
    
    content = file_path.read_text(encoding='utf-8')
    
    # Fix navigation section - replace the old one
    old_pattern = "- **Project Root**: [README](../../../README.md)\n- **Parent Directory**: [codomyrmex](../README.md)\n- **Src Hub**: [src](../../../src/README.md)"
    new_pattern = "- **Project Root**: [README](../../../../README.md)\n- **Parent Directory**: [security](../README.md)\n- **Codomyrmex**: [codomyrmex](../../README.md)\n- **Src Hub**: [src](../../../../src/README.md)"
    
    content = content.replace(old_pattern, new_pattern)
    
    file_path.write_text(content, encoding='utf-8')
    print(f"Fixed: {file_path}")

if __name__ == "__main__":
    main()

