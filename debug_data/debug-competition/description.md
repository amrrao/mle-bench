# Debug Competition

Welcome to the debug competition used for integration tests.

## Objective

Generate predictions for the rows in `test.csv` and submit them using the exact
schema defined in `sample_submission.csv`.

## Files

- `train.csv` – toy training set with features and a target column.
- `test.csv` – rows to score during inference.
- `sample_submission.csv` – target submission structure.

## Evaluation

Submissions are evaluated offline. Any CSV that matches the sample submission
columns and row count is considered valid for testing purposes.
