#!/usr/bin/env bash
# Serve the built Docusaurus site the way GitHub Pages does: under /codomyrmex/,
# with text responses gzipped.
#
# The build emits an absolute baseUrl (/codomyrmex/), so serving build/ at the
# server root makes every asset request 404 — Lighthouse then scores a page
# with no CSS or JavaScript and reports a perfect number for a site nobody
# ships. The sibling .py server adds gzip, which Pages does and http.server
# does not; without it the emulated link measures compressibility instead of
# the site.
set -euo pipefail
port="${PORT:-4173}"
root="$(mktemp -d)"
ln -s "$(pwd)/src/codomyrmex/documentation/build" "$root/codomyrmex"

python3 "$(pwd)/.github/scripts/serve_docs_site.py" "$root" "$port" &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null' EXIT

for _ in $(seq 1 100); do
  if curl -sf -o /dev/null "http://127.0.0.1:${port}/codomyrmex/"; then
    echo "listening on http://127.0.0.1:${port}/codomyrmex/ (gzip)"
    break
  fi
  sleep 0.2
done

wait "$server_pid"
