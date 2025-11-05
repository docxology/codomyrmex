#!/usr/bin/env python3
"""
Comprehensively fix all broken references in tutorial and documentation files.

Fixes:
- API_SPECIFICATION.md references (if file doesn't exist, point to README or remove)
- USAGE_EXAMPLES.md references (if file doesn't exist, point to README or remove)
- MCP_TOOL_SPECIFICATION.md references (check if exists)
"""

import re
from pathlib import Path
import sys


def fix_all_tutorial_references():
    """Fix all broken references comprehensively."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Find all markdown files in modules
    modules_dir = repo_root / 'src' / 'codomyrmex'
    markdown_files = list(modules_dir.rglob('*.md'))
    
    print(f"Scanning {len(markdown_files)} markdown files for broken references...\n")
    
    fixed_count = 0
    
    for md_file in markdown_files:
        # Skip certain directories
        if any(part in str(md_file) for part in ['__pycache__', 'node_modules', '.git']):
            continue
        
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Determine module path
            # Go up from current file to find module root
            current = md_file.parent
            module_path = None
            while current != modules_dir.parent:
                if (current / '__init__.py').exists() or (current / 'README.md').exists():
                    # Check if it's a module directory
                    parent_name = current.parent.name
                    if parent_name == 'codomyrmex':
                        module_path = current
                        break
                current = current.parent
            
            if not module_path:
                continue
            
            # Check what files exist in module
            api_spec = module_path / 'API_SPECIFICATION.md'
            usage_examples = module_path / 'USAGE_EXAMPLES.md'
            mcp_spec = module_path / 'MCP_TOOL_SPECIFICATION.md'
            readme = module_path / 'README.md'
            
            api_spec_exists = api_spec.exists()
            usage_examples_exists = usage_examples.exists()
            mcp_spec_exists = mcp_spec.exists()
            readme_exists = readme.exists()
            
            # Calculate relative path from current file to module root
            try:
                rel_to_module = md_file.relative_to(module_path)
                depth = len(rel_to_module.parent.parts) - 1  # -1 because we're in module root
                up_path = '../' * depth if depth > 0 else './'
            except:
                up_path = '../'
            
            # Fix API_SPECIFICATION.md references
            if '../API_SPECIFICATION.md' in content or './API_SPECIFICATION.md' in content:
                if not api_spec_exists:
                    if readme_exists:
                        # Replace with README link
                        content = re.sub(
                            r'\[([^\]]+)\]\(\.\./API_SPECIFICATION\.md\)',
                            rf'[\1]({up_path}README.md#api-reference)',
                            content
                        )
                        content = re.sub(
                            r'\[([^\]]+)\]\(\./API_SPECIFICATION\.md\)',
                            rf'[\1]({up_path}README.md#api-reference)',
                            content
                        )
                    else:
                        # Remove the reference
                        content = re.sub(
                            r'\[[^\]]+\]\(\.\./API_SPECIFICATION\.md\)[^\n]*\n?',
                            '',
                            content
                        )
            
            # Fix USAGE_EXAMPLES.md references
            if '../USAGE_EXAMPLES.md' in content or './USAGE_EXAMPLES.md' in content:
                if not usage_examples_exists:
                    if readme_exists:
                        # Replace with README link
                        content = re.sub(
                            r'\[([^\]]+)\]\(\.\./USAGE_EXAMPLES\.md\)',
                            rf'[\1]({up_path}README.md#usage-examples)',
                            content
                        )
                        content = re.sub(
                            r'\[([^\]]+)\]\(\./USAGE_EXAMPLES\.md\)',
                            rf'[\1]({up_path}README.md#usage-examples)',
                            content
                        )
                    else:
                        # Remove the reference
                        content = re.sub(
                            r'\[[^\]]+\]\(\.\./USAGE_EXAMPLES\.md\)[^\n]*\n?',
                            '',
                            content
                        )
            
            # Fix MCP_TOOL_SPECIFICATION.md references
            if '../MCP_TOOL_SPECIFICATION.md' in content or './MCP_TOOL_SPECIFICATION.md' in content:
                if not mcp_spec_exists:
                    if readme_exists:
                        # Replace with README link
                        content = re.sub(
                            r'\[([^\]]+)\]\(\.\./MCP_TOOL_SPECIFICATION\.md\)',
                            rf'[\1]({up_path}README.md#mcp-tools)',
                            content
                        )
                        content = re.sub(
                            r'\[([^\]]+)\]\(\./MCP_TOOL_SPECIFICATION\.md\)',
                            rf'[\1]({up_path}README.md#mcp-tools)',
                            content
                        )
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                rel_path = md_file.relative_to(repo_root)
                print(f"✅ Fixed: {rel_path}")
                fixed_count += 1
                
        except Exception as e:
            rel_path = md_file.relative_to(repo_root) if md_file else 'unknown'
            print(f"⚠️  Error processing {rel_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} files")
    return 0


if __name__ == '__main__':
    sys.exit(fix_all_tutorial_references())

