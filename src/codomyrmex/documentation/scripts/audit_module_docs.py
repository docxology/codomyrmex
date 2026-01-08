from pathlib import Path
import json

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
def audit_modules(base_path: Path) -> dict:
    """



    #!/usr/bin/env python3
    """Audit module documentation completeness."""

logger = get_logger(__name__)

Audit all modules for documentation completeness."""
    results = {
        "modules": {},
        "missing_docs": [],
        "missing_agents": [],
        "missing_readme": [],
        "missing_spec": [],
        "submodules": {}
    }
    
    # Get all module directories
    modules = [d for d in base_path.iterdir() 
               if d.is_dir() and not d.name.startswith('_') and d.name != 'tests']
    
    for module_dir in sorted(modules):
        module_name = module_dir.name
        module_info = {
            "has_agents": (module_dir / "AGENTS.md").exists(),
            "has_readme": (module_dir / "README.md").exists(),
            "has_spec": (module_dir / "SPEC.md").exists(),
            "submodules": []
        }
        
        # Check for submodules
        submodules = [d for d in module_dir.iterdir() 
                     if d.is_dir() and not d.name.startswith('_') 
                     and d.name not in ['tests', 'docs', '__pycache__', '.cursor']]
        
        for submodule_dir in submodules:
            submodule_name = submodule_dir.name
            submodule_info = {
                "has_agents": (submodule_dir / "AGENTS.md").exists(),
                "has_readme": (submodule_dir / "README.md").exists(),
                "has_spec": (submodule_dir / "SPEC.md").exists(),
            }
            module_info["submodules"].append({
                "name": submodule_name,
                **submodule_info
            })
            
            if not submodule_info["has_agents"]:
                results["missing_agents"].append(f"{module_name}/{submodule_name}")
            if not submodule_info["has_readme"]:
                results["missing_readme"].append(f"{module_name}/{submodule_name}")
            if not submodule_info["has_spec"]:
                results["missing_spec"].append(f"{module_name}/{submodule_name}")
        
        results["modules"][module_name] = module_info
        
        if not module_info["has_agents"]:
            results["missing_agents"].append(module_name)
        if not module_info["has_readme"]:
            results["missing_readme"].append(module_name)
        if not module_info["has_spec"]:
            results["missing_spec"].append(module_name)
    
    return results

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent / "src" / "codomyrmex"
    results = audit_modules(base_path)
    
    print("=" * 60)
    print("MODULE DOCUMENTATION AUDIT")
    print("=" * 60)
    print(f"\nTotal modules audited: {len(results['modules'])}")
    print(f"\nMissing AGENTS.md: {len(results['missing_agents'])}")
    if results['missing_agents']:
        for item in results['missing_agents']:
            print(f"  - {item}")
    
    print(f"\nMissing README.md: {len(results['missing_readme'])}")
    if results['missing_readme']:
        for item in results['missing_readme']:
            print(f"  - {item}")
    
    print(f"\nMissing SPEC.md: {len(results['missing_spec'])}")
    if results['missing_spec']:
        for item in results['missing_spec']:
            print(f"  - {item}")
    
    print("\n" + "=" * 60)
    print("SUBMODULES FOUND:")
    print("=" * 60)
    for module_name, module_info in results['modules'].items():
        if module_info['submodules']:
            print(f"\n{module_name}/")
            for sub in module_info['submodules']:
                status = []
                if sub['has_agents']: status.append("AGENTS")
                if sub['has_readme']: status.append("README")
                if sub['has_spec']: status.append("SPEC")
                print(f"  - {sub['name']}: {', '.join(status) if status else 'NO DOCS'}")
    
    # Save JSON report
    output_file = base_path.parent.parent / "output" / "module_doc_audit.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n\nFull report saved to: {output_file}")
