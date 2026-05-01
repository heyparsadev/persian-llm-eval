# Data

This directory contains a small curated v1 seed dataset:

- `persian_eval_v1.dev.jsonl`: smoke/dev examples.
- `persian_eval_v1.public_eval.jsonl`: public evaluation examples.
- `external_sources.yml`: references to compatible public Persian benchmarks that can be adapted into larger official splits.

The seed data is intentionally small. It proves the schema, runner, scoring, validation, and leaderboard path. A production leaderboard should expand the public and hidden splits with source attribution, license review, and duplicate/contamination checks.
