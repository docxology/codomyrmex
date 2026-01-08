
import os

target_file = "scripts/events/examples/example_basic.py"

with open(target_file, "r") as f:
    lines = f.readlines()

new_lines = []
in_main_block = False
try_start_index = -1
except_index = -1

for i, line in enumerate(lines):
    # Detect runner.start()
    if "runner.start()" in line:
        new_lines.append(line)
        new_lines.append(line.replace("runner.start()", "try:")) # Reuse indentation
        try_start_index = len(new_lines) - 1
        continue
    
    # Detect except block at end
    if line.strip().startswith("except Exception as e:") and i > 400: # heuristic
        except_index = i
        new_lines.append(line) # Don't indent except
        continue
    
    # If we passed runner.start() but haven't reached specific except
    if try_start_index != -1 and (except_index == -1):
        if line.strip() == "":
            new_lines.append(line)
        else:
            new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open(target_file, "w") as f:
    f.writelines(new_lines)

print(f"Fixed indentation in {target_file}")
