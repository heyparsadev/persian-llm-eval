# Persian Eval — Frontier model benchmark report

**Run date:** 2026-05-15 (post-review rescore; original run 2026-05-14)
**Dataset version:** persian_eval_v1.1, post-review (149 public_eval + 145 hard items)
**Tracks:** public_eval × {knowledge, short_qa, reading, instruction, culture}
+ hard × {hard_reasoning, hard_math, hard_reading, hard_instruction, hard_culture}.
~29–30 items per (split, track) bucket after the v1.1 cleanup.

> **What's new in this revision.** Every v1.1 item that had been flagged
> `pending_review` went through a Sonnet 4.6 / Haiku 4.5 review pass.
> 254 items are now `accepted`; 6 were `rejected` and removed from the
> JSONL (factual or logical errors that were penalising correct model
> answers — see commit `f081372` for the list). For 169 `revise` items,
> safe model proposals were applied (extra accepted-answer phrasings,
> loosened word bounds, prompt rewrites for clarity). Every result file
> below was then re-scored with `persian-eval rescore` against the
> updated dataset — no model was re-run. Scores rose ~3 pp across the
> board because accepted-answer lists are no longer artificially narrow.

## Phase 1 (October 2026): Claude Opus 5.5 and Sonnet 5.5

Seven settings over all four splits (544 items each): Opus 5.5 at `low`,
`medium`, and `high` effort, and Sonnet 5.5 without thinking and at the same
three efforts. Every run went through Anthropic's own API as a Message Batch
(`configs/anthropic_models.json`), `max_new_tokens` 4096 plus the effort
headroom. `max` effort is left for phase 2.

| Setting | practical | challenge | hard | public_eval | mean | cost (USD) | output tokens / item |
|---|:---:|:---:|:---:|:---:|:---:|---:|---:|
| Opus 5.5 · low | **0.957** | 0.880 | **0.897** | **0.927** | **0.915** | 0.91 | 125 |
| Opus 5.5 · medium | 0.950 | **0.890** | 0.873 | 0.925 | 0.910 | 1.10 | 161 |
| Opus 5.5 · high | 0.944 | 0.870 | 0.888 | 0.924 | 0.906 | 1.17 | 174 |
| Sonnet 5.5 · no thinking | 0.879 | 0.750 | 0.856 | 0.896 | 0.845 | 0.31 | 72 |
| Sonnet 5.5 · low | 0.899 | 0.790 | 0.868 | 0.871 | 0.857 | 0.37 | 94 |
| Sonnet 5.5 · medium | 0.904 | 0.780 | 0.881 | 0.868 | 0.858 | 0.38 | 99 |
| Sonnet 5.5 · high | 0.944 | 0.830 | 0.862 | 0.916 | 0.888 | 0.59 | 173 |

Costs are batch prices for all 544 items; output tokens include thinking.
The 95% bootstrap intervals are about ±3 pp on practical, hard, and
public_eval and ±6 pp on challenge, so most gaps inside one model are noise.

**1. Opus 5.5 is best at `low` effort, which is also its cheapest setting.**
`medium` and `high` cost 20–30% more and land within noise of `low` (the
same pattern as Opus 4.7 in v1.1). For this benchmark, run Opus 5.5 at
`low`.

**2. Sonnet 5.5 needs `high` effort to close the gap.** `high` adds 4–5 pp on
practical and challenge over `medium` and is the best Sonnet setting, at
about 55% more cost. Without thinking, Sonnet scores 0.845 for $0.31,
the cheapest result by far.

**3. The challenge split does its job.** It is the hardest split for every
setting (0.75–0.89) and spreads the settings 14 pp apart, against 6 pp on
public_eval. `challenge_wordplay` separates Sonnet without thinking (0.45)
from Opus (0.85), and `challenge_ambiguity` is the hardest track (0.50–0.70).
`challenge_grounding` is at 1.0 for every setting and needs harder items.

**4. Opus 5.5's safety classifier refuses mistyped Persian.** The
wrong-keyboard-layout items in `practical_editing` (`003`–`005`, Persian typed
on an English layout) were declined with `stop_reason: refusal`, category
`cyber`: three refusals across Opus `medium` and `high`, while Opus `low` and
every Sonnet setting answered them. Refusals score 0, which costs Opus `high`
8 pp on that track (2 of 25 items). It is a real false positive
for a common Persian user habit.

**5. Legacy instruction scoring penalises correct Persian spelling.** The
v1.1 `min_words`/`max_words` checks count a ZWNJ compound such as «لامپ‌های»
as two words, and `required_suffix` fails on a trailing period. Claude 5.5
writes ZWNJ consistently, so on public_eval's `instruction` track 4–10 of
its 5–15 failures per setting would pass under the ZWNJ-aware count and the
punctuation-tolerant suffix the new splits use (GPT-5.5 had one failure).
That is up to 0.33 on the track and up to 6–7 pp on public_eval overall.
The comparison below therefore understates Claude 5.5 on public_eval. The
fix changes published scoring, so it waits for a decision; `rescore` would
apply it without calling any model.

**6. Against v1.1 models (mean of public_eval and hard, as scored today):**
Opus 5.5 · low 0.912, Sonnet 4.6 0.920, Opus 4.7 0.903, GPT-5.5 0.940,
GPT-5.5 thinking-high 0.945, gpt-5-mini 0.927. The v1.1 runs used other
token limits and older prompts, and point 5 applies, so read this as a rough
placement, not a ranking.

**7. The cost estimate was more than ten times too high.** The whole phase cost
**$4.83** against an estimate of about $55. The models think far less than
assumed on these short items (72–174 output tokens per item, answer
included, against 600–4,000 assumed thinking tokens), and Claude 5.5 reads
about 1.4 Persian characters per token, not 1.0.

**Data fix found by this run.** The prompt of `peval-hard-reading-025` had
been replaced by a reviewer note during the v1.1 review pass (commit
`5b390f7`), so phase-1 models saw no passage (Opus declined it twice as
`reasoning_extraction`). The prompt is restored, with the reviewer's
suggested constraint added; this item's phase-1 scores are not meaningful.
Opus 5.5 `high` also returned two MCQ answers with no text block (3 output
tokens, `end_turn`); the backend now records the content block types of
empty answers.

## Headline

Overall scores on the hard split, sorted, with 1000-iteration bootstrap
95% confidence intervals on the overall score:

![Overall scores on hard split with bootstrap CI](charts/overall_hard.png)

Generalisation between the public and hard splits — every model lands
below `y = x`, which means hard is genuinely harder, not a calibration
artefact:

![Public-eval vs hard scatter](charts/public_vs_hard.png)

Per-track heatmap on the hard split. `Reading` is the hardest track for
every model; `Culture` and `Math` are saturated at the top:

![Per-track heatmap on hard split](charts/track_heatmap.png)

Best variant per family, broken down by track:

![Best-of-family grouped bars across tracks](charts/top_models_tracks.png)

Claude Opus 4.7 thinking-effort sweep. Overall peaks at `+T(low)` and
then drops because more thinking inflates verbosity, which trips
`max_words` penalties on the `Instruction` track:

![Opus 4.7 thinking sweep across tracks](charts/opus_thinking.png)

Regenerate any of these with `python3 scripts/build_charts.py`
(requires `pip install -e ".[viz]"`).

## Combined ranking (mean of public_eval and hard overall)

| Rank | Model | Mode | public_eval | hard | combined |
|:---:|---|---|:---:|:---:|:---:|
| 1 | **gpt-5.5** | +thinking (high) | 0.9702 | **0.9197** | **0.9450** |
| 2 | gpt-5.5 | standard | 0.9622 | 0.9183 | 0.9403 |
| 3 | gpt-5.5 | +thinking (medium) | 0.9651 | 0.9147 | 0.9399 |
| 4 | gpt-5 | standard | **0.9659** | 0.8903 | 0.9281 |
| 5 | gpt-5-mini | standard | 0.9558 | 0.8979 | 0.9269 |
| 6 | **claude-sonnet-4-6** | standard | 0.9318 | 0.9090 | 0.9204 |
| 7 | gpt-5 | +thinking (medium) | 0.9479 | 0.8774 | 0.9127 |
| 8 | claude-opus-4-7 | standard | 0.9296 | 0.8766 | 0.9031 |
| 9 | claude-opus-4-7 | +thinking (low) | — | 0.8973 | — |
| 10 | claude-opus-4-7 | +thinking (medium) | — | 0.8910 | — |
| 11 | gpt-5-nano | standard | 0.9397 | 0.8502 | 0.8950 |
| 12 | claude-opus-4-7 | +thinking (high) | — | 0.8680 | — |
| 13 | claude-haiku-4-5 | standard | 0.8434 | 0.8219 | 0.8326 |

All scores are macro-averages across the five tracks in each split. The
combined column is a plain mean of the two split overall scores; it is not
weighted by item count. Bootstrap 95% CIs (1000 iterations) overlap heavily
across the top eight rows — no two adjacent rows are statistically
distinguishable.

## Per-track scores

### public_eval (29–30 items per track)

| Track | gpt-5.5 | gpt-5.5 +T(h) | gpt-5 | gpt-5-mini | sonnet-4-6 | opus-4-7 | haiku-4-5 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| knowledge | 1.000 | 1.000 | 1.000 | 0.967 | 1.000 | 0.967 | 0.967 |
| culture | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.967 |
| short_qa | 0.931 | 0.931 | 0.931 | 0.931 | 0.931 | 0.931 | 0.862 |
| reading | 0.913 | 0.920 | 0.899 | 0.881 | 0.928 | 0.950 | 0.888 |
| instruction | 0.967 | 1.000 | 1.000 | 1.000 | 0.800 | 0.800 | 0.533 |

### hard (29–30 items per track)

| Track | gpt-5.5 +T(h) | gpt-5.5 | gpt-5.5 +T(m) | sonnet-4-6 | gpt-5 | opus-4-7 | opus-4-7 +T(l) | haiku-4-5 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| hard_culture | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.964 |
| hard_math | 1.000 | 1.000 | 1.000 | 0.931 | 0.931 | 0.966 | 0.966 | 0.931 |
| hard_reasoning | 0.897 | 0.897 | 0.897 | **0.966** | 0.966 | 0.931 | 0.966 | 0.828 |
| hard_reading | 0.702 | 0.695 | 0.710 | 0.715 | 0.688 | 0.753 | 0.789 | 0.686 |
| hard_instruction | 1.000 | 1.000 | 0.967 | 0.933 | 0.867 | 0.733 | 0.767 | 0.700 |

## Key findings

### 1. GPT-5.5 is the strongest model on this benchmark
All three gpt-5.5 variants — standard, +T(medium), +T(high) — occupy
the top three combined ranks. The gap between gpt-5.5 and the strongest
Claude (Sonnet 4.6) is ~2.5 pp; bootstrap 95% CIs still overlap so the
"win" is not statistically certain, but it is consistent across both
splits and every thinking level.

### 2. Sonnet 4.6 beats Opus 4.7, even with thinking
On the hard split Sonnet 4.6 (0.9090) edges out Opus 4.7 with low-effort
thinking (0.8973) and beats every other Opus configuration. The combined
delta is 1.7 pp in Sonnet's favour. The dominant driver is once again
`hard_instruction`: Sonnet 0.933, Opus 0.733 (no thinking) → 0.633
(thinking high). Opus is more verbose by default and gets more so under
extra thinking, blowing through `max_words` constraints. Sonnet is
disciplined enough to obey the limits. On `hard_reasoning` Opus +T(low)
ties Sonnet at 0.966, so this is squarely about output discipline, not
raw reasoning skill.

### 3. Reasoning sometimes hurts, and Opus thinking peaks at "low"

We ran four points on the Opus 4.7 thinking-effort curve on the hard
split:

| Effort | hard | hard_instruction | hard_reading | hard_reasoning |
|---|:---:|:---:|:---:|:---:|
| standard (no thinking) | 0.8766 | 0.733 | 0.753 | 0.931 |
| + thinking low | **0.8973** | 0.767 | **0.789** | **0.966** |
| + thinking medium | 0.8910 | 0.767 | — | — |
| + thinking high | 0.8680 | 0.633 | — | — |

Performance peaks at **low** effort and degrades from there. The collapse
is concentrated in `hard_instruction` (0.767 → 0.633 from low to high):
more thinking produces longer final answers that blow through `max_words`
limits. `hard_reasoning` also dips at high effort, suggesting the extra
thinking lets the model second-guess otherwise-correct answers.

Similar pattern in the GPT family:
- gpt-5 + thinking medium scores **lower** than gpt-5 standard (0.9127 vs
  0.9281 combined). The thinking variant over-elaborates on simple Q&A.
- gpt-5.5 + thinking medium scores only +0.005 over gpt-5.5 standard on
  `hard` (0.9147 vs 0.9183 — basically a wash).
- gpt-5.5 + thinking high edges out standard by ~0.005 on combined — well
  inside the bootstrap CI.

The takeaway: thinking helps on tracks that benefit from re-reading or
constraint checking (reading at low effort, instruction at low effort
for Opus). It hurts when it pushes the model to write more than the
prompt asked for. "More thinking ≠ better" on short-answer Persian.

### 4. The verbosity penalty is real and reproducible
Opus 4.7 fails `hard_instruction` at 0.733; every constraint check passes
except `max_words`. The same pattern shows up on Sonnet 4.6 at 0.933 —
it occasionally violates `max_words` too, just less often. Models that
produce shorter, more disciplined responses (gpt-5.5, gpt-5-mini) score
1.000 on `hard_instruction`.

### 5. gpt-5-mini is the value pick
At 0.9269 combined, gpt-5-mini ranks fifth — ahead of Sonnet 4.6 and Opus
4.7 — at a fraction of the API cost. For Persian short-answer and MCQ
workloads it is essentially indistinguishable from the flagships.

### 6. Haiku 4.5 is competitive on factual tracks only
Haiku scores ≥ 0.95 on `knowledge`, `culture`, and `hard_culture` but
collapses to 0.533 on `instruction`. Constraint following needs scale.

### 7. The v1.1 review pass moved the leaderboard, not the rankings
Re-scoring against the post-review dataset lifted every score by roughly
3 pp, but the relative ordering of the top eight rows is unchanged.
The largest reshuffle is gpt-5-mini moving ahead of claude-opus-4-7 on
combined (0.9269 vs 0.9031) — driven by Opus losing 7 pp to gpt-5-mini
on `hard` because of `hard_instruction` (0.733 vs 1.000). This is the
verbosity finding amplified by the more lenient post-review scoring.

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

### Review log
Every v1.1 item that was previously `pending_review` went through a
model-assisted review pass. The proposals are captured in
`scripts/review_pending_items.py` output (gitignored at
`data/review_proposals.jsonl`) and applied via
`scripts/apply_review_decisions.py`. Summary of decisions:

- **85 items** accepted as-is (only rubric tweaks proposed).
- **44 items** accepted with no content change (rubric notes only).
- **66 items** had safe additions applied (extra accepted-answer
  phrasings, loosened word bounds).
- **45 items** had `rewrite_prompt` proposals applied for clarity.
- **14 items** got individual decisions: 4 reasoning/math items had
  genuinely wrong labelled answers and were fixed; 5 culture MCQ items
  had stylistic replacement suggestions that would have broken the
  MCQ choice match, so the suggestion was rejected; 5 instruction/
  reading items needed only metadata tweaks.
- **6 items** rejected and removed from the dataset entirely: factual
  or logical errors that penalised correct model answers
  (`peval-public-shortqa-027`, `peval-hard-reasoning-014`,
  `peval-hard-reading-028`, `peval-hard-culture-012`,
  `peval-hard-math-029`, `peval-hard-culture-008`).

### Next run

The next revision adds two splits — `practical` (150 everyday-use and
creative items) and `challenge` (100 items on false premises, unanswerable
questions, ambiguity, chained knowledge, and word play) — and runs a new
model matrix — Claude Fable 5.1 and Opus 5.5, GPT-6 Astra / Sol / Luna,
Gemini, Grok, DeepSeek — through OpenRouter with per-call cost tracking
(estimated at about $102 for all four splits). A Claude-only matrix runs on
Anthropic's own API as Message Batches: Opus 5.5 at low, medium, and high
effort and Sonnet 5.5 without thinking and at the same three levels; its
results are in "Phase 1" above (actual cost $4.83). Max effort for both
follows in phase 2. See [`ROADMAP_FA.md`](ROADMAP_FA.md),
`configs/openrouter_models.json`, and `configs/anthropic_models.json`. The
OpenRouter matrix has not been run yet.

### Limitations
- 30 items per track (now 29–30 after rejects) keeps bootstrap CIs at
  roughly ±5 to ±7 percentage points. Most rankings within the top eight
  are within noise.
- Open-weight model results from earlier in the repo
  (`results/legacy/qwen*.json`, `results/legacy/llama*.json`, etc.) were
  run against the v1 baseline (20 items, strict scoring) and are
  **not** comparable to this report. Re-running them on the v1.1
  post-review dataset is the next step (RunPod H100 work).
- The review pass was model-assisted; a strong reviewer (Sonnet 4.6 /
  Haiku 4.5) flagged issues and proposed fixes, and a human applied the
  decisions in bulk. Edge cases were inspected individually but the
  bulk of the changes are still essentially model-graded. A second
  human pass would tighten further.
