from pathlib import Path
import re
import sys




#!/usr/bin/env python3
"""
Comprehensive fixer for all documentation issues.

Fixes:
1. References to API_SPECIFICATION.md, USAGE_EXAMPLES.md that don't exist
2. Updates example_tutorial.md files to use correct references
3. Ensures all broken links are resolved
"""



def fix_example_tutorial_references():
    """Fix all references in example_tutorial.md files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Find all example_tutorial.md files
    tutorial_files = list((repo_root / 'src' / 'codomyrmex').rglob('**/example_tutorial.md'))
    
    print(f"Fixing {len(tutorial_files)} example_tutorial.md files...\n")
    
    fixed_count = 0
    
    for tutorial_file in tutorial_files:
        try:
            content = tutorial_file.read_text(encoding='utf-8')
            original_content = content
            
            # Determine module root (go up from docs/tutorials/example_tutorial.md)
            module_path = tutorial_file.parent.parent.parent
            
            # Check what exists
            api_spec = module_path / 'API_SPECIFICATION.md'
            usage_examples = module_path / 'USAGE_EXAMPLES.md'
            readme = module_path / 'README.md'
            
            # Fix API_SPECIFICATION.md references
            if '../API_SPECIFICATION.md' in content:
                if api_spec.exists():
                    # Keep it
                    pass
                elif readme.exists():
                    # Replace with README
                    content = content.replace(
                        '../API_SPECIFICATION.md',
                        '../README.md#api-reference'
                    )
                else:
                    # Remove reference
                    content = re.sub(
                        r'- \[.*?API.*?\]\(\.\./API_SPECIFICATION\.md\)[^\n]*\n?',
                        '',
                        content
                    )
            
            # Fix USAGE_EXAMPLES.md references
            if '../USAGE_EXAMPLES.md' in content:
                if usage_examples.exists():
                    # Keep it
                    pass
                elif readme.exists():
                    # Replace with README
                    content = content.replace(
                        '../USAGE_EXAMPLES.md',
                        '../README.md#usage-examples'
                    )
                else:
                    # Remove reference
                    content = re.sub(
                        r'- \[.*?Usage.*?\]\(\.\./USAGE_EXAMPLES\.md\)[^\n]*\n?',
                        '',
                        content
                    )
            
            if content != original_content:
                tutorial_file.write_text(content, encoding='utf-8')
                rel_path = tutorial_file.relative_to(repo_root)
                print(f"✅ Fixed: {rel_path}")
                fixed_count += 1
                
        except Exception as e:
            rel_path = tutorial_file.relative_to(repo_root) if tutorial_file else 'unknown'
            print(f"❌ Error fixing {rel_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} tutorial files")
    return fixed_count


def fix_docs_index_references():
    """Fix references in docs/index.md files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    index_files = list((repo_root / 'src' / 'codomyrmex').rglob('**/docs/index.md'))
    
    print(f"\nFixing {len(index_files)} docs/index.md files...\n")
    
    fixed_count = 0
    
    for index_file in index_files:
        try:
            content = index_file.read_text(encoding='utf-8')
            original_content = content
            
            module_path = index_file.parent.parent
            
            # Check what exists
            api_spec = module_path / 'API_SPECIFICATION.md'
            usage_examples = module_path / 'USAGE_EXAMPLES.md'
            mcp_spec = module_path / 'MCP_TOOL_SPECIFICATION.md'
            readme = module_path / 'README.md'
            
            # Fix API_SPECIFICATION.md references
            if '../API_SPECIFICATION.md' in content:
                if not api_spec.exists() and readme.exists():
                    content = content.replace(
                        '../API_SPECIFICATION.md',
                        '../README.md#api-reference'
                    )
            
            # Fix USAGE_EXAMPLES.md references
            if '../USAGE_EXAMPLES.md' in content:
                if not usage_examples.exists() and readme.exists():
                    content = content.replace(
                        '../USAGE_EXAMPLES.md',
                        '../README.md#usage-examples'
                    )
            
            # Fix MCP_TOOL_SPECIFICATION.md references
            if '../MCP_TOOL_SPECIFICATION.md' in content:
                if not mcp_spec.exists() and readme.exists():
                    content = content.replace(
                        '../MCP_TOOL_SPECIFICATION.md',
                        '../README.md#mcp-tools'
                    )
            
            if content != original_content:
                index_file.write_text(content, encoding='utf-8')
                rel_path = index_file.relative_to(repo_root)
                print(f"✅ Fixed: {rel_path}")
                fixed_count += 1
                
        except Exception as e:
            rel_path = index_file.relative_to(repo_root) if index_file else 'unknown'
            print(f"❌ Error fixing {rel_path}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} index files")
    return fixed_count


def main():
    """Main function."""
    print("=" * 80)
    print("Comprehensive Documentation Fixer")
    print("=" * 80)
    print()
    
    tutorial_count = fix_example_tutorial_references()
    index_count = fix_docs_index_references()
    
    print()
    print("=" * 80)
    print(f"Summary: Fixed {tutorial_count + index_count} files")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

