from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
import argparse
import ast
import json
import logging
import re
import sys
import time

from dataclasses import dataclass, asdict

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging




























































#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides comprehensive_filepath_audit functionality including:
- 18 functions: main, to_dict, __init__...
- 7 classes: BrokenLink, SignpostingIssue, StructureIssue...

Usage:
    # Example usage here
"""
Comprehensive Filepath and Signpost Audit for Codomyrmex Repository.

This script performs a complete repository-wide audit of:
1. All markdown links across the entire repository
2. Signposting sections in AGENTS.md files
3. Folder structure validation
4. Code import and file reference validation
5. Configuration file reference validation
6. Cross-reference validation

Generates comprehensive reports for all audit areas.
"""


try:
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class BrokenLink:
    """Represents a broken link."""
    file_path: str
    line_number: int
    link_text: str
    link_url: str
    resolved_path: str
    issue_type: str


@dataclass
class SignpostingIssue:
    """Represents a signposting issue."""
    file_path: str
    section: str  # 'Parent', 'Self', 'Children', 'Key Artifacts'
    issue_type: str
    description: str
    severity: str


@dataclass
class StructureIssue:
    """Represents a folder structure issue."""
    file_path: str
    documented_path: str
    actual_path: Optional[str]
    issue_type: str  # 'missing', 'extra', 'mismatch'
    description: str


@dataclass
class CodeReferenceIssue:
    """Represents a code import/reference issue."""
    file_path: str
    line_number: int
    reference: str
    issue_type: str  # 'broken_import', 'missing_file'
    description: str


@dataclass
class ConfigReferenceIssue:
    """Represents a configuration file reference issue."""
    config_file: str
    reference: str
    issue_type: str
    description: str


@dataclass
class ComprehensiveAuditReport:
    """Comprehensive audit report."""
    timestamp: str
    repo_root: str
    
    # Link validation
    total_markdown_files: int
    total_links: int
    broken_links: List[BrokenLink]
    
    # Signposting audit
    total_agents_files: int
    signposting_issues: List[SignpostingIssue]
    
    # Structure validation
    structure_issues: List[StructureIssue]
    
    # Code reference validation
    code_reference_issues: List[CodeReferenceIssue]
    
    # Config reference validation
    config_reference_issues: List[ConfigReferenceIssue]
    
    # Summary
    validation_time: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp,
            'repo_root': self.repo_root,
            'link_validation': {
                'total_markdown_files': self.total_markdown_files,
                'total_links': self.total_links,
                'broken_links_count': len(self.broken_links),
                'broken_links': [asdict(link) for link in self.broken_links]
            },
            'signposting_audit': {
                'total_agents_files': self.total_agents_files,
                'issues_count': len(self.signposting_issues),
                'issues': [asdict(issue) for issue in self.signposting_issues]
            },
            'structure_validation': {
                'issues_count': len(self.structure_issues),
                'issues': [asdict(issue) for issue in self.structure_issues]
            },
            'code_reference_validation': {
                'issues_count': len(self.code_reference_issues),
                'issues': [asdict(issue) for issue in self.code_reference_issues]
            },
            'config_reference_validation': {
                'issues_count': len(self.config_reference_issues),
                'issues': [asdict(issue) for issue in self.config_reference_issues]
            },
            'summary': {
                'total_issues': (
                    len(self.broken_links) +
                    len(self.signposting_issues) +
                    len(self.structure_issues) +
                    len(self.code_reference_issues) +
                    len(self.config_reference_issues)
                ),
                'validation_time': self.validation_time
            }
        }


class ComprehensiveFilepathAuditor:
    """Comprehensive filepath and signpost auditor."""
    
    def __init__(self, repo_root: Path):
        """Initialize auditor."""
        self.repo_root = repo_root.resolve()
        self.broken_links: List[BrokenLink] = []
        self.signposting_issues: List[SignpostingIssue] = []
        self.structure_issues: List[StructureIssue] = []
        self.code_reference_issues: List[CodeReferenceIssue] = []
        self.config_reference_issues: List[ConfigReferenceIssue] = []
        self.markdown_files: Set[Path] = set()
        self.agents_files: Set[Path] = set()
        
    def find_all_markdown_files(self) -> Set[Path]:
        """Find all markdown files in repository."""
        logger.info("Scanning for markdown files...")
        md_files = set()
        
        for pattern in ['**/*.md', '**/*.MD']:
            md_files.update(self.repo_root.glob(pattern))
        
        # Filter out files in ignored directories
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache'}
        filtered_files = {
            f for f in md_files 
            if not any(ignored in f.parts for ignored in ignored_dirs)
        }
        
        logger.info(f"Found {len(filtered_files)} markdown files")
        return filtered_files
    
    def extract_links(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Extract markdown links from a file."""
        links = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Match markdown links: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for line_num, line in enumerate(content.split('\n'), 1):
                for match in re.finditer(link_pattern, line):
                    link_text = match.group(1)
                    link_url = match.group(2)
                    
                    # Skip anchor-only links
                    if link_url.startswith('#'):
                        continue
                    
                    links.append((line_num, link_text, link_url))
        
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
        
        return links
    
    def resolve_internal_link(self, source_file: Path, link_url: str) -> Tuple[bool, Optional[Path], str]:
        """Resolve an internal link relative to source file."""
        # Remove anchor if present
        anchor = None
        if '#' in link_url:
            parts = link_url.split('#', 1)
            link_url = parts[0]
            anchor = parts[1]
        
        if not link_url:
            return (True, None, 'anchor')
        
        # Skip external URLs
        if link_url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return (True, None, 'external')
        
        # Handle absolute and relative paths
        if link_url.startswith('/'):
            # Absolute from repo root
            target = self.repo_root / link_url.lstrip('/')
        elif link_url.startswith('../'):
            # Relative with parent directory navigation
            levels_up = link_url.count('../')
            current_dir = source_file.parent
            for _ in range(levels_up):
                if current_dir == self.repo_root:
                    break
                current_dir = current_dir.parent
            link_url = link_url.lstrip('../')
            target = current_dir / link_url
        elif link_url.startswith('./'):
            # Relative to current directory
            target = source_file.parent / link_url[2:]
        else:
            # Relative to current file's directory
            target = source_file.parent / link_url
        
        # Normalize path
        try:
            target = target.resolve()
            # Check if within repo
            try:
                target.relative_to(self.repo_root)
            except ValueError:
                return (False, target, 'outside_repo')
        except Exception:
            pass
        
        # Check if file or directory exists
        exists = target.exists() and (target.is_file() or target.is_dir())
        
        return (exists, target, 'internal')
    
    def validate_all_links(self) -> Tuple[int, int]:
        """Validate all links in markdown files."""
        logger.info("Validating all markdown links...")
        
        self.markdown_files = self.find_all_markdown_files()
        total_links = 0
        
        for md_file in self.markdown_files:
            links = self.extract_links(md_file)
            total_links += len(links)
            
            for line_num, link_text, link_url in links:
                exists, target, link_type = self.resolve_internal_link(md_file, link_url)
                
                if not exists and link_type == 'internal':
                    try:
                        resolved_str = str(target.relative_to(self.repo_root))
                    except ValueError:
                        resolved_str = str(target)
                    
                    self.broken_links.append(BrokenLink(
                        file_path=str(md_file.relative_to(self.repo_root)),
                        line_number=line_num,
                        link_text=link_text,
                        link_url=link_url,
                        resolved_path=resolved_str,
                        issue_type='broken_internal'
                    ))
        
        logger.info(f"Found {len(self.broken_links)} broken links out of {total_links} total links")
        return len(self.markdown_files), total_links
    
    def find_all_agents_files(self) -> Set[Path]:
        """Find all AGENTS.md files."""
        agents_files = set(self.repo_root.glob('**/AGENTS.md'))
        
        # Filter out ignored directories
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache'}
        filtered = {
            f for f in agents_files
            if not any(ignored in f.parts for ignored in ignored_dirs)
        }
        
        return filtered
    
    def extract_signposting_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a signposting section from AGENTS.md."""
        # Look for "## Signposting" section
        signposting_match = re.search(
            r'##\s+Signposting\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not signposting_match:
            return None
        
        signposting_content = signposting_match.group(1)
        
        # Extract specific section
        section_pattern = rf'-?\s*\*\*{section_name}\*\*:\s*(.*?)(?=\n\s*-?\s*\*\*|\Z)'
        section_match = re.search(section_pattern, signposting_content, re.DOTALL | re.MULTILINE)
        
        if section_match:
            return section_match.group(1).strip()
        
        return None
    
    def validate_signposting(self) -> int:
        """Validate signposting in all AGENTS.md files."""
        logger.info("Validating signposting sections...")
        
        self.agents_files = self.find_all_agents_files()
        
        for agents_file in self.agents_files:
            try:
                content = agents_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for signposting section
                if '## Signposting' not in content:
                    self.signposting_issues.append(SignpostingIssue(
                        file_path=str(agents_file.relative_to(self.repo_root)),
                        section='Signposting',
                        issue_type='missing_section',
                        description='Missing Signposting section',
                        severity='error'
                    ))
                    continue
                
                # Validate Parent
                parent_content = self.extract_signposting_section(content, 'Parent')
                if parent_content:
                    # Extract links from parent content
                    parent_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', parent_content)
                    for link_text, link_path in parent_links:
                        exists, target, _ = self.resolve_internal_link(agents_file, link_path)
                        if not exists:
                            self.signposting_issues.append(SignpostingIssue(
                                file_path=str(agents_file.relative_to(self.repo_root)),
                                section='Parent',
                                issue_type='broken_link',
                                description=f'Parent link broken: [{link_text}]({link_path})',
                                severity='error'
                            ))
                
                # Validate Self
                self_content = self.extract_signposting_section(content, 'Self')
                if self_content:
                    self_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', self_content)
                    for link_text, link_path in self_links:
                        # Self should link to current file
                        if link_path != 'AGENTS.md' and not link_path.endswith('/AGENTS.md'):
                            self.signposting_issues.append(SignpostingIssue(
                                file_path=str(agents_file.relative_to(self.repo_root)),
                                section='Self',
                                issue_type='incorrect_link',
                                description=f'Self link should point to AGENTS.md: [{link_text}]({link_path})',
                                severity='warning'
                            ))
                
                # Validate Children
                children_content = self.extract_signposting_section(content, 'Children')
                if children_content:
                    # Extract child directory names
                    child_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', children_content)
                    for link_text, link_path in child_links:
                        exists, target, _ = self.resolve_internal_link(agents_file, link_path)
                        if not exists:
                            self.signposting_issues.append(SignpostingIssue(
                                file_path=str(agents_file.relative_to(self.repo_root)),
                                section='Children',
                                issue_type='broken_link',
                                description=f'Child link broken: [{link_text}]({link_path})',
                                severity='error'
                            ))
                    
                    # Check if all subdirectories with AGENTS.md are listed
                    agents_dir = agents_file.parent
                    actual_children = set()
                    for item in agents_dir.iterdir():
                        if item.is_dir() and (item / 'AGENTS.md').exists():
                            actual_children.add(item.name)
                    
                    documented_children = {link_text for link_text, _ in child_links}
                    missing_children = actual_children - documented_children
                    if missing_children:
                        self.signposting_issues.append(SignpostingIssue(
                            file_path=str(agents_file.relative_to(self.repo_root)),
                            section='Children',
                            issue_type='missing_child',
                            description=f'Missing children in signposting: {", ".join(sorted(missing_children))}',
                            severity='error'
                        ))
                
                # Validate Key Artifacts
                artifacts_content = self.extract_signposting_section(content, 'Key Artifacts')
                if artifacts_content:
                    artifact_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', artifacts_content)
                    for link_text, link_path in artifact_links:
                        exists, target, _ = self.resolve_internal_link(agents_file, link_path)
                        if not exists:
                            self.signposting_issues.append(SignpostingIssue(
                                file_path=str(agents_file.relative_to(self.repo_root)),
                                section='Key Artifacts',
                                issue_type='broken_link',
                                description=f'Key artifact link broken: [{link_text}]({link_path})',
                                severity='error'
                            ))
            
            except Exception as e:
                logger.warning(f"Error validating signposting in {agents_file}: {e}")
                self.signposting_issues.append(SignpostingIssue(
                    file_path=str(agents_file.relative_to(self.repo_root)),
                    section='Signposting',
                    issue_type='validation_error',
                    description=f'Error validating signposting: {str(e)}',
                    severity='warning'
                ))
        
        logger.info(f"Found {len(self.signposting_issues)} signposting issues")
        return len(self.agents_files)
    
    def validate_folder_structure(self):
        """Validate folder structures match documentation."""
        logger.info("Validating folder structures...")
        
        # Check documented structures in README.md files
        for readme_file in self.repo_root.glob('**/README.md'):
            try:
                content = readme_file.read_text(encoding='utf-8', errors='ignore')
                
                # Extract folder structure from code blocks
                structure_pattern = r'```[^\n]*\n(.*?)```'
                structures = re.findall(structure_pattern, content, re.DOTALL)
                
                for structure in structures:
                    # Parse directory tree structure
                    lines = structure.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # Extract directory/file names from tree structure
                        # Handle patterns like: ├── dir/, │   ├── file, └── file
                        if '──' in line or '│' in line:
                            # Extract the actual path
                            path_match = re.search(r'[├└│]\s*──\s*([^\s]+)', line)
                            if path_match:
                                path_str = path_match.group(1)
                                # Resolve relative to README location
                                readme_dir = readme_file.parent
                                if path_str.startswith('/'):
                                    target = self.repo_root / path_str.lstrip('/')
                                else:
                                    target = readme_dir / path_str
                                
                                if not target.exists():
                                    self.structure_issues.append(StructureIssue(
                                        file_path=str(readme_file.relative_to(self.repo_root)),
                                        documented_path=str(target.relative_to(self.repo_root)),
                                        actual_path=None,
                                        issue_type='missing',
                                        description=f'Documented path does not exist: {path_str}'
                                    ))
            
            except Exception as e:
                logger.debug(f"Error validating structure in {readme_file}: {e}")
        
        logger.info(f"Found {len(self.structure_issues)} structure issues")
    
    def validate_code_imports(self):
        """Validate Python import statements and file references."""
        logger.info("Validating code imports and file references...")
        
        # Find all Python files
        python_files = set(self.repo_root.glob('**/*.py'))
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.pytest_cache', '__pycache__'}
        filtered_python = {
            f for f in python_files
            if not any(ignored in f.parts for ignored in ignored_dirs)
        }
        
        for py_file in filtered_python:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                
                # Parse AST to find imports
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._check_import(py_file, alias.name, node.lineno)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._check_import(py_file, node.module, node.lineno)
                
                except SyntaxError:
                    # Skip files with syntax errors
                    continue
                
                # Check for file path references (Path, open, etc.)
                path_patterns = [
                    r'Path\(["\']([^"\']+)["\']\)',
                    r'open\(["\']([^"\']+)["\']',
                    r'["\']([^"\']+\.(?:py|md|json|yaml|yml|txt|toml))["\']'  # noqa: W605
                ]
                
                for line_num, line in enumerate(content.split('\n'), 1):
                    for pattern in path_patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            file_ref = match.group(1)
                            # Skip if it's clearly a URL or external reference
                            if file_ref.startswith(('http://', 'https://', 'ftp://')):
                                continue
                            
                            # Resolve relative to current file
                            if file_ref.startswith('/'):
                                target = self.repo_root / file_ref.lstrip('/')
                            else:
                                target = py_file.parent / file_ref
                            
                            if not target.exists() and not target.is_absolute():
                                self.code_reference_issues.append(CodeReferenceIssue(
                                    file_path=str(py_file.relative_to(self.repo_root)),
                                    line_number=line_num,
                                    reference=file_ref,
                                    issue_type='missing_file',
                                    description=f'Referenced file does not exist: {file_ref}'
                                ))
            
            except Exception as e:
                logger.debug(f"Error validating imports in {py_file}: {e}")
        
        logger.info(f"Found {len(self.code_reference_issues)} code reference issues")
    
    def _check_import(self, py_file: Path, module_name: str, line_num: int):
        """Check if an import resolves correctly."""
        # Skip standard library and external packages (basic check)
        if '.' not in module_name or module_name.startswith(('http', 'https')):
            return
        
        # Check for codomyrmex imports
        if module_name.startswith('codomyrmex'):
            # Resolve to source file
            module_path = module_name.replace('.', '/')
            # Try different possible locations
            possible_paths = [
                self.repo_root / 'src' / f'{module_path}.py',
                self.repo_root / 'src' / module_path / '__init__.py',
            ]
            
            found = False
            for possible_path in possible_paths:
                if possible_path.exists():
                    found = True
                    break
            
            if not found:
                self.code_reference_issues.append(CodeReferenceIssue(
                    file_path=str(py_file.relative_to(self.repo_root)),
                    line_number=line_num,
                    reference=module_name,
                    issue_type='broken_import',
                    description=f'Import cannot be resolved: {module_name}'
                ))
    
    def validate_config_references(self):
        """Validate file references in configuration files."""
        logger.info("Validating configuration file references...")
        
        config_files = [
            self.repo_root / 'pyproject.toml',
            self.repo_root / 'package.json',
            self.repo_root / 'pytest.ini',
            self.repo_root / 'Makefile',
            self.repo_root / 'resources.json',
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                continue
            
            try:
                content = config_file.read_text(encoding='utf-8', errors='ignore')
                
                # Extract file references based on file type
                if config_file.suffix == '.toml':
                    # Look for path references in TOML
                    path_pattern = r'["\']([^"\']+\.(?:py|md|json|yaml|yml|txt))["\']'
                    matches = re.finditer(path_pattern, content)
                    for match in matches:
                        file_ref = match.group(1)
                        self._check_config_reference(config_file, file_ref)
                
                elif config_file.suffix == '.json':
                    # Look for path references in JSON
                    path_pattern = r'["\']([^"\']+\.(?:py|md|json|yaml|yml|txt))["\']'
                    matches = re.finditer(path_pattern, content)
                    for match in matches:
                        file_ref = match.group(1)
                        self._check_config_reference(config_file, file_ref)
                
                elif config_file.name == 'Makefile':
                    # Look for script references in Makefile
                    script_pattern = r'(?:python|uv|python3)\s+([^\s]+\.py)'
                    matches = re.finditer(script_pattern, content)
                    for match in matches:
                        script_ref = match.group(1)
                        self._check_config_reference(config_file, script_ref)
            
            except Exception as e:
                logger.debug(f"Error validating config file {config_file}: {e}")
        
        logger.info(f"Found {len(self.config_reference_issues)} config reference issues")
    
    def _check_config_reference(self, config_file: Path, file_ref: str):
        """Check if a config file reference exists."""
        # Skip URLs and external references
        if file_ref.startswith(('http://', 'https://', 'ftp://')):
            return
        
        # Resolve relative to config file
        if file_ref.startswith('/'):
            target = self.repo_root / file_ref.lstrip('/')
        else:
            target = config_file.parent / file_ref
        
        if not target.exists():
            self.config_reference_issues.append(ConfigReferenceIssue(
                config_file=str(config_file.relative_to(self.repo_root)),
                reference=file_ref,
                issue_type='missing_file',
                description=f'Referenced file does not exist: {file_ref}'
            ))
    
    def run_comprehensive_audit(self) -> ComprehensiveAuditReport:
        """Run comprehensive audit."""
        start_time = time.time()
        
        logger.info("="*80)
        logger.info("Starting Comprehensive Filepath and Signpost Audit")
        logger.info("="*80)
        
        # Phase 1: Link validation
        total_md_files, total_links = self.validate_all_links()
        
        # Phase 2: Signposting audit
        total_agents = self.validate_signposting()
        
        # Phase 3: Structure validation
        self.validate_folder_structure()
        
        # Phase 4: Code reference validation
        self.validate_code_imports()
        
        # Phase 5: Config reference validation
        self.validate_config_references()
        
        validation_time = time.time() - start_time
        
        report = ComprehensiveAuditReport(
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            repo_root=str(self.repo_root),
            total_markdown_files=total_md_files,
            total_links=total_links,
            broken_links=self.broken_links,
            total_agents_files=total_agents,
            signposting_issues=self.signposting_issues,
            structure_issues=self.structure_issues,
            code_reference_issues=self.code_reference_issues,
            config_reference_issues=self.config_reference_issues,
            validation_time=validation_time
        )
        
        logger.info("="*80)
        logger.info("Comprehensive Audit Complete")
        logger.info("="*80)
        logger.info(f"Validation time: {validation_time:.2f}s")
        
        return report
    
    def export_report(self, report: ComprehensiveAuditReport, output_path: Path, format: str = "json") -> Path:
        """Export audit report."""
        output_path.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            output_file = output_path / "comprehensive_filepath_audit.json"
            output_file.write_text(json.dumps(report.to_dict(), indent=2))
            logger.info(f"Report exported to {output_file}")
            return output_file
        
        elif format == "html":
            output_file = output_path / "comprehensive_filepath_audit.html"
            html_content = self._generate_html_report(report)
            output_file.write_text(html_content)
            logger.info(f"HTML report exported to {output_file}")
            return output_file
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, report: ComprehensiveAuditReport) -> str:
        """Generate HTML report."""
        total_issues = (
            len(report.broken_links) +
            len(report.signposting_issues) +
            len(report.structure_issues) +
            len(report.code_reference_issues) +
            len(report.config_reference_issues)
        )
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Filepath and Signpost Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .success {{ color: #388e3c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        .section {{ margin: 30px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Comprehensive Filepath and Signpost Audit Report</h1>
        <p><strong>Generated:</strong> {report.timestamp}</p>
        <p><strong>Repository:</strong> <code>{report.repo_root}</code></p>
        
        <div class="summary">
            <h2>Summary</h2>
            <div class="stat">
                <div class="stat-value">{report.total_markdown_files}</div>
                <div class="stat-label">Markdown Files</div>
            </div>
            <div class="stat">
                <div class="stat-value">{report.total_links}</div>
                <div class="stat-label">Total Links</div>
            </div>
            <div class="stat">
                <div class="stat-value {'error' if len(report.broken_links) > 0 else 'success'}">{len(report.broken_links)}</div>
                <div class="stat-label">Broken Links</div>
            </div>
            <div class="stat">
                <div class="stat-value {'error' if len(report.signposting_issues) > 0 else 'success'}">{len(report.signposting_issues)}</div>
                <div class="stat-label">Signposting Issues</div>
            </div>
            <div class="stat">
                <div class="stat-value {'error' if total_issues > 0 else 'success'}">{total_issues}</div>
                <div class="stat-label">Total Issues</div>
            </div>
        </div>
"""
        
        # Broken Links Section
        if report.broken_links:
            html += """
        <div class="section">
            <h2>Broken Links</h2>
            <table>
                <tr>
                    <th>File</th>
                    <th>Line</th>
                    <th>Link Text</th>
                    <th>Target</th>
                </tr>
"""
            for link in report.broken_links[:100]:  # Limit to first 100
                html += f"""
                <tr>
                    <td><code>{link.file_path}</code></td>
                    <td>{link.line_number}</td>
                    <td>{link.link_text}</td>
                    <td><code>{link.resolved_path}</code></td>
                </tr>
"""
            if len(report.broken_links) > 100:
                html += f"""
                <tr>
                    <td colspan="4"><em>... and {len(report.broken_links) - 100} more broken links</em></td>
                </tr>
"""
            html += "            </table>\n        </div>\n"
        
        # Signposting Issues Section
        if report.signposting_issues:
            html += """
        <div class="section">
            <h2>Signposting Issues</h2>
            <table>
                <tr>
                    <th>File</th>
                    <th>Section</th>
                    <th>Issue Type</th>
                    <th>Description</th>
                </tr>
"""
            for issue in report.signposting_issues:
                html += f"""
                <tr>
                    <td><code>{issue.file_path}</code></td>
                    <td>{issue.section}</td>
                    <td class="{issue.severity}">{issue.issue_type}</td>
                    <td>{issue.description}</td>
                </tr>
"""
            html += "            </table>\n        </div>\n"
        
        # Structure Issues Section
        if report.structure_issues:
            html += """
        <div class="section">
            <h2>Structure Issues</h2>
            <table>
                <tr>
                    <th>Documented Path</th>
                    <th>Issue Type</th>
                    <th>Description</th>
                </tr>
"""
            for issue in report.structure_issues:
                html += f"""
                <tr>
                    <td><code>{issue.documented_path}</code></td>
                    <td>{issue.issue_type}</td>
                    <td>{issue.description}</td>
                </tr>
"""
            html += "            </table>\n        </div>\n"
        
        # Code Reference Issues Section
        if report.code_reference_issues:
            html += """
        <div class="section">
            <h2>Code Reference Issues</h2>
            <table>
                <tr>
                    <th>File</th>
                    <th>Line</th>
                    <th>Reference</th>
                    <th>Issue</th>
                </tr>
"""
            for issue in report.code_reference_issues[:50]:  # Limit to first 50
                html += f"""
                <tr>
                    <td><code>{issue.file_path}</code></td>
                    <td>{issue.line_number}</td>
                    <td><code>{issue.reference}</code></td>
                    <td>{issue.description}</td>
                </tr>
"""
            if len(report.code_reference_issues) > 50:
                html += f"""
                <tr>
                    <td colspan="4"><em>... and {len(report.code_reference_issues) - 50} more issues</em></td>
                </tr>
"""
            html += "            </table>\n        </div>\n"
        
        # Config Reference Issues Section
        if report.config_reference_issues:
            html += """
        <div class="section">
            <h2>Configuration Reference Issues</h2>
            <table>
                <tr>
                    <th>Config File</th>
                    <th>Reference</th>
                    <th>Issue</th>
                </tr>
"""
            for issue in report.config_reference_issues:
                html += f"""
                <tr>
                    <td><code>{issue.config_file}</code></td>
                    <td><code>{issue.reference}</code></td>
                    <td>{issue.description}</td>
                </tr>
"""
            html += "            </table>\n        </div>\n"
        
        html += f"""
        <p><small>Validation completed in {report.validation_time:.2f} seconds</small></p>
    </div>
</body>
</html>
"""
        return html


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Comprehensive filepath and signpost audit for Codomyrmex repository"
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path.cwd(),
        help='Repository root directory'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output'),
        help='Output directory for results'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'html', 'both'],
        default='both',
        help='Output format'
    )
    parser.add_argument(
        '--fail-on-issues',
        action='store_true',
        help='Exit with error code if issues found'
    )
    
    args = parser.parse_args()
    
    # Run audit
    auditor = ComprehensiveFilepathAuditor(args.repo_root)
    report = auditor.run_comprehensive_audit()
    
    # Export results
    if args.format in ['json', 'both']:
        auditor.export_report(report, args.output, 'json')
    
    if args.format in ['html', 'both']:
        auditor.export_report(report, args.output, 'html')
    
    # Print summary
    print("\n" + "="*80)
    print("COMPREHENSIVE FILEPATH AND SIGNPOST AUDIT SUMMARY")
    print("="*80)
    print(f"Markdown files scanned: {report.total_markdown_files}")
    print(f"Total links: {report.total_links}")
    print(f"Broken links: {len(report.broken_links)}")
    print(f"AGENTS.md files: {report.total_agents_files}")
    print(f"Signposting issues: {len(report.signposting_issues)}")
    print(f"Structure issues: {len(report.structure_issues)}")
    print(f"Code reference issues: {len(report.code_reference_issues)}")
    print(f"Config reference issues: {len(report.config_reference_issues)}")
    total_issues = (
        len(report.broken_links) +
        len(report.signposting_issues) +
        len(report.structure_issues) +
        len(report.code_reference_issues) +
        len(report.config_reference_issues)
    )
    print(f"Total issues: {total_issues}")
    print(f"Validation time: {report.validation_time:.2f}s")
    print("="*80)
    
    # Exit with error if requested and issues found
    if args.fail_on_issues and total_issues > 0:
        print("\n❌ Audit failed: issues found")
        sys.exit(1)
    
    if total_issues == 0:
        print("\n✅ Audit complete! No issues found.")
    else:
        print(f"\n⚠️  Audit complete! Found {total_issues} issues. See report for details.")
    
    sys.exit(0)


if __name__ == '__main__':
    main()

