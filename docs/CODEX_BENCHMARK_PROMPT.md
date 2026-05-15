# Codex prompt — run OpenAI benchmarks for persian-llm-eval

Paste the body between the `---` lines into Codex. It is self-contained:
clone + install + run + commit + push. Replace `<OPENAI_API_KEY>` with a real
key (or set it as an env var Codex already has).

---

**Mission**

Run the Persian LLM evaluation benchmark against a slate of OpenAI models and
push the resulting JSON files back to GitHub. The benchmarking framework, the
prompts, and the scoring logic are already implemented and committed; you do
not need to modify any code. Your job is purely to execute runs and commit
results.

**Repository and branch**

- Repo: `heyparsadev/persian-llm-eval`
- Branch (develop and push here): `main`
- Do **not** push to `main` and do **not** open a pull request unless the user
  explicitly asks for it.

**Environment setup**

```bash
git clone https://github.com/heyparsadev/persian-llm-eval.git
cd persian-llm-eval
git checkout main
git pull origin main
python3 -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -e .
export OPENAI_API_KEY="<OPENAI_API_KEY>"
mkdir -p results
```

The runner uses only stdlib HTTP, so no extra dependencies are needed.

**What the framework already does for you**

You can skip reading the codebase, but for context:
- Prompts for `exact`/`f1` tracks ask the model for a one-line answer with no
  explanation or markdown. Long verbose answers are penalised by `max_words`
  checks on the `instruction` and `hard_instruction` tracks.
- Scoring is tolerant: `exact` falls back to a contiguous token-subsequence
  match, and `f1` evaluates the best sliding-window F1 across the prediction
  tokens. So a final answer embedded in a longer response still scores.
- The result JSON includes a per-sample `prediction` field so results can be
  rescored later without re-running the model.

**Model matrix to run**

Run every model on both splits unless noted. Use exactly these CLI invocations.
If an invocation fails with `model_not_found`, retry with the closest
currently-available model ID from your API tier (for example swap `gpt-5` for
`gpt-4.1` or `gpt-4o`); record the substitution in the commit message.

```bash
# 1) gpt-5-mini (Chat Completions)
persian-eval run --model gpt-5-mini --backend openai-compatible \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/gpt-5-mini.public_eval.json --max-new-tokens 256

persian-eval run --model gpt-5-mini --backend openai-compatible \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/gpt-5-mini.hard.json --max-new-tokens 256

# 2) gpt-5 (Chat Completions)
persian-eval run --model gpt-5 --backend openai-compatible \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/gpt-5.public_eval.json --max-new-tokens 256

persian-eval run --model gpt-5 --backend openai-compatible \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/gpt-5.hard.json --max-new-tokens 256

# 3) gpt-5 with reasoning (Responses API) — equivalent to "gpt-5 thinking"
persian-eval run --model gpt-5 --backend openai-responses \
  --reasoning-effort medium \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/gpt-5-thinking-medium.public_eval.json --max-new-tokens 512

persian-eval run --model gpt-5 --backend openai-responses \
  --reasoning-effort medium \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/gpt-5-thinking-medium.hard.json --max-new-tokens 512

# 4) Optional, only if budget allows: gpt-5 with high effort on hard
persian-eval run --model gpt-5 --backend openai-responses \
  --reasoning-effort high \
  --data data/persian_eval_v1.hard.jsonl \
  --output results/gpt-5-thinking-high.hard.json --max-new-tokens 768
```

Each invocation prints `[i/150] <id> (<track>)` per item and a final
`wrote …` line with the overall score. 150 items × ~250 input tokens per item
keeps per-split cost in the low single digits even on `gpt-5`.

**Per-track sanity check (recommended)**

After each run finishes, eyeball the per-track scores:

```bash
python3 - <<'PY'
import json, sys
for path in sys.argv[1:]:
    r = json.load(open(path))
    print(path, "overall=", round(r["overall_score"], 4))
    for t, d in sorted(r["task_scores"].items()):
        print(f"  {t:18} {d['score']:.3f} (n={d['n']})")
PY
results/*.json
```

If any non-MCQ track scores below 0.3 across all models, the predictions in
`samples[*].prediction` are probably being truncated — re-run with
`--max-new-tokens 512` (or `768` for reasoning models). MCQ tracks should land
in the 0.85–1.00 range for any competent model.

**Commit and push**

`results/*.json` is gitignored, so use `git add -f`:

```bash
git add -f results/gpt-5-mini.public_eval.json \
            results/gpt-5-mini.hard.json \
            results/gpt-5.public_eval.json \
            results/gpt-5.hard.json \
            results/gpt-5-thinking-medium.public_eval.json \
            results/gpt-5-thinking-medium.hard.json
git commit -m "Add OpenAI GPT-5 benchmark results (public_eval + hard, with/without reasoning)"
git push origin main
```

If you had to swap any model ID, include a one-line note in the commit message:

```text
Note: substituted gpt-4.1 for gpt-5 because gpt-5 was not available on this key.
```

**Hard rules**

- Do **not** commit `.env`, the API key, or any file under `data/hidden/`.
- Do **not** use `--no-samples`. The per-sample `prediction` field is the
  single most valuable artifact — it lets us re-score without re-running.
- Do **not** change `persian_eval/`, the data files, or the scoring code.
  If something seems wrong, document it in the commit message; the human
  will decide whether to fix.
- Do **not** open a pull request.
- Stop and ask the human if any single run is going to cost more than $10.

**When you're done**

Report:
1. The exact model IDs you ran (and any substitutions).
2. The overall score for every result file you committed.
3. The commit SHA you pushed.
4. Anything unusual you noticed (truncation, errors, suspicious tracks).

---
