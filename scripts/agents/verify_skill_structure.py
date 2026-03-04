
import re
from pathlib import Path
import sys

def verify_skill_md():
    skill_path = Path("~/.claude/skills/Codomyrmex/SKILL.md").expanduser().resolve()

    if not skill_path.exists():
        print(f"❌ SKILL.md not found at {skill_path}")
        sys.exit(1)

    content = skill_path.read_text()
    print(f"📄 Analyzing {skill_path} ({len(content)} bytes)...")

    # Check Frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        print("❌ Missing or malformed YAML frontmatter")
    else:
        print("✅ Frontmatter found")
        if "name: Codomyrmex" in frontmatter_match.group(1):
            print("  - name: Codomyrmex (Found)")
        else:
            print("  - name: Codomyrmex (MISSING)")

    # Check Workflow Routing Table
    print("\n🔍 Checking Workflow Routing...")
    routing_match = re.search(r"## Workflow Routing.*?(?=\n##|$)", content, re.DOTALL)
    if routing_match:
        section = routing_match.group(0)
        # Look for the definition line
        if "| Workflow | Trigger | File |" in section:
            print("✅ Routing table header found")
        else:
            print("❌ Routing table header MISSING or malformed")

        # Check specific entries
        if "/codomyrmexVerify" in section:
             print("  - /codomyrmexVerify (Found)")
        else:
             print("  - /codomyrmexVerify (MISSING)")

        if "/codomyrmexTrust" in section:
             print("  - /codomyrmexTrust (Found)")
        else:
             print("  - /codomyrmexTrust (MISSING)")
    else:
        print("❌ Workflow Routing section MISSING")

    # Check Prompts Table
    print("\n🔍 Checking Prompts...")
    prompts_match = re.search(r"## Prompts.*?(?=\n##|$)", content, re.DOTALL)
    if prompts_match:
        section = prompts_match.group(0)
        if "| Name | Description |" in section:
             print("✅ Prompts table header found")
        else:
             print("❌ Prompts table header MISSING")

        # Check for our new prompts
        if "codomyrmexVerify" in section:
            print("  - codomyrmexVerify (Found)")
        else:
            print("  - codomyrmexVerify (MISSING)")

        if "codomyrmexTrust" in section:
            print("  - codomyrmexTrust (Found)")
        else:
            print("  - codomyrmexTrust (MISSING)")
    else:
        print("❌ Prompts section MISSING")

    # Parsing Check (Basic markdown table regex)
    # PAI likely splits by pipe. Let's see if the lines are well-formed.
    lines = content.split('\n')
    malformed_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('|'):
            # Basic check: starts and ends with pipe (ignoring whitespace)
            if not line.strip().endswith('|'):
                malformed_lines.append((i+1, line))

    if malformed_lines:
        print("\n⚠️ Potential Malformed Table Lines (missing end pipe?):")
        for ln, text in malformed_lines:
            print(f"  Line {ln}: {text}")
    else:
        print("\n✅ Table rows look structurally okay (start/end with |)")

if __name__ == "__main__":
    verify_skill_md()
