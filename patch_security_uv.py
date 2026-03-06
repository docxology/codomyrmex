import re

with open('.github/workflows/security.yml', 'r') as f:
    content = f.read()

# Replace all uv commands to correctly use pip/setup-python where necessary
pattern = r"uv python install \$\{\{ env\.PYTHON_VERSION \}\}"
replacement = r"python -m pip install --upgrade pip"

new_content = re.sub(pattern, replacement, content)

with open('.github/workflows/security.yml', 'w') as f:
    f.write(new_content)
