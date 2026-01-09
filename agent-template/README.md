## Agent Template Quick Guide

This folder is meant to be copied into `mle-bench/agents/<your-agent-name>/`.
Everything inside is ready to run a baseline agent that simply mirrors the
competition data and writes a constant prediction. Replace the baseline logic
with your own model; keep the surrounding structure.

### 1. Copy & Rename

```bash
cp -r agent-template mle-bench/agents/my-agent
```

Update every reference to `my-agent` in the copied `config.yaml` and in the
MLE-bench registry so the runner can find your agent.

### 2. Where to Add Your Logic

- `run_agent.py`  
  Replace `generate_baseline_submission` (or the entire file) with your model.
  Inputs from `/home/data` and the required `submission.csv` output are already
  prepared for you. Environment overrides (`DATA_DIR`, `SUBMISSION_PATH`,
  `CODE_DIR`, `LOG_DIR`) make local testing easy.

- `start.sh`  
  Activates the `agent` conda environment and runs `run_agent.py`. You can add
  extra setup steps before the python call if necessary.

- `requirements.txt`  
  List Python packages that should be installed into the container’s `agent`
  environment.

### 3. Build & Test

1. Rebuild the container (from the MLE-bench repository root):
   ```bash
   python -m mlebench build-agent my-agent
   ```

2. Run a local smoke test (using any competition you have prepared):
   ```bash
   python -m mlebench run my-agent spaceship-titanic
   ```

3. Check the submission in `runs/<timestamp>/<competition>/submission/submission.csv`.

### 4. Fast Local Check

Inside the copied agent directory:
```bash
pip install pytest
pytest tests/test_template.py
```

The test fabricates a miniature competition folder, runs `run_agent.py` with
environment overrides, and asserts that a well-formed submission is produced.
Use it as a sanity check after you modify your agent logic.

### 5. Runtime Contract

Every agent must:

1. Read data from `/home/data` (read-only).  
2. Produce `/home/submission/submission.csv` with the exact schema shown in
   `sample_submission.csv`.

Optional but encouraged:

- Write logs to `/home/logs`.
- Save artifacts or source snapshots to `/home/code`.

MLE-bench takes care of:

- Mounting the directories (`/home/data`, `/home/submission`, `/home/logs`,
  `/home/code`, `/home/agent`).
- Injecting environment variables (`COMPETITION_ID`, `TIME_LIMIT_SECS`,
  `STEP_LIMIT`, and anything specified in `config.yaml`).
- Enforcing time/step limits and evaluating the generated submission.

### 6. Files in This Template

```
start.sh          - Shell entrypoint invoked by MLE-bench.
run_agent.py      - Python baseline that you should replace with your logic.
requirements.txt  - Default Python dependencies (edit freely).
Dockerfile        - Builds the agent image; rarely needs changes.
config.yaml       - Example registry entry; update IDs before use.
tests/            - Pytest smoke test to validate the template wiring.
```

Keep the structure, swap out the baseline logic, and your agent is ready to
benchmark. Good luck!
