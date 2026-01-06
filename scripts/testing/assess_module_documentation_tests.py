#!/usr/bin/env python3
"""Assess module documentation and test coverage."""

import os
from pathlib import Path
from collections import defaultdict

def assess_modules(base_path: Path):
    """Assess all modules for documentation and testing."""
    modules_dir = base_path / "src/codomyrmex"
    testing_dir = base_path / "testing"
    
    results = defaultdict(dict)
    
    # Get all modules
    modules = [d for d in modules_dir.iterdir() 
               if d.is_dir() and not d.name.startswith('_') 
               and d.name not in ['codomyrmex', 'template', 'tests']]
    
    for module in sorted(modules):
        module_name = module.name
        results[module_name] = {
            'module_path': str(module.relative_to(base_path)),
            'docs': {},
            'tests': {},
            'source_files': [],
            'test_files': [],
            'coverage_estimate': 0
        }
        
        # Check documentation
        for doc_file in ['README.md', 'AGENTS.md', 'SPEC.md', 'API_SPECIFICATION.md', 'USAGE_EXAMPLES.md']:
            doc_path = module / doc_file
            results[module_name]['docs'][doc_file] = doc_path.exists()
        
        # Count source files
        source_files = list(module.rglob("*.py"))
        source_files = [f for f in source_files 
                       if '__pycache__' not in str(f) 
                       and 'tests' not in str(f)
                       and f.name != '__init__.py']
        results[module_name]['source_files'] = [str(f.relative_to(base_path)) for f in source_files]
        results[module_name]['source_file_count'] = len(source_files)
        
        # Find test files
        # Check in module's tests directory
        module_tests = list((module / "tests").rglob("test_*.py")) if (module / "tests").exists() else []
        
        # Check in testing/unit directory
        unit_tests = list((testing_dir / "unit").glob(f"test_{module_name}*.py"))
        unit_tests.extend(list((testing_dir / "unit").glob(f"test_{module_name.replace('_', '_')}*.py")))
        
        # Check in testing/integration directory
        integration_tests = list((testing_dir / "integration").glob(f"*{module_name}*.py"))
        
        all_test_files = module_tests + unit_tests + integration_tests
        results[module_name]['test_files'] = [str(f.relative_to(base_path)) for f in all_test_files]
        results[module_name]['test_file_count'] = len(all_test_files)
        
        # Estimate coverage (rough: test files / source files ratio)
        if results[module_name]['source_file_count'] > 0:
            results[module_name]['coverage_estimate'] = min(100, 
                (results[module_name]['test_file_count'] / results[module_name]['source_file_count']) * 100)
        else:
            results[module_name]['coverage_estimate'] = 100 if results[module_name]['test_file_count'] > 0 else 0
    
    return results

def generate_report(results: dict, output_path: Path):
    """Generate assessment report."""
    report = ["# Module Documentation and Testing Assessment\n"]
    report.append(f"**Generated**: {Path(__file__).stat().st_mtime}\n")
    report.append("## Summary\n\n")
    
    total_modules = len(results)
    modules_with_all_docs = sum(1 for r in results.values() 
                                if r['docs'].get('README.md') and 
                                   r['docs'].get('AGENTS.md') and 
                                   r['docs'].get('SPEC.md'))
    modules_with_tests = sum(1 for r in results.values() if r['test_file_count'] > 0)
    modules_with_good_coverage = sum(1 for r in results.values() if r['coverage_estimate'] >= 80)
    
    report.append(f"- **Total Modules**: {total_modules}\n")
    report.append(f"- **Modules with Complete Docs** (README+AGENTS+SPEC): {modules_with_all_docs}/{total_modules}\n")
    report.append(f"- **Modules with Tests**: {modules_with_tests}/{total_modules}\n")
    report.append(f"- **Modules with ≥80% Coverage Estimate**: {modules_with_good_coverage}/{total_modules}\n\n")
    
    report.append("## Module Details\n\n")
    report.append("| Module | Docs | Source Files | Test Files | Coverage Est. | Status |\n")
    report.append("|--------|------|--------------|------------|---------------|--------|\n")
    
    for module_name, data in sorted(results.items()):
        docs_status = "✅" if (data['docs'].get('README.md') and 
                              data['docs'].get('AGENTS.md') and 
                              data['docs'].get('SPEC.md')) else "❌"
        tests_status = "✅" if data['test_file_count'] > 0 else "❌"
        coverage = f"{data['coverage_estimate']:.0f}%"
        
        if data['coverage_estimate'] >= 80 and docs_status == "✅":
            status = "✅ Complete"
        elif data['test_file_count'] == 0:
            status = "⚠️ Needs Tests"
        elif docs_status == "❌":
            status = "⚠️ Needs Docs"
        else:
            status = "⚠️ Low Coverage"
        
        report.append(f"| {module_name} | {docs_status} | {data['source_file_count']} | "
                     f"{data['test_file_count']} | {coverage} | {status} |\n")
    
    report.append("\n## Modules Needing Attention\n\n")
    
    # Modules without tests
    no_tests = [name for name, data in results.items() if data['test_file_count'] == 0]
    if no_tests:
        report.append("### Modules Without Tests\n\n")
        for name in sorted(no_tests):
            report.append(f"- **{name}**: {results[name]['source_file_count']} source files, 0 test files\n")
        report.append("\n")
    
    # Modules with low coverage
    low_coverage = [name for name, data in results.items() 
                   if data['test_file_count'] > 0 and data['coverage_estimate'] < 80]
    if low_coverage:
        report.append("### Modules with Low Coverage (<80%)\n\n")
        for name in sorted(low_coverage):
            report.append(f"- **{name}**: {results[name]['coverage_estimate']:.0f}% "
                         f"({results[name]['test_file_count']} test files, "
                         f"{results[name]['source_file_count']} source files)\n")
        report.append("\n")
    
    # Modules missing documentation
    missing_docs = [name for name, data in results.items() 
                   if not (data['docs'].get('README.md') and 
                          data['docs'].get('AGENTS.md') and 
                          data['docs'].get('SPEC.md'))]
    if missing_docs:
        report.append("### Modules Missing Documentation\n\n")
        for name in sorted(missing_docs):
            missing = [doc for doc, exists in data['docs'].items() 
                     if doc in ['README.md', 'AGENTS.md', 'SPEC.md'] and not exists]
            report.append(f"- **{name}**: Missing {', '.join(missing)}\n")
    
    output_path.write_text(''.join(report), encoding='utf-8')
    print(f"Report generated: {output_path}")

def main():
    """Run assessment."""
    base_path = Path("/Users/mini/Documents/GitHub/codomyrmex")
    results = assess_modules(base_path)
    
    report_path = base_path / "output" / "module_assessment_report.md"
    report_path.parent.mkdir(exist_ok=True)
    generate_report(results, report_path)
    
    # Print summary
    print("\n=== MODULE ASSESSMENT SUMMARY ===")
    total = len(results)
    with_docs = sum(1 for r in results.values() 
                   if r['docs'].get('README.md') and 
                      r['docs'].get('AGENTS.md') and 
                      r['docs'].get('SPEC.md'))
    with_tests = sum(1 for r in results.values() if r['test_file_count'] > 0)
    good_coverage = sum(1 for r in results.values() if r['coverage_estimate'] >= 80)
    
    print(f"Total modules: {total}")
    print(f"Modules with complete docs: {with_docs}/{total}")
    print(f"Modules with tests: {with_tests}/{total}")
    print(f"Modules with ≥80% coverage: {good_coverage}/{total}")
    
    # Show modules needing attention
    no_tests = [name for name, data in results.items() if data['test_file_count'] == 0]
    if no_tests:
        print(f"\n⚠️  Modules without tests ({len(no_tests)}): {', '.join(sorted(no_tests))}")

if __name__ == "__main__":
    main()

