#!/usr/bin/env python3
"""
Update parent module __init__.py files to include new submodules.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_BASE = PROJECT_ROOT / "src" / "codomyrmex"

# Updates for each parent module
UPDATES = {
    "api": {
        "submodules": ["webhooks", "mocking", "circuit_breaker", "pagination"],
        "docstring_additions": """    - webhooks: Webhook dispatch and receipt management
    - mocking: API mock server for development and testing
    - circuit_breaker: Resilience patterns (retry, circuit breaker, bulkhead)
    - pagination: Cursor and offset pagination utilities"""
    },
    "cache": {
        "submodules": ["warmers", "async_ops", "replication"],
        "docstring_additions": """    - warmers: Cache pre-population and predictive caching
    - async_ops: Async cache operations for non-blocking access
    - replication: Cross-region cache synchronization"""
    },
    "security": {
        "submodules": ["scanning", "secrets", "compliance", "audit"],
        "docstring_additions": """    - scanning: SAST/DAST integration for automated security testing
    - secrets: Secret detection, rotation, and secure storage
    - compliance: GDPR, SOC2, HIPAA compliance checking
    - audit: Security audit logging and forensic analysis"""
    },
    "telemetry": {
        "submodules": ["tracing", "sampling", "alerting"],
        "docstring_additions": """    - tracing: Distributed tracing setup helpers
    - sampling: Dynamic sampling strategies
    - alerting: Alert rule configuration and routing"""
    },
    "orchestrator": {
        "submodules": ["pipelines", "triggers", "state", "templates"],
        "docstring_additions": """    - pipelines: Multi-step pipeline definitions with DAG support
    - triggers: Event and time-based workflow triggers
    - state: State machine implementations
    - templates: Reusable workflow templates"""
    },
    "database_management": {
        "submodules": ["connections", "replication", "sharding", "audit"],
        "docstring_additions": """    - connections: Connection pooling and lifecycle management
    - replication: Read replica routing and load balancing
    - sharding: Horizontal sharding utilities
    - audit: Query logging and slow query detection"""
    },
    "validation": {
        "submodules": ["schemas", "sanitizers", "rules"],
        "docstring_additions": """    - schemas: Schema registry and versioning
    - sanitizers: Input sanitization utilities
    - rules: Custom validation rule definitions"""
    },
    "skills": {
        "submodules": ["marketplace", "versioning", "permissions"],
        "docstring_additions": """    - marketplace: Skill discovery from external sources
    - versioning: Skill version management
    - permissions: Skill capability permissions"""
    },
}


def update_init_file(module_name: str, info: dict) -> bool:
    """Update an __init__.py file to include new submodules."""
    init_path = SRC_BASE / module_name / "__init__.py"
    
    if not init_path.exists():
        print(f"  ⚠️  {init_path} not found")
        return False
    
    content = init_path.read_text()
    modified = False
    
    # Add imports for new submodules
    import_lines = []
    for submod in info["submodules"]:
        import_line = f"from . import {submod}"
        if import_line not in content:
            import_lines.append(import_line)
    
    if import_lines:
        # Find a good place to insert imports (after existing imports)
        lines = content.split('\n')
        insert_idx = len(lines)
        
        for i, line in enumerate(lines):
            if line.startswith('__all__') or line.startswith('__version__'):
                insert_idx = i
                break
        
        # Insert new imports
        for import_line in import_lines:
            lines.insert(insert_idx, import_line)
            insert_idx += 1
        
        content = '\n'.join(lines)
        modified = True
    
    # Add submodules to __all__ if it exists
    for submod in info["submodules"]:
        all_entry = f"'{submod}'"
        if all_entry not in content and f'"{submod}"' not in content:
            # Find __all__ and add to it
            if "__all__ = [" in content:
                content = content.replace("__all__ = [", f"__all__ = [\n    '{submod}',")
                modified = True
    
    if modified:
        init_path.write_text(content)
        return True
    
    return False


def main():
    """Main execution."""
    print("=" * 60)
    print("UPDATING PARENT MODULE __init__.py FILES")
    print("=" * 60)
    
    updated = 0
    for module_name, info in UPDATES.items():
        print(f"\n  {module_name}/")
        if update_init_file(module_name, info):
            print(f"    ✓ Updated __init__.py")
            updated += 1
        else:
            print(f"    ○ No changes needed")
    
    print(f"\n✅ Updated {updated} modules")
    return 0


if __name__ == "__main__":
    sys.exit(main())
