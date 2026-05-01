#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m persian_eval.cli run --model smoke --backend mock --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
python3 -m persian_eval.cli run --model smoke-public --backend mock --data data/persian_eval_v1.public_eval.jsonl --output results/smoke_public.json
python3 -m persian_eval.cli leaderboard build results/smoke.json results/smoke_public.json --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
python3 scripts/build_static_leaderboard.py
