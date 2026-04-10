#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: ralph-loop.sh [options] <prompt>"
  echo ""
  echo "Options:"
  echo "  -i, --interval SECS   seconds between runs (default: 10)"
  echo "  -n, --max-runs N      max iterations, 0 = unlimited (default: 0)"
  echo "  -c, --continue        continue the last opencode session"
  echo "  -s, --session ID      continue a specific opencode session"
  echo "  -m, --model MODEL     model in provider/model format"
  echo "  -h, --help            show this help"
  echo ""
  echo "Examples:"
  echo "  ralph-loop.sh 'check the build status'"
  echo "  ralph-loop.sh -i 30 -n 5 'run tests and report failures'"
  echo "  ralph-loop.sh -c -i 60 'continue reviewing the PR'"
  exit 0
}

INTERVAL=10
MAX_RUNS=0
CONTINUE=false
SESSION=""
MODEL=""
PROMPT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -i|--interval) INTERVAL="$2"; shift 2 ;;
    -n|--max-runs) MAX_RUNS="$2"; shift 2 ;;
    -c|--continue) CONTINUE=true; shift ;;
    -s|--session)  SESSION="$2"; shift 2 ;;
    -m|--model)    MODEL="$2"; shift 2 ;;
    -h|--help)     usage ;;
    -*)            echo "Unknown option: $1" >&2; exit 1 ;;
    *)             PROMPT="$1"; shift ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Error: prompt is required" >&2
  echo "Run 'ralph-loop.sh --help' for usage" >&2
  exit 1
fi

# Build opencode args
OC_ARGS=(run "$PROMPT")
[[ "$CONTINUE" == true ]] && OC_ARGS+=(--continue)
[[ -n "$SESSION" ]] && OC_ARGS+=(--session "$SESSION")
[[ -n "$MODEL" ]] && OC_ARGS+=(--model "$MODEL")

ITERATION=0

echo "Starting ralph loop"
echo "  prompt:   \"$PROMPT\""
echo "  interval: ${INTERVAL}s"
[[ "$MAX_RUNS" -gt 0 ]] && echo "  max runs: $MAX_RUNS"
[[ -n "$MODEL" ]] && echo "  model:    $MODEL"
echo "Press Ctrl+C to stop."

while true; do
  ITERATION=$((ITERATION + 1))

  if [[ "$MAX_RUNS" -gt 0 && "$ITERATION" -gt "$MAX_RUNS" ]]; then
    echo ""
    echo "=== Reached max runs ($MAX_RUNS). Done. ==="
    break
  fi

  echo ""
  echo "=== Ralph Loop iteration #${ITERATION} — $(date) ==="
  opencode "${OC_ARGS[@]}" || echo "WARNING: opencode exited with status $?"
  echo "=== Iteration #${ITERATION} complete — sleeping ${INTERVAL}s ==="
  sleep "$INTERVAL"
done
