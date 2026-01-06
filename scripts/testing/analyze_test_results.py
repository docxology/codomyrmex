#!/usr/bin/env python3
"""
Parse pytest output and generate comprehensive test assessment report.

This script analyzes pytest test results, extracts metrics, categorizes failures,
analyzes warnings, and generates detailed assessment reports.
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TestError:
    """Represents a test collection or execution error."""
    test_file: str
    error_type: str
    error_message: str
    traceback: List[str]
    line_number: Optional[int] = None


@dataclass
class WarningInfo:
    """Represents a warning from the test run."""
    category: str
    file_path: str
    line_number: Optional[int]
    message: str
    warning_type: str


@dataclass
class TestSummary:
    """Summary statistics from test run."""
    total_collected: int = 0
    errors: int = 0
    failures: int = 0
    skipped: int = 0
    passed: int = 0
    xfailed: int = 0
    xpassed: int = 0
    warnings: int = 0
    duration: float = 0.0
    collection_errors: List[TestError] = None
    execution_failures: List[TestError] = None
    warning_list: List[WarningInfo] = None
    
    def __post_init__(self):
        if self.collection_errors is None:
            self.collection_errors = []
        if self.execution_failures is None:
            self.execution_failures = []
        if self.warning_list is None:
            self.warning_list = []


def parse_pytest_output(output_file: Path) -> TestSummary:
    """Parse pytest output file and extract test results."""
    summary = TestSummary()
    
    if not output_file.exists():
        print(f"Error: Output file not found: {output_file}", file=sys.stderr)
        return summary
    
    content = output_file.read_text()
    lines = content.split('\n')
    
    # Extract test collection count
    collected_match = re.search(r'collected (\d+) items', content)
    if collected_match:
        summary.total_collected = int(collected_match.group(1))
    
    # Extract final summary
    summary_match = re.search(
        r'(\d+) (?:passed|failed|skipped|warnings|errors)',
        content
    )
    
    # More comprehensive summary extraction
    final_summary = re.search(
        r'=+\s+(\d+) warnings, (\d+) errors in ([\d.]+)s',
        content
    )
    if final_summary:
        summary.warnings = int(final_summary.group(1))
        summary.errors = int(final_summary.group(2))
        summary.duration = float(final_summary.group(3))
    
    # Extract errors section - look for ERROR collecting patterns
    errors_section = False
    current_error = None
    in_error_block = False
    
    for i, line in enumerate(lines):
        # Detect errors section start
        if 'ERRORS =' in line or 'ERROR collecting' in line:
            errors_section = True
            in_error_block = True
            # Extract test file from ERROR collecting line
            if 'ERROR collecting' in line:
                test_file_match = re.search(r'src/codomyrmex/tests/[^\s]+', line)
                test_file = test_file_match.group(0) if test_file_match else "unknown"
                
                if current_error:
                    summary.collection_errors.append(current_error)
                
                current_error = TestError(
                    test_file=test_file,
                    error_type="CollectionError",
                    error_message="",
                    traceback=[]
                )
            continue
        
        # Detect end of errors section
        if errors_section and ('short test summary' in line.lower() or 'warnings summary' in line.lower()):
            errors_section = False
            in_error_block = False
            if current_error:
                summary.collection_errors.append(current_error)
                current_error = None
            continue
        
        # Parse error details within errors section
        if errors_section and current_error:
            # Look for error type and message (E   ErrorType: message)
            error_type_match = re.search(r'^E\s+(\w+Error):\s*(.+)', line)
            if error_type_match:
                current_error.error_type = error_type_match.group(1)
                current_error.error_message = error_type_match.group(2).strip()
            
            # Also check for NameError pattern
            if 'NameError:' in line:
                name_error_match = re.search(r'NameError:\s*(.+)', line)
                if name_error_match:
                    current_error.error_type = "NameError"
                    current_error.error_message = name_error_match.group(1).strip()
            
            # Collect traceback lines
            if line.strip() and (line.startswith(' ') or line.startswith('E') or line.startswith('>')):
                if len(current_error.traceback) < 50:  # Limit traceback size
                    current_error.traceback.append(line.rstrip())
    
    # Add last error if still in progress
    if current_error:
        summary.collection_errors.append(current_error)
    
    # Extract warnings - format is:
    # file/path:line_number
    #   /full/path/to/file:line_number: WarningType: message
    #     code_line
    warnings_section = False
    
    for i, line in enumerate(lines):
        if 'warnings summary' in line.lower():
            warnings_section = True
            continue
        
        if warnings_section:
            # End of warnings section
            if line.strip().startswith('-- Docs:') or line.strip().startswith('==='):
                warnings_section = False
                continue
            
            # Look for warning type and message pattern: "WarningType: message"
            warning_match = re.search(r'/([^:]+):(\d+):\s+(\w+Warning):\s+(.+)', line)
            if warning_match:
                file_path = warning_match.group(1)
                line_num = int(warning_match.group(2))
                warning_type = warning_match.group(3)
                message = warning_match.group(4).strip()
                
                # Clean up file path (remove leading path components if needed)
                if file_path.startswith('/Users/'):
                    # Keep full path for source files
                    pass
                elif 'src/codomyrmex' in file_path:
                    file_path = file_path.split('src/codomyrmex/')[-1] if 'src/codomyrmex' in file_path else file_path
                
                warning = WarningInfo(
                    category="unknown",
                    file_path=file_path,
                    line_number=line_num,
                    message=message,
                    warning_type=warning_type
                )
                summary.warning_list.append(warning)
    
    # Count errors and warnings (use parsed values if available, otherwise count)
    if summary.errors == 0:
        summary.errors = len(summary.collection_errors)
    if summary.warnings == 0:
        summary.warnings = len(summary.warning_list)
    
    # Extract from short summary
    short_summary_match = re.search(
        r'(\d+) (?:passed|failed|skipped|warnings|errors)',
        content
    )
    
    # Try to extract individual counts
    passed_match = re.search(r'(\d+) passed', content)
    if passed_match:
        summary.passed = int(passed_match.group(1))
    
    failed_match = re.search(r'(\d+) failed', content)
    if failed_match:
        summary.failures = int(failed_match.group(1))
    
    skipped_match = re.search(r'(\d+) skipped', content)
    if skipped_match:
        summary.skipped = int(skipped_match.group(1))
    
    return summary


def categorize_errors(errors: List[TestError]) -> Dict[str, List[TestError]]:
    """Categorize errors by type and module."""
    by_type = defaultdict(list)
    by_module = defaultdict(list)
    
    for error in errors:
        by_type[error.error_type].append(error)
        
        # Extract module from test file path
        module_match = re.search(r'src/codomyrmex/tests/(\w+)/', error.test_file)
        if module_match:
            module = module_match.group(1)
            by_module[module].append(error)
        else:
            by_module['unknown'].append(error)
    
    return {
        'by_type': dict(by_type),
        'by_module': dict(by_module)
    }


def categorize_warnings(warnings: List[WarningInfo]) -> Dict[str, Any]:
    """Categorize warnings by type and source."""
    by_type = defaultdict(list)
    by_source = defaultdict(list)
    
    for warning in warnings:
        by_type[warning.warning_type].append(warning)
        
        # Categorize by source
        if 'src/codomyrmex/tests/' in warning.file_path:
            by_source['test_code'].append(warning)
        elif 'src/codomyrmex' in warning.file_path:
            by_source['source_code'].append(warning)
        elif '.venv' in warning.file_path or 'site-packages' in warning.file_path:
            by_source['dependencies'].append(warning)
        else:
            by_source['other'].append(warning)
    
    return {
        'by_type': dict(by_type),
        'by_source': dict(by_source)
    }


def analyze_coverage(coverage_file: Optional[Path]) -> Dict[str, Any]:
    """Analyze coverage JSON file if available."""
    if not coverage_file or not coverage_file.exists():
        return {
            'available': False,
            'message': 'Coverage file not found or not generated'
        }
    
    try:
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)
        
        totals = coverage_data.get('totals', {})
        
        return {
            'available': True,
            'line_coverage': totals.get('percent_covered', 0),
            'branch_coverage': totals.get('percent_covered_branches', 0),
            'files': len(coverage_data.get('files', {})),
            'target': 80.0,
            'meets_target': totals.get('percent_covered', 0) >= 80.0
        }
    except Exception as e:
        return {
            'available': False,
            'message': f'Error parsing coverage file: {str(e)}'
        }


def extract_performance_data(content: str) -> Dict[str, Any]:
    """Extract performance/duration data from test output."""
    performance = {
        'available': False,
        'slowest_tests': [],
        'total_duration': 0.0
    }
    
    # Look for durations output (pytest --durations)
    durations_section = False
    for line in content.split('\n'):
        if 'slowest' in line.lower() and 'durations' in line.lower():
            durations_section = True
            continue
        
        if durations_section:
            # Parse duration lines: "X.XXs call     test_file::test_name"
            duration_match = re.search(r'([\d.]+)s\s+call\s+(.+)', line)
            if duration_match:
                duration = float(duration_match.group(1))
                test_name = duration_match.group(2).strip()
                performance['slowest_tests'].append({
                    'test': test_name,
                    'duration': duration
                })
            elif line.strip() and not line.startswith('='):
                durations_section = False
    
    # Extract total duration from final summary
    duration_match = re.search(r'(\d+\.\d+)s\s*$', content)
    if duration_match:
        performance['total_duration'] = float(duration_match.group(1))
        performance['available'] = True
    
    # Sort by duration
    performance['slowest_tests'].sort(key=lambda x: x['duration'], reverse=True)
    
    return performance


def generate_report(
    summary: TestSummary,
    error_categories: Dict[str, Any],
    warning_categories: Dict[str, Any],
    coverage: Dict[str, Any],
    output_file: Path,
    performance_data: Optional[Dict[str, Any]] = None
) -> None:
    """Generate comprehensive markdown assessment report."""
    
    if performance_data is None:
        performance_data = {'available': False, 'slowest_tests': [], 'total_duration': 0.0}
    
    report_lines = []
    report_lines.append("# Codomyrmex Test Suite Assessment Report")
    report_lines.append("")
    report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    
    if summary.errors > 0:
        status = "❌ **FAILED** - Collection errors prevented test execution"
    elif summary.failures > 0:
        status = "⚠️ **PARTIAL FAILURE** - Some tests failed"
    elif summary.total_collected == 0:
        status = "⚠️ **NO TESTS** - No tests were collected"
    else:
        status = "✅ **PASSED** - All tests passed"
    
    report_lines.append(f"**Overall Status**: {status}")
    report_lines.append("")
    report_lines.append("### Test Statistics")
    report_lines.append("")
    report_lines.append(f"- **Total Tests Collected**: {summary.total_collected}")
    report_lines.append(f"- **Tests Passed**: {summary.passed}")
    report_lines.append(f"- **Tests Failed**: {summary.failures}")
    report_lines.append(f"- **Tests Skipped**: {summary.skipped}")
    report_lines.append(f"- **Collection Errors**: {summary.errors}")
    report_lines.append(f"- **Warnings**: {summary.warnings}")
    report_lines.append(f"- **Execution Time**: {summary.duration:.2f}s")
    report_lines.append("")
    
    if coverage.get('available'):
        report_lines.append("### Coverage Summary")
        report_lines.append("")
        report_lines.append(f"- **Line Coverage**: {coverage['line_coverage']:.2f}%")
        report_lines.append(f"- **Branch Coverage**: {coverage['branch_coverage']:.2f}%")
        report_lines.append(f"- **Target**: {coverage['target']:.0f}%")
        report_lines.append(f"- **Meets Target**: {'✅ Yes' if coverage['meets_target'] else '❌ No'}")
        report_lines.append("")
    
    # Critical Issues
    if summary.errors > 0:
        report_lines.append("### Critical Issues")
        report_lines.append("")
        report_lines.append(f"⚠️ **{summary.errors} collection error(s)** prevented test execution.")
        report_lines.append("These must be fixed before tests can run.")
        report_lines.append("")
    
    # Detailed Error Report
    if summary.collection_errors:
        report_lines.append("## Detailed Error Report")
        report_lines.append("")
        
        for i, error in enumerate(summary.collection_errors, 1):
            report_lines.append(f"### Error {i}: {error.test_file}")
            report_lines.append("")
            report_lines.append(f"- **Error Type**: `{error.error_type}`")
            report_lines.append(f"- **Error Message**: {error.error_message}")
            report_lines.append("")
            
            if error.traceback:
                report_lines.append("**Traceback:**")
                report_lines.append("```")
                report_lines.extend(error.traceback[:20])  # Limit traceback length
                if len(error.traceback) > 20:
                    report_lines.append(f"... ({len(error.traceback) - 20} more lines)")
                report_lines.append("```")
                report_lines.append("")
            
            # Root cause analysis
            if 'Optional' in error.error_message:
                report_lines.append("**Root Cause**: Missing import for `Optional` from `typing`")
                report_lines.append("**Suggested Fix**: Add `from typing import Optional` to the file")
            elif 'ImportError' in error.error_type:
                report_lines.append("**Root Cause**: Import error - module or dependency not available")
                report_lines.append("**Suggested Fix**: Check imports and dependencies")
            else:
                report_lines.append("**Root Cause**: Code error preventing module import")
                report_lines.append("**Suggested Fix**: Review the error traceback above")
            
            report_lines.append("")
        
        # Error Categories
        report_lines.append("### Error Categories")
        report_lines.append("")
        
        by_type = error_categories.get('by_type', {})
        report_lines.append("#### By Error Type")
        report_lines.append("")
        for error_type, errors in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.append(f"- **{error_type}**: {len(errors)} occurrence(s)")
        report_lines.append("")
        
        by_module = error_categories.get('by_module', {})
        report_lines.append("#### By Module")
        report_lines.append("")
        for module, errors in sorted(by_module.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.append(f"- **{module}**: {len(errors)} error(s)")
            for error in errors:
                report_lines.append(f"  - {error.test_file}")
        report_lines.append("")
    
    # Warning Report
    if summary.warning_list:
        report_lines.append("## Warning Report")
        report_lines.append("")
        report_lines.append(f"Total warnings: {len(summary.warning_list)}")
        report_lines.append("")
        
        by_type = warning_categories.get('by_type', {})
        report_lines.append("### Warnings by Type")
        report_lines.append("")
        for warn_type, warnings in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.append(f"- **{warn_type}**: {len(warnings)} occurrence(s)")
        report_lines.append("")
        
        by_source = warning_categories.get('by_source', {})
        report_lines.append("### Warnings by Source")
        report_lines.append("")
        for source, warnings in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
            report_lines.append(f"- **{source}**: {len(warnings)} warning(s)")
        report_lines.append("")
        
        report_lines.append("### Detailed Warnings")
        report_lines.append("")
        for i, warning in enumerate(summary.warning_list[:20], 1):  # Limit to first 20
            report_lines.append(f"#### Warning {i}")
            report_lines.append("")
            report_lines.append(f"- **Type**: {warning.warning_type}")
            report_lines.append(f"- **File**: `{warning.file_path}`")
            if warning.line_number:
                report_lines.append(f"- **Line**: {warning.line_number}")
            report_lines.append(f"- **Message**: {warning.message}")
            report_lines.append("")
        
        if len(summary.warning_list) > 20:
            report_lines.append(f"*... and {len(summary.warning_list) - 20} more warnings*")
            report_lines.append("")
    
    # Performance Report
    report_lines.append("## Performance Report")
    report_lines.append("")
    
    if not performance_data.get('available') or not performance_data.get('slowest_tests'):
        report_lines.append("⚠️ **No performance data available**")
        report_lines.append("")
        report_lines.append("Tests did not execute due to collection errors, so performance metrics could not be collected.")
        report_lines.append("")
    else:
        report_lines.append(f"**Total Execution Time**: {performance_data['total_duration']:.2f}s")
        report_lines.append("")
        
        if performance_data['slowest_tests']:
            report_lines.append("### Slowest Tests")
            report_lines.append("")
            for i, test_info in enumerate(performance_data['slowest_tests'][:20], 1):
                report_lines.append(f"{i}. **{test_info['test']}**: {test_info['duration']:.2f}s")
            report_lines.append("")
            
            # Flag tests exceeding thresholds
            slow_tests = [t for t in performance_data['slowest_tests'] if t['duration'] > 5.0]
            if slow_tests:
                report_lines.append("### Performance Warnings")
                report_lines.append("")
                report_lines.append(f"⚠️ {len(slow_tests)} test(s) exceeded 5 second threshold:")
                report_lines.append("")
                for test_info in slow_tests:
                    report_lines.append(f"- `{test_info['test']}`: {test_info['duration']:.2f}s")
                report_lines.append("")
    
    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    
    if summary.errors > 0:
        report_lines.append("### Priority 1: Fix Collection Errors")
        report_lines.append("")
        report_lines.append("Collection errors must be fixed before any tests can execute:")
        report_lines.append("")
        
        # Check for common patterns
        optional_errors = [e for e in summary.collection_errors if 'Optional' in e.error_message]
        if optional_errors:
            report_lines.append("1. **Fix Missing Optional Imports**")
            report_lines.append("   - Multiple files are missing `from typing import Optional`")
            report_lines.append("   - Add the import to affected files in `src/codomyrmex/security/`")
            report_lines.append("")
        
        report_lines.append("2. **Verify All Imports**")
        report_lines.append("   - Check that all module imports are correct")
        report_lines.append("   - Ensure dependencies are installed")
        report_lines.append("")
    
    if summary.warning_list:
        report_lines.append("### Priority 2: Address Warnings")
        report_lines.append("")
        
        deprecation_warnings = [w for w in summary.warning_list if 'DeprecationWarning' in w.warning_type]
        if deprecation_warnings:
            report_lines.append("1. **Deprecation Warnings**")
            report_lines.append("   - Replace deprecated `pkg_resources` with modern alternatives")
            report_lines.append("   - Update code to use current APIs")
            report_lines.append("")
        
        syntax_warnings = [w for w in summary.warning_list if 'SyntaxWarning' in w.warning_type]
        if syntax_warnings:
            report_lines.append("2. **Syntax Warnings**")
            report_lines.append("   - Fix invalid escape sequences in regex patterns")
            report_lines.append("   - Use raw strings (r'...') for regex patterns")
            report_lines.append("")
    
    if coverage.get('available') and not coverage.get('meets_target'):
        report_lines.append("### Priority 3: Improve Coverage")
        report_lines.append("")
        report_lines.append(f"- Current coverage: {coverage['line_coverage']:.2f}%")
        report_lines.append(f"- Target: {coverage['target']:.0f}%")
        report_lines.append(f"- Gap: {coverage['target'] - coverage['line_coverage']:.2f}%")
        report_lines.append("")
        report_lines.append("Add tests for uncovered code paths.")
        report_lines.append("")
    
    report_lines.append("### General Recommendations")
    report_lines.append("")
    report_lines.append("1. **Run tests after fixing collection errors** to get actual test results")
    report_lines.append("2. **Address warnings systematically** starting with deprecation warnings")
    report_lines.append("3. **Monitor test performance** - ensure tests complete in reasonable time")
    report_lines.append("4. **Maintain test coverage** above 80% target")
    report_lines.append("")
    
    # Write report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text('\n'.join(report_lines))
    print(f"Assessment report written to: {output_file}")


def generate_summary_json(
    summary: TestSummary,
    error_categories: Dict[str, Any],
    warning_categories: Dict[str, Any],
    coverage: Dict[str, Any],
    output_file: Path
) -> None:
    """Generate machine-readable JSON summary."""
    
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_collected': summary.total_collected,
            'passed': summary.passed,
            'failed': summary.failures,
            'skipped': summary.skipped,
            'errors': summary.errors,
            'warnings': summary.warnings,
            'duration_seconds': summary.duration,
            'status': 'failed' if summary.errors > 0 else ('partial' if summary.failures > 0 else 'passed')
        },
        'errors': {
            'total': len(summary.collection_errors),
            'by_type': {k: len(v) for k, v in error_categories.get('by_type', {}).items()},
            'by_module': {k: len(v) for k, v in error_categories.get('by_module', {}).items()},
            'details': [
                {
                    'test_file': e.test_file,
                    'error_type': e.error_type,
                    'error_message': e.error_message[:200]  # Truncate long messages
                }
                for e in summary.collection_errors
            ]
        },
        'warnings': {
            'total': len(summary.warning_list),
            'by_type': {k: len(v) for k, v in warning_categories.get('by_type', {}).items()},
            'by_source': {k: len(v) for k, v in warning_categories.get('by_source', {}).items()}
        },
        'coverage': coverage
    }
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(json_data, indent=2))
    print(f"Summary JSON written to: {output_file}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "output"
    test_output = output_dir / "test_suite_results_full.txt"
    coverage_file = project_root / "coverage.json"
    report_file = output_dir / "test_suite_assessment.md"
    summary_file = output_dir / "test_suite_summary.json"
    
    print("Analyzing test results...")
    print(f"Reading test output from: {test_output}")
    
    # Read test output content for performance analysis
    test_output_content = test_output.read_text() if test_output.exists() else ""
    
    # Parse test output
    summary = parse_pytest_output(test_output)
    
    # Extract performance data
    performance_data = extract_performance_data(test_output_content)
    
    # Categorize errors and warnings
    error_categories = categorize_errors(summary.collection_errors)
    warning_categories = categorize_warnings(summary.warning_list)
    
    # Analyze coverage
    coverage = analyze_coverage(coverage_file)
    
    # Generate reports
    print("\nGenerating assessment report...")
    generate_report(summary, error_categories, warning_categories, coverage, report_file, performance_data)
    
    print("Generating JSON summary...")
    generate_summary_json(summary, error_categories, warning_categories, coverage, summary_file)
    
    print("\nAnalysis complete!")
    print(f"\nSummary:")
    print(f"  - Tests collected: {summary.total_collected}")
    print(f"  - Collection errors: {summary.errors}")
    print(f"  - Warnings: {summary.warnings}")
    print(f"  - Duration: {summary.duration:.2f}s")


if __name__ == "__main__":
    main()

