#!/usr/bin/env python3
"""
Automatic Documentation Generator for Codomyrmex.

Uses smart template engine to automatically regenerate documentation for modules.
"""

import sys
from pathlib import Path
from typing import List, Optional
import json

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Import smart template engine
sys.path.insert(0, str(Path(__file__).parent))
from smart_template_engine import SmartTemplateEngine


class AutoDocumentationGenerator:
    """Automatically generates documentation using smart templates."""
    
    def __init__(self, repo_root: Path, dry_run: bool = False):
        """Initialize generator."""
        self.repo_root = repo_root.resolve()
        self.src_path = repo_root / 'src' / 'codomyrmex'
        self.template_engine = SmartTemplateEngine(repo_root)
        self.dry_run = dry_run
        
    def find_modules(self, module_name: Optional[str] = None) -> List[Path]:
        """Find Python modules to document."""
        if module_name:
            # Find specific module
            module_path = self.src_path / module_name
            if not module_path.exists():
                logger.error(f"Module not found: {module_name}")
                return []
            
            # Find __init__.py in the module
            init_file = module_path / '__init__.py'
            if init_file.exists():
                return [init_file]
            else:
                logger.warning(f"No __init__.py found in {module_name}")
                return []
        
        # Find all modules
        modules = []
        for module_dir in self.src_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('_'):
                init_file = module_dir / '__init__.py'
                if init_file.exists():
                    modules.append(init_file)
        
        return sorted(modules)
    
    def generate_readme(self, module_path: Path, analysis: any) -> str:
        """Generate README.md content."""
        content = self.template_engine.generate_readme_content(analysis)
        
        readme_template = f"""# {content['module_name'].replace('_', ' ').title()}

**Version**: {content.get('version', '0.1.0')} | **Status**: {content.get('status', 'Active')}

## Overview

{content.get('description', 'Module documentation')}

## Quick Start

```{content.get('language', 'python')}
{content.get('quick_start_example', '# Example usage here')}
```

## Architecture

```mermaid
{content.get('architecture_diagram', 'graph TB')}
```

## API Reference

"""
        
        # Add API functions
        api_functions = content.get('api_functions', [])
        for func in api_functions:
            readme_template += f"""### `{func['name']}()`

{func.get('description', 'Function description')}

**Parameters**:
"""
            for param in func.get('parameters', []):
                readme_template += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
            
            readme_template += f"\n**Returns**: {func.get('returns', 'None')}\n\n"
            readme_template += f"**Example**:\n```python\n{func.get('example', '')}\n```\n\n"
        
        readme_template += """
## Integration

See the module's AGENTS.md for integration and orchestration details.

## Testing

Comprehensive tests are available in the `tests/` directory.

## Documentation

For complete documentation, see:
- [Module API](API_SPECIFICATION.md)
- [Module MCP Tools](MCP_TOOL_SPECIFICATION.md)
"""
        
        return readme_template
    
    def generate_agents_md(self, module_path: Path, analysis: any) -> str:
        """Generate AGENTS.md content."""
        content = self.template_engine.generate_agents_content(module_path, analysis)
        
        agents_template = f"""# Codomyrmex Agents — {content['relative_path']}

## Purpose
{content.get('purpose_description', 'Module coordination and orchestration')}

## Active Components
"""
        
        for component in content.get('components', []):
            agents_template += f"- **{component['name']}** - {component['description']}\n"
        
        agents_template += """
## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All exposed functions must be real, executable implementations (no stubs).

"""
        
        # Add related modules if any
        if content.get('related_modules'):
            agents_template += "## Related Modules\n"
            for rel in content['related_modules']:
                agents_template += f"- **{rel['name']}** (`{rel['path']}`) - {rel['relationship']}\n"
            agents_template += "\n"
        
        agents_template += "## Navigation Links\n"
        for link in content.get('nav_links', []):
            agents_template += f"- **{link['icon']} {link['label']}**: [{link['title']}]({link['path']}) - {link['description']}\n"
        
        return agents_template
    
    def generate_documentation(self, module_name: Optional[str] = None) -> int:
        """Generate documentation for modules."""
        modules = self.find_modules(module_name)
        
        if not modules:
            logger.error("No modules found to document")
            return 1
        
        logger.info(f"Found {len(modules)} modules to document")
        
        generated_count = 0
        
        for module_path in modules:
            module_dir = module_path.parent
            module_name = module_dir.name
            
            logger.info(f"Generating documentation for {module_name}...")
            
            try:
                # Analyze module
                analysis = self.template_engine.analyze_module(module_path)
                
                # Generate README
                readme_content = self.generate_readme(module_path, analysis)
                readme_path = module_dir / 'README.md'
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would write README to: {readme_path}")
                    print(f"\n--- README.md preview for {module_name} ---")
                    print(readme_content[:500] + "...\n")
                else:
                    readme_path.write_text(readme_content, encoding='utf-8')
                    logger.info(f"Generated: {readme_path}")
                
                # Generate AGENTS.md
                agents_content = self.generate_agents_md(module_path, analysis)
                agents_path = module_dir / 'AGENTS.md'
                
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would write AGENTS.md to: {agents_path}")
                else:
                    agents_path.write_text(agents_content, encoding='utf-8')
                    logger.info(f"Generated: {agents_path}")
                
                generated_count += 1
                
            except Exception as e:
                logger.error(f"Error generating documentation for {module_name}: {e}")
                continue
        
        logger.info(f"Successfully generated documentation for {generated_count}/{len(modules)} modules")
        
        return 0 if generated_count > 0 else 1


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatically generate module documentation")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--module', type=str, default=None,
                       help='Specific module to document (default: all modules)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without writing files')
    parser.add_argument('--all', action='store_true',
                       help='Generate documentation for all modules')
    
    args = parser.parse_args()
    
    # Create generator
    generator = AutoDocumentationGenerator(args.repo_root, dry_run=args.dry_run)
    
    # Generate documentation
    module_name = args.module if not args.all else None
    
    if args.dry_run:
        print("\n" + "="*80)
        print("DRY RUN MODE - No files will be modified")
        print("="*80 + "\n")
    
    result = generator.generate_documentation(module_name)
    
    if args.dry_run:
        print("\n" + "="*80)
        print("DRY RUN COMPLETE - No files were modified")
        print("Run without --dry-run to apply changes")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("DOCUMENTATION GENERATION COMPLETE")
        print("="*80)
    
    sys.exit(result)


if __name__ == '__main__':
    main()

