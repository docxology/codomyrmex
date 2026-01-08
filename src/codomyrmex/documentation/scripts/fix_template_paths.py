from pathlib import Path
import re
import sys

from codomyrmex.logging_monitoring import get_logger




#!/usr/bin/env python3

Fix template/module_template path references to point to correct location.
"""

#!/usr/bin/env python3

logger = get_logger(__name__)

def fix_template_paths():
    """Fix all template/module_template path references."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Find all markdown files
    markdown_files = list(repo_root.rglob('*.md'))
    
    print(f"Fixing template path references in {len(markdown_files)} files...\n")
    
    fixed_count = 0
    
    for md_file in markdown_files:
        # Skip certain directories
        if any(part in str(md_file) for part in ['__pycache__', 'node_modules', '.git']):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Fix various patterns of template/module_template references
            patterns = [
                (r'`template/module_template/MCP_TOOL_SPECIFICATION\.md`', 
                 lambda m: calculate_correct_path(md_file, repo_root)),
                (r'\[([^\]]+)\]\(\.\./\.\./template/module_template/MCP_TOOL_SPECIFICATION\.md\)',
                 lambda m: f'[{m.group(1)}]({calculate_correct_path(md_file, repo_root)})'),
                (r'\[([^\]]+)\]\(\.\./template/module_template/MCP_TOOL_SPECIFICATION\.md\)',
                 lambda m: f'[{m.group(1)}]({calculate_correct_path(md_file, repo_root)})'),
                (r'template/module_template/MCP_TOOL_SPECIFICATION\.md',
                 lambda m: calculate_correct_path_text(md_file, repo_root)),
            ]
            
            for pattern, replacement in patterns:
                if isinstance(replacement, str):
                    content = re.sub(pattern, replacement, content)
                else:
                    content = re.sub(pattern, lambda m: replacement(m), content)
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                rel_path = md_file.relative_to(repo_root)
                print(f"✅ Fixed: {rel_path}")
                fixed_count += 1
                
        except Exception as e:
            rel_path = md_file.relative_to(repo_root) if md_file else 'unknown'
            print(f"⚠️  Error processing {rel_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} files")
    return 0

def calculate_correct_path(from_file: Path, repo_root: Path) -> str:
    """Calculate correct relative path to module_template/MCP_TOOL_SPECIFICATION.md."""
    target = repo_root / 'src' / 'codomyrmex' / 'module_template' / 'MCP_TOOL_SPECIFICATION.md'
    
    try:
        # Calculate relative path
        rel_path = Path(target).relative_to(Path(from_file).parent)
        return str(rel_path).replace('\\', '/')
    except ValueError:
        # Fallback: calculate from repo root
        from_rel = Path(from_file).relative_to(repo_root)
        depth = len(from_rel.parent.parts)
        up_path = '../' * depth
        return f'{up_path}src/codomyrmex/module_template/MCP_TOOL_SPECIFICATION.md'

def calculate_correct_path_text(from_file: Path, repo_root: Path) -> str:
    """Calculate correct path for text (not markdown link)."""
    return calculate_correct_path(from_file, repo_root)

if __name__ == '__main__':
    sys.exit(fix_template_paths())
