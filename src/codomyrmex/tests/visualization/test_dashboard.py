from codomyrmex.visualization import generate_report
from pathlib import Path
import shutil

def test_report_generation():
    output_dir = "test_report_output"
    path = generate_report(output_dir)
    assert Path(path).exists()
    assert "Codomyrmex Executive Dashboard" in Path(path).read_text()
    
    # Cleanup
    shutil.rmtree(output_dir)
