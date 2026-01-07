import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from codomyrmex.website.generator import WebsiteGenerator

@pytest.fixture
def mock_dirs(tmp_path):
    output_dir = tmp_path / "output"
    
    # We need a valid module dir for templates
    module_dir = tmp_path / "module"
    module_dir.mkdir()
    (module_dir / "templates").mkdir()
    (module_dir / "assets").mkdir()
    
    # Create a dummy template
    (module_dir / "templates" / "index.html").write_text("Hello {{ system.status }}")
    
    return output_dir, module_dir

def test_generator_initialization(tmp_path):
    gen = WebsiteGenerator(output_dir=str(tmp_path / "out"), root_dir=str(tmp_path))
    assert gen.output_dir == tmp_path / "out"
    assert gen.root_dir == tmp_path

def test_generate_flow(mock_dirs):
    output_dir, module_dir = mock_dirs
    
    # Patch the module path resolution in the class to use our temp module_dir
    with patch("codomyrmex.website.generator.Path") as MockPath:
        # We need to let normal Path works for everything EXCEPT __file__ resolution if we were doing it that way.
        # But since we can't easily patch __file__, we might need to rely on the fact that the test environment 
        # uses the REAL source code. 
        # Instead, let's just instantiate the real class but rely on mocking the DataProvider or template loading if needed.
        # Ideally, we'd pass module_dir into the constructor, but it calculates it from __file__.
        # For this test, we accept we are testing the REAL templates on disk, unless we refactor.
        pass

    # A more integration-style test using the real templates:
    # This requires the source code to be present and valid.
    
    output_dir.mkdir(parents=True, exist_ok=True) # Ensure parent exists
    
    gen = WebsiteGenerator(output_dir=str(output_dir))
    
    # Run generation
    gen.generate()
    
    # Verify outputs
    assert (output_dir / "index.html").exists()
    assert (output_dir / "assets").exists()
    assert (output_dir / "assets" / "style.css").exists()
    
    content = (output_dir / "index.html").read_text()
    assert "Codomyrmex" in content
    assert "System Status" in content
