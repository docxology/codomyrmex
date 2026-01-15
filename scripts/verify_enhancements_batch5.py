
import unittest
import sys
import logging
import io
from pathlib import Path

from codomyrmex.system_discovery.discovery_engine import SystemDiscovery

class TestBatch5LegacyCleanup(unittest.TestCase):
    def setUp(self):
        self.project_root = Path("/Users/4d/Documents/GitHub/codomyrmex")
        self.discovery = SystemDiscovery(project_root=self.project_root)
        
    def test_broken_modules_are_fixed(self):
        """Test that previously broken modules are now importable."""
        print("\n🔍 Scanning system for legacy module health...")
        
        # Capture logs to check for import warnings
        log_capture_string = io.StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.WARNING)
        logger = logging.getLogger("codomyrmex.system_discovery.discovery_engine")
        logger.addHandler(ch)
        
        inventory = self.discovery.scan_system()
        
        logger.removeHandler(ch)
        log_contents = log_capture_string.getvalue()
        
        # Define the list of modules that were broken
        formerly_broken_modules = [
            "codomyrmex.tools",
            "codomyrmex.physical_management",
            "codomyrmex.scrape",
            "codomyrmex.cloud",
            "codomyrmex.environment_setup",
            "codomyrmex.spatial",
            "codomyrmex.pattern_matching",
            "codomyrmex.cerebrum",
            "codomyrmex.fpf" 
        ]
        
        print(f"Checking {len(formerly_broken_modules)} formerly broken modules...")
        print(f"Available keys: {list(inventory['modules'].keys())}")
        
        all_passed = True
        for module_name in formerly_broken_modules:
            # Try both full name and short name
            short_name = module_name.split(".")[-1]
            if module_name in inventory["modules"]:
                module_info = inventory["modules"][module_name]
            elif short_name in inventory["modules"]:
                module_info = inventory["modules"][short_name]
            else:
                print(f"  {module_name:<35} ❓ NOT FOUND")
                all_passed = False
                continue

            status = "✅ FIXED" if module_info['is_importable'] else "❌ BROKEN"
            print(f"  {module_name:<35} {status}")
            
            if not module_info['is_importable']:
                    all_passed = False
                    print(f"    Error: {module_info.get('error', 'Unknown error')}")
            else:
                print(f"  {module_name:<35} ❓ NOT FOUND")
                all_passed = False

        # Additional assertions
        self.assertTrue(all_passed, "Some legacy modules are still broken.")
        
        # Check specific fixes
        self.assertIn("Camera3D", str(inventory["modules"].get("codomyrmex.spatial", {})))
        self.assertIn("CodaAuthenticationError", str(inventory["modules"].get("codomyrmex.cloud", {})))
        
        # Check logs for "Could not import"
        if "Could not import" in log_contents:
            print("\n⚠️  Warnings found in system scan:")
            print(log_contents)
            # We want this to be clean, so fail if we see import errors
            self.fail("System scan produced import warnings.")
            
        print("\n✨ All legacy modules successfully repaired!")

if __name__ == "__main__":
    unittest.main()
