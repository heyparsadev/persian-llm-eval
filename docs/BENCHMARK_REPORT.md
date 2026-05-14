# Persian Eval — Claude family benchmark report

**Run date:** 2026-05-14
**Dataset version:** persian_eval_v1.1 (150 items per split × 2 splits)
**Tracks:** public_eval × {knowledge, short_qa, reading, instruction, culture} +
hard × {hard_reasoning, hard_math, hard_reading, hard_instruction, hard_culture}.
30 items per (split, track) bucket.

## Headline results (overall score, macro-averaged across tracks)

| Model | Mode | public_eval | hard | 95% CI (hard) |
|---|---|:---:|:---:|:---:|
| **claude-opus-4-7** | standard | **0.9160** | 0.8464 | [0.799, 0.892] |
| **claude-opus-4-7** | + thinking (low) | — | 0.8615 | [0.815, 0.903] |
| **claude-sonnet-4-6** | standard | 0.9063 | **0.8692** | [0.833, 0.907] |
| **claude-haiku-4-5** | standard | 0.8226 | 0.7705 | [0.712, 0.823] |

Confidence intervals come from a 1000-iteration non-parametric bootstrap over
sample-level scores. The Sonnet ↔ Opus gap is *not* statistically significant on
either split — the CIs overlap substantially.

## Per-track breakdown

### public_eval

| Track | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 |
|---|:---:|:---:|:---:|
| knowledge | 0.967 | **1.000** | 0.967 |
| culture | **1.000** | **1.000** | 0.967 |
| short_qa | **0.933** | 0.900 | 0.833 |
| reading | **0.880** | 0.832 | 0.813 |
| instruction | 0.800 | 0.800 | 0.533 |

### hard

| Track | Opus 4.7 | Opus 4.7 +T | Sonnet 4.6 | Haiku 4.5 |
|---|:---:|:---:|:---:|:---:|
| hard_culture | **1.000** | **1.000** | **1.000** | 0.967 |
| hard_math | **0.967** | **0.967** | 0.900 | 0.833 |
| hard_reasoning | 0.867 | 0.867 | **0.933** | 0.800 |
| hard_reading | 0.665 | **0.708** | 0.579 | 0.552 |
| hard_instruction | 0.733 | 0.767 | **0.933** | 0.700 |

## Key findings

### 1. Opus is verbose — and the benchmark penalises that
Opus 4.7 is the strongest model on `hard_math` and `hard_reading`, exactly the
tracks that reward extra reasoning. But it scores 0.733 on `hard_instruction`
versus Sonnet's 0.933. Inspection of failing items shows the same pattern: every
constraint check (`required_keywords`, `forbidden`, `min_words`,
`required_prefix`) passes, and only `max_words` fails. Opus consistently writes
longer than the limit even when explicitly told to be brief. Sonnet obeys the
limit. Extended thinking (low effort) lifts `hard_instruction` from 0.733 to
0.767 but does not close the gap.

### 2. Extended thinking helps reading, not reasoning
Turning on adaptive thinking lifts Opus's `hard_reading` from 0.665 to 0.708
and `hard_instruction` from 0.733 to 0.767 — both tracks that benefit from
careful re-checking of the passage or constraints. `hard_reasoning` and
`hard_math` are unchanged: Opus solves them without thinking, or not at all.

### 3. Haiku 4.5 is competitive on factual tracks
Haiku scores 0.967 on `knowledge`, `culture`, and `hard_culture` — within one
item of the larger models. Where it falls behind is `instruction` (0.533) and
`hard_instruction` (0.700): a smaller model is markedly worse at multi-clause
constraint following.

## Methodology notes

### Strict short-answer prompt
For non-MCQ tracks (`exact`, `f1` scoring) the prompt asks for a one-line
answer with no explanation or markdown. This was added after an initial pass
where models including Sonnet wrote multi-paragraph reasoning that strict
exact-match scoring then marked wrong despite the final answer being correct.

### Lenient scoring fallbacks
- `score_exact`: after exact normalised-string equality fails, also accept
  the answer if its tokens appear as a contiguous subsequence in the
  prediction's tokens. This handles "...بنابراین عدد پنجم ۲۰" against
  accepted "۲۰".
- `score_f1`: in addition to F1 against the whole candidate, evaluate F1 on
  every sliding window of the candidate of size |gold|. This rescues short
  gold answers from low precision against long predictions.

These changes were applied retroactively to the original Sonnet predictions
via `persian-eval rescore`. Sonnet's public_eval rose from 0.7474 (strict) to
0.9114 (lenient) without re-running the model. The lifted score reflects what
the model actually answered — it had been correct on most items but penalised
for prose form.

### Cost
For 150 items in a split, average ~250 input + ~100 output tokens per item:

| Model | Per-split | Both splits |
|---|:---:|:---:|
| Haiku 4.5 | ~$0.11 | ~$0.22 |
| Sonnet 4.6 | ~$0.32 | ~$0.64 |
| Opus 4.7 | ~$1.58 | ~$3.16 |
| Opus 4.7 + thinking (low) | ~$4 | — |

Total spend for this report: under $10.

### Limitations
- 30 items per track keeps bootstrap CIs in the ±5 to ±7 pp range. Many
  cross-model comparisons are not statistically significant.
- `hard_reading` ceilings around 0.7 across all models — the passages are
  hard, but the gap may also reflect dataset quality on this track.
- All items still carry `metadata.review.status = "pending_review"`. Human
  review is needed before promoting these scores to a public leaderboard.
- OpenAI and open-weight models were not in this report; those runs happen
  outside this sandbox.
