#!/usr/bin/env bash
# Serve the built Docusaurus site the way GitHub Pages does: under /codomyrmex/.
#
# The build emits an absolute baseUrl (/codomyrmex/), so serving build/ at the
# server root makes every asset request 404. Lighthouse then scores a page with
# no CSS or JavaScript and reports a perfect performance score for a site
# nobody ships. This script builds the same layout Pages produces, starts a
# static server, and prints a readiness line only once the site actually
# answers, so the collector does not wait out its startup timeout.
set -euo pipefail
port="${PORT:-4173}"
root="$(mktemp -d)"
ln -s "$(pwd)/src/codomyrmex/documentation/build" "$root/codomyrmex"

python3 -m http.server "$port" --bind 127.0.0.1 --directory "$root" &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null' EXIT

for _ in $(seq 1 100); do
  if curl -sf -o /dev/null "http://127.0.0.1:${port}/codomyrmex/"; then
    echo "listening on http://127.0.0.1:${port}/codomyrmex/"
    break
  fi
  sleep 0.2
done

wait "$server_pid"
