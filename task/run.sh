#!/usr/bin/env bash
# Entry point. Works from any directory.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-python3}"
case "${1:-help}" in
  web)   shift; exec "$PY" server.py "$@" ;;
  help|-h|--help) exec "$PY" taskctl.py --help ;;
  *)     exec "$PY" taskctl.py "$@" ;;
esac
