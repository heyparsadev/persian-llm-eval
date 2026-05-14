# Persian Eval — Frontier model benchmark report

**Run date:** 2026-05-14
**Dataset version:** persian_eval_v1.1 (150 items per split × 2 splits)
**Tracks:** public_eval × {knowledge, short_qa, reading, instruction, culture}
+ hard × {hard_reasoning, hard_math, hard_reading, hard_instruction, hard_culture}.
30 items per (split, track) bucket.

## Combined ranking (mean of public_eval and hard overall)

| Rank | Model | Mode | public_eval | hard | combined |
|:---:|---|---|:---:|:---:|:---:|
| 1 | **gpt-5.5** | +thinking (high) | 0.9460 | 0.8654 | **0.9057** |
| 2 | **gpt-5.5** | standard | 0.9429 | 0.8641 | 0.9035 |
| 3 | gpt-5.5 | +thinking (medium) | 0.9436 | 0.8554 | 0.8995 |
| 4 | gpt-5 | standard | 0.9459 | 0.8376 | 0.8918 |
| 5 | gpt-5-mini | standard | 0.9354 | 0.8422 | 0.8888 |
| 6 | **claude-sonnet-4-6** | standard | 0.9063 | **0.8692** | 0.8878 |
| 7 | claude-opus-4-7 | standard | 0.9160 | 0.8464 | 0.8812 |
| 8 | gpt-5 | +thinking (medium) | 0.9292 | 0.8202 | 0.8747 |
| 9 | claude-opus-4-7 | +thinking (low) | — | 0.8615 | — |
| 10 | claude-opus-4-7 | +thinking (medium) | — | 0.8520 | — |
| 11 | claude-opus-4-7 | +thinking (high) | — | 0.8167 | — |
| 12 | gpt-5-nano | standard | 0.9190 | 0.7958 | 0.8574 |
| 13 | claude-haiku-4-5 | standard | 0.8226 | 0.7705 | 0.7965 |

All scores are macro-averages across the five tracks in each split. The
combined column is a plain mean of the two split overall scores; it is not
weighted by item count. Confidence intervals (1000-iteration non-parametric
bootstrap, 95%) overlap heavily across the top eight rows — no two adjacent
rows are statistically distinguishable.

## Per-track scores

### public_eval (n=30 per track)

| Track | gpt-5.5 | gpt-5.5 +T(h) | gpt-5 | gpt-5-mini | sonnet-4-6 | opus-4-7 | haiku-4-5 | gpt-5-nano |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| knowledge | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.967 | 0.967 | 1.000 |
| culture | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.967 | 1.000 |
| short_qa | 0.967 | 0.967 | 0.967 | 0.967 | 0.900 | 0.933 | 0.833 | 0.967 |
| reading | 0.880 | 0.880 | 0.880 | 0.847 | 0.832 | 0.880 | 0.813 | 0.847 |
| instruction | 0.867 | 0.883 | 0.883 | 0.863 | 0.800 | 0.800 | 0.533 | 0.783 |

### hard (n=30 per track)

| Track | sonnet-4-6 | gpt-5.5 +T(h) | gpt-5.5 | opus-4-7 +T(l) | opus-4-7 | gpt-5.5 +T(m) | gpt-5-mini | gpt-5 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| hard_culture | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| hard_math | 0.900 | 0.967 | 0.967 | 0.967 | 0.967 | 0.967 | 0.967 | 0.967 |
| hard_reasoning | **0.933** | 0.867 | 0.867 | 0.867 | 0.867 | 0.867 | 0.867 | 0.867 |
| hard_reading | 0.579 | 0.745 | 0.687 | 0.708 | 0.665 | 0.713 | 0.598 | 0.665 |
| hard_instruction | **0.933** | 0.748 | 0.800 | 0.767 | 0.733 | 0.728 | 0.778 | 0.689 |

## Key findings

### 1. GPT-5.5 is the strongest model on this benchmark
Every variant of gpt-5.5 places in the top three. The combined score gap
between gpt-5.5 and the strongest Claude is roughly 2 pp, which is within the
bootstrap CI margin. Calling this a "GPT-5.5 win" is fair on point estimates
but not statistically robust.

### 2. Sonnet 4.6 owns `hard` — including against the GPT-5 family
Sonnet 4.6 scores 0.8692 on hard, higher than every GPT-5 / GPT-5.5 variant
including thinking. The win is driven by `hard_reasoning` (0.933) and
`hard_instruction` (0.933) — both tracks where staying on-format and not
over-writing matters more than raw smarts.

### 3. Reasoning sometimes hurts, and Opus thinking has a sweet spot at "low"

We ran four points on the Opus 4.7 thinking-effort curve on the hard
split:

| Effort | hard | hard_instruction | hard_reading | hard_reasoning |
|---|:---:|:---:|:---:|:---:|
| standard (no thinking) | 0.8464 | 0.733 | 0.665 | 0.867 |
| + thinking low | **0.8615** | 0.767 | **0.708** | 0.867 |
| + thinking medium | 0.8520 | 0.767 | 0.660 | 0.867 |
| + thinking high | 0.8167 | 0.633 | 0.650 | 0.833 |

Performance peaks at **low** effort and degrades from there. The collapse
is concentrated in `hard_instruction` (0.767 → 0.633 from low to high): more
thinking produces longer final answers that blow through `max_words`
limits. `hard_reasoning` also dips at high effort, suggesting the extra
thinking lets the model second-guess otherwise-correct answers.

Similar pattern in the GPT family:
- gpt-5 + thinking medium scores **lower** than gpt-5 standard (0.8747 vs
  0.8918). The thinking variant over-elaborates on simple Q&A.
- gpt-5.5 + thinking medium scores **lower** than gpt-5.5 standard on `hard`
  (0.8554 vs 0.8641).
- gpt-5.5 + thinking high recovers and edges out standard by 0.002 — within
  noise.

The takeaway: thinking helps on tracks that benefit from re-reading or
constraint checking (reading at low effort, instruction at low effort). It
hurts when it pushes the model to write more than the prompt asked for.
"More thinking ≠ better" on short-answer Persian.

### 4. The verbosity penalty is real and reproducible
Opus 4.7 fails `hard_instruction` at 0.733; every constraint check passes
except `max_words`. The same pattern shows up on GPT-5 + thinking
(`hard_instruction` = 0.689). Models that produce shorter, more disciplined
responses (Sonnet 4.6, gpt-5-mini) are rewarded.

### 5. gpt-5-mini is the value pick
At 0.8888 combined, gpt-5-mini ranks fifth — between gpt-5 standard and
claude-sonnet-4-6 — at a fraction of the API cost. For Persian short-answer
and MCQ workloads it is essentially indistinguishable from the flagship.

### 6. Haiku 4.5 is competitive on factual tracks only
Haiku scores ≥ 0.95 on `knowledge`, `culture`, and `hard_culture` but
collapses to 0.533 on `instruction`. Constraint following needs scale.

## Methodology notes

### Prompt
For non-MCQ tracks (`exact` and `f1` scoring) the system instructs:
> فقط پاسخ نهایی را در یک خط بنویس. بدون توضیح، بدون فرمول، بدون
> مارک‌داون، بدون پیشوند «پاسخ:».

The prompt is identical across every model and mode.

### Scoring
- MCQ — first label or first matched choice text wins.
- exact — normalised string equality, with a token-subsequence fallback so
  that "...بنابراین عدد پنجم ۲۰" still scores against accepted "۲۰".
- f1 — best F1 between the prediction and any accepted answer, evaluated
  both on the full candidate and on every sliding window of size |gold|.
- instruction — strict pass/fail on the constraint dict; partial credit is
  not given (this is why `max_words` failures are punishing).

### Cost (approximate)

| Model | Per split | Both splits |
|---|:---:|:---:|
| claude-haiku-4-5 | $0.11 | $0.22 |
| gpt-5-nano | ~$0.05 | ~$0.10 |
| gpt-5-mini | ~$0.15 | ~$0.30 |
| claude-sonnet-4-6 | $0.32 | $0.64 |
| gpt-5 standard | ~$0.40 | ~$0.80 |
| gpt-5.5 standard | ~$0.50 | ~$1.00 |
| claude-opus-4-7 | $1.58 | $3.16 |
| gpt-5 / 5.5 +thinking | ~$1–4 | ~$2–8 |

Total spend across this report (Claude + every GPT variant): under $25.

### Operational notes from the Codex run
- Chat Completions for the GPT-5 family required swapping `max_tokens` →
  `max_completion_tokens`; Codex did this transparently with a local proxy.
- Several reasoning runs needed `max_new_tokens=2048` or more — the
  default 512 produced empty outputs.
- gpt-5-nano on `hard` has 3 empty predictions out of 150 (in
  `hard_reasoning` and `hard_instruction`); all three are scored 0. Wall-time
  for the full Codex job was about three hours, dominated by the
  reasoning-mode runs.

### Limitations
- 30 items per track keeps bootstrap CIs at roughly ±5 to ±7 percentage
  points. Most rankings within the top eight are within noise.
- Open-weight model results from earlier in the repo (`results/qwen*.json`,
  `results/llama*.json`, etc.) were run against the v1 baseline (20 items,
  strict scoring) and are **not** comparable to this report. Re-running
  them on the v1.1 dataset with the current scoring is the next step.
- Every v1.1 item still carries `metadata.review.status = "pending_review"`.
  Human review should precede any public release of these scores.
