#!/usr/bin/env python3
"""
Multi-Module Workflow: Monitoring Dashboard

This workflow demonstrates integration of multiple modules:
- Logging Monitoring: Centralized logging infrastructure
- Performance: System and application performance monitoring
- System Discovery: Module health checks and system exploration
- Data Visualization: Performance metrics visualization
- Events: Real-time event streaming and monitoring
- Config Management: Monitoring configuration management

This example shows a real-world scenario: comprehensive system monitoring
and observability dashboard with automated health checks and reporting.
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.performance.performance_monitor import get_system_metrics
from codomyrmex.system_discovery.health_checker import perform_health_check
from codomyrmex.system_discovery.discovery_engine import SystemDiscovery
from codomyrmex.data_visualization.plotter import create_bar_chart
from codomyrmex.events import get_event_bus, EventType, publish_event

from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, ensure_output_dir

def main():
    """Run the monitoring dashboard workflow."""
    config = load_config(Path(__file__).parent / "config_workflow_monitoring.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Multi-Module Monitoring Dashboard")

        # Setup logging
        setup_logging()
        logger = get_logger('workflow.monitoring')

        # Initialize event bus
        event_bus = get_event_bus()

        # Get monitoring configuration
        monitoring_config = config.get('monitoring', {})

        results = {
            'metrics_collected': 0,
            'health_checks_performed': 0,
            'modules_discovered': 0,
            'alerts_generated': 0,
            'visualizations_created': 0
        }

        # Publish monitoring start event
        publish_event(EventType.SYSTEM_STARTUP, source='workflow', data={
            'workflow_name': 'monitoring_dashboard',
            'monitoring_intervals': monitoring_config.get('intervals', {})
        })

        # Create output directory
        output_dir = Path("output/monitoring_dashboard")
        ensure_output_dir(output_dir)

        # Stage 1: System Metrics Collection
        print("\n[1/5] Collecting System Metrics...")
        metrics_collection = []

        try:
            # Collect current system metrics
            metrics = get_system_metrics()

            if metrics:
                metrics_collection.append(metrics)
                results['metrics_collected'] = 1

                cpu_percent = metrics.get('cpu_percent', 0)
                memory_percent = metrics.get('memory_percent', 0)
                disk_usage = metrics.get('disk_usage_percent', 0)

                print(f"✓ System Status: CPU {cpu_percent:.1f}%, "
                      f"Memory {memory_percent:.1f}%, Disk {disk_usage:.1f}%")

                # Check for alerts
                alerts = []
                if cpu_percent > monitoring_config.get('alert_thresholds', {}).get('cpu_percent', 90):
                    alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
                if memory_percent > monitoring_config.get('alert_thresholds', {}).get('memory_percent', 90):
                    alerts.append(f"High memory usage: {memory_percent:.1f}%")

                if alerts:
                    results['alerts_generated'] = len(alerts)
                    results['active_alerts'] = alerts
                    logger.warning(f"System alerts: {', '.join(alerts)}")
                    print(f"⚠️  Alerts: {', '.join(alerts)}")
                else:
                    print("✓ No system alerts detected")

            else:
                print("✗ Failed to collect system metrics")

        except Exception as e:
            print(f"✗ Error collecting system metrics: {e}")
            logger.error(f"Metrics collection error: {e}")

        # Stage 2: Module Health Checks
        print("\n[2/5] Performing Module Health Checks...")
        health_checks = []

        try:
            # Discover available modules
            discovery = SystemDiscovery()
            modules = discovery.discover_modules()

            if modules:
                results['modules_discovered'] = len(modules)
                print(f"✓ Discovered {len(modules)} modules")

                # Perform health checks on modules
                for module_name in modules[:5]:  # Limit to first 5 for demo
                    try:
                        health_status = perform_health_check(module_name)

                        if health_status:
                            health_checks.append({
                                'module': module_name,
                                'status': health_status.get('status', 'unknown'),
                                'response_time': health_status.get('response_time', 0),
                                'last_check': health_status.get('timestamp')
                            })

                            results['health_checks_performed'] += 1

                            status = health_status.get('status', 'unknown')
                            response_time = health_status.get('response_time', 0)
                            print(f"✓ {module_name}: {status} ({response_time:.3f}s)")

                    except Exception as e:
                        print(f"✗ Health check failed for {module_name}: {e}")
                        logger.error(f"Health check error for {module_name}: {e}")

            else:
                print("Note: No modules discovered")

        except Exception as e:
            print(f"✗ Error in module discovery: {e}")
            logger.error(f"Module discovery error: {e}")

        # Stage 3: Generate Visualizations
        print("\n[3/5] Generating Monitoring Visualizations...")

        try:
            if health_checks:
                # Create health status chart
                health_data = {}
                for check in health_checks:
                    status = check.get('status', 'unknown')
                    if status not in health_data:
                        health_data[status] = 0
                    health_data[status] += 1

                if health_data:
                    health_chart_path = create_bar_chart(
                        health_data,
                        title="Module Health Status",
                        output_file=str(output_dir / "health_status.png")
                    )

                    results['visualizations_created'] += 1
                    print(f"✓ Health visualization saved: {health_chart_path}")

            if metrics_collection:
                # Create system metrics chart
                metrics = metrics_collection[0]
                metrics_data = {
                    'CPU Usage': metrics.get('cpu_percent', 0),
                    'Memory Usage': metrics.get('memory_percent', 0),
                    'Disk Usage': metrics.get('disk_usage_percent', 0)
                }

                metrics_chart_path = create_bar_chart(
                    metrics_data,
                    title="System Resource Usage",
                    output_file=str(output_dir / "system_metrics.png")
                )

                results['visualizations_created'] += 1
                print(f"✓ Metrics visualization saved: {metrics_chart_path}")

        except Exception as e:
            print(f"✗ Error generating visualizations: {e}")
            logger.error(f"Visualization error: {e}")

        # Stage 4: Event Monitoring
        print("\n[4/5] Monitoring System Events...")

        try:
            # Simulate monitoring events for a short period
            events_monitored = 0
            monitoring_duration = monitoring_config.get('event_monitoring_duration', 2)

            print(f"Monitoring events for {monitoring_duration} seconds...")

            # In a real implementation, this would subscribe to events
            # and monitor them in real-time
            time.sleep(monitoring_duration)

            # Simulate some monitoring events
            publish_event(EventType.SYSTEM_STARTUP, source='monitoring', data={
                'dashboard_active': True,
                'monitored_modules': len(health_checks)
            })

            events_monitored += 1
            print(f"✓ Monitored {events_monitored} system events")

        except Exception as e:
            print(f"✗ Error monitoring events: {e}")
            logger.error(f"Event monitoring error: {e}")

        # Stage 5: Generate Monitoring Report
        print("\n[5/5] Generating Monitoring Report...")

        monitoring_report = {
            'timestamp': time.time(),
            'system_status': 'healthy' if results['alerts_generated'] == 0 else 'warning',
            'modules_status': f"{results['health_checks_performed']}/{results['modules_discovered']} healthy",
            'active_alerts': results.get('active_alerts', []),
            'recommendations': []
        }

        # Generate recommendations based on findings
        if results['alerts_generated'] > 0:
            monitoring_report['recommendations'].append("Address high resource usage alerts")
        if results['health_checks_performed'] < results['modules_discovered']:
            monitoring_report['recommendations'].append("Review failed module health checks")

        # Save monitoring report
        report_path = output_dir / "monitoring_report.json"
        import json
        with open(report_path, 'w') as f:
            json.dump(monitoring_report, f, indent=2, default=str)

        print(f"✓ Monitoring report saved: {report_path}")

        # Publish monitoring complete event
        publish_event(EventType.SYSTEM_STARTUP, source='workflow', data={
            'workflow_name': 'monitoring_dashboard',
            'status': monitoring_report['system_status'],
            'report_path': str(report_path)
        })

        # Final summary
        results['summary'] = {
            'monitoring_completed': True,
            'system_health': monitoring_report['system_status'],
            'total_checks': (results['metrics_collected'] +
                           results['health_checks_performed'] +
                           results['visualizations_created']),
            'report_generated': True
        }

        print_section("Monitoring Dashboard Complete")
        print_results(results['summary'], "System Monitoring Summary")

        runner.validate_results(results)
        runner.save_results(results)

        runner.complete("Monitoring dashboard workflow completed successfully")

    except Exception as e:
        runner.error("Workflow failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()

