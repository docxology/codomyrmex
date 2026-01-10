from pathlib import Path
from typing import Dict, List
import json
import re

from codomyrmex.logging_monitoring import get_logger




















"""
Validate all child references in AGENTS.md files.
Check that children point to existing directories with AGENTS.md files.
"""




logger = get_logger(__name__)

def extract_children_references(content: str) -> List[Dict]:
    """Extract all child references from AGENTS.md content."""
    children = []
    # Find the Children section
    children_pattern = r'- \*\*Children\*\*:\s*\n((?:    - \[[^\]]+\]\([^)]+\)\s*\n?)*)'
    match = re.search(children_pattern, content)
    if match:
        children_block = match.group(1)
        # Extract each child reference
        child_pattern = r'    - \[([^\]]+)\]\(([^)]+)\)'
        for child_match in re.finditer(child_pattern, children_block):
            label, path = child_match.groups()
            children.append({
                'label': label,
                'path': path,
                'line': content[:match.start() + child_match.start()].count('\n') + 1
            })
    return children

def resolve_path(base_path: Path, relative_path: str, repo_root: Path) -> tuple[bool, Path | None]:
    """Resolve a relative path and check if it exists."""
    try:
        if relative_path.startswith('http://') or relative_path.startswith('https://'):
            return (True, None)  # External links
        
        # Handle relative paths
        if relative_path.startswith('../'):
            levels_up = relative_path.count('../')
            current_dir = base_path.parent
            for _ in range(levels_up):
                if current_dir == repo_root or current_dir == current_dir.parent:
                    break
                current_dir = current_dir.parent
            relative_path = relative_path.lstrip('../')
            target = current_dir / relative_path
        elif relative_path.startswith('./'):
            target = base_path.parent / relative_path[2:]
        elif relative_path.startswith('/'):
            target = repo_root / relative_path.lstrip('/')
        else:
            target = base_path.parent / relative_path
        
        target = target.resolve()
        # Check if within repo
        try:
            target.relative_to(repo_root)
        except ValueError:
            return (False, None)
        
        exists = target.exists()
        return (exists, target)
    except Exception:
        return (False, None)

def validate_agents_file(file_path: Path, repo_root: Path) -> Dict:
    """Validate child references in a single AGENTS.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'file': str(file_path.relative_to(repo_root)),
            'error': f'Could not read file: {e}'
        }
    
    relative_path = file_path.relative_to(repo_root)
    children = extract_children_references(content)
    
    issues = []
    validated_children = []
    
    for child in children:
        exists, resolved = resolve_path(file_path, child['path'], repo_root)
        child_info = {
            **child,
            'exists': exists,
            'resolved': str(resolved) if resolved else None
        }
        validated_children.append(child_info)
        
        if not exists:
            issues.append({
                'type': 'broken_child_path',
                'line': child['line'],
                'label': child['label'],
                'path': child['path'],
                'message': f"Child path does not exist: {child['path']}"
            })
        elif resolved:
            if resolved.is_file():
                # Check if it's an AGENTS.md file
                if resolved.name != 'AGENTS.md':
                    issues.append({
                        'type': 'child_not_agents',
                        'line': child['line'],
                        'label': child['label'],
                        'path': child['path'],
                        'message': f"Child reference points to file that is not AGENTS.md: {resolved.name}"
                    })
            elif resolved.is_dir():
                # Check if directory has AGENTS.md
                agents_in_dir = resolved / 'AGENTS.md'
                if not agents_in_dir.exists():
                    issues.append({
                        'type': 'child_missing_agents',
                        'line': child['line'],
                        'label': child['label'],
                        'path': child['path'],
                        'message': f"Child directory does not have AGENTS.md: {child['path']}"
                    })
    
    return {
        'file': str(relative_path),
        'children': validated_children,
        'issues': issues
    }

def main():
    """Main validation function."""
    repo_root = Path(__file__).parent.parent.parent
    
    # Find all AGENTS.md files
    agents_files = []
    for path in repo_root.rglob("AGENTS.md"):
        if ".venv" in str(path) or "node_modules" in str(path):
            continue
        agents_files.append(path)
    
    print(f"Validating {len(agents_files)} AGENTS.md files...")
    
    results = []
    total_issues = 0
    for agents_file in sorted(agents_files):
        result = validate_agents_file(agents_file, repo_root)
        results.append(result)
        if result.get('issues'):
            total_issues += len(result['issues'])
            print(f"  {result['file']}: {len(result['issues'])} issues")
            for issue in result['issues']:
                print(f"    - {issue['message']}")
    
    # Save results
    output_file = repo_root / 'output' / 'child_references_validation.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        'summary': {
            'total_files': len(agents_files),
            'total_issues': total_issues,
            'files_with_issues': sum(1 for r in results if r.get('issues'))
        },
        'results': results
    }
    
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nValidation complete!")
    print(f"  Total files: {report['summary']['total_files']}")
    print(f"  Files with issues: {report['summary']['files_with_issues']}")
    print(f"  Total issues: {report['summary']['total_issues']}")
    print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    main()
