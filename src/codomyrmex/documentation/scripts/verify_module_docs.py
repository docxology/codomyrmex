from collections import defaultdict
from pathlib import Path
import json

from codomyrmex.logging_monitoring import get_logger




















#!/usr/bin/env python3
"""
def verify_modules(base_path: Path) -> dict:
    """



    #!/usr/bin/env python3
    """Verify all modules have required documentation files."""

logger = get_logger(__name__)

Verify all modules have README.md, AGENTS.md, and SPEC.md."""
    results = {
        "modules": {},
        "missing_files": defaultdict(list),
        "summary": {
            "total_modules": 0,
            "complete_modules": 0,
            "incomplete_modules": 0,
            "missing_readme": 0,
            "missing_agents": 0,
            "missing_spec": 0
        }
    }
    
    # Get all module directories (excluding special dirs)
    exclude_dirs = {'__pycache__', '.DS_Store', '.cursor', 'tests'}
    modules = [d for d in base_path.iterdir() 
               if d.is_dir() and d.name not in exclude_dirs]
    
    for module_dir in sorted(modules):
        module_name = module_dir.name
        results["summary"]["total_modules"] += 1
        
        has_readme = (module_dir / "README.md").exists()
        has_agents = (module_dir / "AGENTS.md").exists()
        has_spec = (module_dir / "SPEC.md").exists()
        
        module_info = {
            "has_readme": has_readme,
            "has_agents": has_agents,
            "has_spec": has_spec,
            "complete": has_readme and has_agents and has_spec
        }
        
        results["modules"][module_name] = module_info
        
        if module_info["complete"]:
            results["summary"]["complete_modules"] += 1
        else:
            results["summary"]["incomplete_modules"] += 1
            
            if not has_readme:
                results["summary"]["missing_readme"] += 1
                results["missing_files"]["README.md"].append(module_name)
            if not has_agents:
                results["summary"]["missing_agents"] += 1
                results["missing_files"]["AGENTS.md"].append(module_name)
            if not has_spec:
                results["summary"]["missing_spec"] += 1
                results["missing_files"]["SPEC.md"].append(module_name)
    
    return results

if __name__ == "__main__":
    base_path = Path(__file__).parent.parent / "src" / "codomyrmex"
    results = verify_modules(base_path)
    
    print("=" * 70)
    print("MODULE DOCUMENTATION VERIFICATION")
    print("=" * 70)
    
    summary = results["summary"]
    print(f"\nTotal Modules: {summary['total_modules']}")
    print(f"Complete Modules: {summary['complete_modules']}")
    print(f"Incomplete Modules: {summary['incomplete_modules']}")
    
    if summary['incomplete_modules'] > 0:
        print(f"\nMissing Files:")
        print(f"  - README.md: {summary['missing_readme']} modules")
        print(f"  - AGENTS.md: {summary['missing_agents']} modules")
        print(f"  - SPEC.md: {summary['missing_spec']} modules")
        
        print("\n" + "=" * 70)
        print("DETAILED BREAKDOWN")
        print("=" * 70)
        
        for file_type, modules in results["missing_files"].items():
            if modules:
                print(f"\nMissing {file_type}:")
                for module in sorted(modules):
                    status = []
                    mod_info = results["modules"][module]
                    if mod_info["has_readme"]: status.append("README")
                    if mod_info["has_agents"]: status.append("AGENTS")
                    if mod_info["has_spec"]: status.append("SPEC")
                    print(f"  - {module} (has: {', '.join(status) if status else 'none'})")
        
        print("\n" + "=" * 70)
        print("COMPLETE MODULES")
        print("=" * 70)
        complete = [name for name, info in results["modules"].items() if info["complete"]]
        for module in sorted(complete):
            print(f"  ✓ {module}")
    else:
        print("\n✓ All modules have complete documentation!")
    
    # Save JSON report
    output_file = base_path.parent.parent / "output" / "module_doc_verification.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n\nFull report saved to: {output_file}")
