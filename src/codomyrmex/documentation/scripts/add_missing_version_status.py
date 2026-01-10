from pathlib import Path
import os
import os
import re

from codomyrmex.logging_monitoring import get_logger




















"""
def has_version_status(content: str) -> bool:
    """



    #!/usr/bin/env python3
    """Add missing version/status information to documentation files."""

logger = get_logger(__name__)

Check if file has version/status information."""
    patterns = [
        r'\*\*Version\*\*',
        r'\*\*Status\*\*',
        r'Version.*Status',
        r'v0\.1\.0.*Active'
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

def add_version_status(file_path: Path) -> bool:
    """Add version/status information to a file."""
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if has_version_status(content):
            return False
        
        # Find the title line (first line starting with #)
        lines = content.split('\n')
        title_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                title_idx = i
                break
        
        if title_idx == -1:
            return False
        
        # Insert version/status after title
        version_line = "**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025"
        
        # Check if there's already a blank line after title
        if title_idx + 1 < len(lines) and lines[title_idx + 1].strip() == '':
            # Insert after blank line
            lines.insert(title_idx + 2, version_line)
        else:
            # Insert after title with blank line
            lines.insert(title_idx + 1, '')
            lines.insert(title_idx + 2, version_line)
        
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Add version/status to all documentation files."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    fixed_count = 0
    
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and 
                   d not in ['__pycache__', 'node_modules', 'venv', '.venv', '.git', '@output']]
        
        for file in ['README.md', 'AGENTS.md', 'SPEC.md']:
            file_path = Path(root) / file
            if file_path.exists():
                if add_version_status(file_path):
                    fixed_count += 1
                    if fixed_count % 20 == 0:
                        print(f"Fixed {fixed_count} files...")
    
    print(f"\nCompleted: Fixed {fixed_count} files with version/status")

if __name__ == "__main__":
    main()
