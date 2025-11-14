import os
import subprocess
import sys
from pathlib import Path

import pandas as pd


def _create_competition_fixture(base: Path) -> None:
    data_dir = base / "data"
    data_dir.mkdir()

    pd.DataFrame(
        {
            "PassengerId": [1, 2, 3, 4],
            "Feature": [0.1, 0.2, 0.3, 0.4],
            "Transported": [True, False, True, False],
        }
    ).to_csv(data_dir / "train.csv", index=False)

    pd.DataFrame(
        {"PassengerId": [5, 6], "Feature": [0.5, 0.6]}
    ).to_csv(data_dir / "test.csv", index=False)

    pd.DataFrame({"PassengerId": [5, 6], "Transported": [False, False]}).to_csv(
        data_dir / "sample_submission.csv", index=False
    )


def test_template_runner_creates_submission(tmp_path: Path) -> None:
    _create_competition_fixture(tmp_path)

    env = os.environ.copy()
    env.update(
        {
            "DATA_DIR": str(tmp_path / "data"),
            "SUBMISSION_PATH": str(tmp_path / "submission" / "submission.csv"),
            "CODE_DIR": str(tmp_path / "code"),
            "LOG_DIR": str(tmp_path / "logs"),
        }
    )

    script = Path(__file__).resolve().parents[1] / "run_agent.py"
    subprocess.run(
        [sys.executable, str(script)],
        cwd=script.parent,
        check=True,
        env=env,
    )

    submission_path = Path(env["SUBMISSION_PATH"])
    assert submission_path.exists(), "Submission file was not created."

    submission = pd.read_csv(submission_path)
    assert list(submission.columns) == ["PassengerId", "Transported"]
    assert len(submission) == 2

    log_file = Path(env["LOG_DIR"]) / "agent.log"
    assert log_file.exists(), "Expected agent log was not written."
