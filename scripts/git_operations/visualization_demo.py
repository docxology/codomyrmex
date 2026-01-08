#!/usr/bin/env python3
"""
Git Visualization Demo Orchestrator

Thin orchestrator script that triggers the git visualization demonstrations
defined in codomyrmex.git_operations.demo.
"""

import sys
import argparse
from pathlib import Path

# Setup path to include src
# scripts/git_operations/visualization_demo.py -> git_operations -> scripts -> codomyrmex (root)
root_dir = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root_dir / "src"))

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module functions
try:
    from codomyrmex.git_operations.demo import GitVisualizationDemo
except ImportError:
    # Fallback shouldn't be needed usually but kept for safety
    from codomyrmex.git_operations.demo import GitVisualizationDemo

logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="Git Visualization Demo",
        epilog="""
Examples:
  %(prog)s
  %(prog)s /path/to/my/repo
  %(prog)s --skip-sample --output-dir ./my_demo
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "repository_path", 
        nargs='?', 
        help="Path to Git repository to analyze"
    )
    parser.add_argument(
        "--output-dir", 
        help="Output directory for demo files"
    )
    parser.add_argument(
        "--skip-sample", 
        action="store_true", 
        help="Skip sample data demonstrations"
    )
    parser.add_argument(
        "--skip-workflows", 
        action="store_true", 
        help="Skip workflow diagram demonstrations"
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting Git Visualization Demo...")
        
        demo = GitVisualizationDemo(output_dir=args.output_dir)
        success = demo.run_all_demos(
            repository_path=args.repository_path,
            skip_sample=args.skip_sample,
            skip_workflows=args.skip_workflows
        )
        
        if success:
            logger.info("Demo completed successfully!")
            return 0
        else:
            logger.error("Demo failed or completed with errors.")
            return 1
            
    except Exception as e:
        logger.exception("Unexpected error during demo execution")
        return 1


if __name__ == "__main__":
    sys.exit(main())
