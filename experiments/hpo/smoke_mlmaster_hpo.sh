#!/usr/bin/env bash
# Smoke-test each ML-Master HPO factorial variant (1 seed, 10 min, spaceship-titanic).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source venv/bin/activate
set -a && source .env.local && set +a

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: OPENAI_API_KEY not set (.env.local)"
  exit 1
fi

AGENTS=(
  mlmaster/smoke
  mlmaster-hpo-code/smoke
  mlmaster-hpo-prompt/smoke
  mlmaster-hpo-both/smoke
)

COMP_SET=experiments/splits/smoke_spaceship.txt
TS=$(date -u +%Y%m%d_%H%M%S)
LOG_DIR=runs/hpo_smoke_${TS}
mkdir -p "$LOG_DIR"

echo "Smoke log dir: $LOG_DIR"
echo "Competition set: $COMP_SET"
echo

for agent in "${AGENTS[@]}"; do
  safe=$(echo "$agent" | tr '/' '_')
  log="$LOG_DIR/${safe}.log"
  echo "=== Running $agent ===" | tee "$log"
  set +e
  python3 run_agent.py \
    --agent-id "$agent" \
    --competition-set "$COMP_SET" \
    --n-seeds 1 \
    --n-workers 1 \
    2>&1 | tee -a "$log"
  rc=${PIPESTATUS[0]}
  set -e
  echo "=== $agent exit_code=$rc ===" | tee -a "$log"
  echo "$agent $rc" >> "$LOG_DIR/summary.txt"
  echo
done

echo "Summary:"
cat "$LOG_DIR/summary.txt"
