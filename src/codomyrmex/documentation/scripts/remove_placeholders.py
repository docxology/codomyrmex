#!/usr/bin/env python3
"""
Remove placeholder content from README.md files.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

PLACEHOLDER_PATTERNS = [
    r'## Getting Started\s+To use this module in your project, import the necessary components:\s+```python\s+# Example usage\s+from codomyrmex\.your_module import main_component\s+def example\(\):\s+result = main_component\.process\(\)\s+print\(f"Result: {result}"\)\s+```',
    r'## detailed_overview\s+This module is a critical part of the Codomyrmex ecosystem\. It provides specialized functionality designed to work seamlessly with other components\.\s+The architecture focuses on modularity, reliability, and performance\.',
    r'## Contributing\s+We welcome contributions! Please ensure you:\s+1\.\s+Follow the project coding standards\.\s+2\.\s+Add tests for new functionality\.\s+3\.\s+Update documentation as needed\.\s+See the root `CONTRIBUTING\.md` for more details\.',
]

def remove_placeholders(filepath: Path) -> bool:
    """Remove placeholder content from a file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        # Remove placeholder sections
        for pattern in PLACEHOLDER_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Remove standalone placeholder lines
        content = re.sub(r'## detailed_overview\s*', '', content)
        content = re.sub(r'from codomyrmex\.your_module import main_component', '', content)
        content = re.sub(r'result = main_component\.process\(\)', '', content)
        
        # Clean up extra blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Process all README.md files."""
    readme_files = list(REPO_ROOT.rglob("README.md"))
    readme_files = [f for f in readme_files if ".venv" not in str(f) and "node_modules" not in str(f)]
    
    updated = 0
    for filepath in readme_files:
        if remove_placeholders(filepath):
            updated += 1
            print(f"Updated: {filepath.relative_to(REPO_ROOT)}")
    
    print(f"\nUpdated {updated} files")

if __name__ == "__main__":
    main()

