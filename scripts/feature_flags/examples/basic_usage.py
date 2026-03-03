#!/usr/bin/env python3
"""Feature Flags Module - Comprehensive Usage Script.

Demonstrates feature flag management with full configurability,
unified logging, and output saving using the improved FeatureManager.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --dry-run                # Preview without executing
    python basic_usage.py --verbose                # Verbose output
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Setup project root and src path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "process" / "script_base.py"

spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class FeatureFlagsScript(ScriptBase):
    """Comprehensive feature flags module demonstration."""

    def __init__(self):
        super().__init__(
            name="feature_flags_usage",
            description="Demonstrate and test improved feature flag management",
            version="1.1.0",
        )

    def add_arguments(self, parser):
        """Add feature flags-specific arguments."""
        group = parser.add_argument_group("Feature Flags Options")
        group.add_argument(
            "--test-users", type=int, default=50,
            help="Number of test users for rollout simulation (default: 50)"
        )
        group.add_argument(
            "--rollout-percentage", type=float, default=25.0,
            help="Percentage for rollout tests (default: 25.0)"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute feature flags demonstrations."""
        results = {
            "demo_steps": [],
            "status": "success",
        }

        # Import feature_flags module
        from codomyrmex.feature_flags import FeatureManager
        from codomyrmex.feature_flags.evaluation import TargetingRule

        manager = FeatureManager()

        # Step 1: Basic Boolean Flags
        self.log_info("Step 1: Basic Boolean Flags")
        manager.create_flag("dark_mode", enabled=True)
        manager.create_flag("new_sidebar", enabled=False)
        
        dark_mode_on = manager.is_enabled("dark_mode")
        sidebar_on = manager.is_enabled("new_sidebar")
        
        self.log_success(f"  dark_mode: {'ON' if dark_mode_on else 'OFF'}")
        self.log_success(f"  new_sidebar: {'ON' if sidebar_on else 'OFF'}")
        
        results["demo_steps"].append({"step": 1, "dark_mode": dark_mode_on, "new_sidebar": sidebar_on})

        # Step 2: Percentage Rollout
        self.log_info(f"Step 2: Percentage Rollout ({args.rollout_percentage}%)")
        manager.create_flag("ai_search", percentage=args.rollout_percentage)
        
        enabled_count = 0
        for i in range(args.test_users):
            if manager.is_enabled("ai_search", user_id=f"user_{i}"):
                enabled_count += 1
        
        actual_pct = (enabled_count / args.test_users) * 100
        self.log_success(f"  Rollout for {args.test_users} users: {enabled_count} enabled ({actual_pct:.1f}%)")
        results["demo_steps"].append({"step": 2, "enabled_count": enabled_count, "actual_percentage": actual_pct})

        # Step 3: Multivariate Flags
        self.log_info("Step 3: Multivariate Flags")
        manager.create_flag("theme_color", metadata={"value": "cobalt"})
        theme = manager.get_value("theme_color", default="gray")
        self.log_success(f"  theme_color value: {theme}")
        results["demo_steps"].append({"step": 3, "theme_color": theme})

        # Step 4: Targeting Rules
        self.log_info("Step 4: Targeting Rules")
        premium_rule = TargetingRule(attribute="tier", operator="eq", value="premium")
        manager.create_flag("early_access", targeting_rules=[premium_rule])
        
        premium_user = manager.is_enabled("early_access", tier="premium")
        free_user = manager.is_enabled("early_access", tier="free")
        
        self.log_success(f"  Premium user access: {'YES' if premium_user else 'NO'}")
        self.log_success(f"  Free user access: {'YES' if free_user else 'NO'}")
        results["demo_steps"].append({"step": 4, "premium_user": premium_user, "free_user": free_user})

        # Step 5: Overrides
        self.log_info("Step 5: Overrides")
        manager.set_override("new_sidebar", True)
        sidebar_override = manager.is_enabled("new_sidebar")
        self.log_success(f"  new_sidebar after override: {'ON' if sidebar_override else 'OFF'}")
        results["demo_steps"].append({"step": 5, "sidebar_override": sidebar_override})

        return results



    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "feature_flags" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/feature_flags/config.yaml")

if __name__ == "__main__":
    script = FeatureFlagsScript()
    sys.exit(script.execute())
