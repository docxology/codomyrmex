
import sys
import importlib
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

import codomyrmex

print(f"Codomyrmex Version: {codomyrmex.get_version()}")
print(f"Module Path: {codomyrmex.get_module_path()}")

# Try to access exported submodules
modules_to_check = [
    "agents", "api", "auth", "build_synthesis", "cache", "cerebrum",
    "ci_cd_automation", "cli", "cloud", "coding", "compression",
    "config_management", "containerization", "data_visualization",
    "database_management", "documentation", "documents", "encryption",
    "environment_setup", "events", "examples", "exceptions", "fpf",
    "git_operations", "ide", "llm", "logging_monitoring", "logistics",
    "metrics", "model_context_protocol", "module_template", "networking",
    "orchestrator", "pattern_matching", "performance", "physical_management",
    "plugin_system", "scrape", "security", "serialization", "skills",
    "spatial", "static_analysis", "system_discovery", "templating",
    "terminal_interface", "tests", "tools", "utils", "validation", "website"
]

failed = []
print("\nChecking submodule accessibility:")
for mod_name in modules_to_check:
    try:
        if hasattr(codomyrmex, mod_name):
            print(f"✅ codomyrmex.{mod_name} available")
        else:
            print(f"❌ codomyrmex.{mod_name} NOT exported")
            failed.append(mod_name)
    except Exception as e:
        print(f"🔥 Error accessing {mod_name}: {e}")
        failed.append(mod_name)

if failed:
    print(f"\nFailed modules: {failed}")
    sys.exit(1)
else:
    print("\nAll modules verified successfully.")
