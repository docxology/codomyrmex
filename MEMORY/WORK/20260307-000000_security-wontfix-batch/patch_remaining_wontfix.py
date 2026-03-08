"""
Patch the remaining 13 confirmed false-positive security findings by exact ID.
These were verified by direct file inspection to be enum labels, category names,
and docstring placeholder values — not actual secrets.
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

# Confirmed false positives by direct file inspection:
# - scrape/firecrawl: api_key="fc-your-key" is a docstring placeholder
# - security/cognitive/awareness_training.py: PASSWORD_SECURITY is a category enum
# - security/digital/secrets_detector.py: secret_type is a field name
# - security/digital/security_analyzer.py: HARD_CODED_SECRET is a vulnerability type enum
# - security/physical/access_control.py: TOP_SECRET is a classification enum
# - security/scanning/__init__.py: HARDCODED_SECRET is a vulnerability type enum
# - security/secrets/__init__.py: GITHUB_TOKEN/PRIVATE_KEY/PASSWORD are secret type enums ("github_token" etc.)
# - security/secrets/models.py: same enum pattern

REMAINING_IDS = [
    "security::src/codomyrmex/scrape/firecrawl/adapter.py::security::hardcoded_secret_name::src/codomyrmex/scrape/firecrawl/adapter.py::40",
    "security::src/codomyrmex/scrape/firecrawl/client.py::security::hardcoded_secret_name::src/codomyrmex/scrape/firecrawl/client.py::31",
    "security::src/codomyrmex/security/cognitive/awareness_training.py::security::hardcoded_secret_name::src/codomyrmex/security/cognitive/awareness_training.py::17",
    "security::src/codomyrmex/security/digital/secrets_detector.py::security::hardcoded_secret_name::src/codomyrmex/security/digital/secrets_detector.py::170",
    "security::src/codomyrmex/security/digital/security_analyzer.py::security::hardcoded_secret_name::src/codomyrmex/security/digital/security_analyzer.py::31",
    "security::src/codomyrmex/security/physical/access_control.py::security::hardcoded_secret_name::src/codomyrmex/security/physical/access_control.py::30",
    "security::src/codomyrmex/security/scanning/__init__.py::security::hardcoded_secret_name::src/codomyrmex/security/scanning/__init__.py::37",
    "security::src/codomyrmex/security/secrets/__init__.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/__init__.py::27",
    "security::src/codomyrmex/security/secrets/__init__.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/__init__.py::28",
    "security::src/codomyrmex/security/secrets/__init__.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/__init__.py::29",
    "security::src/codomyrmex/security/secrets/models.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/models.py::12",
    "security::src/codomyrmex/security/secrets/models.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/models.py::13",
    "security::src/codomyrmex/security/secrets/models.py::security::hardcoded_secret_name::src/codomyrmex/security/secrets/models.py::14",
]


def main():
    print(f"Loading {STATE_FILE} ...")
    with open(STATE_FILE) as f:
        state = json.load(f)

    findings = state.get("findings", {})
    now_iso = datetime.now(UTC).isoformat()
    marked = []
    not_found = []

    for fid in REMAINING_IDS:
        if fid in findings:
            finding = findings[fid]
            if finding.get("status") == "open":
                finding["status"] = "wontfix"
                finding["note"] = WONTFIX_NOTE
                finding["resolved_at"] = now_iso
                marked.append((fid, finding.get("summary", "")))
            else:
                print(f"  SKIP (status={finding['status']}): {fid}")
        else:
            not_found.append(fid)

    print(f"\nMarked {len(marked)} additional findings as wontfix:")
    for fid, summary in marked:
        print(f"  [{summary}] {fid}")

    if not_found:
        print(f"\nNOT FOUND ({len(not_found)}):")
        for fid in not_found:
            print(f"  {fid}")

    print("\nWriting updated state file atomically ...")
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
    print(f"\nTotal additional findings marked wontfix: {len(marked)}")
    return len(marked)


if __name__ == "__main__":
    main()
