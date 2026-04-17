#!/usr/bin/env bash
# Convenience wrapper: run from repo root after `source .venv/bin/activate`.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec bash "${ROOT}/MLEvolve/run_experiments.sh" "$@"
