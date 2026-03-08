import json

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

FALSE_POSITIVE_FILE_PATTERNS = [
    "scripts/security/audit_secrets.py",
]

FALSE_POSITIVE_KINDS = {"hardcoded_secret_name", "hardcoded_secret_value"}

with open("/Users/mini/Documents/GitHub/codomyrmex/.desloppify/state-python.json") as f:
    state = json.load(f)

findings = state.get("findings", {})

candidates = []
for fid, finding in findings.items():
    if finding.get("status") != "open":
        continue
    detector = finding.get("detector", "")
    if "security" not in detector.lower():
        continue
    detail = finding.get("detail", {})
    kind = detail.get("kind", "")
    if kind not in FALSE_POSITIVE_KINDS:
        continue
    file_path = finding.get("file", "")
    summary = finding.get("summary", "")
    content = detail.get("content", "")

    # Check: hardcoded_secret_value in audit_secrets.py (regex patterns)
    if kind == "hardcoded_secret_value":
        for fp in FALSE_POSITIVE_FILE_PATTERNS:
            if fp in file_path:
                candidates.append((fid, finding, "hardcoded_secret_value in audit script"))
                break
        continue

    # Check: hardcoded_secret_name with false-positive variable names
    matched_var = None
    for var in FALSE_POSITIVE_VAR_NAMES:
        # Check summary (e.g. "Hardcoded secret in variable 'api_key_config_key'")
        if f"'{var}'" in summary or f'"{var}"' in summary:
            matched_var = var
            break
        # Also check finding ID
        if var in fid:
            matched_var = var
            break
    if matched_var:
        candidates.append((fid, finding, f"hardcoded_secret_name: var={matched_var}"))

print(f"Open security false positives found: {len(candidates)}")
print()
for fid, finding, reason in candidates:
    print(f"  [{reason}]")
    print(f"  {fid}")
    print(f'  File: {finding.get("file")}:{finding.get("detail", {}).get("line")}')
    print(f'  Summary: {finding.get("summary")}')
    print()
