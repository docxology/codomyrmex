#!/usr/bin/env python3
"""
Verification Agent: Structure Parity Check
Verifies that the `scripts/` directory structure mirrors `src/codomyrmex/`
and that every module has a corresponding orchestrator.
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Set, Tuple, List

# Add src to path to import AntigravityClient (scripts/utils/file.py -> parents[2] is repo root)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codomyrmex.ide.antigravity import AntigravityClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_parity")

def get_subdirectories(path: Path) -> Set[str]:
    """Get all immediate subdirectories excluding hidden/special ones."""
    if not path.exists():
        return set()
    return {
        d.name for d in path.iterdir() 
        if d.is_dir() 
        and not d.name.startswith((".", "__"))
        and d.name != "tests"
    }

def verify_structure(src_root: Path, scripts_root: Path) -> Tuple[bool, str]:
    """
    Verifies that scripts/ mirrors src/codomyrmex structure.
    Returns (success, report_message).
    """
    src_modules = get_subdirectories(src_root)
    script_modules = get_subdirectories(scripts_root)
    
    missing_in_scripts = src_modules - script_modules
    extra_in_scripts = script_modules - src_modules
    
    # Check for orchestrate.py in existing script directories
    missing_orchestrators = []
    for module in src_modules:
        if module in script_modules:
            orch_path = scripts_root / module / "orchestrate.py"
            if not orch_path.exists():
                missing_orchestrators.append(module)
                
    # Build Report
    success = not missing_in_scripts and not missing_orchestrators
    
    report = ["**Structure Parity Report**"]
    report.append(f"Source Modules: {len(src_modules)}")
    report.append(f"Script Modules: {len(script_modules)}")
    
    if success:
        report.append("\n✅ **SUCCESS:** Structure is fully synchronized.")
        report.append(f"- All {len(src_modules)} source modules have matching script directories.")
        report.append(f"- All script directories contain `orchestrate.py`.")
    else:
        report.append("\n❌ **FAILURE:** Structure mismatch detected.")
        
        if missing_in_scripts:
            report.append(f"\nMissing Script Directories ({len(missing_in_scripts)}):")
            for m in sorted(missing_in_scripts):
                report.append(f"- {m}")
                
        if missing_orchestrators:
            report.append(f"\nMissing orchestrate.py ({len(missing_orchestrators)}):")
            for m in sorted(missing_orchestrators):
                report.append(f"- {m}/orchestrate.py")
                
    if extra_in_scripts:
        report.append(f"\nExtra Script Directories ({len(extra_in_scripts)}):")
        # These aren't necessarily failures, but good to know
        for m in sorted(extra_in_scripts):
            report.append(f"- {m}")

    return success, "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Verify scripts/ vs src/codomyrmex/ parity.")
    parser.add_argument("--gui", action="store_true", help="Send report via GUI automation")
    args = parser.parse_args()
    
    # Path is scripts/utils/verify_structure_parity.py -> parents[2] is scripts/, parents[3] is repo root
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "src" / "codomyrmex"
    scripts_dir = repo_root / "scripts"
    
    logger.info(f"Verifying structure: {src_dir} vs {scripts_dir}")
    
    success, report = verify_structure(src_dir, scripts_dir)
    
    print(report)
    
    # Dispatch Agent to Report (optional - don't fail if unavailable)
    try:
        client = AntigravityClient()
        if client.connect():
            logger.info("Dispatching report to Antigravity Chat...")
            if args.gui:
                client.send_chat_gui(report)
            else:
                client.send_chat_message(report)
        else:
            logger.info("Antigravity not available - report printed to stdout only.")
    except Exception as e:
        logger.info(f"Skipping Antigravity dispatch: {e}")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
