#!/usr/bin/env python3
"""
AGENTS.md Structure Validator for Codomyrmex Documentation.

Validates that all AGENTS.md files follow the standardized structure.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    file_path: str
    issue_type: str
    description: str
    severity: str  # 'error', 'warning', 'info'


@dataclass
class AgentsFileValidation:
    """Validation result for an AGENTS.md file."""
    file_path: str
    is_valid: bool
    has_purpose: bool
    has_active_components: bool
    has_operating_contracts: bool
    has_navigation_links: bool
    issues: List[ValidationIssue]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'file_path': self.file_path,
            'is_valid': self.is_valid,
            'has_purpose': self.has_purpose,
            'has_active_components': self.has_active_components,
            'has_operating_contracts': self.has_operating_contracts,
            'has_navigation_links': self.has_navigation_links,
            'issues': [asdict(issue) for issue in self.issues]
        }


@dataclass
class StructureValidationReport:
    """Overall validation report."""
    total_files: int
    valid_files: int
    invalid_files: int
    file_validations: List[AgentsFileValidation]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'total_files': self.total_files,
            'valid_files': self.valid_files,
            'invalid_files': self.invalid_files,
            'file_validations': [v.to_dict() for v in self.file_validations],
            'summary': {
                'validation_rate': f"{(self.valid_files / self.total_files * 100) if self.total_files > 0 else 0:.1f}%",
                'files_needing_fix': self.invalid_files
            }
        }


class AgentsStructureValidator:
    """Validates AGENTS.md file structure."""
    
    # Required sections
    REQUIRED_SECTIONS = {
        'purpose': r'##\s+Purpose',
        'active_components': r'##\s+Active\s+Components',
        'operating_contracts': r'##\s+Operating\s+Contracts',
        'navigation_links': r'##\s+Navigation\s+Links'
    }
    
    # Standard operating contracts that should be present
    STANDARD_CONTRACTS = [
        'Maintain alignment between code, documentation, and configured workflows',
        'Ensure Model Context Protocol interfaces remain available',
        'Record outcomes in shared telemetry'
    ]
    
    def __init__(self, repo_root: Path):
        """Initialize validator."""
        self.repo_root = repo_root.resolve()
        
    def find_agents_files(self) -> List[Path]:
        """Find all AGENTS.md files."""
        agents_files = list(self.repo_root.glob('**/AGENTS.md'))
        
        # Filter out ignored directories
        ignored_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
        filtered = [
            f for f in agents_files
            if not any(ignored in f.parts for ignored in ignored_dirs)
        ]
        
        return sorted(filtered)
    
    def check_title_format(self, content: str, file_path: Path) -> Optional[ValidationIssue]:
        """Check if title follows the standard format."""
        # Expected: # Codomyrmex Agents — {path}
        first_line = content.split('\n')[0] if content else ''
        
        if not first_line.startswith('# Codomyrmex Agents'):
            return ValidationIssue(
                file_path=str(file_path.relative_to(self.repo_root)),
                issue_type='title_format',
                description='Title does not follow standard format: "# Codomyrmex Agents — {path}"',
                severity='error'
            )
        
        # Check for em dash (—) vs hyphen (-)
        if '—' not in first_line and ' - ' in first_line:
            return ValidationIssue(
                file_path=str(file_path.relative_to(self.repo_root)),
                issue_type='title_punctuation',
                description='Title uses hyphen instead of em dash (—)',
                severity='warning'
            )
        
        return None
    
    def check_section_exists(self, content: str, section_name: str, pattern: str) -> bool:
        """Check if a required section exists."""
        return bool(re.search(pattern, content, re.MULTILINE))
    
    def check_purpose_quality(self, content: str) -> List[ValidationIssue]:
        """Check the quality of the Purpose section."""
        issues = []
        
        # Extract purpose section
        purpose_match = re.search(
            r'##\s+Purpose\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not purpose_match:
            return []
        
        purpose_content = purpose_match.group(1).strip()
        
        # Check if purpose is too short
        if len(purpose_content) < 50:
            issues.append(ValidationIssue(
                file_path='',
                issue_type='purpose_too_short',
                description='Purpose section is too brief (< 50 characters)',
                severity='warning'
            ))
        
        # Check if purpose contains placeholders
        placeholder_patterns = ['TODO', 'FIXME', 'placeholder', 'TBD']
        for pattern in placeholder_patterns:
            if pattern.lower() in purpose_content.lower():
                issues.append(ValidationIssue(
                    file_path='',
                    issue_type='purpose_placeholder',
                    description=f'Purpose section contains placeholder: {pattern}',
                    severity='error'
                ))
        
        return issues
    
    def check_active_components_quality(self, content: str) -> List[ValidationIssue]:
        """Check the quality of the Active Components section."""
        issues = []
        
        # Extract active components section
        components_match = re.search(
            r'##\s+Active\s+Components\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not components_match:
            return []
        
        components_content = components_match.group(1).strip()
        
        # Check if section has any bullets or content
        if not components_content or len(components_content) < 10:
            issues.append(ValidationIssue(
                file_path='',
                issue_type='components_empty',
                description='Active Components section is empty or too brief',
                severity='error'
            ))
        
        return issues
    
    def check_operating_contracts(self, content: str) -> List[ValidationIssue]:
        """Check operating contracts section."""
        issues = []
        
        # Extract operating contracts section
        contracts_match = re.search(
            r'##\s+Operating\s+Contracts\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not contracts_match:
            return []
        
        contracts_content = contracts_match.group(1).strip()
        
        # Check for standard contracts
        missing_standard = []
        for standard in self.STANDARD_CONTRACTS:
            if standard.lower() not in contracts_content.lower():
                missing_standard.append(standard)
        
        if missing_standard:
            issues.append(ValidationIssue(
                file_path='',
                issue_type='missing_standard_contracts',
                description=f'Missing standard contracts: {", ".join(missing_standard[:2])}...',
                severity='warning'
            ))
        
        return issues
    
    def check_navigation_links(self, content: str) -> List[ValidationIssue]:
        """Check navigation links section."""
        issues = []
        
        # Extract navigation links section
        nav_match = re.search(
            r'##\s+Navigation\s+Links\s*\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.MULTILINE
        )
        
        if not nav_match:
            return []
        
        nav_content = nav_match.group(1).strip()
        
        # Check if section has links
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', nav_content)
        
        if len(links) < 2:
            issues.append(ValidationIssue(
                file_path='',
                issue_type='insufficient_navigation',
                description='Navigation Links section has fewer than 2 links',
                severity='warning'
            ))
        
        return issues
    
    def validate_file(self, file_path: Path) -> AgentsFileValidation:
        """Validate a single AGENTS.md file."""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Check title format
            title_issue = self.check_title_format(content, file_path)
            if title_issue:
                issues.append(title_issue)
            
            # Check required sections
            has_purpose = self.check_section_exists(
                content, 'purpose', self.REQUIRED_SECTIONS['purpose']
            )
            has_active_components = self.check_section_exists(
                content, 'active_components', self.REQUIRED_SECTIONS['active_components']
            )
            has_operating_contracts = self.check_section_exists(
                content, 'operating_contracts', self.REQUIRED_SECTIONS['operating_contracts']
            )
            has_navigation_links = self.check_section_exists(
                content, 'navigation_links', self.REQUIRED_SECTIONS['navigation_links']
            )
            
            # Add issues for missing sections
            if not has_purpose:
                issues.append(ValidationIssue(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    issue_type='missing_section',
                    description='Missing required section: Purpose',
                    severity='error'
                ))
            
            if not has_active_components:
                issues.append(ValidationIssue(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    issue_type='missing_section',
                    description='Missing required section: Active Components',
                    severity='error'
                ))
            
            if not has_operating_contracts:
                issues.append(ValidationIssue(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    issue_type='missing_section',
                    description='Missing required section: Operating Contracts',
                    severity='error'
                ))
            
            if not has_navigation_links:
                issues.append(ValidationIssue(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    issue_type='missing_section',
                    description='Missing required section: Navigation Links',
                    severity='error'
                ))
            
            # Check section quality
            if has_purpose:
                issues.extend(self.check_purpose_quality(content))
            
            if has_active_components:
                issues.extend(self.check_active_components_quality(content))
            
            if has_operating_contracts:
                issues.extend(self.check_operating_contracts(content))
            
            if has_navigation_links:
                issues.extend(self.check_navigation_links(content))
            
            # Update file paths in issues
            for issue in issues:
                if not issue.file_path:
                    issue.file_path = str(file_path.relative_to(self.repo_root))
            
            # Determine if valid (no errors)
            is_valid = not any(issue.severity == 'error' for issue in issues)
            
            return AgentsFileValidation(
                file_path=str(file_path.relative_to(self.repo_root)),
                is_valid=is_valid,
                has_purpose=has_purpose,
                has_active_components=has_active_components,
                has_operating_contracts=has_operating_contracts,
                has_navigation_links=has_navigation_links,
                issues=issues
            )
            
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return AgentsFileValidation(
                file_path=str(file_path.relative_to(self.repo_root)),
                is_valid=False,
                has_purpose=False,
                has_active_components=False,
                has_operating_contracts=False,
                has_navigation_links=False,
                issues=[ValidationIssue(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    issue_type='validation_error',
                    description=f'Error during validation: {str(e)}',
                    severity='error'
                )]
            )
    
    def validate_all_files(self) -> StructureValidationReport:
        """Validate all AGENTS.md files."""
        logger.info("Starting AGENTS.md structure validation...")
        
        agents_files = self.find_agents_files()
        logger.info(f"Found {len(agents_files)} AGENTS.md files to validate")
        
        file_validations = []
        
        for agents_file in agents_files:
            logger.debug(f"Validating {agents_file.relative_to(self.repo_root)}")
            validation = self.validate_file(agents_file)
            file_validations.append(validation)
        
        # Calculate summary statistics
        valid_files = sum(1 for v in file_validations if v.is_valid)
        invalid_files = len(file_validations) - valid_files
        
        report = StructureValidationReport(
            total_files=len(file_validations),
            valid_files=valid_files,
            invalid_files=invalid_files,
            file_validations=file_validations
        )
        
        logger.info(f"Validation complete. {valid_files}/{len(file_validations)} files valid")
        
        return report
    
    def export_report(self, report: StructureValidationReport, output_path: Path, format: str = "json") -> Path:
        """Export validation report."""
        if format == "json":
            output_file = output_path / "agents_structure_validation.json"
            output_file.write_text(json.dumps(report.to_dict(), indent=2))
            logger.info(f"Report exported to {output_file}")
            return output_file
        
        elif format == "html":
            output_file = output_path / "agents_structure_validation.html"
            html_content = self._generate_html_report(report)
            output_file.write_text(html_content)
            logger.info(f"HTML report exported to {output_file}")
            return output_file
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, report: StructureValidationReport) -> str:
        """Generate HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AGENTS.md Structure Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin: 10px 20px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .stat-label {{ color: #666; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .valid {{ color: #4CAF50; font-weight: bold; }}
        .invalid {{ color: #F44336; font-weight: bold; }}
        .error {{ color: #F44336; }}
        .warning {{ color: #FF9800; }}
        .info {{ color: #2196F3; }}
    </style>
</head>
<body>
    <h1>AGENTS.md Structure Validation Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stat">
            <div class="stat-value">{report.total_files}</div>
            <div class="stat-label">Total Files</div>
        </div>
        <div class="stat">
            <div class="stat-value valid">{report.valid_files}</div>
            <div class="stat-label">Valid Files</div>
        </div>
        <div class="stat">
            <div class="stat-value invalid">{report.invalid_files}</div>
            <div class="stat-label">Invalid Files</div>
        </div>
        <div class="stat">
            <div class="stat-value">{(report.valid_files / report.total_files * 100) if report.total_files > 0 else 0:.1f}%</div>
            <div class="stat-label">Validation Rate</div>
        </div>
    </div>
    
    <h2>Invalid Files</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Issues</th>
        </tr>
"""
        
        for validation in report.file_validations:
            if not validation.is_valid:
                issue_list = '<br>'.join([
                    f'<span class="{issue.severity}">[{issue.severity.upper()}] {issue.description}</span>'
                    for issue in validation.issues
                ])
                html += f"""
        <tr>
            <td><code>{validation.file_path}</code></td>
            <td>{issue_list}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate AGENTS.md file structure")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for results')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--fail-on-invalid', action='store_true',
                       help='Exit with error if any files are invalid')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Run validation
    validator = AgentsStructureValidator(args.repo_root)
    report = validator.validate_all_files()
    
    # Export results
    if args.format in ['json', 'both']:
        validator.export_report(report, args.output, 'json')
    
    if args.format in ['html', 'both']:
        validator.export_report(report, args.output, 'html')
    
    # Print summary
    print("\n" + "="*80)
    print("AGENTS.md STRUCTURE VALIDATION SUMMARY")
    print("="*80)
    print(f"Total files: {report.total_files}")
    print(f"Valid files: {report.valid_files}")
    print(f"Invalid files: {report.invalid_files}")
    print(f"Validation rate: {(report.valid_files / report.total_files * 100) if report.total_files > 0 else 0:.1f}%")
    print("="*80)
    
    # Exit with error if requested and invalid files found
    if args.fail_on_invalid and report.invalid_files > 0:
        print(f"\n❌ Validation failed: {report.invalid_files} invalid files found")
        sys.exit(1)
    
    print("\n✅ Validation complete!")
    sys.exit(0)


if __name__ == '__main__':
    main()

