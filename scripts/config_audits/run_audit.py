#!/usr/bin/env python3
"""
Orchestrator script for configuration audits.
Demonstrates how to use the codomyrmex.config_audits module.
"""
import json
import os
from pathlib import Path

from codomyrmex.config_audits import ConfigAuditor


def create_sample_configs(temp_dir: Path):
    """Create some sample configuration files with intentional issues."""
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Valid config
    with open(temp_dir / "valid_config.json", "w") as f:
        json.dump({"app_name": "MyApp", "version": "1.0.0"}, f)
    os.chmod(temp_dir / "valid_config.json", 0o600)

    # 2. Config with secret
    with open(temp_dir / "secret_config.json", "w") as f:
        f.write('{"db_password": "super_secret_password"}')
    os.chmod(temp_dir / "secret_config.json", 0o600)

    # 3. Production config with debug enabled
    with open(temp_dir / "prod_config.json", "w") as f:
        f.write('{"debug": true, "env": "production"}')
    os.chmod(temp_dir / "prod_config.json", 0o600)

    # 4. Invalid JSON
    with open(temp_dir / "invalid_config.json", "w") as f:
        f.write('{"missing_quote: value}')
    os.chmod(temp_dir / "invalid_config.json", 0o600)

    # 5. Overly permissive file
    permissive_file = temp_dir / "permissive_config.json"
    with open(permissive_file, "w") as f:
        json.dump({"setting": "value"}, f)
    os.chmod(permissive_file, 0o666)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config_audits" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/config_audits/config.yaml")

    print("Starting Configuration Audit Orchestrator...")

    temp_dir = Path("temp_audit_samples")
    create_sample_configs(temp_dir)

    try:
        auditor = ConfigAuditor()
        print(f"Auditing directory: {temp_dir}")

        results = auditor.audit_directory(temp_dir)

        report = auditor.generate_report(results)
        print("\nAudit Results Summary:")
        print(report)

        # Check if overall compliant
        all_compliant = all(r.is_compliant for r in results)
        if not all_compliant:
            print("Action Required: Non-compliant configurations detected!")
        else:
            print("Success: All configurations are compliant.")

    finally:
        # Cleanup
        for file in temp_dir.glob("*"):
            file.unlink()
        temp_dir.rmdir()
        print("\nCleanup complete.")


if __name__ == "__main__":
    main()
