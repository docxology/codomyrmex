#!/usr/bin/env python3
"""
Multi-Module Workflow: Analysis Pipeline

This workflow demonstrates integration of multiple modules:
- Static Analysis: Code quality checking
- Security Audit: Vulnerability scanning
- Data Visualization: Results visualization
- Logging Monitoring: Centralized logging
- Events: Event-driven communication

This example shows a real-world scenario: analyzing a codebase for quality,
security issues, and generating visual reports.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.static_analysis import analyze_file
from codomyrmex.security import scan_vulnerabilities
from codomyrmex.data_visualization import create_bar_chart
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.events import get_event_bus, EventType, publish_event, Event

# Import common utilities directly
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, ensure_output_dir

def main():
    """Run the multi-module analysis workflow."""
    config = load_config(Path(__file__).parent / "config_workflow_analysis.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()
    
    try:
        print_section("Multi-Module Analysis Workflow")
        
        # Setup logging
        setup_logging()
        logger = get_logger('workflow.analysis')
        
        # Initialize event bus for module communication
        event_bus = get_event_bus()
        
        # Publish workflow start event
        start_event = Event(
            event_type=EventType.ANALYSIS_START,
            source='workflow',
            data={
                'workflow_name': 'analysis_pipeline',
                'target': config.get('analysis', {}).get('target_path', 'src/')
            }
        )
        publish_event(start_event)
        
        logger.info("Starting analysis workflow")
        
        # Step 1: Static Analysis
        print("\n[1/4] Running static analysis...")
        target_path = config.get('analysis', {}).get('target_path', 'src/')
        
        # For demo, analyze a sample file
        sample_file = Path(target_path) / "codomyrmex" / "__init__.py"
        if sample_file.exists():
            analysis_results = analyze_file(str(sample_file))
            logger.info(f"Static analysis completed: {len(analysis_results)} issues found")
            print(f"✓ Found {len(analysis_results)} static analysis issues")
        else:
            analysis_results = []
            print("Note: Sample file not found, using empty results")
        
        # Step 2: Security Audit
        print("\n[2/4] Running security audit...")
        try:
            security_results = scan_vulnerabilities(target_path)
            logger.info(f"Security audit completed: {len(security_results)} vulnerabilities found")
            print(f"✓ Found {len(security_results)} security issues")
        except Exception as e:
            logger.warning(f"Security audit skipped: {e}")
            security_results = []
            print(f"Note: Security audit skipped")
        
        # Step 3: Aggregate Results
        print("\n[3/4] Aggregating results...")
        aggregated_data = {
            'static_analysis_issues': len(analysis_results),
            'security_vulnerabilities': len(security_results),
            'total_issues': len(analysis_results) + len(security_results)
        }
        
        print_results(aggregated_data, "Analysis Summary")
        
        # Step 4: Generate Visualizations
        print("\n[4/4] Generating visualizations...")
        output_dir = Path("output/workflow_analysis")
        ensure_output_dir(output_dir)
        
        # Create summary chart
        chart_data = {
            'Static Analysis': len(analysis_results),
            'Security Issues': len(security_results)
        }
        
        if any(chart_data.values()):
            categories = list(chart_data.keys())
            values = list(chart_data.values())
            chart_path = create_bar_chart(
                categories=categories,
                values=values,
                title="Analysis Results Summary",
                output_path=str(output_dir / "analysis_summary.png")
            )
            logger.info(f"Visualization saved to: {chart_path}")
            print(f"✓ Visualization saved to: {chart_path}")
        else:
            chart_path = None
            print("Note: No issues found, skipping visualization")
        
        # Publish workflow complete event
        complete_event = Event(
            event_type=EventType.ANALYSIS_COMPLETE,
            source='workflow',
            data={
                'workflow_name': 'analysis_pipeline',
                'results': aggregated_data
            }
        )
        publish_event(complete_event)
        
        # Final results
        results = {
            'status': 'success',
            'workflow': 'analysis_pipeline',
            'modules_used': ['static_analysis', 'security_audit', 'data_visualization', 'logging_monitoring', 'events'],
            'summary': aggregated_data,
            'visualization': str(chart_path) if chart_path else None,
            'target_path': target_path
        }
        
        print_section("Workflow Complete")
        print_results(results, "Final Results")
        
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete("Analysis workflow completed successfully")
        
    except Exception as e:
        runner.error("Workflow failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

