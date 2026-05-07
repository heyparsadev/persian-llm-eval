# Claude Code Notes - persian-llm-eval

## What This Repo Is

This is a Python 3.10+ benchmark runner and leaderboard scaffold for evaluating
LLMs on Iranian Persian. The core package is `persian_eval/`. Dataset records
are JSONL rows with `id`, `track`, `prompt`, `choices`, `answer`, `metadata`,
`source`, and `split`; see [README.md](./README.md) for the full schema.

## Layout

- `persian_eval/` - core package: CLI, runner, backends, scoring, normalization,
  dataset loading, result validation, and leaderboard generation.
- `data/` - JSONL splits (`dev`, `public_eval`, `hard`) and external source references.
- `tests/` - `unittest.TestCase` tests, executed through `pytest`.
- `scripts/` - helper shell scripts for model runs and publishing.
- `configs/baselines.yml` - suggested baseline matrix.
- `hf/` and `spaces/leaderboard/` - Hugging Face Dataset and Space templates.
- `.github/workflows/ci.yml` - lint, format, type, validation, test, and smoke checks.

## Common Commands

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy persian_eval
pytest --cov=persian_eval --cov-report=term-missing
persian-eval run --model smoke --backend mock --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
persian-eval validate results/smoke.json
persian-eval leaderboard build results/*.json --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
```

## Conventions

- Line length is 100, formatting is handled by Ruff, and Python 3.10 is the baseline.
- Do not use syntax that requires Python 3.11+.
- Keep `persian_eval/` dependency-free at runtime; use extras for optional integrations.
- Tests may stay as `unittest.TestCase` classes even though `pytest` is the runner.
- Do not commit generated `results/*.json` or `leaderboard/*` artifacts.
- Preserve CLI flags, dataset schema, result schema, and scoring semantics unless the task
  explicitly asks to change them.

## Hidden Split

`data/hidden/` documents the private split workflow. Never commit hidden split JSONL files
or sample-level predictions from hidden runs. Use `--no-samples` for official hidden
evaluations.
