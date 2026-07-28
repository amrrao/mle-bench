# ML-Master HPO factorial experiments

2×2 ablation of how hyperparameter optimization is injected into ML-Master:

| Axis | Mechanism |
|------|-----------|
| **Prompt HPO** | `HYPERPARAMETER OPTIMIZATION DIRECTIVE` in `additional_notes.txt` (injected via `start.sh` + `envsubst`) |
| **Code HPO** | HPO scoring / reward shaping / baseline-phase policy in `agent/mcts_agent.py` |

## Agent matrix

| Agent id | Folder / Docker image | HPO code (`mcts_agent.py`) | HPO directive in notes |
|----------|------------------------|----------------------------|-------------------------|
| `mlmaster` | `agents/mlmaster` → `mlmaster` | no | no |
| `mlmaster-hpo-code` | `agents/mlmaster_hpo_code` → `mlmaster_hpo_code` | yes | no |
| `mlmaster-hpo-prompt` | `agents/mlmaster_hpo_prompt` → `mlmaster_hpo_prompt` | no | yes |
| `mlmaster-hpo-both` | `agents/mlmaster_hpo_both` → `mlmaster_hpo_both` | yes | yes |

Default time limit for all four: **7200s**. Primary model: `gpt-5-mini`.

## Canonical sources

Editable sources of truth (used by the packaging script):

```
experiments/hpo/mlmaster_sources/
  additional_notes_baseline.txt
  additional_notes_hpo.txt
  mcts_agent_baseline.py
  mcts_agent_hpo.py
```

Regenerate the four agent folders after editing sources:

```bash
python3 experiments/hpo/package_mlmaster_hpo.py
```

## Build images

```bash
# Fast path: overlay notes + mcts onto an existing mlmaster:latest
bash experiments/hpo/build_mlmaster_hpo_images.sh

# Optional full rebuild from mlebench-env (may fail on torch_cluster):
bash experiments/hpo/build_mlmaster_hpo_images.sh --full
```

This builds:

- `mlmaster:latest` (baseline)
- `mlmaster_hpo_code:latest`
- `mlmaster_hpo_prompt:latest`
- `mlmaster_hpo_both:latest`

## Smoke test

10-minute / 15-step run on `spaceship-titanic` for each variant:

```bash
bash experiments/hpo/smoke_mlmaster_hpo.sh
```

Agent ids: `mlmaster/smoke`, `mlmaster-hpo-code/smoke`, `mlmaster-hpo-prompt/smoke`, `mlmaster-hpo-both/smoke`.

## Verify matrix

```bash
bash experiments/hpo/verify_mlmaster_hpo.sh
```

Checks that each folder matches the notes/code matrix and that configs point at the right paths.

## Run example

```bash
python3 run_agent.py \
  --agent-id mlmaster-hpo-both \
  --competition-set experiments/splits/playground_3comps.txt \
  --n-seeds 10 \
  --n-workers 3
```

Swap `--agent-id` for `mlmaster`, `mlmaster-hpo-code`, or `mlmaster-hpo-prompt`.
