#!/usr/bin/env bash
# Build Docker images for the 4 ML-Master HPO factorial variants.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Ensure base env image exists (MLE-bench convention)
if ! docker image inspect mlebench-env >/dev/null 2>&1; then
  echo "WARNING: mlebench-env image not found. Build it first if these builds fail."
fi

build_one() {
  local folder="$1"
  local tag="$2"
  echo "=== Building ${tag} from agents/${folder} ==="
  docker build -t "${tag}" -f "agents/${folder}/Dockerfile" "agents/${folder}"
}

build_one mlmaster mlmaster:latest
build_one mlmaster_hpo_code mlmaster_hpo_code:latest
build_one mlmaster_hpo_prompt mlmaster_hpo_prompt:latest
build_one mlmaster_hpo_both mlmaster_hpo_both:latest

echo
echo "Built images:"
docker images --format '{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.Size}}' \
  | grep -E '^mlmaster(_hpo_(code|prompt|both))?:' || true

echo
echo "Verifying matrix on host files..."
bash experiments/hpo/verify_mlmaster_hpo.sh
