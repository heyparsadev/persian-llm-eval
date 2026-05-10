# Persian Eval — Dataset Contribution & Review Guide

This document defines the process for adding or revising items in
`data/persian_eval_v1.*.jsonl`. The goal is a benchmark that is hard to
contaminate, fair across models, and statistically meaningful per track.

If you are only running models, see [README.md](./README.md). This file is for
authors and reviewers of dataset items.

## 1. Schema

Every JSONL row must follow the v1 schema (see [README.md](./README.md) for
the full reference). Authors should also populate the optional `metadata.review`
block:

```json
{
  "id": "peval-public-knowledge-005",
  "track": "knowledge",
  "prompt": "...",
  "choices": ["...", "...", "...", "..."],
  "answer": "...",
  "metadata": {
    "scoring": "mcq",
    "answer_index": 2,
    "category": "geography",
    "review": {
      "author": "alias-or-handle",
      "reviewers": ["alias-or-handle"],
      "status": "pending_review",
      "rubric": {
        "clarity": 5,
        "ambiguity": 1,
        "cultural_fit": 5,
        "leakage_risk": 1,
        "difficulty": 3
      },
      "notes": "Optional free-text rationale."
    }
  },
  "source": "curated:v1",
  "split": "public_eval"
}
```

`status` is one of `pending_review`, `accepted`, `revise`, `rejected`. The
automated validator does not require `metadata.review` (existing v1 items pre-date
it), but new items added in v1.1+ should always carry it.

## 2. Per-track guidance

### `knowledge` — closed-book factual MCQ

- 4 choices, 1 correct. Distractors plausible but unambiguously wrong.
- Topics: geography, calendar/dates, science, basic technology, history.
- Avoid time-sensitive facts unless the prompt anchors a date
  (e.g., "تا سال ۱۴۰۰" / "according to the 2020 reform").
- Vary the correct-answer position across items (no single position should
  exceed ~35% of correct answers in a track).

### `short_qa` — short open-ended factual

- One short canonical answer plus 1–3 acceptable surface variants in
  `answer` (list of strings).
- Avoid items where multiple legitimate answers exist that you have not
  enumerated. Add variants for spacing, ZWNJ, and Arabic↔Persian letter
  alternates only if they survive normalization (most do not need to be
  enumerated thanks to `normalize_persian`).

### `reading` — short comprehension

- Passage of 2–5 sentences embedded in the prompt with the lead-in
  "متن را بخوان و پاسخ کوتاه بده:".
- Question must be answerable from the passage alone.
- Use `f1` scoring; populate `answer` with 2–4 paraphrases of the same
  short answer.
- Passages must be original; do not paste public Wikipedia or news text.

### `instruction` — constraint-controlled writing

- Use `instruction` scoring. The answer object lists constraints:
  `required_keywords`, `forbidden`, `min_words`, `max_words`,
  `required_prefix`, `required_suffix`.
- Keep at least 2 and at most 5 active constraints per item, otherwise
  the item becomes either trivial or impossible.
- Prefer constraints that test format and structure (prefix, length,
  forbidden punctuation), not opinions.

### `culture` — Iranian cultural literacy

- MCQ, 4 choices. Cover idioms, etiquette, taarof, calendar customs,
  classical literature references, music, and food.
- Distractors should reflect plausible misreadings, not random topics.
- Avoid items that depend on a regional sub-culture without naming it.

### `hard_*` mirrors above with raised difficulty

- `hard_reasoning`: multi-step deduction, ordering, modus tollens,
  consistency, conditional reasoning. Use MCQ with 4 distractors.
- `hard_math`: 1–3 step word problems. Mix of percentage, mean, weighted
  averages, probability, geometry, simple algebra. Use `exact` scoring
  with both Persian and Latin digit variants in `answer`.
- `hard_reading`: causal, decision, confounding, UX, or policy passages
  that require an inference (not a copy-paste lookup).
- `hard_instruction`: 4–6 active constraints; include at least one
  forbidden token and one structural requirement.
- `hard_culture`: idioms, taarof register, code-switched phrasing,
  politeness markers, classical references.

## 3. Quality rubric (1–5 each, lower is better for risk axes)

| Axis           | 5 means                                                    |
|----------------|------------------------------------------------------------|
| `clarity`      | A literate native speaker reads it once and is sure.       |
| `ambiguity`    | Multiple defensible answers exist (BAD — aim for 1).       |
| `cultural_fit` | Item is meaningful in modern Iranian Persian context.      |
| `leakage_risk` | Phrasing is verbatim from a public source (BAD — aim 1).   |
| `difficulty`   | 1=easy, 3=baseline, 5=requires careful multi-step thought. |

For `public_eval`, target `difficulty` ∈ {2,3,4}. For `hard`, target
`difficulty` ∈ {3,4,5}. Acceptance gate: `clarity ≥ 4`, `ambiguity ≤ 2`,
`cultural_fit ≥ 4`, `leakage_risk ≤ 2`.

## 4. Authoring checklist

Before opening a PR, the author must verify:

- [ ] `id` follows `peval-{split}-{track}-{NNN}` and is unique.
- [ ] Persian text uses Persian (not Arabic) `ی` and `ک`. Do not paste
  text that contains `ي`, `ك`, `ة` outside intentional cases.
- [ ] No final answer or any choice text appears verbatim in the prompt.
- [ ] Numbers in MCQ choices (when used) are written consistently
  (all Persian digits, all Latin digits, or both clearly distinguished).
- [ ] For `mcq` items, the correct option is paraphrased in `answer`
  to match exactly one of `choices`.
- [ ] For `instruction` items, the constraints are mutually satisfiable
  (try writing a compliant 2-line answer yourself).
- [ ] For `reading`, the passage was written from scratch.
- [ ] `metadata.review.status` is set to `pending_review`.

## 5. Reviewer checklist

A reviewer accepts an item only when:

- The author checklist is satisfied.
- The reviewer can independently produce the same answer without ambiguity.
- The rubric scores satisfy the acceptance gate above.
- A web search for the prompt's first 8–10 distinctive words returns
  no near-duplicate page (basic leakage check).

When accepting, set `metadata.review.status` to `accepted` and add your
handle to `metadata.review.reviewers`.

## 6. Automated validator

`scripts/validate_dataset.py` runs in CI on every push. It enforces
mechanical quality rules that do not require human judgment:

- Schema and `id` uniqueness.
- ID convention `peval-{split}-{track}-{NNN}`.
- Track ↔ split consistency (no `hard_*` track in `public_eval`, no
  `public_eval` track in `hard`).
- No verbatim `answer` text inside the `prompt`.
- No verbatim `choice` text inside the `prompt` (except the lead-in).
- Per-track minimum count (default ≥ 20 in `public_eval` and `hard`).
- For `mcq`: 3–5 choices, choices unique after normalization, exactly
  one matches the canonical answer.
- For `instruction`: at least one active constraint and `min_words` ≤
  `max_words` when both present.
- Correct-answer position skew per track stays under 50%.
- Minimum prompt length per track (so reading passages are not stubs).

Run locally with:

```bash
python scripts/validate_dataset.py data/persian_eval_v1.*.jsonl
```

## 7. Adding to the hidden split

Hidden items follow the same schema and review process but live outside
this repository. Never PR hidden split items. Hidden items must be
authored only by reviewers with a clean public split history (no items
they authored have been rejected in the last 60 days). The hidden split
should be drawn from the same category mix as `hard` to keep the
public/hidden gap measurable.
