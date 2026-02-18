#!/usr/bin/env bash
# Codomyrmex Local Web Viewer — start server and open browser
set -e

PORT=8787
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve Python: prefer .venv, fall back to system python
if [ -x "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    PYTHON="python"
fi

# Check Python dependencies
if ! "$PYTHON" -c "import codomyrmex" 2>/dev/null; then
    echo "❌ Missing Python dependencies. Run: pip install -e ."
    exit 1
fi

# Check if port is already in use
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
        echo "❌ Port $PORT is already in use"
        exit 1
    fi
else
    # Fallback: use Python to check port availability
    if "$PYTHON" -c "import socket; s=socket.socket(); s.settimeout(1); exit(0 if s.connect_ex(('localhost',$PORT))==0 else 1)" 2>/dev/null; then
        echo "❌ Port $PORT is already in use"
        exit 1
    fi
fi

# Start the server in the background
"$PYTHON" -m codomyrmex.website &
SERVER_PID=$!

# Wait for the port to be ready (up to 10 seconds)
for i in $(seq 1 20); do
    if "$PYTHON" -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT')" >/dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# Open browser (platform-appropriate)
URL="http://localhost:$PORT"
case "$(uname -s)" in
    Darwin)  open "$URL" ;;
    Linux)   xdg-open "$URL" 2>/dev/null || echo "Open $URL in your browser" ;;
    MINGW*|MSYS*|CYGWIN*) start "$URL" ;;
    *)       echo "Open $URL in your browser" ;;
esac

# Handle Ctrl+C for graceful shutdown
trap 'echo ""; echo "Shutting down..."; kill $SERVER_PID 2>/dev/null; exit 0' INT TERM

# Wait for the server process
wait $SERVER_PID
