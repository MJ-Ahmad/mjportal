#!/usr/bin/env bash
# Stewardship Task System runner.
set -euo pipefail
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"

usage() {
  cat <<'EOF'

Stewardship Task System

Usage:
  ./run.sh init
  ./run.sh task "Heading" "Description" [options]
      --steps "step one, step two"
      --add-note "task note"          (repeatable)
      --add-file path/to/file         (repeatable)
      --heading-en "English heading"
      --heading-bn "বাংলা শিরোনাম"
      --description-en "English description"
      --description-bn "বাংলা বিবরণ"

  ./run.sh track TASK-000001 <step_id>
  ./run.sh step-add TASK-000001 "New step"
  ./run.sh step-add TASK-000001 "Substep" --parent 2
  ./run.sh step-note TASK-000001 <step_id> "Note text"
  ./run.sh complete TASK-000001
  ./run.sh validate
  ./run.sh web [port]

Environment:
  BIND=0.0.0.0 ./run.sh web
      Allow other devices on your trusted local network to view the dashboard.

EOF
}

case "${1:-help}" in
  init)
    "$PY" -c "import _lib; _lib.ensure_structure(); print('Ready: data.json, registry.json, attachments/, assets/')"
    ;;

  task)
    shift
    "$PY" add_task.py "$@"
    ;;

  track)
    shift
    "$PY" track_task.py "$@"
    ;;

  step-add)
    shift
    "$PY" manage_steps.py add "$@"
    ;;

  step-note)
    shift
    "$PY" manage_steps.py note "$@"
    ;;

  complete)
    shift
    "$PY" complete_task.py "$@"
    ;;

  validate)
    "$PY" validate.py
    ;;

  web)
    PORT="${2:-8000}"
    BIND="${BIND:-127.0.0.1}"

    "$PY" -c "import _lib; _lib.ensure_structure()"

    echo "Dashboard: http://${BIND}:${PORT}/"
    echo "For local-only access, use the default BIND=127.0.0.1."
    exec "$PY" -m http.server "$PORT" --bind "$BIND"
    ;;

  help|-h|--help)
    usage
    ;;

  *)
    usage
    echo "Unknown command: $1" >&2
    exit 1
    ;;
esac
