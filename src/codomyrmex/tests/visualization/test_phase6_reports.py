import pytest
import os
from codomyrmex.data_visualization import generate_report
from codomyrmex.data_visualization.reports.finance import FinanceReport
from codomyrmex.data_visualization.reports.marketing import MarketingReport
from codomyrmex.data_visualization.reports.logistics import LogisticsReport

def test_finance_report_generation(tmpdir):
    report = FinanceReport()
    report.generate()
    output_path = tmpdir.join("finance.html")
    report.dashboard.render(str(output_path))
    
    with open(str(output_path), 'r') as f:
        html = f.read()
        
    assert "Financial Overview" in html
    assert "Net Profit" in html
    assert "CDMX Stock" in html

def test_marketing_report_generation(tmpdir):
    report = MarketingReport()
    report.generate()
    output_path = tmpdir.join("marketing.html")
    report.dashboard.render(str(output_path))
    
    with open(str(output_path), 'r') as f:
        html = f.read()
        
    assert "Marketing Analysis" in html
    assert "Brand Awareness" in html
    assert "User Acquisition" in html

def test_logistics_report_generation(tmpdir):
    report = LogisticsReport()
    report.generate()
    output_path = tmpdir.join("logistics.html")
    report.dashboard.render(str(output_path))
    
    with open(str(output_path), 'r') as f:
        html = f.read()
        
    assert "Logistics & Operations" in html
    assert "Shipment #1234" in html
    assert "Goods Flow" in html # Section title
    assert "sankey-beta" in html # Diagram content

def test_generate_report_wrapper(tmpdir):
    # Test the backward compatibility wrapper with new types
    output_dir = str(tmpdir)
    
    # General (Default)
    path = generate_report(output_dir)
    assert os.path.exists(path)
    assert "general_report.html" in path
    
    # Finance
    path = generate_report(output_dir, "finance")
    assert os.path.exists(path)
    assert "finance_report.html" in path
    
    # Marketing
    path = generate_report(output_dir, "marketing")
    assert os.path.exists(path)
    assert "marketing_report.html" in path

    # Logistics
    path = generate_report(output_dir, "logistics")
    assert os.path.exists(path)
    assert "logistics_report.html" in path
