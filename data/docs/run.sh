#!/usr/bin/env bash
# ./run.sh serve [port] | add | add-dir | menu | rm | stats | check | migrate   (see: ./run.sh help)
cd "$(dirname "$0")" || exit 1
c="${1:-help}"; [ $# -gt 0 ] && shift
case "$c" in
  serve) p="${1:-8000}"; echo "Open http://localhost:$p"; exec python3 -m http.server "$p" ;;
  add|add-dir|menu|rm|stats|check|migrate) exec python3 tools/registry.py "$c" "$@" ;;
  *) python3 tools/registry.py --help ; echo; echo "  ./run.sh serve [port]    start the viewer (default 8000)" ;;
esac
