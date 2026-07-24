# MLMaster HPO changes

MLMaster is vendored/checked out under `agents/mlmaster/core` (upstream: [ML-Master](https://github.com/sjtu-sai-agents/ML-Master)).

## Files touched for HPO

| File | Role |
|------|------|
| `agent/mcts_agent.py` | Control-loop HPO scoring + HPO-oriented draft/improve/debug prompts |
| `utils/config_mcts.py` | Adds `require_hyperparameter_tuning: bool` on `AgentConfig` |

There is **no** separate `additional_notes.txt`; prompt HPO is inside `mcts_agent.py`.

## Apply patch (from repo root)

Against a clean `agents/mlmaster/core` at upstream `main`:

```bash
cd agents/mlmaster/core
git apply ../../../experiments/hpo/mlmaster/mlmaster_hpo.patch
```

Or copy the modified files from your working tree after applying.

Set `require_hyperparameter_tuning=true` in your run kwargs / config when you want the control-loop gate enabled (declare it in `config_mcts.yaml` or pass via CLI).
