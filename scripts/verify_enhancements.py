
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codomyrmex.serialization.serializer import Serializer, SerializationFormat
from codomyrmex.plugin_system.plugin_manager import PluginManager
from codomyrmex.orchestrator.runner import run_function, run_script

def dummy_func(x):
    return x * 2

class TestEnhancements(unittest.TestCase):
    
    def test_serialization(self):
        print("\nTesting Serialization Enhancements...")
        s = Serializer()
        
        # Test Path serialization
        p = Path("/tmp/test")
        json_bytes = s.serialize(p, SerializationFormat.JSON)
        print(f"Path JSON: {json_bytes}")
        self.assertIn(b"/tmp/test", json_bytes)
        
        # Test YAML
        try:
            import yaml
            data = {"key": "value", "path": Path("foo/bar")}
            yaml_bytes = s.serialize(data, SerializationFormat.YAML)
            print(f"YAML output: {yaml_bytes}")
            self.assertIn(b"key: value", yaml_bytes)
            self.assertIn(b"path: foo/bar", yaml_bytes)
            
            restored = s.deserialize(yaml_bytes, SerializationFormat.YAML)
            self.assertEqual(restored['key'], 'value')
        except ImportError:
            print("PyYAML not installed, skipping YAML test")

    def test_plugin_topological_sort(self):
        print("\nTesting Plugin Topological Sort...")
        manager = PluginManager()
        
        # Mock registry
        manager.registry.get_plugin_info = MagicMock()
        
        def get_info(name):
            info = MagicMock()
            if name == "A": info.dependencies = ["B", "C"]
            elif name == "B": info.dependencies = ["C"]
            elif name == "C": info.dependencies = []
            elif name == "D": info.dependencies = ["A"]
            return info
            
        manager.registry.get_plugin_info.side_effect = get_info
        
        plugins = ["A", "B", "C", "D"]
        sorted_plugins = manager.resolve_load_order(plugins)
        print(f"Sorted plugins: {sorted_plugins}")
        
        # C must come before B and A
        self.assertLess(sorted_plugins.index("C"), sorted_plugins.index("B"))
        self.assertLess(sorted_plugins.index("C"), sorted_plugins.index("A"))
        # B must come before A
        self.assertLess(sorted_plugins.index("B"), sorted_plugins.index("A"))
        # A must come before D
        self.assertLess(sorted_plugins.index("A"), sorted_plugins.index("D"))

    def test_orchestrator_runner(self):
        print("\nTesting Orchestrator Runner...")
        
        # Test run_function
            
        result = run_function(dummy_func, args=(21,))
        print(f"Function result: {result}")
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['result'], 42)
        
        # Test memory limit (soft test, just checking it doesn't crash)
        # We can't easily trigger OOM without massive allocation, 
        # but we can verify it runs with a reasonable limit
        result_mem = run_function(dummy_func, args=(10,), memory_limit_mb=100)
        self.assertEqual(result_mem['status'], 'passed')

if __name__ == '__main__':
    unittest.main()
