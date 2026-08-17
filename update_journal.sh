if [ ! -f .jules/bolt.md ]; then
  mkdir -p .jules
  touch .jules/bolt.md
fi

cat << 'INNER_EOF' >> .jules/bolt.md
## $(date +%Y-%m-%d) - Dictionary Allocation Overhead in Hot Paths
**Learning:** In highly trafficked factory functions (like `create_policy` in cache policies), re-creating the same static dictionary mapping strings to classes on every single invocation introduces measurable Python object allocation and garbage collection overhead.
**Action:** When a dictionary maps static keys to constant values (like classes or functions), hoist it out of the function body into a module-level or class-level constant to make the lookup O(1) in both time and allocation cost.
INNER_EOF
