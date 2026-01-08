from pathlib import Path
import re















#!/usr/bin/env python3
"""Remove links to non-existent SPEC.md files in scripts/."""


def remove_nonexistent_spec_links(file_path: Path, base_path: Path) -> bool:
    """Remove links to non-existent SPEC.md files."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # Find Library Spec links
        pattern = r'- \*\*Library Spec\*\*: \[.*?\]\([^)]+SPEC\.md\)[^\n]*\n'
        content = re.sub(pattern, '', content)
        
        # Also handle other variations
        pattern2 = r'- \*\*.*Spec\*\*: \[.*?\]\([^)]+SPEC\.md\)[^\n]*\n'
        # But be careful - only remove if the file doesn't exist
        matches = list(re.finditer(r'\[([^\]]+)\]\(([^)]+SPEC\.md)\)', content))
        for match in reversed(matches):
            link_url = match.group(2)
            # Resolve path
            if link_url.startswith('../'):
                levels_up = link_url.count('../')
                base_dir = file_path.parent
                for _ in range(levels_up):
                    base_dir = base_dir.parent
                resolved = base_dir / link_url.lstrip('../')
            else:
                resolved = file_path.parent / link_url
            
            if not resolved.exists():
                # Remove the entire line containing this link
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end]
                if 'Spec' in line or 'spec' in line.lower():
                    content = content[:line_start] + content[line_end+1:]
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Remove nonexistent SPEC.md links."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    scripts_dir = base_path / "scripts"
    fixed_count = 0
    
    for spec in scripts_dir.rglob("SPEC.md"):
        if remove_nonexistent_spec_links(spec, base_path):
            fixed_count += 1
            print(f"Fixed: {spec.relative_to(base_path)}")
    
    print(f"\nCompleted: Fixed {fixed_count} SPEC.md files")

if __name__ == "__main__":
    main()

