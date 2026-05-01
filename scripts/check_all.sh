#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m unittest discover -s tests
python3 -m persian_eval.cli validate --dataset data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl
python3 -m persian_eval.cli leakage data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl
python3 -m py_compile spaces/leaderboard/app.py
