from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json
import logging
import sys

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.logging_monitoring.logger_config import get_logger, setup_logging




















#!/usr/bin/env python3
"""
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class QualityGateEnforcer:
    """


    #!/usr/bin/env python3
    """

Quality Gate Enforcement for Codomyrmex Documentation.

Enforces minimum quality standards for documentation in CI/CD pipelines.
"""


try:
    setup_logging()


logger = get_logger(__name__)

Enforces documentation quality gates."""
    
    def __init__(self, repo_root: Path, output_dir: Path):
        """Initialize enforcer."""
        self.repo_root = repo_root.resolve()
        self.output_dir = output_dir
        
    def load_results(self) -> Dict:
        """Load all validation results."""
        results = {}
        
        # Load link validation
        link_file = self.output_dir / 'link_validation_results.json'
        if link_file.exists():
            results['links'] = json.loads(link_file.read_text())
        
        # Load quality report
        quality_file = self.output_dir / 'content_quality_report.json'
        if quality_file.exists():
            results['quality'] = json.loads(quality_file.read_text())
        
        # Load AGENTS validation
        agents_file = self.output_dir / 'agents_structure_validation.json'
        if agents_file.exists():
            results['agents'] = json.loads(agents_file.read_text())
        
        return results
    
    def check_overall_completion(self, min_score: float = 80.0) -> Tuple[bool, str]:
        """Check if overall completion meets minimum."""
        results = self.load_results()
        
        if not results.get('quality'):
            return False, "No quality data available"
        
        avg_score = results['quality'].get('average_score', 0)
        
        if avg_score < min_score:
            return False, f"Average quality score {avg_score:.1f} below minimum {min_score}"
        
        return True, f"Average quality score {avg_score:.1f} meets minimum {min_score}"
    
    def check_broken_links(self, max_broken: int = 0) -> Tuple[bool, str]:
        """Check if broken links are within limit."""
        results = self.load_results()
        
        if not results.get('links'):
            return True, "No link validation data (skipping)"
        
        broken_links = len(results['links'].get('broken_links', []))
        
        if broken_links > max_broken:
            return False, f"Found {broken_links} broken links (max allowed: {max_broken})"
        
        return True, f"Broken links ({broken_links}) within limit ({max_broken})"
    
    def check_placeholder_content(self, max_placeholders: int = 50) -> Tuple[bool, str]:
        """Check if placeholder count is within limit."""
        results = self.load_results()
        
        if not results.get('quality'):
            return False, "No quality data available"
        
        total_placeholders = results['quality'].get('total_placeholders', 0)
        
        if total_placeholders > max_placeholders:
            return False, f"Found {total_placeholders} placeholders (max allowed: {max_placeholders})"
        
        return True, f"Placeholder count ({total_placeholders}) within limit ({max_placeholders})"
    
    def check_agents_validation(self, min_valid_rate: float = 90.0) -> Tuple[bool, str]:
        """Check if AGENTS.md validation rate meets minimum."""
        results = self.load_results()
        
        if not results.get('agents'):
            return True, "No AGENTS.md validation data (skipping)"
        
        total = results['agents'].get('total_files', 1)
        valid = results['agents'].get('valid_files', 0)
        validation_rate = (valid / total * 100) if total > 0 else 0
        
        if validation_rate < min_valid_rate:
            return False, f"AGENTS.md validation rate {validation_rate:.1f}% below minimum {min_valid_rate}%"
        
        return True, f"AGENTS.md validation rate {validation_rate:.1f}% meets minimum {min_valid_rate}%"
    
    def enforce_gates(self, 
                     min_quality_score: float = 80.0,
                     max_broken_links: int = 0,
                     max_placeholders: int = 50,
                     min_agents_valid_rate: float = 90.0,
                     fail_on_any: bool = True) -> bool:
        """Enforce all quality gates."""
        
        checks = [
            ("Overall Quality Score", self.check_overall_completion(min_quality_score)),
            ("Broken Links", self.check_broken_links(max_broken_links)),
            ("Placeholder Content", self.check_placeholder_content(max_placeholders)),
            ("AGENTS.md Validation", self.check_agents_validation(min_agents_valid_rate))
        ]
        
        print("\n" + "="*80)
        print("DOCUMENTATION QUALITY GATE CHECKS")
        print("="*80)
        
        passed = 0
        failed = 0
        warnings = 0
        
        for check_name, (success, message) in checks:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"\n{check_name}:")
            print(f"  {status}: {message}")
            
            if success:
                passed += 1
            else:
                # Some checks are warnings only
                if check_name in ["Broken Links"] and not fail_on_any:
                    warnings += 1
                else:
                    failed += 1
        
        print("\n" + "="*80)
        print(f"Summary: {passed} passed, {failed} failed, {warnings} warnings")
        print("="*80)
        
        if failed > 0:
            print("\n❌ Quality gates FAILED")
            return False
        
        if warnings > 0:
            print("\n⚠️  Quality gates PASSED with warnings")
        else:
            print("\n✅ All quality gates PASSED")
        
        return True


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description="Enforce documentation quality gates")
    parser.add_argument('--repo-root', type=Path, default=Path.cwd(),
                       help='Repository root directory')
    parser.add_argument('--output', type=Path, default=Path('output'),
                       help='Output directory with validation results')
    parser.add_argument('--min-quality-score', type=float, default=80.0,
                       help='Minimum average quality score')
    parser.add_argument('--max-broken-links', type=int, default=0,
                       help='Maximum number of broken links allowed')
    parser.add_argument('--max-placeholders', type=int, default=50,
                       help='Maximum number of placeholders allowed')
    parser.add_argument('--min-agents-valid-rate', type=float, default=90.0,
                       help='Minimum AGENTS.md validation rate percentage')
    parser.add_argument('--fail-on-any', action='store_true', default=True,
                       help='Fail if any check fails (vs warnings)')
    parser.add_argument('--allow-warnings', action='store_true',
                       help='Allow warnings without failing')
    
    args = parser.parse_args()
    
    # Create enforcer
    enforcer = QualityGateEnforcer(args.repo_root, args.output)
    
    # Run enforcement
    success = enforcer.enforce_gates(
        min_quality_score=args.min_quality_score,
        max_broken_links=args.max_broken_links,
        max_placeholders=args.max_placeholders,
        min_agents_valid_rate=args.min_agents_valid_rate,
        fail_on_any=not args.allow_warnings
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
