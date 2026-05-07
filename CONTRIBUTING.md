# Contributing to Persian LLM Eval

Thanks for your interest. This guide covers code contributions. For submitting
model results to the leaderboard, see [SUBMISSION.md](./SUBMISSION.md).

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Local Checks

Run these before pushing:

```bash
ruff check .
ruff format --check .
mypy persian_eval
pytest --cov=persian_eval --cov-report=term-missing
persian-eval validate --dataset data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl data/persian_eval_v1.hard.jsonl
persian-eval leakage data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl data/persian_eval_v1.hard.jsonl
```

CI runs the same core checks on Python 3.10, 3.11, and 3.12.

## Adding Dataset Samples

Append JSONL records to the appropriate split under `data/`. Each record must
follow the schema documented in the "Dataset Schema" section of [README.md](./README.md).
Run validation and leakage checks locally before opening a pull request.

## Adding a Backend

Backends live in `persian_eval/backends.py`. Implement the same generation
interface as the existing mock, Hugging Face, and OpenAI-compatible backends.
Add tests under `tests/` for at least one multiple-choice path and one short-QA path.

## Commit Style

Use imperative-mood subject lines:

```text
Add Qwen3 14B hard benchmark result
Fix Hugging Face chat generation backend
```

Keep commits focused; one logical change per commit.

## Pull Requests

Reference any related issue, include a short test plan, and wait for CI to pass
on every matrix leg before merging.
