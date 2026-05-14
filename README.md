# Persian LLM Eval (v1.1)

A practical benchmark runner and leaderboard scaffold for evaluating large
language models on **Iranian Persian**. The repo ships a CLI, a JSONL dataset
(300 items across two splits, ten tracks), deterministic scoring with bootstrap
confidence intervals, and pluggable backends for the major API families plus
local Hugging Face models.

> **Status:** v1.1 dataset; 23 reference result files from frontier models
> (Claude Opus/Sonnet/Haiku, GPT‑5 / 5.5 with and without reasoning). See
> [`docs/BENCHMARK_REPORT.md`](docs/BENCHMARK_REPORT.md) for the full
> methodology write-up and per-track tables.

## Headline results

| Rank | Model | Mode | public_eval | hard | combined |
|:---:|---|---|:---:|:---:|:---:|
| 1 | gpt-5.5 | + thinking (high) | 0.9460 | 0.8654 | **0.9057** |
| 2 | gpt-5.5 | standard | 0.9429 | 0.8641 | 0.9035 |
| 3 | gpt-5.5 | + thinking (medium) | 0.9436 | 0.8554 | 0.8995 |
| 4 | gpt-5 | standard | 0.9459 | 0.8376 | 0.8918 |
| 5 | gpt-5-mini | standard | 0.9354 | 0.8422 | 0.8888 |
| 6 | claude-sonnet-4-6 | standard | 0.9063 | **0.8692** | 0.8878 |
| 7 | claude-opus-4-7 | standard | 0.9160 | 0.8464 | 0.8812 |

Bootstrap 95% CIs overlap heavily across the top eight rows — no two adjacent
rows are statistically distinguishable on n=30 per track.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Smoke test against the mock backend (no API key, no GPU).
persian-eval run --model smoke --backend mock \
  --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
persian-eval validate results/smoke.json
persian-eval leaderboard build results/*.json \
  --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
```

Run the test suite:

```bash
pytest -q
```

If you do not code, start with the Persian guide [`START_HERE_FA.md`](START_HERE_FA.md)
or on macOS, double-click [`RUN_ME.command`](RUN_ME.command).

## Backends

| Backend | Models | Required env |
|---|---|---|
| `mock` | Deterministic stub for smoke tests | — |
| `hf` | Any Hugging Face causal LM, optionally 4/8-bit quantised | install with `.[hf]` |
| `openai-compatible` | GPT-4.x, GPT-5 family, and any OpenAI-compatible Chat Completions endpoint | `OPENAI_API_KEY`, optional `OPENAI_BASE_URL` |
| `openai-responses` | GPT-5 family Responses API with `--reasoning-effort` | `OPENAI_API_KEY` |
| `anthropic` | Claude 3.x, 4.x, and 4.7 (with adaptive thinking via `--reasoning-effort`) | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_BASE_URL` |

```bash
# Anthropic — Claude Sonnet 4.6
export ANTHROPIC_API_KEY=...
persian-eval run --model claude-sonnet-4-6 --backend anthropic \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/claude-sonnet-4-6.public_eval.json

# Anthropic — Claude Opus 4.7 with low-effort extended thinking
persian-eval run --model claude-opus-4-7 --backend anthropic \
  --reasoning-effort low \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/claude-opus-4-7-thinking.hard.json

# OpenAI — GPT-5 with medium reasoning (Responses API)
export OPENAI_API_KEY=...
persian-eval run --model gpt-5 --backend openai-responses \
  --reasoning-effort medium --max-new-tokens 512 \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/gpt-5-thinking-medium.hard.json

# Hugging Face — any open-weight Persian-tuned model
pip install -e ".[hf]"
persian-eval run --model PartAI/Dorna2-Llama3.1-8B-Instruct --backend hf \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/dorna2.json
```

`--reasoning-effort` accepts `minimal`, `low`, `medium`, `high`, `xhigh`. The
Anthropic backend maps these to the Claude 4.7 adaptive thinking API
(`low`/`medium`/`high`) and sets a max-tokens headroom; the OpenAI Responses
backend forwards the effort to the API directly.

## CLI

```bash
persian-eval run        --model <id> --backend <name> --data <jsonl ...> --output <out.json>
persian-eval rescore    <result.json> --output <rescored.json>
persian-eval validate   <result.json | --dataset <jsonl ...>>
persian-eval leakage    <jsonl ...>
persian-eval leaderboard build <result.json ...> --output <out.json> [--csv <out.csv>]
```

- **`run`** generates predictions, scores them in-process, and writes the
  result schema. Filter tracks with `--tasks knowledge,reading` and splits
  with `--split public_eval`. Reasoning models often need
  `--max-new-tokens 512` or `768`.
- **`rescore`** re-applies the current scoring rules to a previously written
  result file's saved sample predictions. Use this whenever you tighten an
  accepted-answer list or fix an item — no model re-run is needed:

  ```bash
  persian-eval rescore results/claude-opus-4-7.hard.json \
    --output results/claude-opus-4-7.hard.rescored.json
  ```

- **`validate`** type-checks a result JSON or a dataset JSONL.
- **`leakage`** flags duplicate prompts across the provided JSONLs.
- **`leaderboard build`** aggregates result files, sorts by overall score,
  and attaches bootstrap CIs (1000 iterations, 95% by default). Open-weight
  rows land in `main`; API-backed rows in `reference`. The Hugging Face
  Space under `spaces/leaderboard/` reads the resulting JSON.

## Dataset (v1.1)

300 items across three JSONL files in [`data/`](data):

| File | Items | Use |
|---|:---:|---|
| `persian_eval_v1.dev.jsonl` | 10 | Smoke and debug |
| `persian_eval_v1.public_eval.jsonl` | 150 | Public leaderboard |
| `persian_eval_v1.hard.jsonl` | 150 | Harder public split |

Each split carries five tracks at 30 items each. `public_eval` covers
`knowledge`, `short_qa`, `reading`, `instruction`, `culture`. `hard` covers
`hard_reasoning`, `hard_math`, `hard_reading`, `hard_instruction`,
`hard_culture`. A separate **hidden** split is documented in
[`data/hidden/README.md`](data/hidden/README.md); never commit it.

### Schema

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
    "category": "geography",
    "review": {"author": "human", "status": "accepted", "rubric": {...}}
  },
  "source": "curated:v1",
  "split": "public_eval"
}
```

Supported `metadata.scoring` values:

- `mcq` — label or choice-text matching.
- `exact` — normalised string equality with a contiguous token-subsequence
  fallback (a correct final answer embedded in a longer rationale still
  scores 1.0).
- `f1` — token F1, evaluated both on the full candidate and on every
  sliding window of size equal to the gold answer; the maximum wins.
- `instruction` — strict pass/fail on a constraint dict
  (`required_keywords`, `forbidden`, `min_words`, `max_words`,
  `required_prefix`, `required_suffix`). One violated constraint scores 0.

Contributing items, the authoring checklist, and the review rubric are in
[`CONTRIBUTING_DATASET.md`](CONTRIBUTING_DATASET.md). Mechanical checks are
enforced in CI via [`scripts/validate_dataset.py`](scripts/validate_dataset.py).

## Methodology

The runner applies a uniform short-answer prompt for `exact`/`f1` tracks:

```
{prompt}

فقط پاسخ نهایی را در یک خط بنویس. بدون توضیح، بدون فرمول، بدون مارک‌داون،
بدون پیشوند «پاسخ:».
```

Notes:

- **Verbosity penalty is real**: the `instruction` scorer is strict
  pass/fail. Verbose models (Opus 4.7 in particular) lose `hard_instruction`
  by violating `max_words` even when the content is correct. Extended
  thinking amplifies this — see the Opus thinking sweep in
  [`docs/BENCHMARK_REPORT.md`](docs/BENCHMARK_REPORT.md).
- **Bootstrap CIs**: the leaderboard reports 95% CIs over 1000 resamples
  per row. At n=30 items per track the CI is roughly ±5–7 pp; most
  rankings inside the top eight rows are not statistically distinguishable.
- **Persian text normalisation** unifies ی/ك, ZWNJ usage, NFKC, and
  Arabic↔Persian digits before scoring.

## Result schema

```json
{
  "model_id": "claude-sonnet-4-6",
  "model_type": "api",
  "revision": null,
  "backend": "anthropic",
  "task_scores": {
    "knowledge": {"score": 1.0, "n": 30},
    "short_qa":  {"score": 0.9, "n": 30}
  },
  "overall_score": 0.9063,
  "run_config": {"...": "..."},
  "timestamp": "2026-05-14T...",
  "samples": [{"id": "...", "track": "...", "prediction": "...", "score": 1.0, "details": {...}}]
}
```

Sample-level predictions are included by default and are what makes
`persian-eval rescore` possible. Use `--no-samples` only when running the
hidden official split.

## Cost guidance (approx, per split of 150 items)

| Model | Per split | Both splits |
|---|:---:|:---:|
| claude-haiku-4-5 | $0.11 | $0.22 |
| gpt-5-nano | ~$0.05 | ~$0.10 |
| gpt-5-mini | ~$0.15 | ~$0.30 |
| claude-sonnet-4-6 | $0.32 | $0.64 |
| gpt-5 standard | ~$0.40 | ~$0.80 |
| gpt-5.5 standard | ~$0.50 | ~$1.00 |
| claude-opus-4-7 | $1.58 | $3.16 |
| gpt-5 / 5.5 + thinking | $1–4 | $2–8 |

Running the full Claude + GPT matrix used in this report came in under $25.

## Repository tour

- [`persian_eval/`](persian_eval) — dep-free runtime package: CLI, backends,
  dataset loading, scoring, leaderboard, normalisation.
- [`data/`](data) — JSONL splits plus
  [`data/external_sources.yml`](data/external_sources.yml) referencing PerMMLU,
  Persian IFEval, ParsiNLU, PerCul, and FarsEval-PKBETS.
- [`docs/`](docs) — current benchmark report and the Codex prompt used for
  reproducible OpenAI runs.
- [`results/`](results) — per-model result JSONs (gitignored; force-add to
  commit). Pre-v1.1 results live in [`results/legacy/`](results/legacy) and
  are skipped by the leaderboard builder.
- [`scripts/`](scripts) — model launch scripts (`run_*.sh`), the dataset
  validator, and `build_leaderboard.sh`.
- [`tests/`](tests) — unittest-style tests run through pytest.
- [`configs/baselines.yml`](configs/baselines.yml) — suggested baseline matrix.
- [`spaces/leaderboard/`](spaces/leaderboard) — Gradio HF Space template.

## Hidden official split

[`data/hidden/README.md`](data/hidden/README.md) documents the private split
workflow. Keep the JSONL outside the public repo and use `--no-samples` when
publishing official numbers:

```bash
persian-eval run \
  --data /secure/path/persian_eval_v1.hidden.jsonl \
  --no-samples \
  --output results/<model>_official.json
```

## License

MIT. See [`LICENSE`](LICENSE).
