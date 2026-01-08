from pathlib import Path
import re















#!/usr/bin/env python3
"""Fix or remove links to non-existent API_SPECIFICATION.md and USAGE_EXAMPLES.md files."""


def fix_missing_api_links(file_path: Path) -> bool:
    """Fix links to missing API/Usage files."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Check if API_SPECIFICATION.md exists in same directory
        api_spec = file_path.parent / "API_SPECIFICATION.md"
        usage_examples = file_path.parent / "USAGE_EXAMPLES.md"
        
        # Fix API_SPECIFICATION.md links
        if not api_spec.exists():
            # Remove the link but keep the text, or remove the entire line
            # Pattern: - **[API Reference](API_SPECIFICATION.md)** - ...
            pattern1 = r'- \*\*API Reference\*\*: \[API_SPECIFICATION\.md\]\(API_SPECIFICATION\.md\)[^\n]*\n'
            content = re.sub(pattern1, '', content)
            # Also handle other variations
            pattern2 = r'\[API_SPECIFICATION\.md\]\(API_SPECIFICATION\.md\)'
            content = re.sub(pattern2, 'API_SPECIFICATION.md (not available)', content)
        
        # Fix USAGE_EXAMPLES.md links
        if not usage_examples.exists():
            # Remove the link but keep the text, or remove the entire line
            pattern1 = r'- \*\*Usage Examples\*\*: \[USAGE_EXAMPLES\.md\]\(USAGE_EXAMPLES\.md\)[^\n]*\n'
            content = re.sub(pattern1, '', content)
            # Also handle other variations
            pattern2 = r'\[USAGE_EXAMPLES\.md\]\(USAGE_EXAMPLES\.md\)'
            content = re.sub(pattern2, 'USAGE_EXAMPLES.md (not available)', content)
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix missing API links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    # Check all AGENTS.md files
    for agents in base_path.rglob("AGENTS.md"):
        if fix_missing_api_links(agents):
            fixed_count += 1
            print(f"Fixed: {agents.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} files")

if __name__ == "__main__":
    main()

