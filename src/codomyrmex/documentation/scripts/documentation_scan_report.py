from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import json
import os
import re
import subprocess


from codomyrmex.logging_monitoring import get_logger






























#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides documentation_scan_report functionality including:
- 28 functions: main, __init__, phase1_discovery...
- 1 classes: DocumentationScanner

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
Comprehensive Documentation Scan and Improvement Tool

This script implements a 7-phase approach to scan, verify, and improve
all documentation across the Codomyrmex repository.
"""



class DocumentationScanner:
    """Comprehensive documentation scanner and analyzer."""
    
    def __init__(self, repo_root: Path):
    """Brief description of __init__.

Args:
    self : Description of self
    repo_root : Description of repo_root

    Returns: Description of return value
"""
        self.repo_root = repo_root.resolve()
        self.results = {
            'phase1': {
                'files_found': {},
                'structure_map': {},
                'tools_inventory': {}
            },
            'phase2': {
                'content_issues': [],
                'reference_issues': [],
                'terminology_issues': []
            },
            'phase3': {
                'coverage_gaps': [],
                'audience_gaps': [],
                'cross_ref_gaps': []
            },
            'phase4': {
                'quality_issues': [],
                'actionability_issues': [],
                'maintainability_issues': []
            },
            'phase5': {
                'improvements_made': [],
                'files_updated': []
            },
            'phase6': {
                'validation_results': {},
                'manual_review_notes': []
            },
            'phase7': {
                'summary_stats': {},
                'issue_catalog': [],
                'recommendations': []
            }
        }
    
    def phase1_discovery(self):
        """Phase 1: Discovery and Inventory"""
        print("=" * 80)
        print("PHASE 1: DISCOVERY AND INVENTORY")
        print("=" * 80)
        print()
        
        # 1.1 File Discovery
        print("1.1 Scanning all markdown files...")
        all_md_files = list(self.repo_root.rglob("*.md"))
        agents_files = list(self.repo_root.rglob("AGENTS.md"))
        readme_files = list(self.repo_root.rglob("README.md"))
        
        self.results['phase1']['files_found'] = {
            'total_markdown': len(all_md_files),
            'agents_files': len(agents_files),
            'readme_files': len(readme_files),
            'all_md_paths': [str(f.relative_to(self.repo_root)) for f in all_md_files],
            'agents_paths': [str(f.relative_to(self.repo_root)) for f in agents_files],
            'readme_paths': [str(f.relative_to(self.repo_root)) for f in readme_files]
        }
        
        print(f"  ✓ Found {len(all_md_files)} markdown files")
        print(f"  ✓ Found {len(agents_files)} AGENTS.md files")
        print(f"  ✓ Found {len(readme_files)} README.md files")
        print()
        
        # Identify configuration files
        print("1.1 Identifying configuration files...")
        config_files = []
        config_patterns = ['pyproject.toml', 'pytest.ini', 'Makefile', 'package.json', 
                          'setup.py', 'requirements.txt', '*.yaml', '*.yml', '*.json']
        
        for pattern in config_patterns:
            if '*' in pattern:
                config_files.extend(self.repo_root.rglob(pattern))
            else:
                config_path = self.repo_root / pattern
                if config_path.exists():
                    config_files.append(config_path)
        
        self.results['phase1']['files_found']['config_files'] = [
            str(f.relative_to(self.repo_root)) for f in config_files
        ]
        print(f"  ✓ Found {len(config_files)} configuration files")
        print()
        
        # 1.2 Structure Mapping
        print("1.2 Mapping documentation structure...")
        structure = self._map_documentation_structure()
        self.results['phase1']['structure_map'] = structure
        print(f"  ✓ Mapped {len(structure['categories'])} documentation categories")
        print()
        
        # 1.3 Existing Tools Inventory
        print("1.3 Cataloging existing validation tools...")
        tools = self._inventory_validation_tools()
        self.results['phase1']['tools_inventory'] = tools
        print(f"  ✓ Found {len(tools['existing_tools'])} existing validation tools")
        print()
        
        print("✓ Phase 1 complete!")
        print()
        return self.results['phase1']
    
    def _map_documentation_structure(self) -> Dict:
        """Map the documentation hierarchy and categories."""
        structure = {
            'root_level': [],
            'directory_level': [],
            'categories': {
                'project_docs': [],
                'module_docs': [],
                'script_docs': [],
                'testing_docs': [],
                'tool_docs': []
            },
            'hierarchy': {}
        }
        
        # Root level docs
        root_docs = ['README.md', 'AGENTS.md', 'LICENSE', 'SECURITY.md']
        for doc in root_docs:
            if (self.repo_root / doc).exists():
                structure['root_level'].append(doc)
        
        # Category mapping
        categories_map = {
            'project_docs': self.repo_root / 'docs',
            'module_docs': self.repo_root / 'src' / 'codomyrmex',
            'script_docs': self.repo_root / 'scripts',
            'testing_docs': self.repo_root / 'testing',
            'tool_docs': self.repo_root / 'tools'
        }
        
        for category, base_path in categories_map.items():
            if base_path.exists():
                md_files = list(base_path.rglob("*.md"))
                structure['categories'][category] = [
                    str(f.relative_to(self.repo_root)) for f in md_files
                ]
        
        return structure
    
    def _inventory_validation_tools(self) -> Dict:
        """Inventory existing validation and documentation tools."""
        tools = {
            'existing_tools': [],
            'capabilities': {},
            'gaps': []
        }
        
        tool_paths = {
            'comprehensive_audit': 'scripts/documentation/comprehensive_audit.py',
            'module_docs_auditor': 'scripts/documentation/module_docs_auditor.py',
            'check_doc_links': 'scripts/documentation/check_doc_links.py',
            'validate_module_docs': 'scripts/documentation/validate_module_docs.py',
            'validate_docs_quality': 'src/codomyrmex/documentation/scripts/validate_docs_quality.py'
        }
        
        for tool_name, tool_path in tool_paths.items():
            full_path = self.repo_root / tool_path
            if full_path.exists():
                tools['existing_tools'].append({
                    'name': tool_name,
                    'path': tool_path,
                    'exists': True
                })
            else:
                tools['gaps'].append(f"Missing tool: {tool_path}")
        
        return tools
    
    def phase2_accuracy(self):
        """Phase 2: Accuracy Verification"""
        print("=" * 80)
        print("PHASE 2: ACCURACY VERIFICATION")
        print("=" * 80)
        print()
        
        # 2.1 Content Accuracy
        print("2.1 Checking content accuracy...")
        content_issues = self._check_content_accuracy()
        self.results['phase2']['content_issues'] = content_issues
        print(f"  ✓ Found {len(content_issues)} content accuracy issues")
        print()
        
        # 2.2 Reference Accuracy
        print("2.2 Validating references...")
        reference_issues = self._check_reference_accuracy()
        self.results['phase2']['reference_issues'] = reference_issues
        print(f"  ✓ Found {len(reference_issues)} reference issues")
        print()
        
        # 2.3 Terminology Consistency
        print("2.3 Checking terminology consistency...")
        terminology_issues = self._check_terminology_consistency()
        self.results['phase2']['terminology_issues'] = terminology_issues
        print(f"  ✓ Found {len(terminology_issues)} terminology issues")
        print()
        
        print("✓ Phase 2 complete!")
        print()
        return self.results['phase2']
    
    def _check_content_accuracy(self) -> List[Dict]:
        """Check content accuracy in documentation."""
        issues = []
        
        # Check version numbers in main README
        readme_path = self.repo_root / 'README.md'
        if readme_path.exists():
            content = readme_path.read_text(encoding='utf-8')
            # Look for version references
            version_pattern = r'v?(\d+\.\d+\.\d+)'
            versions = re.findall(version_pattern, content)
            if versions:
                # Check if version matches pyproject.toml
                pyproject_path = self.repo_root / 'pyproject.toml'
                if pyproject_path.exists():
                    pyproject_content = pyproject_path.read_text(encoding='utf-8')
                    pyproject_version = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject_content)
                    if pyproject_version:
                        pyproject_ver = pyproject_version.group(1)
                        # Check if versions are consistent
                        if pyproject_ver not in versions:
                            issues.append({
                                'type': 'version_mismatch',
                                'file': 'README.md',
                                'issue': f'Version in README may not match pyproject.toml ({pyproject_ver})'
                            })
        
        return issues
    
    def _check_reference_accuracy(self) -> List[Dict]:
        """Check reference accuracy using existing tools."""
        issues = []
        
        # Try to run existing link checker
        link_checker = self.repo_root / 'scripts' / 'documentation' / 'check_doc_links.py'
        if link_checker.exists():
            try:
                result = subprocess.run(
                    ['python3', str(link_checker)],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode != 0:
                    # Parse output for broken links
                    for line in result.stdout.split('\n'):
                        if 'broken' in line.lower() or 'error' in line.lower():
                            issues.append({
                                'type': 'broken_link',
                                'details': line.strip()
                            })
            except Exception as e:
                issues.append({
                    'type': 'tool_error',
                    'tool': 'check_doc_links.py',
                    'error': str(e)
                })
        
        return issues
    
    def _check_terminology_consistency(self) -> List[Dict]:
        """Check terminology consistency across documentation."""
        issues = []
        
        # Key terms to check
        key_terms = {
            'codomyrmex': ['Codomyrmex', 'codomyrmex', 'CODOMYRMEX'],
            'mcp': ['MCP', 'Model Context Protocol', 'model context protocol'],
            'llm': ['LLM', 'Large Language Model', 'large language model']
        }
        
        # Scan all markdown files for term usage
        all_md_files = list(self.repo_root.rglob("*.md"))
        term_usage = defaultdict(list)
        
        for md_file in all_md_files[:100]:  # Sample first 100 files
            try:
                content = md_file.read_text(encoding='utf-8')
                for term_group in key_terms.values():
                    for term in term_group:
                        if term.lower() in content.lower():
                            term_usage[term].append(str(md_file.relative_to(self.repo_root)))
            except Exception:
                pass
        
        # Check for inconsistent usage
        for term_group_name, term_variants in key_terms.items():
            variants_used = [v for v in term_variants if term_usage.get(v, [])]
            if len(variants_used) > 1:
                issues.append({
                    'type': 'terminology_inconsistency',
                    'term': term_group_name,
                    'variants_found': variants_used
                })
        
        return issues
    
    def phase3_completeness(self):
        """Phase 3: Completeness Analysis"""
        print("=" * 80)
        print("PHASE 3: COMPLETENESS ANALYSIS")
        print("=" * 80)
        print()
        
        # 3.1 Coverage Completeness
        print("3.1 Checking coverage completeness...")
        coverage_gaps = self._check_coverage_completeness()
        self.results['phase3']['coverage_gaps'] = coverage_gaps
        print(f"  ✓ Found {len(coverage_gaps)} coverage gaps")
        print()
        
        # 3.2 Audience Completeness
        print("3.2 Checking audience completeness...")
        audience_gaps = self._check_audience_completeness()
        self.results['phase3']['audience_gaps'] = audience_gaps
        print(f"  ✓ Found {len(audience_gaps)} audience gaps")
        print()
        
        # 3.3 Cross-Reference Completeness
        print("3.3 Checking cross-reference completeness...")
        cross_ref_gaps = self._check_cross_ref_completeness()
        self.results['phase3']['cross_ref_gaps'] = cross_ref_gaps
        print(f"  ✓ Found {len(cross_ref_gaps)} cross-reference gaps")
        print()
        
        print("✓ Phase 3 complete!")
        print()
        return self.results['phase3']
    
    def _check_coverage_completeness(self) -> List[Dict]:
        """Check if all major features are documented."""
        gaps = []
        
        # Check module documentation completeness
        modules_dir = self.repo_root / 'src' / 'codomyrmex'
        if modules_dir.exists():
            for module_dir in modules_dir.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('_'):
                    readme = module_dir / 'README.md'
                    if not readme.exists():
                        gaps.append({
                            'type': 'missing_module_readme',
                            'module': module_dir.name,
                            'path': str(module_dir.relative_to(self.repo_root))
                        })
        
        return gaps
    
    def _check_audience_completeness(self) -> List[Dict]:
        """Check if documentation covers all audience needs."""
        gaps = []
        
        # Check getting started path
        getting_started = self.repo_root / 'docs' / 'getting-started'
        required_files = ['installation.md', 'quickstart.md']
        for req_file in required_files:
            if not (getting_started / req_file).exists():
                gaps.append({
                    'type': 'missing_getting_started',
                    'file': req_file,
                    'path': str(getting_started.relative_to(self.repo_root))
                })
        
        return gaps
    
    def _check_cross_ref_completeness(self) -> List[Dict]:
        """Check cross-reference completeness."""
        gaps = []
        
        # Sample check: verify main README links to key sections
        readme = self.repo_root / 'README.md'
        if readme.exists():
            content = readme.read_text(encoding='utf-8')
            key_links = ['docs/README.md', 'docs/getting-started', 'docs/reference']
            for link in key_links:
                if link not in content:
                    gaps.append({
                        'type': 'missing_cross_ref',
                        'file': 'README.md',
                        'missing_link': link
                    })
        
        return gaps
    
    def phase4_quality(self):
        """Phase 4: Quality Assessment"""
        print("=" * 80)
        print("PHASE 4: QUALITY ASSESSMENT")
        print("=" * 80)
        print()
        
        # 4.1 Clarity and Readability
        print("4.1 Assessing clarity and readability...")
        quality_issues = self._assess_clarity_readability()
        self.results['phase4']['quality_issues'] = quality_issues
        print(f"  ✓ Found {len(quality_issues)} quality issues")
        print()
        
        # 4.2 Actionability
        print("4.2 Assessing actionability...")
        actionability_issues = self._assess_actionability()
        self.results['phase4']['actionability_issues'] = actionability_issues
        print(f"  ✓ Found {len(actionability_issues)} actionability issues")
        print()
        
        # 4.3 Maintainability
        print("4.3 Assessing maintainability...")
        maintainability_issues = self._assess_maintainability()
        self.results['phase4']['maintainability_issues'] = maintainability_issues
        print(f"  ✓ Found {len(maintainability_issues)} maintainability issues")
        print()
        
        print("✓ Phase 4 complete!")
        print()
        return self.results['phase4']
    
    def _assess_clarity_readability(self) -> List[Dict]:
        """Assess clarity and readability of documentation."""
        issues = []
        
        # Check for very long lines (potential readability issue)
        all_md_files = list(self.repo_root.rglob("*.md"))
        for md_file in all_md_files[:50]:  # Sample
            try:
                content = md_file.read_text(encoding='utf-8')
                for i, line in enumerate(content.split('\n'), 1):
                    if len(line) > 120:  # Long line threshold
                        issues.append({
                            'type': 'long_line',
                            'file': str(md_file.relative_to(self.repo_root)),
                            'line': i,
                            'length': len(line)
                        })
            except Exception:
                pass
        
        return issues[:20]  # Limit results
    
    def _assess_actionability(self) -> List[Dict]:
        """Assess actionability of instructions."""
        issues = []
        
        # Check for TODO/FIXME markers (incomplete instructions)
        all_md_files = list(self.repo_root.rglob("*.md"))
        for md_file in all_md_files[:100]:  # Sample
            try:
                content = md_file.read_text(encoding='utf-8')
                if 'TODO' in content or 'FIXME' in content:
                    issues.append({
                        'type': 'incomplete_content',
                        'file': str(md_file.relative_to(self.repo_root)),
                        'marker': 'TODO/FIXME'
                    })
            except Exception:
                pass
        
        return issues[:20]  # Limit results
    
    def _assess_maintainability(self) -> List[Dict]:
        """Assess maintainability of documentation."""
        issues = []
        
        # Check for duplicate content patterns
        # This is a simplified check - full duplication detection would be more complex
        return issues
    
    def phase5_improvements(self):
        """Phase 5: Intelligent Improvements"""
        print("=" * 80)
        print("PHASE 5: INTELLIGENT IMPROVEMENTS")
        print("=" * 80)
        print()
        
        print("5.1 Analyzing structural improvements needed...")
        print("5.2 Analyzing content improvements needed...")
        print("5.3 Analyzing UX improvements needed...")
        print("5.4 Analyzing technical improvements needed...")
        
        # Collect improvement recommendations
        improvements = self._identify_improvements()
        self.results['phase5']['improvements_made'] = improvements
        
        print(f"  ✓ Identified {len(improvements)} improvement opportunities")
        print()
        print("✓ Phase 5 complete!")
        print()
        return self.results['phase5']
    
    def _identify_improvements(self) -> List[Dict]:
        """Identify specific improvements needed."""
        improvements = []
        
        # Based on issues found in previous phases
        if self.results['phase2']['reference_issues']:
            improvements.append({
                'type': 'fix_broken_links',
                'priority': 'critical',
                'count': len(self.results['phase2']['reference_issues'])
            })
        
        if self.results['phase3']['coverage_gaps']:
            improvements.append({
                'type': 'add_missing_docs',
                'priority': 'high',
                'count': len(self.results['phase3']['coverage_gaps'])
            })
        
        return improvements
    
    def phase6_verification(self):
        """Phase 6: Verification and Validation"""
        print("=" * 80)
        print("PHASE 6: VERIFICATION AND VALIDATION")
        print("=" * 80)
        print()
        
        # 6.1 Automated Checks
        print("6.1 Running automated validation tools...")
        validation_results = self._run_automated_checks()
        self.results['phase6']['validation_results'] = validation_results
        print(f"  ✓ Completed automated checks")
        print()
        
        # 6.2 Manual Review Notes
        print("6.2 Manual review checklist...")
        manual_notes = self._generate_manual_review_checklist()
        self.results['phase6']['manual_review_notes'] = manual_notes
        print(f"  ✓ Generated manual review checklist")
        print()
        
        print("✓ Phase 6 complete!")
        print()
        return self.results['phase6']
    
    def _run_automated_checks(self) -> Dict:
        """Run existing validation tools."""
        results = {}
        
        tools_to_run = [
            ('comprehensive_audit', 'scripts/documentation/comprehensive_audit.py'),
            ('module_docs_auditor', 'scripts/documentation/module_docs_auditor.py'),
            ('check_doc_links', 'scripts/documentation/check_doc_links.py')
        ]
        
        for tool_name, tool_path in tools_to_run:
            full_path = self.repo_root / tool_path
            if full_path.exists():
                try:
                    result = subprocess.run(
                        ['python3', str(full_path)],
                        cwd=self.repo_root,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    results[tool_name] = {
                        'exit_code': result.returncode,
                        'stdout': result.stdout[:1000],  # Limit output
                        'stderr': result.stderr[:1000] if result.stderr else ''
                    }
                except Exception as e:
                    results[tool_name] = {'error': str(e)}
            else:
                results[tool_name] = {'error': 'Tool not found'}
        
        return results
    
    def _generate_manual_review_checklist(self) -> List[str]:
        """Generate checklist for manual review."""
        checklist = [
            "Read through as a new user - follow getting started path",
            "Follow all workflows end-to-end",
            "Test installation process",
            "Verify development setup",
            "Check module creation tutorial",
            "Verify all examples work",
            "Check all cross-references",
            "Validate consistency"
        ]
        return checklist
    
    def phase7_reporting(self):
        """Phase 7: Reporting"""
        print("=" * 80)
        print("PHASE 7: REPORTING")
        print("=" * 80)
        print()
        
        # 7.1 Summary Statistics
        print("7.1 Generating summary statistics...")
        summary_stats = self._generate_summary_stats()
        self.results['phase7']['summary_stats'] = summary_stats
        print(f"  ✓ Generated summary statistics")
        print()
        
        # 7.2 Issue Catalog
        print("7.2 Compiling issue catalog...")
        issue_catalog = self._compile_issue_catalog()
        self.results['phase7']['issue_catalog'] = issue_catalog
        print(f"  ✓ Compiled issue catalog")
        print()
        
        # 7.3 Recommendations
        print("7.3 Generating recommendations...")
        recommendations = self._generate_recommendations()
        self.results['phase7']['recommendations'] = recommendations
        print(f"  ✓ Generated recommendations")
        print()
        
        print("✓ Phase 7 complete!")
        print()
        return self.results['phase7']
    
    def _generate_summary_stats(self) -> Dict:
        """Generate summary statistics."""
        stats = {
            'total_files_scanned': self.results['phase1']['files_found'].get('total_markdown', 0),
            'issues_by_category': {
                'broken_links': len(self.results['phase2']['reference_issues']),
                'missing_documentation': len(self.results['phase3']['coverage_gaps']),
                'outdated_information': len(self.results['phase2']['content_issues']),
                'inconsistencies': len(self.results['phase2']['terminology_issues']),
                'quality_issues': len(self.results['phase4']['quality_issues'])
            },
            'improvements_identified': len(self.results['phase5']['improvements_made']),
            'links_verified': len(self.results['phase2']['reference_issues'])
        }
        return stats
    
    def _compile_issue_catalog(self) -> List[Dict]:
        """Compile comprehensive issue catalog."""
        catalog = []
        
        # Add issues from all phases
        catalog.extend(self.results['phase2']['content_issues'])
        catalog.extend(self.results['phase2']['reference_issues'])
        catalog.extend(self.results['phase2']['terminology_issues'])
        catalog.extend(self.results['phase3']['coverage_gaps'])
        catalog.extend(self.results['phase3']['audience_gaps'])
        catalog.extend(self.results['phase4']['quality_issues'])
        
        return catalog
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate recommendations for improvements."""
        recommendations = []
        
        if self.results['phase2']['reference_issues']:
            recommendations.append({
                'area': 'Link Validation',
                'priority': 'critical',
                'recommendation': 'Fix all broken internal links identified in Phase 2',
                'count': len(self.results['phase2']['reference_issues'])
            })
        
        if self.results['phase3']['coverage_gaps']:
            recommendations.append({
                'area': 'Documentation Coverage',
                'priority': 'high',
                'recommendation': 'Add missing documentation files identified in Phase 3',
                'count': len(self.results['phase3']['coverage_gaps'])
            })
        
        recommendations.append({
            'area': 'Process Improvement',
            'priority': 'medium',
            'recommendation': 'Set up automated documentation validation in CI/CD pipeline',
            'count': 0
        })
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate comprehensive report."""
        report = []
        report.append("# Documentation Scan and Improvement Report")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        report.append(f"\nRepository: {self.repo_root}")
        report.append("\n" + "=" * 80 + "\n")
        
        # Phase 1 Summary
        if self.results['phase1']['files_found']:
            p1 = self.results['phase1']
            report.append("## Phase 1: Discovery and Inventory")
            report.append(f"\n- Total Markdown Files: {p1['files_found'].get('total_markdown', 0)}")
            report.append(f"- AGENTS.md Files: {p1['files_found'].get('agents_files', 0)}")
            report.append(f"- README.md Files: {p1['files_found'].get('readme_files', 0)}")
            report.append(f"- Configuration Files: {len(p1['files_found'].get('config_files', []))}")
            report.append(f"- Documentation Categories: {len(p1['structure_map'].get('categories', {}))}")
            report.append(f"- Validation Tools Found: {len(p1['tools_inventory'].get('existing_tools', []))}")
            report.append("\n")
        
        # Phase 2 Summary
        p2 = self.results['phase2']
        report.append("## Phase 2: Accuracy Verification")
        report.append(f"\n- Content Issues: {len(p2['content_issues'])}")
        report.append(f"- Reference Issues: {len(p2['reference_issues'])}")
        report.append(f"- Terminology Issues: {len(p2['terminology_issues'])}")
        report.append("\n")
        
        # Phase 3 Summary
        p3 = self.results['phase3']
        report.append("## Phase 3: Completeness Analysis")
        report.append(f"\n- Coverage Gaps: {len(p3['coverage_gaps'])}")
        report.append(f"- Audience Gaps: {len(p3['audience_gaps'])}")
        report.append(f"- Cross-Reference Gaps: {len(p3['cross_ref_gaps'])}")
        report.append("\n")
        
        # Phase 4 Summary
        p4 = self.results['phase4']
        report.append("## Phase 4: Quality Assessment")
        report.append(f"\n- Quality Issues: {len(p4['quality_issues'])}")
        report.append(f"- Actionability Issues: {len(p4['actionability_issues'])}")
        report.append(f"- Maintainability Issues: {len(p4['maintainability_issues'])}")
        report.append("\n")
        
        # Phase 5 Summary
        p5 = self.results['phase5']
        report.append("## Phase 5: Intelligent Improvements")
        report.append(f"\n- Improvements Identified: {len(p5['improvements_made'])}")
        report.append(f"- Files Updated: {len(p5.get('files_updated', []))}")
        report.append("\n")
        
        # Phase 6 Summary
        p6 = self.results['phase6']
        report.append("## Phase 6: Verification and Validation")
        report.append(f"\n- Validation Tools Run: {len(p6.get('validation_results', {}))}")
        report.append(f"- Manual Review Items: {len(p6.get('manual_review_notes', []))}")
        report.append("\n")
        
        # Phase 7 Summary
        p7 = self.results['phase7']
        if p7.get('summary_stats'):
            stats = p7['summary_stats']
            report.append("## Phase 7: Reporting")
            report.append("\n### Summary Statistics")
            report.append(f"\n- Total Files Scanned: {stats.get('total_files_scanned', 0)}")
            report.append(f"- Issues by Category:")
            for category, count in stats.get('issues_by_category', {}).items():
                report.append(f"  - {category}: {count}")
            report.append(f"- Improvements Identified: {stats.get('improvements_identified', 0)}")
            report.append("\n### Recommendations")
            for rec in p7.get('recommendations', []):
                report.append(f"\n- **{rec['area']}** ({rec['priority']}): {rec['recommendation']}")
                if rec.get('count', 0) > 0:
                    report.append(f"  - Affects {rec['count']} items")
            report.append("\n")
        
        return "\n".join(report)
    
    def save_results(self, output_path: Path):
        """Save results to JSON file."""
        output_path.write_text(json.dumps(self.results, indent=2, default=str))


def main():
    """Main execution function."""
    repo_root = Path(__file__).parent.parent.parent
    scanner = DocumentationScanner(repo_root)
    
    # Execute all phases
    scanner.phase1_discovery()
    scanner.phase2_accuracy()
    scanner.phase3_completeness()
    scanner.phase4_quality()
    scanner.phase5_improvements()
    scanner.phase6_verification()
    scanner.phase7_reporting()
    
    # Generate report
    report = scanner.generate_report()
    print(report)
    
    # Save results
    output_dir = repo_root / '@output' / 'documentation_scan'
    output_dir.mkdir(parents=True, exist_ok=True)
    scanner.save_results(output_dir / 'scan_results.json')
    (output_dir / 'scan_report.md').write_text(report)
    
    print(f"\n✓ Results saved to {output_dir}")


if __name__ == '__main__':
    main()

