#!/bin/bash
sed -i 's/echo "modules=$(printf '\\''%s\\n'\\'' "${affected_modules\[@\]}" | jq -R . | jq -s .)" >> $GITHUB_OUTPUT/modules_json=$(printf '\\''%s\\n'\\'' "${affected_modules\[@\]}" | jq -R . | jq -s -c .)\n          echo "modules=${modules_json}" >> $GITHUB_OUTPUT/' .github/workflows/workflow-coordinator.yml
