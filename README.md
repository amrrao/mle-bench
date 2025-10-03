# llms-for-mle-bench

## Setup

1. Get `sudo` access to GCP VM from Ting
2. Clone this repo
3. Setup a `python` `venv` using `uv` (instructions [here](https://docs.astral.sh/uv/pip/environments/))
4. Run `uv pip install -e .` within the folder containing the fork of `mle-bench`
5. Follow the instructions [here](https://github.com/tingtang2/mle-bench/blob/main/agents/README.md) to run an agent. All the Docker images should already be available on the VM. Don't forget to set the environment variable for `OPENAI_API_KEY`, reach out to Ting for one.

## References
- [MLE-bench (2025)](https://arxiv.org/abs/2410.07095)
    - [GH repo](https://github.com/openai/mle-bench)