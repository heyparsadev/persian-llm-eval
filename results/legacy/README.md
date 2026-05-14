# Legacy result files

These result files were produced against an earlier version of the benchmark
and are **not directly comparable** to the current leaderboard. They are kept
in this subdirectory for historical reference only.

## What changed since these were produced

- **Dataset**: ran on Persian Eval v1 (20 items × 5 tracks = ~100 hard items
  total, before v1.1 expanded each track to 30 items). The current splits
  carry 150 items per split.
- **Scoring**: the current scorer accepts contiguous token-subsequence
  matches for `exact` and sliding-window F1 for short gold answers. These
  legacy files were scored under the original strict equality rules and
  systematically under-rate any model whose final answer is embedded in a
  longer rationale.
- **Prompt**: the current strict short-answer prompt (one line, no
  markdown) was added later. Legacy runs used the older prompt that simply
  appended `پاسخ کوتاه:`.

## How to bring a model back into the comparison

Re-run on the current dataset with the current code:

```bash
persian-eval run \
  --model <model_id> \
  --backend <backend> \
  --data data/persian_eval_v1.public_eval.jsonl data/persian_eval_v1.hard.jsonl \
  --output results/<model_id>.json
```

The leaderboard build script ignores files inside `results/legacy/`, so you
will not see these numbers contaminating the rankings.

## Inventory

| File | Approx. items | Notes |
|---|---|---|
| `deepseek_r1_distill_llama_8b_hard.json` | 20 | DeepSeek R1 distill, 8B Llama base |
| `deepseek_r1_distill_qwen_14b_4bit_hard.json` | 20 | DeepSeek R1 distill, 14B Qwen base, 4-bit |
| `gpt_5_4_high_hard.json` | 20 | Pre-v1.1 GPT-5.4 reasoning high |
| `gpt_5_4_mini_high_hard.json` | 20 | Pre-v1.1 GPT-5.4-mini reasoning high |
| `gpt_5_5_high_hard.json` | 20 | Pre-v1.1 GPT-5.5 reasoning high |
| `llama3_3_70b_instruct_bnb_4bit_hard.json` | 20 | Llama 3.3 70B Instruct, 4-bit |
| `mistral_small_24b_2501_bnb_4bit_hard.json` | 20 | Mistral Small 24B, 4-bit |
| `qwen2_5_0_5b_fast.json` | 8 | Qwen 2.5 0.5B smoke run |
| `qwen2_5_72b_instruct_bnb_4bit_hard.json` | 20 | Qwen 2.5 72B Instruct, 4-bit |
| `qwen3_14b_4bit_hard.json` | 20 | Qwen 3 14B, 4-bit |
| `qwen3_30b_a3b_instruct_2507_hard.json` | 20 | Qwen 3 30B-A3B Instruct (2507) |
| `qwen3_8b_fast.json` | 8 | Qwen 3 8B smoke run |
| `qwen3_8b_hard.json` | 20 | Qwen 3 8B |
| `smoke-claude-haiku.json` | 10 | Initial Anthropic backend smoke test (dev split) |
