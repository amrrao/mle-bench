# RD-Agent Integration with MLE-bench

## Quick Start

To use RD-Agent with MLE-bench, follow these simple steps:

### 1. Run the setup script

```bash
./setup_rdagent.sh
```

This will:
- Initialize git submodules (mle-bench and RD-Agent)
- Build Docker images
- Check your environment is ready

### 2. Set your API key

```bash
export OPENAI_API_KEY=<your-openai-api-key>
```

### 3. Prepare a competition

```bash
cd mle-bench
mlebench prepare -c spaceship-titanic
```

### 4. Run RD-Agent

```bash
python run_agent.py \
  --agent-id rdagent \
  --competition-set experiments/splits/spaceship-titanic.txt
```

### 5. Check results

```bash
# Find the latest run
RUN_GROUP=$(ls -t runs/ | head -1)

# View logs
cat runs/$RUN_GROUP/*/run.log

# Grade submission (when implementation is complete)
python experiments/make_submission.py \
  --metadata runs/$RUN_GROUP/metadata.json \
  --output runs/$RUN_GROUP/submission.jsonl

mlebench grade \
  --submission runs/$RUN_GROUP/submission.jsonl \
  --output-dir runs/$RUN_GROUP

## Quick Checklist (when adding or updating an agent)

- **Bake dependencies into the Dockerfile.** Add your agent's Python libraries (e.g., `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `xgboost`) to the `pip install` line so they are present in the container at runtime.
- **Set realistic limits in `config.yaml`.** Update `vars.time_limit` (`TIME_LIMIT_SECS`) and `vars.step_count` (`STEP_LIMIT`) to match the agent's runtime needs. We round the limit up to at least one hour inside `start.sh` so the RD loop can run even with short caps.
- **Mirror competition data to a writable path.** Follow the `start.sh` pattern—copy `/home/data` into `${AGENT_DIR}/runtime/data/<competition>` and point the agent to that mirror (`DS_LOCAL_DATA_PATH`).
- **Write outputs to the mounted directories.** Ensure submissions land at `${SUBMISSION_DIR}/submission.csv`, logs under `${LOGS_DIR}`, and any code artifacts in `${CODE_DIR}` so MLE-bench can collect them.
- **Document the run command.** Keep this README's quick start section up to date with the exact `run_agent.py` invocation you use for testing.
```

## What's Been Created

I've set up the integration between RD-Agent and MLE-bench. Here's what was created:

### New Files

1. **mle-bench/agents/rdagent/** - RD-Agent as an MLE-bench agent
   - `config.yaml` - Agent configuration (time limits, models, env vars)
   - `Dockerfile` - Docker image that includes RD-Agent
   - `start.sh` - Entry point script that runs RD-Agent with MLE-bench format
   - `requirements.txt` - Python dependencies

2. **INTEGRATION_GUIDE.md** - Complete guide explaining:
   - How the integration works
   - Setup instructions
   - Configuration options
   - Troubleshooting
   - What still needs to be implemented

3. **MLE_BENCH_FORMAT_PLAN.md** - Technical documentation about:
   - MLE-bench prompt format
   - Implementation details
   - Verification tests

4. **setup_rdagent.sh** - Automated setup script

5. **test_integration.py** - Integration tests

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  MLE-bench Framework                                    │
│  (runs agents on Kaggle competitions)                   │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  run_agent.py --agent-id rdagent                        │
│  - Reads config from agents/rdagent/config.yaml         │
│  - Builds Docker container                              │
│  - Mounts competition data at /home/data/               │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Docker Container                                       │
│  - Runs agents/rdagent/start.sh                         │
│  - Detects hardware (GPU/CPU)                           │
│  - Sets up environment                                  │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  RD-Agent Python Script                                 │
│  - Initializes DataScienceScen(competition)             │
│  - Calls _get_description_mle_format()                  │
│  - Gets MLE-bench formatted prompt:                     │
│    • Base instructions from instructions.txt            │
│    • Additional notes (hardware, time, steps)           │
│    • Competition description                            │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  RD-Agent Loop (TO BE IMPLEMENTED)                      │
│  - Research: Propose hypotheses                         │
│  - Development: Implement and test                      │
│  - Iterate until time/step limit                        │
│  - Output: /home/submission/submission.csv              │
└─────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────┐
│  MLE-bench Grading                                      │
│  - Extracts submission, logs, code                      │
│  - Grades submission against test set                   │
│  - Generates grading report                             │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### ✅ Implemented

- **MLE-bench agent registration** - RD-Agent appears as `--agent-id rdagent`
- **Docker containerization** - Isolated execution environment
- **MLE-bench format prompts** - Uses `_get_description_mle_format()` method
- **Environment configuration** - API keys, models, paths all configurable
- **Hardware detection** - Auto-detects GPUs vs CPUs
- **Directory structure** - Proper mounting of data, submission, logs, code

### 🚧 To Be Implemented

The main missing piece is the **actual RD-Agent loop** in `mle-bench/agents/rdagent/start.sh`.

Currently it creates a placeholder submission. You need to:

1. Import RD-Agent's data science scenario components
2. Run the iterative research & development loop
3. Generate predictions in the correct CSV format
4. Handle errors gracefully

See `INTEGRATION_GUIDE.md` section "Completing the Integration" for details.

## Configuration

Edit `mle-bench/agents/rdagent/config.yaml` to customize:

```yaml
rdagent:
  env_vars:
    TIME_LIMIT_SECS: 86400        # 24 hours
    STEP_LIMIT: 500               # 500 iterations
    CHAT_MODEL: gpt-4o            # LLM model
    EMBEDDING_MODEL: text-embedding-3-small
```

## Testing

Several tests are available:

```bash
# Test MLE-bench format generation (standalone)
python RD-Agent/test_mle_format_simple.py

# Test integration
python test_integration.py

# Test actual agent run (after implementation)
cd mle-bench
python run_agent.py \
  --agent-id rdagent \
  --competition-set experiments/splits/spaceship-titanic.txt
```

## Documentation

- **INTEGRATION_GUIDE.md** - Complete how-to guide
- **MLE_BENCH_FORMAT_PLAN.md** - Technical implementation details
- **CLAUDE.md** - General repository documentation

## Next Steps

1. **Finish the RD-Agent loop implementation**
   - Edit `mle-bench/agents/rdagent/start.sh`
   - Replace placeholder with actual RD-Agent code
   - Ensure submission format matches competition requirements

2. **Test thoroughly**
   - Start with simple competitions (spaceship-titanic)
   - Verify submission files are correctly formatted
   - Check logs for errors

3. **Run on benchmark**
   - Test on lite set (22 competitions)
   - Compare results with other agents
   - Document performance

## Answer to PR Comment

**Question**: "Does your fork use the MLE-bench prompt setup?"

**Answer**: **Yes!** The RD-Agent fork:

1. ✅ Uses MLE-bench `instructions.txt` file
2. ✅ Implements `_get_description_mle_format()` method
3. ✅ Generates prompts in MLE-bench format
4. ✅ Integrates with MLE-bench framework as an agent
5. ✅ Follows same structure as AIDE and other agents

The integration is ready for testing, with the main remaining work being the actual RD-Agent loop implementation.

## Support

For issues or questions:
- Check `INTEGRATION_GUIDE.md` troubleshooting section
- Review `mle-bench/agents/README.md` for agent setup details
- See RD-Agent docs in `RD-Agent/README.md`
