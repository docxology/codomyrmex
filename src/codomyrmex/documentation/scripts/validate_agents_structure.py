from pathlib import Path
from typing import Dict, List, Set, Optional
import argparse
import json
import logging
import re
import sys

from dataclasses import dataclass, asdict

from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging






#!/usr/bin/env python3
"""
AGENTS.md Structure Validator for Codomyrmex Documentation.

Validates that all AGENTS.md files follow the standardized structure.
"""


try:
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
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
    directory_content_valid: bool
    navigation_links_valid: bool
    orchestrator_complete: bool
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
            'directory_content_valid': self.directory_content_valid,
            'navigation_links_valid': self.navigation_links_valid,
            'orchestrator_complete': self.orchestrator_complete,
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

    def check_directory_contents(self, agents_file: Path) -> List[ValidationIssue]:
        """Check if Active Components section accurately reflects directory contents."""
        issues = []

        try:
            # Read the AGENTS.md file
            content = agents_file.read_text(encoding='utf-8', errors='ignore')

            # Extract Active Components section
            components_match = re.search(
                r'##\s+Active\s+Components\s*\n(.*?)(?=\n##\s+Operating|\Z)',
                content,
                re.DOTALL | re.MULTILINE
            )

            if not components_match:
                return [ValidationIssue(
                    file_path=str(agents_file.relative_to(self.repo_root)),
                    issue_type='missing_active_components',
                    description='No Active Components section found for directory content validation',
                    severity='warning'
                )]

            components_content = components_match.group(1).strip()

            # Get actual directory contents (excluding AGENTS.md itself and hidden files)
            agents_dir = agents_file.parent
            actual_items = set()

            try:
                # Standard hidden directories/files to exclude from validation
                standard_hidden = {
                    '.git', '.github', '.gitignore', '.gitattributes',
                    '.pre-commit-config.yaml', '.editorconfig',
                    '.encryption_key'  # This might be sensitive
                }

                for item in agents_dir.iterdir():
                    if item.name == 'AGENTS.md':
                        continue
                    if item.name in standard_hidden:
                        continue
                    # Include hidden directories that are project-specific
                    if item.is_file():
                        actual_items.add(item.name)
                    elif item.is_dir():
                        actual_items.add(f"{item.name}/")
            except PermissionError:
                return [ValidationIssue(
                    file_path=str(agents_file.relative_to(self.repo_root)),
                    issue_type='directory_access_error',
                    description='Cannot access directory contents for validation',
                    severity='warning'
                )]

            # Extract documented items from Active Components
            # Only look at top-level bullet points that appear to be file/directory references
            documented_items = set()
            lines = components_content.split('\n')

            # Track whether we're in a descriptive section (hierarchically)
            in_descriptive_section = False
            descriptive_section_level = 0

            for line in lines:
                line = line.strip()

                # Skip empty lines and headers
                if not line or line.startswith('#'):
                    continue

                # Check if this is a section header
                if line.startswith('##') or line.startswith('###') or line.startswith('####'):
                    section_title = line.lstrip('#').strip().lower()
                    header_level = len(line) - len(line.lstrip('#'))

                    # If it's a descriptive section, mark it and all subsections as descriptive
                    if any(word in section_title for word in ['command', 'handler', 'function', 'feature', 'capability', 'types', 'configuration', 'docker']):
                        in_descriptive_section = True
                        descriptive_section_level = header_level
                    elif header_level <= descriptive_section_level:
                        # We've moved to a non-descriptive section at the same or higher level
                        in_descriptive_section = False
                        descriptive_section_level = 0
                    # If we're in a subsection of a descriptive section, stay descriptive
                    continue

                # Only process lines that look like file/directory references
                if line.startswith('- ') and not in_descriptive_section:
                    # Extract item names from various patterns:
                    # - `file.py` – description
                    # - `directory/` – description
                    # - **file.py**: description
                    # - file.py – description

                    # Remove markdown formatting and extract item name
                    line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)  # Remove bold
                    line = re.sub(r'`([^`]+)`', r'\1', line)  # Remove code formatting

                    # Extract the item name before the dash or colon
                    if ' – ' in line:
                        item = line.split(' – ')[0].strip()
                        # Remove leading dash and whitespace
                        item = re.sub(r'^-\s*', '', item).strip()
                        item = item.strip('`').strip('*')
                        documented_items.add(item)
                    elif ': ' in line:
                        item = line.split(': ')[0].strip()
                        item = item.strip('`').strip('*')
                        documented_items.add(item)

            # Check for missing items in documentation
            missing_in_docs = actual_items - documented_items
            if missing_in_docs:
                issues.append(ValidationIssue(
                    file_path=str(agents_file.relative_to(self.repo_root)),
                    issue_type='missing_directory_items',
                    description=f'Active Components missing: {", ".join(sorted(missing_in_docs))}',
                    severity='error'
                ))

            # Check for documented items that don't exist
            extra_in_docs = documented_items - actual_items
            if extra_in_docs:
                # Filter out common false positives (items that might be described differently)
                filtered_extra = set()
                for item in extra_in_docs:
                    # Remove trailing slash for comparison
                    clean_item = item.rstrip('/')
                    if clean_item not in actual_items and f"{clean_item}/" not in actual_items:
                        filtered_extra.add(item)

                if filtered_extra:
                    issues.append(ValidationIssue(
                        file_path=str(agents_file.relative_to(self.repo_root)),
                        issue_type='extra_documented_items',
                        description=f'Active Components references non-existent items: {", ".join(sorted(filtered_extra))}',
                        severity='error'
                    ))

        except Exception as e:
            issues.append(ValidationIssue(
                file_path=str(agents_file.relative_to(self.repo_root)),
                issue_type='directory_validation_error',
                description=f'Error validating directory contents: {str(e)}',
                severity='warning'
            ))

        return issues

    def check_navigation_link_validity(self, agents_file: Path) -> List[ValidationIssue]:
        """Check if navigation links point to existing files."""
        issues = []

        try:
            content = agents_file.read_text(encoding='utf-8', errors='ignore')

            # Extract Navigation Links section
            nav_match = re.search(
                r'##\s+Navigation\s+Links\s*\n(.*?)(?=\n##|\Z)',
                content,
                re.DOTALL | re.MULTILINE
            )

            if not nav_match:
                return []

            nav_content = nav_match.group(1).strip()

            # Find all markdown links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', nav_content)

            for link_text, link_path in links:
                # Skip external links (http/https) and anchor links
                if link_path.startswith(('http://', 'https://', '#')):
                    continue

                # Resolve relative path from agents file location
                try:
                    resolved_path = (agents_file.parent / link_path).resolve()

                    # Check if the path exists (file or directory)
                    if not resolved_path.exists():
                        issues.append(ValidationIssue(
                            file_path=str(agents_file.relative_to(self.repo_root)),
                            issue_type='broken_navigation_link',
                            description=f'Navigation link points to non-existent file: [{link_text}]({link_path})',
                            severity='error'
                        ))
                except Exception as e:
                    issues.append(ValidationIssue(
                        file_path=str(agents_file.relative_to(self.repo_root)),
                        issue_type='invalid_navigation_link',
                        description=f'Cannot resolve navigation link: [{link_text}]({link_path}) - {str(e)}',
                        severity='warning'
                    ))

        except Exception as e:
            issues.append(ValidationIssue(
                file_path=str(agents_file.relative_to(self.repo_root)),
                issue_type='navigation_validation_error',
                description=f'Error validating navigation links: {str(e)}',
                severity='warning'
            ))

        return issues

    def check_orchestrator_completeness(self, agents_file: Path) -> List[ValidationIssue]:
        """Check completeness for orchestrator scripts."""
        issues = []

        try:
            agents_dir = agents_file.parent

            # Check if this is a scripts directory with orchestrate.py
            orchestrate_file = agents_dir / 'orchestrate.py'
            if not orchestrate_file.exists():
                return []  # Not an orchestrator directory

            # Read orchestrate.py to find command handlers
            try:
                orchestrate_content = orchestrate_file.read_text(encoding='utf-8', errors='ignore')

                # Find command handlers in main() function
                handlers_match = re.search(
                    r'handlers\s*=\s*\{(.*?)\}',
                    orchestrate_content,
                    re.DOTALL
                )

                if handlers_match:
                    handlers_block = handlers_match.group(1)
                    # Extract command names
                    actual_commands = set()
                    for line in handlers_block.split('\n'):
                        line = line.strip()
                        if ':' in line and line.startswith('"'):
                            cmd = line.split(':')[0].strip('"')
                            actual_commands.add(cmd)

                    # Read AGENTS.md to check documented commands
                    agents_content = agents_file.read_text(encoding='utf-8', errors='ignore')

                    # Extract documented command handlers from entire Active Components section (including subsections)
                    components_match = re.search(
                        r'##\s+Active\s+Components\s*\n(.*?)(?=\n##\s+Operating|\n##\s+Related|\Z)',
                        agents_content,
                        re.DOTALL | re.MULTILINE
                    )

                    documented_commands = set()
                    if components_match:
                        components_content = components_match.group(1)

                        # Look for command references in the entire Active Components section
                        components_lower = components_content.lower()

                        # Check for each command type
                        command_mappings = {
                            'generate': ['generate', 'generation'],
                            'refactor': ['refactor', 'refactoring'],
                            'analyze': ['analyze', 'analysis'],
                            'validate-api-keys': ['validate-api-keys', 'validate', 'api', 'keys'],
                            'list-providers': ['list-providers', 'providers'],
                            'list-languages': ['list-languages', 'languages'],
                            'list-models': ['list-models', 'models']
                        }

                        for command, keywords in command_mappings.items():
                            if any(keyword in components_lower for keyword in keywords):
                                documented_commands.add(command)

                    # Check for missing command documentation
                    missing_commands = actual_commands - documented_commands
                    if missing_commands:
                        issues.append(ValidationIssue(
                            file_path=str(agents_file.relative_to(self.repo_root)),
                            issue_type='missing_command_documentation',
                            description=f'Orchestrator commands not documented in Active Components: {", ".join(sorted(missing_commands))}',
                            severity='error'
                        ))

            except Exception as e:
                issues.append(ValidationIssue(
                    file_path=str(agents_file.relative_to(self.repo_root)),
                    issue_type='orchestrator_analysis_error',
                    description=f'Error analyzing orchestrator completeness: {str(e)}',
                    severity='warning'
                ))

        except Exception as e:
            issues.append(ValidationIssue(
                file_path=str(agents_file.relative_to(self.repo_root)),
                issue_type='orchestrator_validation_error',
                description=f'Error validating orchestrator completeness: {str(e)}',
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

            # New enhanced validations
            issues.extend(self.check_directory_contents(file_path))
            issues.extend(self.check_navigation_link_validity(file_path))
            issues.extend(self.check_orchestrator_completeness(file_path))
            
            # Update file paths in issues
            for issue in issues:
                if not issue.file_path:
                    issue.file_path = str(file_path.relative_to(self.repo_root))
            
            # Calculate enhanced validation results
            directory_issues = [i for i in issues if i.issue_type in ['missing_directory_items', 'extra_documented_items']]
            navigation_issues = [i for i in issues if i.issue_type in ['broken_navigation_link', 'invalid_navigation_link']]
            orchestrator_issues = [i for i in issues if i.issue_type in ['missing_command_documentation']]

            directory_content_valid = len(directory_issues) == 0
            navigation_links_valid = len(navigation_issues) == 0
            orchestrator_complete = len(orchestrator_issues) == 0

            # Determine if valid (no errors)
            is_valid = not any(issue.severity == 'error' for issue in issues)

            return AgentsFileValidation(
                file_path=str(file_path.relative_to(self.repo_root)),
                is_valid=is_valid,
                has_purpose=has_purpose,
                has_active_components=has_active_components,
                has_operating_contracts=has_operating_contracts,
                has_navigation_links=has_navigation_links,
                directory_content_valid=directory_content_valid,
                navigation_links_valid=navigation_links_valid,
                orchestrator_complete=orchestrator_complete,
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
                directory_content_valid=False,
                navigation_links_valid=False,
                orchestrator_complete=False,
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
            <div class="stat-label">Structure Valid</div>
        </div>
        <div class="stat">
            <div class="stat-value">{sum(1 for v in report.file_validations if v.directory_content_valid) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</div>
            <div class="stat-label">Directory Content Valid</div>
        </div>
        <div class="stat">
            <div class="stat-value">{sum(1 for v in report.file_validations if v.navigation_links_valid) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</div>
            <div class="stat-label">Navigation Links Valid</div>
        </div>
        <div class="stat">
            <div class="stat-value">{sum(1 for v in report.file_validations if v.orchestrator_complete) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</div>
            <div class="stat-label">Orchestrator Complete</div>
        </div>
    </div>
    
    <h2>Validation Summary by Category</h2>
    <table>
        <tr>
            <th>Category</th>
            <th>Valid Files</th>
            <th>Invalid Files</th>
            <th>Success Rate</th>
        </tr>
        <tr>
            <td>Basic Structure</td>
            <td class="valid">{report.valid_files}</td>
            <td class="invalid">{report.invalid_files}</td>
            <td>{(report.valid_files / report.total_files * 100) if report.total_files > 0 else 0:.1f}%</td>
        </tr>
        <tr>
            <td>Directory Content</td>
            <td class="valid">{sum(1 for v in report.file_validations if v.directory_content_valid)}</td>
            <td class="invalid">{sum(1 for v in report.file_validations if not v.directory_content_valid)}</td>
            <td>{sum(1 for v in report.file_validations if v.directory_content_valid) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</td>
        </tr>
        <tr>
            <td>Navigation Links</td>
            <td class="valid">{sum(1 for v in report.file_validations if v.navigation_links_valid)}</td>
            <td class="invalid">{sum(1 for v in report.file_validations if not v.navigation_links_valid)}</td>
            <td>{sum(1 for v in report.file_validations if v.navigation_links_valid) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</td>
        </tr>
        <tr>
            <td>Orchestrator Completeness</td>
            <td class="valid">{sum(1 for v in report.file_validations if v.orchestrator_complete)}</td>
            <td class="invalid">{sum(1 for v in report.file_validations if not v.orchestrator_complete)}</td>
            <td>{sum(1 for v in report.file_validations if v.orchestrator_complete) / report.total_files * 100 if report.total_files > 0 else 0:.1f}%</td>
        </tr>
    </table>

    <h2>Invalid Files by Issue Type</h2>
    <table>
        <tr>
            <th>File</th>
            <th>Issue Type</th>
            <th>Severity</th>
            <th>Description</th>
        </tr>
"""
        
        # Group issues by file and show all issues
        for validation in report.file_validations:
            if validation.issues:
                for issue in validation.issues:
                    html += f"""
        <tr>
            <td><code>{validation.file_path}</code></td>
            <td>{issue.issue_type.replace('_', ' ').title()}</td>
            <td class="{issue.severity}">{issue.severity.upper()}</td>
            <td>{issue.description}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html


def extract_orchestrator_commands(orchestrate_file: Path) -> List[str]:
    """Extract command names from an orchestrator file."""
    try:
        content = orchestrate_file.read_text(encoding='utf-8', errors='ignore')

        # Find the handlers dictionary
        handlers_match = re.search(r'handlers\s*=\s*\{(.*?)\}', content, re.DOTALL)
        if not handlers_match:
            return []

        handlers_block = handlers_match.group(1)

        # Extract command names (keys in the dictionary)
        commands = []
        for line in handlers_block.split('\n'):
            line = line.strip()
            if ':' in line and line.startswith('"'):
                # Extract the command name (key)
                cmd_match = re.match(r'"([^"]+)"', line)
                if cmd_match:
                    commands.append(cmd_match.group(1))

        return sorted(commands)
    except Exception as e:
        logger.error(f'Error extracting commands from {orchestrate_file}: {e}')
        return []


def fix_script_orchestrator_agents(repo_root: Path, orchestrator_dir: Path) -> bool:
    """Fix an AGENTS.md file for a script orchestrator."""
    agents_file = orchestrator_dir / 'AGENTS.md'
    orchestrate_file = orchestrator_dir / 'orchestrate.py'

    if not agents_file.exists() or not orchestrate_file.exists():
        return False

    try:
        # Get directory contents
        actual_items = set()
        for item in orchestrator_dir.iterdir():
            if item.name == 'AGENTS.md':
                continue
            if item.is_file():
                actual_items.add(item.name)
            elif item.is_dir():
                actual_items.add(f"{item.name}/")

        # Extract commands
        commands = extract_orchestrator_commands(orchestrate_file)

        # Get module name from directory
        module_name = orchestrator_dir.name

        # Read current AGENTS.md
        current_content = agents_file.read_text(encoding='utf-8')

        # Extract the title and description
        title_match = re.search(r'# (.+)', current_content)
        if not title_match:
            return False

        title = title_match.group(1)

        # Extract purpose
        purpose_match = re.search(r'## Purpose\s*\n(.*?)(?=\n##|\Z)', current_content, re.DOTALL)
        purpose = purpose_match.group(1).strip() if purpose_match else f"Thin orchestrator script providing CLI access to the `codomyrmex.{module_name}` module."

        # Create new AGENTS.md content
        new_content = f"""# {title}

## Purpose
{purpose}

## Active Components

### Core Files
- `orchestrate.py` – CLI orchestrator script providing command-line interface to {module_name} operations
"""

        if 'README.md' in actual_items:
            new_content += "- `README.md` – Comprehensive usage documentation with examples and command reference\n"

        if commands:
            new_content += "\n### Command Handlers\n"
            new_content += f"The `orchestrate.py` script implements handlers for:\n"
            for cmd in commands:
                # Try to create a reasonable description
                cmd_desc = cmd.replace('-', ' ').title()
                new_content += f"- **{cmd}** - {cmd_desc} operation\n"

        new_content += """
## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All orchestrator scripts must call real module functions (no stubs).
- All orchestrators must use proper exception handling from `codomyrmex.exceptions`.
- All orchestrators must use `codomyrmex.logging_monitoring` for logging.

## Related Modules
- **{module_display} Module** (`../../src/codomyrmex/{module_name}/`) - Core {module_name} implementation

## Navigation Links
- **📚 Scripts Overview**: [../README.md](../README.md) - Scripts directory documentation
- **🔧 {module_display} Module**: [../../src/codomyrmex/{module_name}/README.md](../../src/codomyrmex/{module_name}/README.md) - Core module documentation
- **🔌 API Specification**: [../../src/codomyrmex/{module_name}/API_SPECIFICATION.md](../../src/codomyrmex/{module_name}/API_SPECIFICATION.md) - Detailed API reference
- **🏠 Project Root**: [../../README.md](../../README.md) - Main project README
""".format(
    module_name=module_name,
    module_display=module_name.replace('_', ' ').title()
)

        # Write the new content
        agents_file.write_text(new_content, encoding='utf-8')
        logger.info(f"Updated {agents_file}")
        return True

    except Exception as e:
        logger.error(f"Error fixing {agents_file}: {e}")
        return False


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Validate AGENTS.md file structure")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory for results')
    parser.add_argument('--format', choices=['json', 'html', 'both'], default='both',
                       help='Output format')
    parser.add_argument('--fail-on-invalid', action='store_true',
                       help='Exit with error if any files are invalid')
    parser.add_argument('--fix-script-orchestrators', action='store_true',
                       help='Automatically fix AGENTS.md files for script orchestrators')
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Handle fix command
    if args.fix_script_orchestrators:
        validator = AgentsStructureValidator(args.repo_root)
        fixed_count = 0
        total_count = 0

        # Find all script orchestrator directories
        scripts_dir = args.repo_root / 'scripts'
        if scripts_dir.exists():
            for item in scripts_dir.iterdir():
                if item.is_dir() and (item / 'orchestrate.py').exists():
                    total_count += 1
                    if fix_script_orchestrator_agents(args.repo_root, item):
                        fixed_count += 1

        print(f"\nFixed {fixed_count}/{total_count} script orchestrator AGENTS.md files")
        return

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

