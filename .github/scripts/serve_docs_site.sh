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
set -euo pipefail
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

# 1. The document under the base path is the build's own index.html.
if ! curl -sf "$url" | cmp -s - "$build/index.html"; then
  echo "serve_docs_site: served HTML is not byte-identical to build/index.html" >&2
  echo "serve_docs_site: refusing to measure an unknown page" >&2
  exit 1
fi

html="$(curl -sf "$url")"
js="$(printf '%s' "$html" | grep -o -m1 '/codomyrmex/assets/js/[^"]*\.js' || true)"
css="$(printf '%s' "$html" | grep -o -m1 '/codomyrmex/assets/css/[^"]*\.css' || true)"
if [ -z "$js" ] || [ -z "$css" ]; then
  echo "serve_docs_site: index.html references no JS/CSS asset under /codomyrmex/" >&2
  exit 1
fi

# 2. The assets the page references resolve under the base path.
for asset in "$js" "$css"; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${port}${asset}")"
  if [ "$code" != "200" ]; then
    echo "serve_docs_site: ${asset} returned HTTP ${code}; assets are not resolving" >&2
    exit 1
  fi
done

# 3. Text responses are compressed, as GitHub Pages compresses them.
if ! curl -s -o /dev/null -D - -H 'Accept-Encoding: gzip' "http://127.0.0.1:${port}${js}" \
  | tr -d '\r' | grep -qi '^content-encoding: gzip'; then
  echo "serve_docs_site: ${js} was served without gzip" >&2
  exit 1
fi

# The readiness line stays last: LHCI starts counting when startServerCommand
# prints it, and a line emitted before the port answers becomes a startup timeout.
echo "listening on ${url} (gzip)"
echo "serve_docs_site: artifact verified (index.html byte-identical, assets resolve, gzip on)"

wait "$server_pid"
