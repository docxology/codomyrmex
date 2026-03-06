import re
from collections import defaultdict

lines = open("ty_errors.txt").read().splitlines()
errors = []

current_file = None
current_line = None
current_err = None

for i, line in enumerate(lines):
    # e.g. error[invalid-return-type]: ...
    m = re.match(r"^error\[(.*?)\]: (.*)", line)
    if m:
        current_err = m.group(1)
        msg = m.group(2)
        # The file/line is usually a few lines BEFORE the error message in new ty versions?
        # Actually ty output:
        # error[invalid-assignment]: ...  <-- Wait! Where is the file?
        # Let's check how ty formats errors. Usually:
        #   --> src/codomyrmex/foo.py:10:5
        # error[invalid-assignment]: ...
        # Let's search backwards for '-->'
        file_line = None
        for j in range(i-1, i-5, -1):
            if j >= 0 and "-->" in lines[j]:
                file_line = lines[j].strip().removeprefix("-->").strip()
                break

        if file_line:
            parts = file_line.split(":")
            if len(parts) >= 2:
                file_path = parts[0]
                line_num = parts[1]
                errors.append((current_err, file_path, line_num, msg))

ret_map = defaultdict(list)
ass_map = defaultdict(list)

for err, f, l, msg in errors:
    if err == "invalid-return-type":
        if "website/" in f or "agents/" in f or "orchestration/orchestrator" in f or "logistics/orchestrator" in f:
            ret_map[f].append((l, msg))
    elif err == "invalid-assignment":
        # core modules? let's just count all for now
        ass_map[f].append((l, msg))

print("=== invalid-return-type in website/agents/orchestrator ===")
for f in sorted(ret_map.keys()):
    print(f"{f}: {len(ret_map[f])} errors")

print("\n=== invalid-assignment ===")
ass_sorted = sorted(ass_map.items(), key=lambda x: len(x[1]), reverse=True)
for f, lst in ass_sorted[:20]:
    print(f"{f}: {len(lst)} errors")
