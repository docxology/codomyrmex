import json

with open("/Users/mini/Documents/GitHub/codomyrmex/.desloppify/state-python.json") as f:
    state = json.load(f)

print("Top-level keys:", list(state.keys())[:10])
findings = state.get("findings", {})
print("Total findings:", len(findings))

sec_keys = [k for k in findings if "security" in k.lower() and "hardcoded" in k.lower()]
print("Security hardcoded count:", len(sec_keys))

if sec_keys:
    k = sec_keys[0]
    print("Sample key:", k)
    print("Sample value:", json.dumps(findings[k], indent=2))
