import unittest
import sys
import shutil
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.system_discovery.discovery_engine import SystemDiscovery
from codomyrmex.agents.jules.jules_client import JulesClient
from codomyrmex.agents.every_code.every_code_client import EveryCodeClient
from codomyrmex.agents.core import AgentRequest

class TestBatch4Enhancements(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_system_discovery_scan(self):
        print("\nTesting SystemDiscovery scan_system...")
        discovery = SystemDiscovery(project_root=project_root)
        inventory = discovery.scan_system()
        
        self.assertIsInstance(inventory, dict)
        self.assertIn("modules", inventory)
        self.assertIn("status", inventory)
        self.assertIn("stats", inventory)
        
        # Check specific module presence
        self.assertIn("agents", inventory["modules"])
        
        print(f"✅ System Discovery Scan: PASSED (Found {inventory['stats']['total_modules']} modules)")

    def test_system_discovery_export(self):
        print("\nTesting SystemDiscovery export_inventory...")
        discovery = SystemDiscovery(project_root=project_root)
        export_path = self.temp_path / "inventory.json"
        
        success = discovery.export_inventory(export_path)
        self.assertTrue(success)
        self.assertTrue(export_path.exists())
        
        with open(export_path) as f:
            data = json.load(f)
            self.assertIn("modules", data)
            
        print("✅ System Discovery Export: PASSED")

    def test_jules_client_auth_config(self):
        print("\nTesting JulesClient auth/config support...")
        client = JulesClient()
        
        # Mock _execute_command
        client._execute_command = MagicMock(return_value={"success": True, "stdout": "ok"})
        
        # Test execute_jules_command with config
        config_path = self.temp_path / "jules.config"
        client.execute_jules_command("auth", args=["login"], config_path=config_path)
        
        # Verify args construction
        call_args = client._execute_command.call_args[1]["args"]
        self.assertIn("--config", call_args)
        self.assertIn(str(config_path), call_args)
        self.assertIn("auth", call_args)
        self.assertIn("login", call_args)
        
        print("✅ JulesClient Auth/Config: PASSED")

    def test_jules_client_retry(self):
        print("\nTesting JulesClient retry logic...")
        client = JulesClient()
        
        # Mock _execute_command to fail twice then succeed
        client._execute_command = MagicMock(side_effect=[
             # Fail 1 (Timeout)
             Exception("Timeout"),
             # Fail 2 (Timeout)
             Exception("Timeout"), 
             # Success
             {"success": True, "stdout": "Success!"}
        ])

        # We actually need to mock AgentTimeoutError raising if we want to test that specific path,
        # but here we test general retry loop behavior if we can trigger it.
        # However, _execute_impl catches AgentTimeoutError. 
        # Let's mock _execute_command to return a result directly for success, 
        # but to test retry we need it to raise AgentTimeoutError.
        
        from codomyrmex.agents.core.exceptions import AgentTimeoutError
        
        client._execute_command = MagicMock(side_effect=[
            AgentTimeoutError("Timeout 1"),
            AgentTimeoutError("Timeout 2"),
            {"success": True, "stdout": "Success at last"}
        ])
        
        response = client._execute_impl(AgentRequest(prompt="test"))
        self.assertTrue(response.metadata["jules_success"])
        self.assertEqual(response.metadata["attempt"], 3)
        
        print("✅ JulesClient Retry: PASSED")

    def test_every_code_sanitation(self):
        print("\nTesting EveryCodeClient sanitation...")
        client = EveryCodeClient()
        
        safe_file = self.temp_path / "safe.txt"
        safe_file.touch()
        
        # Test _build_code_input with safe and unsafe paths
        context = {
            "files": [
                str(safe_file),
                "../../etc/passwd", # Unsafe
                "/bin/sh|whoami"   # Unsafe
            ]
        }
        
        input_str = client._build_code_input("analyze", context)
        
        self.assertIn(str(safe_file), input_str)
        self.assertNotIn("passwd", input_str)
        self.assertNotIn("whoami", input_str)
        
        print("✅ EveryCodeClient Sanitation: PASSED")

if __name__ == "__main__":
    unittest.main()
