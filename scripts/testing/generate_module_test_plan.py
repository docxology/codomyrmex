#!/usr/bin/env python3
"""Generate comprehensive plan for module testing improvements."""

import json
from pathlib import Path
from collections import defaultdict

def analyze_module_testing_needs():
    """Analyze what tests are needed for each module."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    modules_dir = base_path / "src/codomyrmex"
    testing_dir = base_path / "testing"
    
    modules = [d for d in modules_dir.iterdir() 
               if d.is_dir() and not d.name.startswith('_') 
               and d.name not in ['codomyrmex', 'template', 'tests']]
    
    plan = {
        'modules_needing_tests': [],
        'modules_needing_coverage': [],
        'test_priorities': []
    }
    
    for module in sorted(modules):
        module_name = module.name
        
        # Count source files
        source_files = list(module.rglob("*.py"))
        source_files = [f for f in source_files 
                       if '__pycache__' not in str(f) 
                       and 'tests' not in str(f)]
        source_count = len(source_files)
        
        # Count test files
        unit_tests = list((testing_dir / "unit").glob(f"test_{module_name}*.py"))
        integration_tests = list((testing_dir / "integration").glob(f"*{module_name}*.py"))
        test_count = len(unit_tests) + len(integration_tests)
        
        # Estimate coverage
        if source_count > 0:
            coverage_est = min(100, (test_count / source_count) * 100)
        else:
            coverage_est = 100 if test_count > 0 else 0
        
        if test_count == 0:
            plan['modules_needing_tests'].append({
                'module': module_name,
                'source_files': source_count,
                'priority': 'high' if source_count > 10 else 'medium'
            })
        elif coverage_est < 80:
            plan['modules_needing_coverage'].append({
                'module': module_name,
                'source_files': source_count,
                'test_files': test_count,
                'coverage_est': coverage_est,
                'needed_tests': max(1, int((source_count * 0.8) - test_count))
            })
    
    # Sort by priority
    plan['modules_needing_tests'].sort(key=lambda x: x['source_files'], reverse=True)
    plan['modules_needing_coverage'].sort(key=lambda x: x['coverage_est'])
    
    return plan

def generate_test_plan_report(plan: dict, output_path: Path):
    """Generate markdown report of testing plan."""
    report = ["# Module Testing Improvement Plan\n\n"]
    report.append("## Overview\n\n")
    report.append(f"- **Modules Needing Tests**: {len(plan['modules_needing_tests'])}\n")
    report.append(f"- **Modules Needing Coverage**: {len(plan['modules_needing_coverage'])}\n\n")
    
    report.append("## Modules Without Tests (Priority Order)\n\n")
    for item in plan['modules_needing_tests']:
        report.append(f"### {item['module']}\n")
        report.append(f"- **Source Files**: {item['source_files']}\n")
        report.append(f"- **Priority**: {item['priority']}\n")
        report.append(f"- **Action**: Create comprehensive test suite\n\n")
    
    report.append("## Modules Needing Coverage Improvements\n\n")
    for item in plan['modules_needing_coverage']:
        report.append(f"### {item['module']}\n")
        report.append(f"- **Current Coverage**: {item['coverage_est']:.0f}%\n")
        report.append(f"- **Source Files**: {item['source_files']}\n")
        report.append(f"- **Test Files**: {item['test_files']}\n")
        report.append(f"- **Needed Tests**: ~{item['needed_tests']} additional test files\n\n")
    
    output_path.write_text(''.join(report), encoding='utf-8')
    print(f"Plan generated: {output_path}")

def main():
    """Generate testing plan."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    plan = analyze_module_testing_needs()
    
    report_path = base_path / "output" / "module_testing_plan.md"
    report_path.parent.mkdir(exist_ok=True)
    generate_test_plan_report(plan, report_path)
    
    # Also save as JSON
    json_path = base_path / "output" / "module_testing_plan.json"
    json_path.write_text(json.dumps(plan, indent=2), encoding='utf-8')
    
    print(f"\n=== TESTING PLAN SUMMARY ===")
    print(f"Modules needing tests: {len(plan['modules_needing_tests'])}")
    print(f"Modules needing coverage: {len(plan['modules_needing_coverage'])}")

if __name__ == "__main__":
    main()

