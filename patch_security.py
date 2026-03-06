import re

with open('.github/workflows/security.yml', 'r') as f:
    content = f.read()

# Replace uv python install with actions/setup-python
pattern = r"(\s+- name: Set up Python\n\s+run: uv python install \$\{\{ env\.PYTHON_VERSION \}\})"
replacement = r"\n      - name: Set up Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: ${{ env.PYTHON_VERSION }}"

new_content = re.sub(pattern, replacement, content)

with open('.github/workflows/security.yml', 'w') as f:
    f.write(new_content)
