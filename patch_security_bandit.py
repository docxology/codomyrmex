import re

with open('.github/workflows/security.yml', 'r') as f:
    content = f.read()

pattern = r"(uv pip install sarif-tools)"
replacement = r"pip install sarif-tools"

new_content = re.sub(pattern, replacement, content)

with open('.github/workflows/security.yml', 'w') as f:
    f.write(new_content)
