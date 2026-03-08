"""
Batch mark security false positives as wontfix in .desloppify/state-python.json.

False positive categories:
1. hardcoded_secret_name where variable is a config key name, metric name, or enum label
2. hardcoded_secret_value in scripts/security/audit_secrets.py (regex patterns)
"""

import json
import os
import tempfile
from datetime import UTC, datetime, timezone

STATE_FILE = "/Users/mini/Documents/GitHub/codomyrmex/.desloppify/state-python.json"

WONTFIX_NOTE = (
    "False positive: config key names, metric names, and regex patterns "
    "in audit scripts are not actual secrets"
)

# Variable names from the user's false-positive list
FALSE_POSITIVE_VAR_NAMES = {
    "api_key_config_key",
    "max_tokens_config_key",
    "token_uri",
    "credentials",
    "BEARER_TOKEN",
    "secret",
    "password",
    "TOKEN_EFFICIENCY",
}

# Files whose hardcoded_secret_value findings are regex patterns, not secrets
FALSE_POSITIVE_VALUE_FILES = {
    "scripts/security/audit_secrets.py",
}

FALSE_POSITIVE_KINDS = {"hardcoded_secret_name", "hardcoded_secret_value"}


def is_false_positive(fid: str, finding: dict) -> bool:
    """Return True if this finding is a confirmed false positive."""
    if finding.get("status") != "open":
        return False
    detector = finding.get("detector", "")
    if "security" not in detector.lower():
        return False
    detail = finding.get("detail", {})
    kind = detail.get("kind", "")
    if kind not in FALSE_POSITIVE_KINDS:
        return False

    file_path = finding.get("file", "")
    summary = finding.get("summary", "")

    # Category 2: regex patterns in audit script
    if kind == "hardcoded_secret_value":
        return file_path in FALSE_POSITIVE_VALUE_FILES

    # Category 1: variable name is a config key / metric name / enum label
    for var in FALSE_POSITIVE_VAR_NAMES:
        if f"'{var}'" in summary or f'"{var}"' in summary:
            return True

    # Also catch findings whose summary contains the var without quotes
    # (e.g. enum labels flagged because var name contains "secret")
    # — but only if the finding ID encodes the file we already inspected
    # We handle this by relying on the broader "secret" match that we verified
    # maps to enum/label patterns only.
    return False


def main():
    print(f"Loading {STATE_FILE} ...")
    with open(STATE_FILE) as f:
        state = json.load(f)

    findings = state.get("findings", {})
    print(f"Total findings in state: {len(findings)}")

    now_iso = datetime.now(UTC).isoformat()
    marked = []
    skipped_not_open = 0
    skipped_not_security = 0

    for fid, finding in findings.items():
        if is_false_positive(fid, finding):
            finding["status"] = "wontfix"
            finding["note"] = WONTFIX_NOTE
            finding["resolved_at"] = now_iso
            marked.append(fid)
        # Count what we skipped for auditability
        elif finding.get("status") != "open":
            skipped_not_open += 1

    print(f"\nMarked {len(marked)} findings as wontfix:")
    for fid in sorted(marked):
        print(f"  {fid}")

    print("\nWriting updated state file atomically ...")
    # Write to temp file in same directory, then rename (atomic on same filesystem)
    state_dir = os.path.dirname(STATE_FILE)
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=state_dir,
        suffix=".tmp",
        delete=False
    ) as tmp:
        json.dump(state, tmp)
        tmp_path = tmp.name

    os.replace(tmp_path, STATE_FILE)
    print(f"Done. Wrote {STATE_FILE}")
    print(f"\nSummary: {len(marked)} findings marked wontfix.")
    return len(marked)


if __name__ == "__main__":
    main()
