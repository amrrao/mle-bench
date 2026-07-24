# HPO experiments (AIDE)

Reproducible agent variants for hyperparameter-optimization (HPO) interventions on AIDE.

## Conditions

| Agent id | Docker image tag | `agent.py` | `additional_notes.txt` |
|----------|------------------|------------|-------------------------|
| `aide` | `aide` | No HPO scoring | Baseline notes (no HPO directive) |
| `aide-hpo-code` | `aide_hpo_code` | **Control-loop HPO** (`_score_hyperparameter_tuning`) | Baseline notes |
| `aide-hpo-prompt` | `aide_hpo_prompt` | No HPO scoring | **HPO directive** block |
| `aide-hpo-both` | `aide_hpo_both` | **Control-loop HPO** | **HPO directive** block |

Each variant is a **self-contained** tree under `agents/<image_tag>/`. Rebuild the matching image after any change to that tree.

## Build

```bash
export SUBMISSION_DIR=/home/submission LOGS_DIR=/home/logs CODE_DIR=/home/code AGENT_DIR=/home/agent

for agent in aide aide_hpo_code aide_hpo_prompt aide_hpo_both; do
  docker build --platform=linux/amd64 -t "$agent" "agents/$agent/" \
    --build-arg SUBMISSION_DIR=$SUBMISSION_DIR \
    --build-arg LOGS_DIR=$LOGS_DIR \
    --build-arg CODE_DIR=$CODE_DIR \
    --build-arg AGENT_DIR=$AGENT_DIR
done
```

## Run

```bash
export OPENAI_API_KEY=...   # do not commit keys

# Example: prompt-only HPO on the 9-comp short list, 2h (default in variant configs)
python run_agent.py \
  --agent-id aide-hpo-prompt \
  --competition-set experiments/splits/kaggle_short_list.txt \
  --n-seeds 1 \
  --n-workers 9

# Control-loop HPO
python run_agent.py \
  --agent-id aide-hpo-code \
  --competition-set experiments/splits/kaggle_short_list.txt \
  --n-seeds 1 \
  --n-workers 9

# Combined (control-loop + prompt directive)
python run_agent.py \
  --agent-id aide-hpo-both \
  --competition-set experiments/splits/kaggle_short_list.txt \
  --n-seeds 1 \
  --n-workers 9

# Baseline
python run_agent.py \
  --agent-id aide \
  --competition-set experiments/splits/kaggle_short_list.txt \
  --n-seeds 1 \
  --n-workers 9
```

Default time limit in the HPO variant configs is **7200s (2 hours)**. Override by editing `vars.time_limit` in that agent’s `config.yaml` (and rebuilding is not required for env/kwargs read from host `config.yaml`, but keep image code/notes in sync with the folder you intend to run).

## What differs in the files

- **Control-loop HPO** (`agents/aide_hpo_code/` and `agents/aide_hpo_both/` `agent.py`): after each execution, scores whether the generated code does real hyperparameter tuning and uses that signal in search/feedback.
- **Prompt HPO** (`agents/aide_hpo_prompt/` and `agents/aide_hpo_both/` `additional_notes.txt`): appends a `HYPERPARAMETER OPTIMIZATION DIRECTIVE` into the task instructions via `start.sh` (`envsubst`).
- **Combined** (`aide-hpo-both`): both of the above.

## MLMaster (related)

See [`mlmaster/README.md`](mlmaster/README.md) and patch [`mlmaster/mlmaster_hpo.patch`](mlmaster/mlmaster_hpo.patch).

Touched upstream files:

- `agent/mcts_agent.py` — control-loop HPO scoring + HPO-oriented prompts
- `utils/config_mcts.py` — adds `require_hyperparameter_tuning: bool`

There is no separate `additional_notes.txt` for MLMaster; prompt HPO is embedded in `mcts_agent.py`.

## Do not commit

- `.env.local` / API keys
- `runs/` artifacts (optional to keep locally for analysis)
