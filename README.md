# Persian LLM Eval (v1.1)

A practical benchmark runner and leaderboard scaffold for evaluating large
language models on **Iranian Persian**. The repo ships a CLI, a JSONL dataset
(544 scored items across four splits and twenty-one tracks, plus a dev set),
deterministic scoring with bootstrap confidence intervals, and pluggable
backends for the major API families, OpenRouter, and local Hugging Face models.

> **Status:** v1.1 dataset plus two new splits pending native-speaker review:
> **`practical`** (150 everyday-use and creative items) and **`challenge`**
> (100 items built to stay hard for frontier models); 23 reference result
> files from frontier models (Claude Opus/Sonnet/Haiku, GPT‑5 / 5.5 with and
> without reasoning). See [`docs/BENCHMARK_REPORT.md`](docs/BENCHMARK_REPORT.md)
> for the methodology write-up and per-track tables, and
> [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md) (Persian) for the improvement plan
> and the OpenRouter model matrix (Claude Fable 5.1 / Opus 5.5, GPT-6
> Astra / Sol / Luna, and more).

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
| `anthropic` | Claude 3.x and 4.x, and the Claude 5.x family (Opus 5.5, Sonnet 5.5, Fable 5.1) with adaptive thinking via `--reasoning-effort`; `--batch` uses the Message Batches API at half price | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_BASE_URL` |
| `openrouter` | Any model on OpenRouter (Claude, GPT, Gemini, Grok, DeepSeek, Qwen, …) through one key, with unified reasoning control, provider pinning, and per-call cost tracking | `OPENROUTER_API_KEY`, optional `OPENROUTER_BASE_URL` |

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

# Anthropic — Claude Opus 5.5 at max effort as one Message Batch (half price)
persian-eval run --model claude-opus-5-5 --backend anthropic \
  --reasoning-effort max --max-new-tokens 4096 --batch \
  --data data/persian_eval_v1.challenge.jsonl \
  --output results/claude-opus-5.5-max.challenge.json

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

`--reasoning-effort` accepts `none`, `minimal`, `low`, `medium`, `high`,
`xhigh`, `max`. On Claude 5.x models the Anthropic backend sends adaptive
thinking with `output_config.effort` (`low` to `max`), never a temperature, and
adds an effort-scaled `max_tokens` headroom (4K/8K/16K, 64K for `xhigh` and
`max`); requests above about 21K tokens are streamed. `none` turns thinking off
only where the model allows it (Sonnet 5.5, sent as `between_tools`); Opus 5.5
and Fable 5.1 always think. Claude 4.7 keeps its earlier mapping to
`low`/`medium`/`high`. The OpenAI Responses backend forwards the effort to the
API directly.

### OpenRouter

One key reaches every provider, so the whole model matrix runs the same code
path:

```bash
export OPENROUTER_API_KEY=sk-or-...

# One model, one split, 6 requests in flight.
persian-eval run --model anthropic/claude-opus-5.5 --backend openrouter \
  --data data/persian_eval_v1.practical.jsonl --max-new-tokens 4096 \
  --concurrency 6 --output results/claude-opus-5.5.practical.json

# GPT-6 Sol with thinking; OpenRouter's unified `reasoning.effort`.
persian-eval run --model openai/gpt-6-sol --backend openrouter \
  --reasoning-effort medium --max-new-tokens 4096 --concurrency 6 \
  --data data/persian_eval_v1.hard.jsonl --output results/gpt-6-sol-thinking-medium.hard.json

# The full matrix in configs/openrouter_models.json over every split.
python scripts/run_matrix.py --estimate  # cost estimate, no key needed
python scripts/run_matrix.py --dry-run   # plan + live slug/price check
python scripts/run_matrix.py
```

`--estimate` prices the planned runs from the real prompt sizes, measured
Persian characters-per-token ratios, and an assumed thinking length per
reasoning effort. For the default matrix (12 rows x 4 splits, 544 items per
row) it comes to about **$102** (roughly $58–$190 depending on how long the
models actually think); the two new splits alone are about $45. Claude
Fable 5.1 and Opus 5.5 cannot turn thinking off, so their rows always set an
effort. Running only the Claude models on Anthropic's own API costs the same
per token, and half that through the Batch API; see
[`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md) for the per-row tables.

- `--reasoning-effort` maps to OpenRouter's `reasoning.effort` (`none` turns
  thinking off where the model allows it; GPT-6 Astra does not). Thinking
  shares `max_tokens` with the answer, so an effort-scaled headroom
  (4K–64K) is added on top of `--max-new-tokens`. `--thinking-budget-tokens`
  sends an explicit `reasoning.max_tokens` instead.
- `--provider anthropic,google-vertex` pins the provider order,
  `--no-fallbacks` forbids routing elsewhere, and `--data-collection deny`
  only uses providers that do not store or train on prompts, which keeps the
  eval set out of training data.
- Every call records tokens, reasoning tokens, USD cost, latency, and the
  serving provider; the result gets a `usage` block and the leaderboard a
  `cost_usd` column.
- Runs are checkpointed to `<output>.partial.jsonl`; if a run dies, rerun the
  same command with `--resume` to skip the items already paid for.

### Claude 5.x on Anthropic's API, as Message Batches

[`configs/anthropic_models.json`](configs/anthropic_models.json) runs Claude
Opus 5.5 at `low`, `medium`, and `max` effort and Claude Sonnet 5.5 without
thinking and at `low`, `medium`, and `max` (Fable 5.1 rows are there but
disabled). Every run is one Message Batch: half price, most batches finish
within an hour, none takes more than 24. The script submits all batches first
and then collects them.

```bash
export ANTHROPIC_API_KEY=...
python scripts/run_matrix.py --config configs/anthropic_models.json --estimate
# Pilot first: 20 challenge items per row, kept out of the leaderboard.
python scripts/run_matrix.py --config configs/anthropic_models.json \
  --splits challenge --max-items 20 --results-dir results/pilot
python scripts/run_matrix.py --config configs/anthropic_models.json
```

The estimate for all seven rows over the four splits is about **$153** at
batch prices ($79–$300 depending on thinking length); the two `max` rows are
about $132 of it. The pilot costs about $6 and its summary table shows the
real output tokens per item, which replace the assumed thinking lengths.

- The batch id is saved in the run's checkpoint right after submission, so an
  interrupted run (or one started with `--no-wait`) collects the same batch on
  `--resume` instead of paying for a second one; starting over without
  `--resume` is refused while a batch is outstanding.
- Items a batch fails on are retried by the next `--resume`, which submits
  only those; `--max-item-errors N` lets up to N of them score 0 instead.
- A refusal (`stop_reason: refusal`) scores as an empty answer and is counted
  in `usage.refusals`. No fallback model is configured, because its answer
  would be scored as this model's.
- `usage.cost_usd` is computed from Anthropic's list prices and the reported
  tokens (thinking is billed as output), halved for batches.

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
  `--max-new-tokens 512` or `768`. `--concurrency N` runs N API requests in
  parallel (results keep dataset order), and `--resume` continues an
  interrupted run from its checkpoint. With the Anthropic backend, `--batch`
  sends the items as one Message Batch (`--no-wait` submits and exits).
  `--max-items N` runs N items spread evenly over the data, for a pilot.
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

## Dataset (v1.1 + practical + challenge)

554 items across five JSONL files in [`data/`](data):

| File | Items | Use |
|---|:---:|---|
| `persian_eval_v1.dev.jsonl` | 10 | Smoke and debug |
| `persian_eval_v1.public_eval.jsonl` | 149 | Public leaderboard |
| `persian_eval_v1.hard.jsonl` | 145 | Harder public split |
| `persian_eval_v1.practical.jsonl` | 150 | Everyday use and creative writing (new, `pending_review`) |
| `persian_eval_v1.challenge.jsonl` | 100 | Hard knowledge, awareness, and word play (new, `pending_review`) |

`public_eval` and `hard` carry five tracks at ~30 items each. `public_eval`
covers `knowledge`, `short_qa`, `reading`, `instruction`, `culture`. `hard`
covers `hard_reasoning`, `hard_math`, `hard_reading`, `hard_instruction`,
`hard_culture`. A separate **hidden** split is documented in
[`data/hidden/README.md`](data/hidden/README.md); never commit it.

The **`practical`** split asks for what people actually bring to an assistant
in Persian, six tracks x 25 items:

| Track | What it tests | Scoring |
|---|---|---|
| `practical_writing` | Leave requests, SMS, formal/colloquial register shifts, support replies, condolence and congratulation messages | `instruction` |
| `practical_editing` | Text typed on the wrong keyboard layout, Finglish to Persian script, spelling (حیاط/حیات, نقص/نقض), ZWNJ (نیم‌فاصله) | `exact`, `f1`, `instruction` |
| `practical_numbers` | Jalali↔Gregorian dates, date arithmetic across Esfand and leap years, weekdays, cheque amounts in words, toman/rial, discounts, VAT, installments | `exact` |
| `practical_extraction` | Real-estate and car ads, bank SMS, tickets, receipts, prescriptions → JSON, including fields that must stay `null` | `json` |
| `practical_pragmatics` | Taarof and social formulas (خسته نباشید، عافیت باشه، چشمتان روشن), natural EN↔FA translation of idioms | `mcq` |
| `practical_creative` | Acrostics (توشیح), lipograms, rhyme and radif, alliteration, anagrams, riddles, abjad, idiom paraphrase | `instruction`, `exact` |

The **`challenge`** split is meant to stay hard for frontier models and to
reward awareness, not recall, five tracks x 20 items:

| Track | What it tests | Scoring |
|---|---|---|
| `challenge_premise` | False premises to push back on (گلستان «by Ferdowsi», «۳۰ اسفند ۱۴۰۵», «the province of Kish»), mixed with true-premise controls that must not be "corrected" | `instruction` |
| `challenge_grounding` | Answer only from a passage; half the questions are not answerable from it and must be declined; the rest need updates, negation, or arithmetic | `exact`, `instruction` |
| `challenge_ambiguity` | Persian homographs without vowels (شیر، کرم، ملک، مهر), sarcasm and irony, pronoun and attachment ambiguity, disambiguation in context | `instruction`, `mcq` |
| `challenge_multihop` | Chained facts on Iranian literature, history, and geography; Persian kinship terms (جاری، باجناق، پسرخاله) | `exact`, `instruction` |
| `challenge_wordplay` | Word and letter palindromes, rhopalic sentences, acrostic + rhyme / lipogram combinations, per-line word counts, letter and dot counting in Persian script | `instruction`, `exact` |

Both new splits are generated by scripts
([`build_practical_items.py`](scripts/build_practical_items.py),
[`build_challenge_items.py`](scripts/build_challenge_items.py)): computable
answers (calendar conversion, number words, keyboard mapping, abjad, letter
counts) come from code, and every non-MCQ item carries a
`metadata.reference_response` that CI requires to score 1.0.

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
  The practical split adds `required_any` (groups of alternatives),
  `forbidden_chars` (lipograms), `required_exact`/`forbidden_exact`
  (ZWNJ-sensitive), `starts_with`/`ends_with` (punctuation-tolerant),
  `line_count`, `line_initials` (acrostics), `lines_end_with` and
  `distinct_line_endings` (rhyme), `word_initial` (alliteration). The
  challenge split adds `word_final`, `word_palindrome`,
  `letter_palindrome` with `min_letters`, `word_length_step` (rhopalic
  sentences), and `words_per_line`; these treat a ZWNJ compound such as
  «می‌روم» as one word.
- `json` — the first JSON object in the reply is compared field by field with
  the gold object; the score is the fraction of fields right. Numbers compare
  numerically (`"8,500,000"` = `8500000`), a list of gold values means "any
  of these", and a gold `null` is satisfied by null or a missing key.

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
  "usage": {"calls": 150, "prompt_tokens": 41250, "completion_tokens": 9120, "cost_usd": 0.43, "providers": {"Anthropic": 150}},
  "samples": [{"id": "...", "track": "...", "prediction": "...", "score": 1.0, "details": {...}, "meta": {"cost_usd": 0.0029, "provider": "Anthropic"}}]
}
```

`usage` and per-sample `meta` appear only for backends that report them
(`openrouter` and `anthropic`).

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
- [`configs/openrouter_models.json`](configs/openrouter_models.json) and
  [`configs/anthropic_models.json`](configs/anthropic_models.json) — the
  OpenRouter and Claude-only model matrices run by
  [`scripts/run_matrix.py`](scripts/run_matrix.py).
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
