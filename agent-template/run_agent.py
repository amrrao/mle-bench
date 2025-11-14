#!/usr/bin/env python3
"""
Baseline agent runner for MLE-bench.

This file is intentionally tiny and heavily commented so that a SWE can read it
once, understand the contract, and then replace the baseline logic with their
own agent.

Key ideas:
    • Read everything from /home/data (read-only).
    • Write exactly one CSV: /home/submission/submission.csv.
    • Optional: drop misc files into /home/logs or /home/code.

To integrate a real agent, keep the skeleton of main() and replace the section
labelled "YOUR MODEL GOES HERE".
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Step 1. Resolve all important paths and metadata from the environment.
# ---------------------------------------------------------------------------
# When MLE-bench launches your agent inside the container it populates several
# environment variables. The baseline keeps things simple and only reads the
# paths, but a production agent will usually inspect many of these:
#   COMPETITION_ID   -> string identifier for the current dataset.
#   STEP_LIMIT       -> max number of interaction steps you may take.
#   TIME_LIMIT_SECS  -> total wall-clock budget (seconds).
#   HARDWARE         -> textual description of available hardware ("GPU", etc.).
#   DATA_DIR         -> read-only root containing the competition bundle.
#   SUBMISSION_PATH  -> file path where your final CSV must be written.
#   LOG_DIR          -> writable folder collected for inspection.
#   CODE_DIR         -> writable folder captured for code snapshots.
#   INSTRUCTIONS_PATH (optional) -> some agents prefer reading the fully
#                                   rendered instructions here instead of
#                                   building their own prompt.
#
# The template still works in local unit tests thanks to the fallbacks below,
# but inside the harness you should assume the environment variables are set
# and use them instead of hard-coding paths.
DATA_DIR = Path(os.environ.get("DATA_DIR", "/home/data"))
SUBMISSION_PATH = Path(
    os.environ.get("SUBMISSION_PATH", "/home/submission/submission.csv")
)
LOG_DIR = Path(os.environ.get("LOG_DIR", "/home/logs"))
CODE_DIR = Path(os.environ.get("CODE_DIR", "/home/code"))


def ensure_directories_exist() -> None:
    """Create output folders so later writes never fail."""
    SUBMISSION_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)


def load_competition_artifacts() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load the three standard files that appear in every Kaggle-style competition.

    For richer competitions you may find additional artefacts alongside these
    CSVs: README files, feature definitions, custom validation scripts, etc.
    They all live somewhere under DATA_DIR.

    Returns
    -------
    train, test, sample_submission : tuple of pandas.DataFrame
    """
    sample = pd.read_csv(DATA_DIR / "sample_submission.csv")
    train = pd.read_csv(DATA_DIR / "train.csv")
    test = pd.read_csv(DATA_DIR / "test.csv")
    return train, test, sample


def build_baseline_submission(
    train: pd.DataFrame, test: pd.DataFrame, sample: pd.DataFrame
) -> pd.DataFrame:
    """
    Produce a trivial set of predictions that matches the sample submission.

    This is only a placeholder so the template runs end-to-end. Replace this
    function with your real model.

    Common pattern in a real agent:
        • Parse instructions (often at /home/instructions.txt) to understand
          evaluation rules.
        • Perform feature engineering / training.
        • Run inference on the test set.
        • Return a DataFrame whose columns match sample_submission exactly.
    """
    submission = sample.copy()

    # Carry identifier columns straight from the test set.
    id_columns = [col for col in sample.columns if col in test.columns]
    submission[id_columns] = test[id_columns]

    # Targets are whatever columns are present in the sample submission but not
    # found in the test set.  We fill them with simple statistics from `train`.
    targets = [col for col in sample.columns if col not in id_columns]
    for target in targets:
        column = train[target]
        if column.empty:
            submission[target] = sample[target]
        elif pd.api.types.is_numeric_dtype(column):
            submission[target] = column.mean()
        else:
            # For categorical columns, use the most common value.
            mode = column.mode(dropna=True)
            if not mode.empty:
                submission[target] = mode.iloc[0]
            else:
                non_na = column.dropna()
                submission[target] = non_na.iloc[0] if not non_na.empty else sample[target]

    return submission


def main() -> int:
    ensure_directories_exist()

    # -----------------------------------------------------------------------
    # YOUR MODEL GOES HERE
    # -----------------------------------------------------------------------
    # Replace the next four lines with:
    #     1. Read anything you need from DATA_DIR. For advanced agents you may
    #        also consume the rendered instructions located at
    #        Path(os.environ.get("INSTRUCTIONS_PATH", "/home/instructions.txt")).
    #     2. Use metadata such as STEP_LIMIT or TIME_LIMIT_SECS (if applicable)
    #        to plan your compute budget.
    #     3. Train / infer. If you need scratch space, write inside LOG_DIR or
    #        CODE_DIR; never modify DATA_DIR in place.
    #     4. Write the final submission to SUBMISSION_PATH. The grader only
    #        reads this CSV, so make sure it exists when your script exits.
    train, test, sample = load_competition_artifacts()
    submission = build_baseline_submission(train, test, sample)
    submission.to_csv(SUBMISSION_PATH, index=False)
    # -----------------------------------------------------------------------

    # Minimal breadcrumb so humans know the agent executed.
    (LOG_DIR / "agent.log").write_text("Baseline agent completed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
