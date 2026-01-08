from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import re




#!/usr/bin/env python3
"""
Audit all AGENTS.md files for filepath and signpost issues.
Catalogs parent references, child references, and navigation links.
"""


def find_agents_files(repo_root: Path) -> List[Path]:
    """Find all AGENTS.md files in the repository."""
    agents_files = []
    for path in repo_root.rglob("AGENTS.md"):
        # Skip .venv and node_modules
        if ".venv" in str(path) or "node_modules" in str(path):
            continue
        agents_files.append(path)
    return sorted(agents_files)

def extract_parent_reference(content: str, file_path: Path) -> Optional[Dict]:
    """Extract parent reference from AGENTS.md content."""
    pattern = r'- \*\*Parent\*\*: \[([^\]]+)\]\(([^)]+)\)'
    match = re.search(pattern, content)
    if match:
        label, path = match.groups()
        return {
            'label': label,
            'path': path,
            'line': content[:match.start()].count('\n') + 1,
            'is_generic': label.lower() == 'parent'
        }
    return None

def extract_children_references(content: str, file_path: Path) -> List[Dict]:
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

def extract_navigation_links(content: str, file_path: Path) -> List[Dict]:
    """Extract navigation links from AGENTS.md content."""
    links = []
    # Find Navigation Links section
    nav_pattern = r'## Navigation Links\s*\n((?:- \*\*[^\*]+\*\*: \[[^\]]+\]\([^)]+\)[^\n]*\n?)*)'
    match = re.search(nav_pattern, content, re.MULTILINE)
    if match:
        nav_block = match.group(1)
        # Extract each link
        link_pattern = r'- \*\*([^\*]+)\*\*: \[([^\]]+)\]\(([^)]+)\)'
        for link_match in re.finditer(link_pattern, nav_block):
            label, text, path = link_match.groups()
            links.append({
                'label': label.strip(),
                'text': text,
                'path': path,
                'line': content[:match.start() + link_match.start()].count('\n') + 1
            })
    return links

def extract_key_artifacts(content: str, file_path: Path) -> List[Dict]:
    """Extract key artifacts references."""
    artifacts = []
    pattern = r'- \*\*Key Artifacts\*\*:\s*\n((?:    - \[[^\]]+\]\([^)]+\)\s*\n?)*)'
    match = re.search(pattern, content)
    if match:
        artifacts_block = match.group(1)
        artifact_pattern = r'    - \[([^\]]+)\]\(([^)]+)\)'
        for artifact_match in re.finditer(artifact_pattern, artifacts_block):
            label, path = artifact_match.groups()
            artifacts.append({
                'label': label,
                'path': path,
                'line': content[:match.start() + artifact_match.start()].count('\n') + 1
            })
    return artifacts

def resolve_path(base_path: Path, relative_path: str, repo_root: Path) -> Tuple[bool, Optional[Path]]:
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
            return (False, target)
        
        exists = target.exists()
        return (exists, target)
    except Exception as e:
        return (False, None)

def audit_agents_file(file_path: Path, repo_root: Path) -> Dict:
    """Audit a single AGENTS.md file."""
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        return {
            'file': str(file_path.relative_to(repo_root)),
            'error': f'Could not read file: {e}'
        }
    
    relative_path = file_path.relative_to(repo_root)
    
    result = {
        'file': str(relative_path),
        'parent': None,
        'children': [],
        'navigation_links': [],
        'key_artifacts': [],
        'issues': []
    }
    
    # Extract parent reference
    parent_ref = extract_parent_reference(content, file_path)
    if parent_ref:
        result['parent'] = parent_ref
        if parent_ref['is_generic']:
            result['issues'].append({
                'type': 'generic_parent_label',
                'line': parent_ref['line'],
                'message': f"Parent reference uses generic '[Parent]' label"
            })
        # Validate parent path
        exists, resolved = resolve_path(file_path, parent_ref['path'], repo_root)
        if not exists:
            result['issues'].append({
                'type': 'broken_parent_path',
                'line': parent_ref['line'],
                'path': parent_ref['path'],
                'resolved': str(resolved) if resolved else None,
                'message': f"Parent path does not exist: {parent_ref['path']}"
            })
    
    # Extract children references
    children = extract_children_references(content, file_path)
    for child in children:
        exists, resolved = resolve_path(file_path, child['path'], repo_root)
        child_info = {
            **child,
            'exists': exists,
            'resolved': str(resolved) if resolved else None
        }
        result['children'].append(child_info)
        
        if not exists:
            result['issues'].append({
                'type': 'broken_child_path',
                'line': child['line'],
                'label': child['label'],
                'path': child['path'],
                'resolved': str(resolved) if resolved else None,
                'message': f"Child path does not exist: {child['path']}"
            })
        elif resolved and resolved.is_file():
            # Check if it's an AGENTS.md file
            if resolved.name != 'AGENTS.md':
                result['issues'].append({
                    'type': 'child_not_agents',
                    'line': child['line'],
                    'label': child['label'],
                    'path': child['path'],
                    'message': f"Child reference points to file that is not AGENTS.md: {resolved.name}"
                })
        elif resolved and resolved.is_dir():
            # Check if directory has AGENTS.md
            agents_in_dir = resolved / 'AGENTS.md'
            if not agents_in_dir.exists():
                result['issues'].append({
                    'type': 'child_missing_agents',
                    'line': child['line'],
                    'label': child['label'],
                    'path': child['path'],
                    'message': f"Child directory does not have AGENTS.md: {child['path']}"
                })
    
    # Extract navigation links
    nav_links = extract_navigation_links(content, file_path)
    for link in nav_links:
        exists, resolved = resolve_path(file_path, link['path'], repo_root)
        link_info = {
            **link,
            'exists': exists,
            'resolved': str(resolved) if resolved else None
        }
        result['navigation_links'].append(link_info)
        
        if not exists:
            result['issues'].append({
                'type': 'broken_nav_link',
                'line': link['line'],
                'label': link['label'],
                'path': link['path'],
                'resolved': str(resolved) if resolved else None,
                'message': f"Navigation link does not exist: {link['path']}"
            })
    
    # Extract key artifacts
    artifacts = extract_key_artifacts(content, file_path)
    for artifact in artifacts:
        exists, resolved = resolve_path(file_path, artifact['path'], repo_root)
        artifact_info = {
            **artifact,
            'exists': exists,
            'resolved': str(resolved) if resolved else None
        }
        result['key_artifacts'].append(artifact_info)
        
        if not exists:
            result['issues'].append({
                'type': 'broken_artifact',
                'line': artifact['line'],
                'label': artifact['label'],
                'path': artifact['path'],
                'resolved': str(resolved) if resolved else None,
                'message': f"Key artifact does not exist: {artifact['path']}"
            })
    
    return result

def main():
    """Main audit function."""
    repo_root = Path(__file__).parent.parent.parent
    print(f"Repository root: {repo_root}")
    
    # Find all AGENTS.md files
    print("Finding AGENTS.md files...")
    agents_files = find_agents_files(repo_root)
    print(f"Found {len(agents_files)} AGENTS.md files")
    
    # Audit each file
    print("Auditing files...")
    results = []
    for agents_file in agents_files:
        result = audit_agents_file(agents_file, repo_root)
        results.append(result)
        if result.get('issues'):
            print(f"  {result['file']}: {len(result['issues'])} issues")
    
    # Generate summary
    total_issues = sum(len(r.get('issues', [])) for r in results)
    generic_parents = sum(1 for r in results if r.get('parent') and r.get('parent', {}).get('is_generic'))
    broken_paths = sum(1 for r in results for issue in r.get('issues', []) if 'broken' in issue.get('type', ''))
    
    summary = {
        'total_files': len(agents_files),
        'total_issues': total_issues,
        'generic_parent_labels': generic_parents,
        'broken_paths': broken_paths,
        'files_with_issues': sum(1 for r in results if r.get('issues'))
    }
    
    # Save results
    output_file = repo_root / 'output' / 'agents_filepath_audit.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        'summary': summary,
        'results': results
    }
    
    with output_file.open('w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nAudit complete!")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Files with issues: {summary['files_with_issues']}")
    print(f"  Total issues: {summary['total_issues']}")
    print(f"  Generic parent labels: {summary['generic_parent_labels']}")
    print(f"  Broken paths: {summary['broken_paths']}")
    print(f"\nResults saved to: {output_file}")
    
    return report

if __name__ == '__main__':
    main()

