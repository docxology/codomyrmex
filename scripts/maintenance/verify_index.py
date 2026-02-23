import re

content = open("src/codomyrmex/INDEX.md").read()

modules = set(re.findall(r"\[([a-z_]+)/\]\(\1/\)", content))
print(f"Total entries in INDEX.md table: {len(modules)}")

if "email" in modules and "calendar" in modules:
    print("Missing modules email and calendar added successfully.")
    
if "**Modules**: 84" in content:
    print("Module count updated in header.")
    
if "| **Total** | **84**" in content:
    print("Module count updated in confirmation table.")
