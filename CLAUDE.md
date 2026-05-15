# Claude Code notes — persian-llm-eval

## What this repo is

Python 3.10+ benchmark runner and leaderboard scaffold for evaluating LLMs on
Iranian Persian. Core package is `persian_eval/`. Dataset records are JSONL
rows with `id`, `track`, `prompt`, optional `choices`, `answer`, `metadata`
(includes `scoring` and optional `review` block), `source`, and `split`.

The dataset is **v1.1**: 300 items total (10 dev + 150 public_eval + 150
hard), five tracks per split, 30 items per (split, track) bucket. The current
benchmark report and full per-model tables live in
[`docs/BENCHMARK_REPORT.md`](docs/BENCHMARK_REPORT.md).

## Layout

- `persian_eval/` — runtime package: CLI (`cli.py`), runner with rescore
  helper (`runner.py`), backends (`backends.py`: mock, hf,
  openai-compatible, openai-responses, anthropic), scoring (`scoring.py`),
  dataset loading (`dataset.py`), result validation (`results.py`),
  leaderboard with bootstrap CI (`leaderboard.py`), Persian
  normalisation (`normalize.py`).
- `data/` — JSONL splits (dev, public_eval, hard) plus external source
  references.
- `tests/` — `unittest.TestCase` tests, run through `pytest`.
- `scripts/` — model launch shells, `build_leaderboard.sh`,
  `validate_dataset.py`, `build_v1_1_items.py` (the v1.1 generator).
- `configs/baselines.yml` — suggested baseline matrix.
- `docs/` — `BENCHMARK_REPORT.md`, `CODEX_BENCHMARK_PROMPT.md`.
- `results/` — per-model result JSONs. Top level holds current v1.1 runs;
  `results/legacy/` holds pre-v1.1 files that are not comparable.
- `hf/` and `spaces/leaderboard/` — Hugging Face dataset and Space templates.
- `.github/workflows/ci.yml` — lint, format, mypy, dataset validation,
  pytest, smoke run.

## Common commands

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy persian_eval
pytest --cov=persian_eval --cov-report=term-missing

# Smoke
persian-eval run --model smoke --backend mock \
  --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
persian-eval validate results/smoke.json

# Real run
persian-eval run --model claude-sonnet-4-6 --backend anthropic \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/claude-sonnet-4-6.public_eval.json

# Re-score saved predictions without re-running the model
persian-eval rescore results/<model>.json --output results/<model>.rescored.json

# Leaderboard
bash scripts/build_leaderboard.sh
```

## Conventions

- Line length 100. Formatting via Ruff. Python 3.10 baseline; do not use
  syntax that requires Python 3.11+.
- Keep `persian_eval/` dependency-free at runtime; optional integrations
  live behind extras (`.[hf]`, `.[dev]`).
- Tests stay as `unittest.TestCase` classes even though `pytest` is the
  runner.
- Do not commit generated `results/*.json` or `leaderboard/*` artifacts;
  the gitignore handles this. When intentionally publishing a result for
  the leaderboard, use `git add -f results/<model>.json`.
- Preserve CLI flags, dataset schema, result schema, and scoring semantics
  unless the task explicitly asks to change them.
- `.env` is gitignored. Never commit API keys.

## Backend notes

- The Anthropic backend uses the native Messages API and supports both the
  legacy `thinking: enabled` budget format (Claude 3.x / 4.x) and the
  newer adaptive thinking with `output_config.effort` (Claude 4.7+).
- For 4.7+ models, `temperature` is not sent and an effort-scaled
  `max_tokens` headroom (4K/8K/16K/32K) is added on top of the user's
  `--max-new-tokens` so the model has room for thinking *and* final answer.
- The OpenAI Chat Completions endpoint for the GPT-5 family uses
  `max_completion_tokens` instead of `max_tokens`. The Codex prompt
  documents a small client-side workaround if you hit this.

## Scoring caveats

- `exact` and `f1` accept token-subsequence and sliding-window F1
  fallbacks so a correct final answer buried in a longer response still
  scores.
- `instruction` is strict pass/fail across all constraints. A single
  `max_words` violation drops the item to 0 even when the rest is right —
  this is intentional and is the dominant cause of the Opus / Sonnet
  underperformance on `hard_instruction`. More thinking makes Opus more
  verbose, so the thinking sweep on hard shows scores degrading past
  `low` effort. See `docs/BENCHMARK_REPORT.md` for the data.

## Hidden split

`data/hidden/` documents the private split workflow. Never commit the
hidden JSONL file or sample-level predictions from hidden runs. Use
`--no-samples` for official hidden evaluations.

## Dataset status

The v1.1 review pass is complete (commit `0b1da03`). All 254 v1.1 items
now carry `metadata.review.status = "accepted"`; 6 items were rejected
and removed from the JSONL splits during the model-assisted review (see
`docs/BENCHMARK_REPORT.md` → "Review log" for the per-bucket breakdown).
The 40 original v1 items remain without a `metadata.review` block and
continue to act as the curated baseline. All current Claude + GPT result
files have been rescored against the post-review dataset via
`persian-eval rescore`.
