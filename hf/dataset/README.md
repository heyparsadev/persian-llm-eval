---
language:
  - fa
license: mit
task_categories:
  - question-answering
  - text-classification
  - text-generation
pretty_name: Persian LLM Eval v1
tags:
  - persian
  - farsi
  - llm-evaluation
  - benchmark
---

# Persian LLM Eval v1

This is a small public seed dataset for an Iranian Persian LLM benchmark.

It contains objective Persian evaluation items across:

- knowledge
- short QA
- reading comprehension
- instruction following
- Persian culture

The official leaderboard workflow may use a private hidden split. This public dataset is intended for development, smoke tests, and reproducible public examples.

## Schema

Each JSONL row contains:

- `id`
- `track`
- `prompt`
- `choices`
- `answer`
- `metadata`
- `source`
- `split`

## Usage

Use the companion runner:

```bash
persian-eval run --model smoke --backend mock --data persian_eval_v1.public_eval.jsonl --output results/smoke.json
```
