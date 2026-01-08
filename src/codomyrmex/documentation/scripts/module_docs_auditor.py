from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json
import os
import re
import sys


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides module_docs_auditor functionality including:
- 11 functions: main, __init__, find_modules...
- 1 classes: ModuleDocsAuditor

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Module Documentation Auditor

Scans all modules in src/codomyrmex/ to identify:
- Missing documentation files
- Broken internal references
- Inconsistent documentation structure
- Issues categorized by severity and fix complexity
"""



class ModuleDocsAuditor:
    """Brief description of ModuleDocsAuditor.

This class provides functionality for...

Attributes:
    # Add attribute descriptions here

Methods:
    # Method descriptions will be added automatically
"""
    def __init__(self, repo_root: Path):
    """Brief description of __init__.

Args:
    self : Description of self
    repo_root : Description of repo_root

    Returns: Description of return value
"""
        self.repo_root = repo_root.resolve()
        self.modules_dir = self.repo_root / 'src' / 'codomyrmex'
        self.issues = {
            'missing_files': defaultdict(list),
            'broken_references': defaultdict(list),
            'structure_issues': defaultdict(list),
            'inconsistent_patterns': []
        }
        
        # Required files for all modules
        self.required_files = {
            'README.md': 'Module overview',
            'AGENTS.md': 'Agent configuration',
            'SECURITY.md': 'Security considerations'
        }
        
        # Optional but commonly referenced files
        self.optional_files = {
            'API_SPECIFICATION.md': 'API documentation',
            'MCP_TOOL_SPECIFICATION.md': 'MCP tool specifications',
            'USAGE_EXAMPLES.md': 'Usage examples',
            'CHANGELOG.md': 'Version history',
            'requirements.txt': 'Dependencies'
        }
        
        # Standard docs/ structure
        self.standard_docs_files = {
            'docs/index.md': 'Documentation index',
            'docs/technical_overview.md': 'Technical architecture (optional)',
            'docs/tutorials/': 'Tutorials directory (optional)'
        }
    
    def find_modules(self) -> List[Path]:
        """Find all module directories in src/codomyrmex/."""
        modules = []
        if not self.modules_dir.exists():
            return modules
        
        for item in self.modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # Skip special directories
                if item.name in ['__pycache__', 'output', 'template']:
                    continue
                # Check if it's a module (has __init__.py or README.md)
                if (item / '__init__.py').exists() or (item / 'README.md').exists():
                    modules.append(item)
        
        return sorted(modules)
    
    def check_module_files(self, module_path: Path) -> Dict[str, List[str]]:
        """Check for required and optional files in a module."""
        module_name = module_path.name
        missing = {
            'required': [],
            'optional': []
        }
        
        # Check required files
        for filename, description in self.required_files.items():
            file_path = module_path / filename
            if not file_path.exists():
                missing['required'].append(f"{filename} ({description})")
        
        # Check optional files (but note if referenced)
        for filename, description in self.optional_files.items():
            file_path = module_path / filename
            if not file_path.exists():
                missing['optional'].append(f"{filename} ({description})")
        
        return missing
    
    def find_broken_references(self, module_path: Path) -> List[Dict]:
        """Find broken references in module documentation files."""
        broken_refs = []
        module_name = module_path.name
        
        # Find all markdown files in the module
        markdown_files = list(module_path.rglob('*.md'))
        
        for md_file in markdown_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                rel_path = md_file.relative_to(self.repo_root)
                
                # Extract markdown links
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                for match in re.finditer(link_pattern, content):
                    link_text = match.group(1)
                    link_url = match.group(2)
                    
                    # Skip external links
                    if link_url.startswith(('http://', 'https://', 'mailto:')):
                        continue
                    
                    # Skip anchor-only links
                    if link_url.startswith('#'):
                        continue
                    
                    # Remove anchor
                    clean_url = link_url.split('#')[0]
                    
                    # Resolve relative path
                    if clean_url.startswith('./'):
                        clean_url = clean_url[2:]
                    
                    if clean_url.startswith('../'):
                        # Count levels up
                        levels_up = clean_url.count('../')
                        base_dir = md_file.parent
                        for _ in range(levels_up):
                            base_dir = base_dir.parent
                        resolved = base_dir / clean_url.lstrip('../')
                    elif clean_url.startswith('/'):
                        resolved = self.repo_root / clean_url.lstrip('/')
                    else:
                        resolved = md_file.parent / clean_url
                    
                    # Check if file exists
                    if not resolved.exists():
                        # Check for common broken patterns
                        issue_type = None
                        if 'CONTRIBUTING.md' in clean_url:
                            issue_type = 'contributing_reference'
                        elif 'example_tutorial.md' in clean_url:
                            issue_type = 'example_tutorial_reference'
                        elif any(fname in clean_url for fname in ['API_SPECIFICATION.md', 'MCP_TOOL_SPECIFICATION.md', 'USAGE_EXAMPLES.md']):
                            issue_type = 'missing_doc_file'
                        
                        broken_refs.append({
                            'file': str(rel_path),
                            'line': content[:match.start()].count('\n') + 1,
                            'link_text': link_text,
                            'link_url': link_url,
                            'resolved': str(resolved),
                            'issue_type': issue_type or 'broken_link'
                        })
            except Exception as e:
                broken_refs.append({
                    'file': str(md_file.relative_to(self.repo_root)),
                    'line': 0,
                    'link_text': '',
                    'link_url': '',
                    'resolved': f'error: {str(e)}',
                    'issue_type': 'read_error'
                })
        
        return broken_refs
    
    def check_docs_structure(self, module_path: Path) -> List[str]:
        """Check if docs/ directory follows standard structure."""
        issues = []
        module_name = module_path.name
        docs_dir = module_path / 'docs'
        
        if not docs_dir.exists():
            return issues
        
        # Check for index.md
        if not (docs_dir / 'index.md').exists():
            issues.append("Missing docs/index.md")
        
        # Check if index.md references non-existent files
        index_file = docs_dir / 'index.md'
        if index_file.exists():
            try:
                content = index_file.read_text(encoding='utf-8')
                # Check for common broken references
                if '../CONTRIBUTING.md' in content or './CONTRIBUTING.md' in content:
                    issues.append("docs/index.md references non-existent CONTRIBUTING.md")
                if 'example_tutorial.md' in content and not (docs_dir / 'tutorials' / 'example_tutorial.md').exists():
                    issues.append("docs/index.md references missing example_tutorial.md")
            except Exception:
                pass
        
        return issues
    
    def audit_all_modules(self):
        """Audit all modules."""
        print("=" * 80)
        print("Module Documentation Auditor")
        print("=" * 80)
        print()
        
        modules = self.find_modules()
        print(f"Found {len(modules)} modules to audit\n")
        
        for module_path in modules:
            module_name = module_path.name
            print(f"Auditing {module_name}...")
            
            # Check for missing files
            missing = self.check_module_files(module_path)
            if missing['required']:
                self.issues['missing_files'][module_name].extend([
                    {'file': f, 'severity': 'required'} for f in missing['required']
                ])
            if missing['optional']:
                self.issues['missing_files'][module_name].extend([
                    {'file': f, 'severity': 'optional'} for f in missing['optional']
                ])
            
            # Find broken references
            broken_refs = self.find_broken_references(module_path)
            if broken_refs:
                self.issues['broken_references'][module_name] = broken_refs
            
            # Check docs structure
            structure_issues = self.check_docs_structure(module_path)
            if structure_issues:
                self.issues['structure_issues'][module_name] = structure_issues
        
        print(f"\n✅ Audit complete!\n")
    
    def generate_report(self) -> str:
        """Generate comprehensive audit report."""
        report = []
        report.append("# Module Documentation Audit Report\n")
        report.append("=" * 80)
        report.append("\n")
        
        # Summary
        total_modules = len(set(
            list(self.issues['missing_files'].keys()) +
            list(self.issues['broken_references'].keys()) +
            list(self.issues['structure_issues'].keys())
        ))
        
        total_issues = (
            sum(len(files) for files in self.issues['missing_files'].values()) +
            sum(len(refs) for refs in self.issues['broken_references'].values()) +
            sum(len(issues) for issues in self.issues['structure_issues'].values())
        )
        
        report.append("## Summary\n")
        report.append(f"- **Modules Audited**: {len(self.find_modules())}\n")
        report.append(f"- **Modules with Issues**: {total_modules}\n")
        report.append(f"- **Total Issues**: {total_issues}\n")
        report.append("\n")
        
        # Missing Files
        if self.issues['missing_files']:
            report.append("## Missing Files\n")
            for module_name, files in sorted(self.issues['missing_files'].items()):
                required = [f for f in files if f['severity'] == 'required']
                optional = [f for f in files if f['severity'] == 'optional']
                
                if required:
                    report.append(f"### {module_name} - Required Files\n")
                    for item in required:
                        report.append(f"- **{item['file']}**\n")
                    report.append("\n")
                
                if optional:
                    report.append(f"### {module_name} - Optional Files\n")
                    for item in optional:
                        report.append(f"- {item['file']}\n")
                    report.append("\n")
        
        # Broken References
        if self.issues['broken_references']:
            report.append("## Broken References\n")
            
            # Group by issue type
            by_type = defaultdict(lambda: defaultdict(list))
            for module_name, refs in self.issues['broken_references'].items():
                for ref in refs:
                    by_type[ref['issue_type']][module_name].append(ref)
            
            for issue_type, modules in sorted(by_type.items()):
                report.append(f"### {issue_type.replace('_', ' ').title()}\n")
                for module_name, refs in sorted(modules.items()):
                    report.append(f"**{module_name}** ({len(refs)} issues):\n")
                    for ref in refs[:10]:  # Limit to first 10
                        report.append(f"- `{ref['file']}` (line {ref['line']}): `{ref['link_url']}`\n")
                    if len(refs) > 10:
                        report.append(f"  ... and {len(refs) - 10} more\n")
                    report.append("\n")
        
        # Structure Issues
        if self.issues['structure_issues']:
            report.append("## Structure Issues\n")
            for module_name, issues in sorted(self.issues['structure_issues'].items()):
                report.append(f"### {module_name}\n")
                for issue in issues:
                    report.append(f"- {issue}\n")
                report.append("\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        report.append("1. Fix all CONTRIBUTING.md references to point to `../../docs/project/contributing.md`\n")
        report.append("2. Create placeholder example_tutorial.md files or remove references\n")
        report.append("3. Create missing API_SPECIFICATION.md and MCP_TOOL_SPECIFICATION.md files where referenced\n")
        report.append("4. Standardize docs/ structure across all modules\n")
        report.append("\n")
        report.append("=" * 80)
        
        return ''.join(report)
    
    def get_contributing_refs(self) -> List[Dict]:
        """Get all CONTRIBUTING.md references that need fixing."""
        refs = []
        for module_name, broken_refs in self.issues['broken_references'].items():
            for ref in broken_refs:
                if ref['issue_type'] == 'contributing_reference':
                    refs.append({
                        'module': module_name,
                        'file': ref['file'],
                        'line': ref['line'],
                        'link_url': ref['link_url']
                    })
        return refs
    
    def get_example_tutorial_refs(self) -> List[Dict]:
        """Get all example_tutorial.md references."""
        refs = []
        for module_name, broken_refs in self.issues['broken_references'].items():
            for ref in broken_refs:
                if ref['issue_type'] == 'example_tutorial_reference':
                    refs.append({
                        'module': module_name,
                        'file': ref['file'],
                        'line': ref['line'],
                        'link_url': ref['link_url'],
                        'resolved': ref['resolved']
                    })
        return refs
    
    def get_missing_doc_files(self) -> Dict[str, List[str]]:
        """Get missing documentation files that are referenced."""
        missing = defaultdict(set)
        for module_name, broken_refs in self.issues['broken_references'].items():
            for ref in broken_refs:
                if ref['issue_type'] == 'missing_doc_file':
                    # Extract filename from resolved path
                    filename = Path(ref['resolved']).name
                    missing[module_name].add(filename)
        return {k: sorted(list(v)) for k, v in missing.items()}


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    auditor = ModuleDocsAuditor(repo_root)
    auditor.audit_all_modules()
    
    # Generate report
    report = auditor.generate_report()
    print(report)
    
    # Save detailed report
    report_path = repo_root / 'docs' / 'project' / 'module-documentation-audit.md'
    report_path.write_text(report, encoding='utf-8')
    print(f"\n📄 Detailed report saved to: {report_path.relative_to(repo_root)}")
    
    # Save structured data for fixing
    data_path = repo_root / 'scripts' / 'documentation' / 'module_audit_data.json'
    audit_data = {
        'contributing_refs': auditor.get_contributing_refs(),
        'example_tutorial_refs': auditor.get_example_tutorial_refs(),
        'missing_doc_files': auditor.get_missing_doc_files()
    }
    data_path.write_text(json.dumps(audit_data, indent=2), encoding='utf-8')
    print(f"📊 Structured data saved to: {data_path.relative_to(repo_root)}")
    
    # Return exit code
    total_issues = (
        sum(len(files) for files in auditor.issues['missing_files'].values()) +
        sum(len(refs) for refs in auditor.issues['broken_references'].values()) +
        sum(len(issues) for issues in auditor.issues['structure_issues'].values())
    )
    return 1 if total_issues > 0 else 0


if __name__ == '__main__':
    sys.exit(main())

