#!/usr/bin/env python3
"""Regenerate the 4 ML-Master HPO agent folders from experiments/hpo/mlmaster_sources/.

Usage:
  python3 experiments/hpo/package_mlmaster_hpo.py

Requires a full agent template tree. By default uses agents/mlmaster/ as the
file tree template (Docker, start.sh, deps, etc.), then overlays notes + mcts
+ config for each variant from mlmaster_sources/.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
TEMPLATE = AGENTS / "mlmaster"
SOURCES = Path(__file__).resolve().parent / "mlmaster_sources"

VARIANTS = [
    # folder, agent_id, notes_file, mcts_file, require_hpo
    ("mlmaster", "mlmaster", "additional_notes_baseline.txt", "mcts_agent_baseline.py", False),
    ("mlmaster_hpo_code", "mlmaster-hpo-code", "additional_notes_baseline.txt", "mcts_agent_hpo.py", True),
    ("mlmaster_hpo_prompt", "mlmaster-hpo-prompt", "additional_notes_hpo.txt", "mcts_agent_baseline.py", False),
    ("mlmaster_hpo_both", "mlmaster-hpo-both", "additional_notes_hpo.txt", "mcts_agent_hpo.py", True),
]


def make_config(folder_name: str, agent_id: str, require_hpo: bool) -> str:
    flag = "true" if require_hpo else "false"
    return f"""vars:
  time_limit: &time_limit 7200
  step_count: &step_count 500

defaults: &defaults
  start: {folder_name}/start.sh
  dockerfile: {folder_name}/Dockerfile
  kwargs_type: omegaconf
  env_vars: &env_vars
    TIME_LIMIT_SECS: *time_limit
    STEP_LIMIT: *step_count

kwargs_common: &kwargs_common
  agent.code.model: gpt-5-mini
  agent.code.temp: 1.0
  agent.code.base_url: "https://api.openai.com/v1"
  agent.code.api_key: ${{OPENAI_API_KEY}}
  agent.feedback.model: gpt-5-mini
  agent.feedback.temp: 1.0
  agent.feedback.base_url: "https://api.openai.com/v1"
  agent.feedback.api_key: ${{OPENAI_API_KEY}}
  agent.steps: *step_count
  agent.steerable_reasoning: false
  agent.check_format: true
  agent.require_hyperparameter_tuning: {flag}
  start_cpu: 0
  cpus_per_task: 22

{agent_id}:
  <<: *defaults
  kwargs:
    <<: *kwargs_common
  env_vars:
    <<: *env_vars
    OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}

{agent_id}/smoke:
  <<: *defaults
  kwargs:
    <<: *kwargs_common
    agent.steps: 15
  env_vars:
    <<: *env_vars
    TIME_LIMIT_SECS: 600
    STEP_LIMIT: 15
    OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
"""


def copy_tree_from_template(dst: Path) -> None:
    """Copy shared agent files from template, preserving destination-specific overlays later."""
    if dst.resolve() == TEMPLATE.resolve():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        TEMPLATE,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
    )


def apply_overlay(dst: Path, notes: str, mcts: str, agent_id: str, require_hpo: bool) -> None:
    (dst / "additional_notes.txt").write_text(notes)
    (dst / "agent" / "mcts_agent.py").write_text(mcts)
    folder = dst.name
    (dst / "config.yaml").write_text(make_config(folder, agent_id, require_hpo))
    test_cfg = make_config(folder, agent_id, require_hpo).replace(
        "time_limit: &time_limit 7200", "time_limit: &time_limit 720"
    )
    (dst / "config_test.yaml").write_text(test_cfg)


def main() -> None:
    required = [
        "additional_notes_baseline.txt",
        "additional_notes_hpo.txt",
        "mcts_agent_baseline.py",
        "mcts_agent_hpo.py",
    ]
    for name in required:
        path = SOURCES / name
        if not path.exists():
            raise SystemExit(f"Missing source file: {path}")

    if not TEMPLATE.exists():
        raise SystemExit(f"Missing template tree: {TEMPLATE}")

    for folder, agent_id, notes_name, mcts_name, require_hpo in VARIANTS:
        dst = AGENTS / folder
        notes = (SOURCES / notes_name).read_text()
        mcts = (SOURCES / mcts_name).read_text()
        copy_tree_from_template(dst)
        apply_overlay(dst, notes, mcts, agent_id, require_hpo)
        print(f"Packaged {dst} (id={agent_id}, require_hpo={require_hpo})")

    print("Done.")


if __name__ == "__main__":
    main()
