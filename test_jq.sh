affected_modules=("database_management")
echo "modules=$(printf '%s\n' "${affected_modules[@]}" | jq -R . | jq -s .)"
