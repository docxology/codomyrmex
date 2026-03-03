#!/bin/bash
sed -i 's/permissions: {}/permissions:\n  contents: read\n  pull-requests: write\n  issues: write/g' .github/workflows/pre-commit.yml
