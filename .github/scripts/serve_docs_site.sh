#!/usr/bin/env bash
# Serve the built Docusaurus site the way GitHub Pages does: under /codomyrmex/,
# with text responses gzipped.
#
# This harness has produced two misleading readings, and it now checks for both
# before it reports a number:
#
#   * The build emits an absolute baseUrl (/codomyrmex/). Serving build/ at the
#     server root made every asset request 404, and Lighthouse then reported a
#     perfect score for a page that shipped no CSS or JavaScript.
#   * http.server does not compress. Uncompressed, the same artifact reported
#     1,759 KB transferred where GitHub Pages sends 337 KB.
#
# A measurement that cannot tell it is measuring the wrong thing is worse than no
# measurement, so: the served HTML must be byte-identical to build/index.html,
# every asset the page references must return 200 under the base path, and a text
# asset must come back gzip-encoded. Any failure exits non-zero instead of
# producing a score.
#
# Those three checks live in verify_docs_site.py and print what they measured.
# LHCI captures this script's stdout only while it runs, so the lines never reach
# the run log; the workflow also runs this script with --check, which serves the
# build, prints the same lines to the log, and exits without measuring anything.
set -euo pipefail
mode="${1:-serve}"
case "$mode" in
  serve | --check) ;;
  *)
    echo "serve_docs_site: unknown argument: ${mode}" >&2
    exit 2
    ;;
esac
port="${PORT:-4173}"
root="$(mktemp -d)"
build="$(pwd)/src/codomyrmex/documentation/build"
ln -s "$build" "$root/codomyrmex"

python3 "$(pwd)/.github/scripts/serve_docs_site.py" "$root" "$port" &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null' EXIT

url="http://127.0.0.1:${port}/codomyrmex/"

ready=0
for _ in $(seq 1 100); do
  if curl -sf -o /dev/null "$url"; then
    ready=1
    break
  fi
  sleep 0.2
done
if [ "$ready" -ne 1 ]; then
  echo "serve_docs_site: server never answered on ${url}" >&2
  exit 1
fi

# 1-3. The served document, its assets, and gzip. The checks live in
# verify_docs_site.py so that this server and the workflow step which prints
# them run the same code and fail for the same reasons.
python3 "$(pwd)/.github/scripts/verify_docs_site.py" --base-url "$url" --build-dir "$build"

if [ "$mode" = "--check" ]; then
  # The workflow step: print the checks to the run log, stop the server, and
  # leave the measurement to LHCI, which starts its own server.
  echo "serve_docs_site: --check complete; server stopped, no measurement taken"
  exit 0
fi

# The readiness line stays last: LHCI starts counting when startServerCommand
# prints it, and a line emitted before the port answers becomes a startup timeout.
echo "listening on ${url} (gzip)"

wait "$server_pid"
