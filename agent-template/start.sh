#!/bin/bash
#
# Minimal MLE-bench start script.
# Copies of this template should only need to change the python command
# near the bottom once `run_agent.py` contains real agent logic.

set -euo pipefail
set -x

cd "${AGENT_DIR}"

eval "$(conda shell.bash hook)"
conda activate agent

mkdir -p "${SUBMISSION_DIR}" "${CODE_DIR}" "${LOGS_DIR}"

TIME_LIMIT_SECS=${TIME_LIMIT_SECS:-0}

if command -v nvidia-smi &> /dev/null && nvidia-smi --query-gpu=name --format=csv,noheader &> /dev/null; then
  HARDWARE=$(nvidia-smi --query-gpu=name --format=csv,noheader | paste -sd ', ' -)
else
  HARDWARE="CPU"
fi

echo "====================================="
echo "Agent Directory: ${AGENT_DIR}"
echo "Competition: ${COMPETITION_ID}"
echo "Time Limit (s): ${TIME_LIMIT_SECS:-unbounded}"
echo "Step Limit: ${STEP_LIMIT:-unbounded}"
echo "Hardware: ${HARDWARE}"
echo "====================================="

if [[ "${TIME_LIMIT_SECS}" =~ ^[0-9]+$ && "${TIME_LIMIT_SECS}" -gt 0 ]]; then
  timeout "${TIME_LIMIT_SECS}" python "${AGENT_DIR}/run_agent.py" "$@"
  EXIT_CODE=$?
  if [[ "${EXIT_CODE}" -eq 124 ]]; then
    echo "Agent timed out after ${TIME_LIMIT_SECS} seconds"
    exit 124
  fi
else
  python "${AGENT_DIR}/run_agent.py" "$@"
  EXIT_CODE=$?
fi

if [[ "${EXIT_CODE}" -ne 0 ]]; then
  echo "Agent exited with status ${EXIT_CODE}"
  exit "${EXIT_CODE}"
fi

SUBMISSION_PATH="${SUBMISSION_DIR}/submission.csv"
if [[ ! -f "${SUBMISSION_PATH}" ]]; then
  echo "Expected submission at ${SUBMISSION_PATH} was not created."
  exit 1
fi

echo "Submission written to ${SUBMISSION_PATH}"
exit 0
