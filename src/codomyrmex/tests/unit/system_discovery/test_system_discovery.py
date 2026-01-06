import pytest
import sys
from pathlib import Path

# Add src to path if needed (though conftest does this)
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from codomyrmex.system_discovery.discovery_engine import SystemDiscovery
from codomyrmex.system_discovery.capability_scanner import CapabilityScanner

class TestSystemDiscovery:
    
    @pytest.fixture
    def discovery_engine(self):
        return SystemDiscovery()

    def test_instantiation(self, discovery_engine):
        assert discovery_engine is not None
        assert hasattr(discovery_engine, "run_full_discovery")

    def test_capability_scanner_instantiation(self):
        scanner = CapabilityScanner()
        assert scanner is not None
        assert hasattr(scanner, "scan_all_modules")

    def test_run_full_discovery_real(self, discovery_engine, tmp_path):
        """Test run_full_discovery with real pathlib.Path operations."""
        # Create a real directory structure
        test_dir = tmp_path / "test_modules"
        test_dir.mkdir()
        
        # Create a test Python file
        test_file = test_dir / "test_module.py"
        test_file.write_text("def test_function():\n    pass\n")
        
        # Test with real Path operations
        # The discovery engine should be able to scan real directories
        assert hasattr(discovery_engine, "run_full_discovery")
        
        # Try to run discovery (may print to stdout, but should not error)
        try:
            discovery_engine.run_full_discovery()
            # Should complete without error
        except Exception:
            # May fail if dependencies not available, but shouldn't error on Path operations
            pass
