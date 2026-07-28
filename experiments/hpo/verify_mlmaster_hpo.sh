#!/usr/bin/env bash
# Verify ML-Master HPO factorial folders match the expected matrix.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

pass=0
fail=0

check_variant() {
  local folder="$1"
  local agent_id="$2"
  local expect_notes="$3"  # yes|no
  local expect_code="$4"   # yes|no

  local notes="agents/${folder}/additional_notes.txt"
  local mcts="agents/${folder}/agent/mcts_agent.py"
  local cfg="agents/${folder}/config.yaml"

  local has_notes=no
  grep -q "HYPERPARAMETER OPTIMIZATION DIRECTIVE" "$notes" && has_notes=yes

  local has_code=no
  if grep -q "def _score_hyperparameter_tuning" "$mcts" && grep -q "in_baseline_phase" "$mcts"; then
    has_code=yes
  fi

  local ok=yes
  [[ -f "$notes" && -f "$mcts" && -f "$cfg" ]] || ok=no
  [[ "$has_notes" == "$expect_notes" ]] || ok=no
  [[ "$has_code" == "$expect_code" ]] || ok=no
  grep -q "^${agent_id}:" "$cfg" || ok=no
  grep -q "start: ${folder}/start.sh" "$cfg" || ok=no
  grep -q "dockerfile: ${folder}/Dockerfile" "$cfg" || ok=no
  grep -q "time_limit: &time_limit 7200" "$cfg" || ok=no

  if [[ "$ok" == yes ]]; then
    echo "OK  ${folder}  (id=${agent_id}, notes=${has_notes}, code=${has_code})"
    pass=$((pass + 1))
  else
    echo "FAIL ${folder}  (id=${agent_id}, notes=${has_notes} expected ${expect_notes}, code=${has_code} expected ${expect_code})"
    fail=$((fail + 1))
  fi
}

check_variant mlmaster mlmaster no no
check_variant mlmaster_hpo_code mlmaster-hpo-code no yes
check_variant mlmaster_hpo_prompt mlmaster-hpo-prompt yes no
check_variant mlmaster_hpo_both mlmaster-hpo-both yes yes

echo
echo "Passed: ${pass}  Failed: ${fail}"
[[ "$fail" -eq 0 ]]
