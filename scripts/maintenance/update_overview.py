import re
import os

DOCS_DIR = "docs/modules"

def add_to_table(content, header, new_row):
    # Find the table under the header
    pattern = re.compile(rf"### \*\*{header}\*\*\n\n.*?\n\| Module \| Purpose \| Key Features \|\n\|.*?\|\n(.*?)\n\n", re.DOTALL)
    match = pattern.search(content)
    if match:
        table_content = match.group(1)
        if new_row.split('|')[1].strip() not in table_content:
            new_table_content = table_content + "\n" + new_row
            content = content[:match.start(1)] + new_table_content + content[match.end(1):]
    return content

def add_to_agents_table(content, header, new_row):
    # Find the table under the header in AGENTS.md
    pattern = re.compile(rf"### {header}\n\n.*?\n\| Module \| Description \|\n\|.*?\|\n(.*?)\n\n", re.DOTALL)
    match = pattern.search(content)
    if match:
        table_content = match.group(1)
        if new_row.split('|')[1].strip() not in table_content:
            # Insert alphabetically just to be cleaner, or just sort the table
            lines = table_content.strip().split('\n')
            lines.append(new_row)
            lines.sort()
            new_table_content = "\n".join(lines)
            content = content[:match.start(1)] + new_table_content + content[match.end(1):]
    return content

with open(f"{DOCS_DIR}/overview.md", "r") as f:
    overview = f.read()

# Remove tree_sitter
overview = re.sub(r'\| \*\*`tree_sitter`\*\* \| AST parsing \| Language-agnostic.*?\|\n', '', overview)

overview = add_to_table(overview, "⚙️ Core Functional Modules", "| **`static_analysis`** | Static analysis | Code parsing, pattern matching, syntax trees |")
overview = add_to_table(overview, "🔧 Service Modules", "| **`calendar`** | Event management | Calendar providers, event scheduling |")
overview = add_to_table(overview, "🎮 Application Modules", "| **`email`** | Email communication | Email parsing, IMAP/SMTP integration |")
overview = add_to_table(overview, "🚀 Advanced Modules", "| **`simulation`** | General simulation framework | Agent-based modeling, discrete event simulation |")
overview = add_to_table(overview, "🚀 Advanced Modules", "| **`networks`** | Network graph analysis | Graph metrics, community detection |")
overview = add_to_table(overview, "🚀 Advanced Modules", "| **`formal_verification`** | Formal verification | Model checking, theorem proving |")

with open(f"{DOCS_DIR}/overview.md", "w") as f:
    f.write(overview)


with open(f"{DOCS_DIR}/AGENTS.md", "r") as f:
    agents = f.read()

# Update the Children list
import glob
src_modules = sorted([os.path.basename(p) for p in glob.glob("src/codomyrmex/*") if os.path.isdir(p) and not os.path.basename(p).startswith("_") and "documentation" != os.path.basename(p)])
src_modules.append("documentation") # keep the same set
src_modules = sorted([m for m in src_modules if os.path.isfile(f"src/codomyrmex/{m}/__init__.py")])
children_list = ", ".join([f"[{m}/]({m}/AGENTS.md)" for m in src_modules])

agents = re.sub(r"- \*\*Children\*\* \(84 modules\):\n  - .*?\n", f"- **Children** (84 modules):\n  - {children_list}\n", agents, flags=re.DOTALL)

# Remove tree_sitter
agents = re.sub(r'\| \[tree_sitter/\]\(tree_sitter/\) \| AST parsing and analysis \|\n', '', agents)

agents = add_to_agents_table(agents, "Code & Analysis Modules", "| [static_analysis/](static_analysis/) | Code parsing, ASTs, pattern matching |")
agents = add_to_agents_table(agents, "Interface & Communication Modules", "| [email/](email/) | Email communication |")
agents = add_to_agents_table(agents, "Interface & Communication Modules", "| [calendar/](calendar/) | Event management |")
agents = add_to_agents_table(agents, "Advanced Modules", "| [simulation/](simulation/) | General simulation framework |")
agents = add_to_agents_table(agents, "Framework & Utilities Modules", "| [networks/](networks/) | Network graph analysis |")
agents = add_to_agents_table(agents, "Code & Analysis Modules", "| [formal_verification/](formal_verification/) | Formal verification |")

with open(f"{DOCS_DIR}/AGENTS.md", "w") as f:
    f.write(agents)

print("Updated overview.md and AGENTS.md")
