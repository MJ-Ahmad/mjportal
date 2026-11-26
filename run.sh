#!/usr/bin/env bash
# Self / Life Tracker runner: validates the database, then serves the dashboard.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${1:-8000}"
BIND="${KHATA_BIND:-127.0.0.1}"

if ! python3 life.py validate; then
  echo "Fix the errors above before starting the dashboard."
  exit 1
fi

echo ""
echo "Dashboard : http://127.0.0.1:${PORT}"
echo "Stop      : Ctrl+C"
echo ""
exec python3 -m http.server "$PORT" --bind "$BIND"

# New optional Markdown viewer command.
# Existing ./run.sh and ./run.sh PORT behavior remains unchanged.
if [[ "${1:-}" == "serve" ]]; then
  shift
  PORT="${1:-8000}"
  BIND="${KHATA_BIND:-127.0.0.1}"

  python3 scripts/content_setup.py --index-only

  if ! python3 life.py validate; then
    echo "Fix the errors above before starting the dashboard."
    exit 1
  fi

  echo ""
  echo "Dashboard        : http://127.0.0.1:${PORT}"
  echo "Markdown viewer  : http://127.0.0.1:${PORT}/markdown/"
  echo "Stop             : Ctrl+C"
  echo ""
  exec python3 -m http.server "$PORT" --bind "$BIND"
fi
