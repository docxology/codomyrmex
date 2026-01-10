from pathlib import Path
import json
import re
import sys

from codomyrmex.logging_monitoring import get_logger





Fix CONTRIBUTING.md references in module documentation.

Updates all references to CONTRIBUTING.md in modules to point to
the correct location at docs/project/contributing.md
"""


logger = get_logger(__name__)

def calculate_relative_path(from_file: Path, to_file: Path, repo_root: Path) -> str:
    """Calculate relative path from one file to another."""
    try:
        relative = Path(to_file).relative_to(Path(from_file).parent)
        return str(relative).replace('\\', '/')
    except ValueError:
        # Files are on different roots, calculate absolute path
        from_file = Path(from_file).resolve()
        to_file = Path(to_file).resolve()
        repo_root = Path(repo_root).resolve()
        
        # Get relative paths from repo root
        from_rel = from_file.relative_to(repo_root)
        to_rel = to_file.relative_to(repo_root)
        
        # Calculate levels up
        from_depth = len(from_rel.parent.parts)
        up_levels = from_depth - 1  # -1 because we go up to src/codomyrmex level
        
        # Build path
        return '../' * up_levels + str(to_rel).replace('\\', '/')

def fix_contributing_refs():
    """Fix all CONTRIBUTING.md references."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    contributing_path = repo_root / 'docs' / 'project' / 'contributing.md'
    
    # Load audit data
    audit_data_path = script_dir / 'module_audit_data.json'
    if not audit_data_path.exists():
        print("Error: module_audit_data.json not found. Run module_docs_auditor.py first.")
        return 1
    
    with open(audit_data_path, 'r') as f:
        audit_data = json.load(f)
    
    contributing_refs = audit_data['contributing_refs']
    
    print(f"Fixing {len(contributing_refs)} CONTRIBUTING.md references...\n")
    
    fixed_count = 0
    for ref in contributing_refs:
        file_path = repo_root / ref['file']
        if not file_path.exists():
            print(f"⚠️  File not found: {ref['file']}")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Calculate correct relative path
            correct_path = calculate_relative_path(file_path, contributing_path, repo_root)
            
            # Fix the line
            line_num = ref['line'] - 1
            if line_num < len(lines):
                old_line = lines[line_num]
                
                # Replace various patterns of CONTRIBUTING.md references
                patterns = [
                    (r'\(\.\./CONTRIBUTING\.md\)', f'({correct_path})'),
                    (r'\(\.\./\.\./CONTRIBUTING\.md\)', f'({correct_path})'),
                    (r'\(\.\./\.\./\.\./CONTRIBUTING\.md\)', f'({correct_path})'),
                    (r'\(\.\./\.\./\.\./\.\./CONTRIBUTING\.md\)', f'({correct_path})'),
                    (r'\(CONTRIBUTING\.md\)', f'({correct_path})'),
                ]
                
                new_line = old_line
                for pattern, replacement in patterns:
                    new_line = re.sub(pattern, replacement, new_line)
                
                if new_line != old_line:
                    lines[line_num] = new_line
                    content = '\n'.join(lines)
                    file_path.write_text(content, encoding='utf-8')
                    print(f"✅ Fixed: {ref['file']} (line {ref['line']})")
                    print(f"   {old_line.strip()}")
                    print(f"   → {new_line.strip()}\n")
                    fixed_count += 1
                else:
                    print(f"⚠️  No pattern matched in: {ref['file']} (line {ref['line']})")
                    print(f"   {old_line.strip()}\n")
        except Exception as e:
            print(f"❌ Error fixing {ref['file']}: {e}\n")
    
    print(f"\n✅ Fixed {fixed_count} of {len(contributing_refs)} references")
    return 0

if __name__ == '__main__':
    sys.exit(fix_contributing_refs())
