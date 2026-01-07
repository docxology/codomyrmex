#!/usr/bin/env python3
"""
Module Documentation Validator

Validates module documentation structure and consistency.
Can be run as part of CI/CD to ensure documentation standards are maintained.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
import sys


class ModuleDocsValidator:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root.resolve()
        self.modules_dir = self.repo_root / 'src' / 'codomyrmex'
        self.errors = []
        self.warnings = []
        
        # Required files for all modules
        self.required_files = ['README.md', 'AGENTS.md', 'SECURITY.md']
        
        # Files that should exist if referenced
        self.referenced_files = [
            'API_SPECIFICATION.md',
            'MCP_TOOL_SPECIFICATION.md',
            'USAGE_EXAMPLES.md',
            'CHANGELOG.md'
        ]
    
    def find_modules(self) -> List[Path]:
        """Find all module directories."""
        modules = []
        if not self.modules_dir.exists():
            return modules
        
        for item in self.modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                if item.name in ['__pycache__', 'output', 'template', 'tests']:
                    continue
                if (item / '__init__.py').exists() or (item / 'README.md').exists():
                    modules.append(item)
        
        return sorted(modules)
    
    def validate_module_structure(self, module_path: Path) -> Tuple[List[str], List[str]]:
        """Validate a single module's documentation structure."""
        module_name = module_path.name
        errors = []
        warnings = []
        
        # Check required files
        for filename in self.required_files:
            file_path = module_path / filename
            if not file_path.exists():
                errors.append(f"{module_name}: Missing required file {filename}")
        
        # Check if referenced files exist when referenced
        docs_index = module_path / 'docs' / 'index.md'
        if docs_index.exists():
            try:
                content = docs_index.read_text(encoding='utf-8')
                
                for filename in self.referenced_files:
                    if filename in content:
                        file_path = module_path / filename
                        if not file_path.exists():
                            warnings.append(
                                f"{module_name}: {filename} is referenced in docs/index.md but doesn't exist"
                            )
            except Exception:
                pass
        
        # Check for broken CONTRIBUTING.md references
        for md_file in module_path.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                if 'CONTRIBUTING.md' in content and '../../docs/project/contributing.md' not in content:
                    # Check if it's a broken reference
                    if '../CONTRIBUTING.md' in content or '../../CONTRIBUTING.md' in content:
                        rel_path = md_file.relative_to(self.repo_root)
                        errors.append(
                            f"{module_name}: Broken CONTRIBUTING.md reference in {rel_path}"
                        )
            except Exception:
                pass
        
        # Check for broken example_tutorial.md references
        docs_index = module_path / 'docs' / 'index.md'
        if docs_index.exists():
            try:
                content = docs_index.read_text(encoding='utf-8')
                if 'example_tutorial.md' in content:
                    tutorial_path = module_path / 'docs' / 'tutorials' / 'example_tutorial.md'
                    if not tutorial_path.exists():
                        warnings.append(
                            f"{module_name}: example_tutorial.md referenced but doesn't exist"
                        )
            except Exception:
                pass
        
        return errors, warnings
    
    def validate_all(self):
        """Validate all modules."""
        print("=" * 80)
        print("Module Documentation Validator")
        print("=" * 80)
        print()
        
        modules = self.find_modules()
        print(f"Validating {len(modules)} modules...\n")
        
        for module_path in modules:
            errors, warnings = self.validate_module_structure(module_path)
            self.errors.extend(errors)
            self.warnings.extend(warnings)
        
        # Print results
        if self.errors:
            print("❌ ERRORS:\n")
            for error in self.errors:
                print(f"  - {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:\n")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ All modules pass validation!")
            print()
        
        # Summary
        print("=" * 80)
        print(f"Summary: {len(self.errors)} errors, {len(self.warnings)} warnings")
        print("=" * 80)
        
        return len(self.errors) == 0
    
    def get_summary(self) -> Dict:
        """Get validation summary."""
        return {
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'error_details': self.errors,
            'warning_details': self.warnings
        }


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    validator = ModuleDocsValidator(repo_root)
    success = validator.validate_all()
    
    # Return exit code (0 = success, 1 = failure)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())

