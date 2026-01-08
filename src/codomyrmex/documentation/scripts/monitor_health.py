from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import json
import logging
import sys


from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging






























#!/usr/bin/env python3
"""
"""Main entry point and utility functions

This module provides monitor_health functionality including:
- 8 functions: main, __init__, load_history...
- 1 classes: DocumentationHealthMonitor

Usage:
    # Example usage here
"""
Documentation Health Monitoring for Codomyrmex.

Continuous monitoring of documentation quality with alerting and reporting.
"""


try:
    setup_logging()
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class DocumentationHealthMonitor:
    """Monitors documentation health over time."""
    
    def __init__(self, repo_root: Path):
        """Initialize monitor."""
        self.repo_root = repo_root.resolve()
        self.output_dir = repo_root / 'output'
        self.history_file = self.output_dir / 'doc_health_history.json'
        
    def load_history(self) -> List[Dict]:
        """Load historical health data."""
        if self.history_file.exists():
            try:
                return json.loads(self.history_file.read_text())
            except:
                return []
        return []
    
    def save_history(self, history: List[Dict]) -> None:
        """Save historical health data."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_file.write_text(json.dumps(history, indent=2))
    
    def collect_current_metrics(self) -> Dict:
        """Collect current documentation metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'quality_score': 0.0,
            'broken_links': 0,
            'placeholders': 0,
            'agents_valid_rate': 0.0
        }
        
        # Load latest validation results
        quality_file = self.output_dir / 'content_quality_report.json'
        if quality_file.exists():
            try:
                data = json.loads(quality_file.read_text())
                metrics['quality_score'] = data.get('average_score', 0)
                metrics['placeholders'] = data.get('total_placeholders', 0)
            except:
                pass
        
        link_file = self.output_dir / 'link_validation_results.json'
        if link_file.exists():
            try:
                data = json.loads(link_file.read_text())
                metrics['broken_links'] = len(data.get('broken_links', []))
            except:
                pass
        
        agents_file = self.output_dir / 'agents_structure_validation.json'
        if agents_file.exists():
            try:
                data = json.loads(agents_file.read_text())
                total = data.get('total_files', 1)
                valid = data.get('valid_files', 0)
                metrics['agents_valid_rate'] = (valid / total * 100) if total > 0 else 0
            except:
                pass
        
        return metrics
    
    def detect_degradation(self, history: List[Dict]) -> List[str]:
        """Detect quality degradation."""
        alerts = []
        
        if len(history) < 2:
            return alerts
        
        current = history[-1]
        previous = history[-2]
        
        # Check quality score
        if current['quality_score'] < previous['quality_score'] - 5:
            alerts.append(f"Quality score degraded: {previous['quality_score']:.1f} → {current['quality_score']:.1f}")
        
        # Check broken links
        if current['broken_links'] > previous['broken_links']:
            alerts.append(f"Broken links increased: {previous['broken_links']} → {current['broken_links']}")
        
        # Check placeholders
        if current['placeholders'] > previous['placeholders']:
            alerts.append(f"Placeholder count increased: {previous['placeholders']} → {current['placeholders']}")
        
        return alerts
    
    def monitor(self) -> Dict:
        """Run health monitoring."""
        logger.info("Running documentation health monitoring...")
        
        # Collect current metrics
        current_metrics = self.collect_current_metrics()
        
        # Load history
        history = self.load_history()
        
        # Add current metrics
        history.append(current_metrics)
        
        # Keep last 30 entries
        history = history[-30:]
        
        # Save history
        self.save_history(history)
        
        # Detect degradation
        alerts = self.detect_degradation(history)
        
        result = {
            'current_metrics': current_metrics,
            'alerts': alerts,
            'trend': self._calculate_trend(history)
        }
        
        logger.info(f"Monitoring complete. {len(alerts)} alerts generated.")
        
        return result
    
    def _calculate_trend(self, history: List[Dict]) -> str:
        """Calculate overall quality trend."""
        if len(history) < 2:
            return 'stable'
        
        recent = history[-5:] if len(history) >= 5 else history
        scores = [m['quality_score'] for m in recent]
        
        if len(scores) < 2:
            return 'stable'
        
        avg_recent = sum(scores[-3:]) / 3 if len(scores) >= 3 else scores[-1]
        avg_older = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]
        
        if avg_recent > avg_older + 2:
            return 'improving'
        elif avg_recent < avg_older - 2:
            return 'degrading'
        else:
            return 'stable'


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Monitor documentation health")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = DocumentationHealthMonitor(args.repo_root)
    
    # Run monitoring
    result = monitor.monitor()
    
    # Print results
    print("\n" + "="*80)
    print("DOCUMENTATION HEALTH MONITORING")
    print("="*80)
    print(f"Quality Score: {result['current_metrics']['quality_score']:.1f}/100")
    print(f"Broken Links: {result['current_metrics']['broken_links']}")
    print(f"Placeholders: {result['current_metrics']['placeholders']}")
    print(f"AGENTS.md Valid Rate: {result['current_metrics']['agents_valid_rate']:.1f}%")
    print(f"\nTrend: {result['trend'].upper()}")
    
    if result['alerts']:
        print(f"\n⚠️  {len(result['alerts'])} ALERTS:")
        for alert in result['alerts']:
            print(f"  - {alert}")
    else:
        print("\n✅ No alerts")
    
    print("="*80)
    
    sys.exit(0)


if __name__ == '__main__':
    main()


