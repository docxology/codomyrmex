affected_modules=("database_management")
{
  echo "modules<<EOF"
  printf '%s\n' "${affected_modules[@]}" | jq -R . | jq -s .
  echo "EOF"
}
