import os

from codomyrmex.data_visualization import generate_report
from codomyrmex.data_visualization.reports.finance import FinanceReport
from codomyrmex.data_visualization.reports.logistics import LogisticsReport
from codomyrmex.data_visualization.reports.marketing import MarketingReport


def test_finance_report_generation(tmp_path):
    """Test functionality: finance report generation."""
    report = FinanceReport()
    report.generate()
    output_path = tmp_path / "finance.html"
    report.dashboard.render(str(output_path))

    html = output_path.read_text()
    assert "Financial Overview" in html
    assert "Net Profit" in html
    assert "CDMX Stock" in html

def test_marketing_report_generation(tmp_path):
    """Test functionality: marketing report generation."""
    report = MarketingReport()
    report.generate()
    output_path = tmp_path / "marketing.html"
    report.dashboard.render(str(output_path))

    html = output_path.read_text()
    assert "Marketing Analysis" in html
    assert "Brand Awareness" in html
    assert "User Acquisition" in html

def test_logistics_report_generation(tmp_path):
    """Test functionality: logistics report generation."""
    report = LogisticsReport()
    report.generate()
    output_path = tmp_path / "logistics.html"
    report.dashboard.render(str(output_path))

    html = output_path.read_text()
    assert "Logistics &amp; Operations" in html or "Logistics & Operations" in html
    assert "Shipment #1234" in html
    assert "Goods Flow" in html  # Section title
    assert "sankey-beta" in html  # Diagram content

def test_generate_report_wrapper(tmp_path):
    """Test functionality: generate report wrapper."""
    output_dir = str(tmp_path)

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
