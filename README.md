# Persian LLM Eval Benchmark v1

A practical benchmark runner and leaderboard scaffold for evaluating LLMs on Iranian Persian.

The v1 goal is adoption: objective scoring, reproducible JSON outputs, simple Hugging Face publication paths, and enough structure for teams to submit comparable model results.

## What Is Included

- A lightweight `persian-eval` CLI.
- Curated Persian JSONL dev/public-eval samples using the v1 dataset schema.
- Deterministic scoring for MCQ, short QA, reading comprehension, instruction-following constraints, and Persian culture/knowledge tasks.
- Optional backends for Hugging Face Transformers and OpenAI-compatible chat APIs.
- Result validation and leaderboard generation.
- A minimal Hugging Face Space app under `spaces/leaderboard`.

Existing Persian benchmarks such as PerMMLU, Persian IFEval, ParsiNLU, PerCul, and FarsEval-PKBETS are referenced in `data/external_sources.yml` but not vendored. Their licenses and release policies should be respected when creating larger official splits.

## Quickstart

If you do not code, start with the Persian guide:

```text
START_HERE_FA.md
```

On macOS, you can also double-click:

```text
RUN_ME.command
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

persian-eval run --model smoke --backend mock --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
persian-eval validate results/smoke.json
persian-eval leaderboard build results/*.json --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
```

Run the tests:

```bash
python3 -m unittest discover -s tests
```

## Running Real Models

Hugging Face local/open-weight model:

```bash
pip install -e ".[hf]"
persian-eval run \
  --model PartAI/Dorna2-Llama3.1-8B-Instruct \
  --backend hf \
  --model-type open-weight \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/dorna2.json
```

OpenAI-compatible API baseline:

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=https://api.openai.com/v1
persian-eval run \
  --model gpt-4.1-mini \
  --backend openai-compatible \
  --model-type api \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/gpt-4.1-mini.json
```

API baselines are marked as reference rows by the leaderboard builder.

## CLI

```bash
persian-eval run --model <model_id> --tasks all --output results/<model>.json
persian-eval validate results/<model>.json
persian-eval validate --dataset data/persian_eval_v1.public_eval.jsonl
persian-eval leakage data/*.jsonl
persian-eval leaderboard build results/*.json
```

Task selection accepts `all` or a comma-separated list of tracks:

```bash
persian-eval run --model smoke --backend mock --tasks knowledge,reading --output results/smoke_subset.json
```

Harder curated examples are available in:

```bash
persian-eval run --model smoke --backend mock --data data/persian_eval_v1.hard.jsonl --output results/smoke_hard.json
```

Advanced open-weight examples for a 24GB GPU:

```bash
scripts/run_qwen3_8b_hard.sh
scripts/run_qwen3_14b_4bit_hard.sh
scripts/run_deepseek_r1_distill_8b_hard.sh
```

`Qwen3-14B` uses `--quantization 4bit` so it can fit on a single RTX 4090-class GPU.

## Dataset Schema

Each JSONL row uses this shape:

```json
{
  "id": "peval-public-knowledge-001",
  "track": "knowledge",
  "prompt": "پرسش فارسی",
  "choices": ["گزینه ۱", "گزینه ۲"],
  "answer": "گزینه ۱",
  "metadata": {
    "scoring": "mcq",
    "answer_index": 0,
    "category": "geography"
  },
  "source": "curated:v1",
  "split": "public_eval"
}
```

Supported `metadata.scoring` values:

- `mcq`: multiple-choice label or choice-text matching.
- `exact`: normalized exact match against one or more accepted answers.
- `f1`: token-level F1, useful for short QA and reading comprehension.
- `instruction`: automatic constraint checks such as required keywords, forbidden tokens, and word limits.

## Result Schema

The CLI writes JSON with the required fields from the plan:

```json
{
  "model_id": "PartAI/Dorna2-Llama3.1-8B-Instruct",
  "model_type": "open-weight",
  "revision": null,
  "backend": "hf",
  "task_scores": {
    "knowledge": {"score": 0.5, "n": 10}
  },
  "overall_score": 0.5,
  "run_config": {},
  "timestamp": "2026-05-01T00:00:00+00:00"
}
```

Sample-level predictions are included by default for public runs. Do not publish sample targets for a private hidden split.

## Hidden Official Split

`data/hidden/README.md` documents the expected private split workflow. Keep the official hidden JSONL outside the public repo and run it with:

```bash
persian-eval run --data /secure/path/persian_eval_v1.hidden.jsonl --no-samples --output results/model_official.json
```

## Hugging Face Space

Build the leaderboard artifact, then copy `leaderboard/leaderboard.json` next to `spaces/leaderboard/app.py` when deploying the Space:

```bash
persian-eval leaderboard build results/*.json --output spaces/leaderboard/leaderboard.json --csv spaces/leaderboard/leaderboard.csv
```

The Space separates main open-weight rows from API reference baselines.
