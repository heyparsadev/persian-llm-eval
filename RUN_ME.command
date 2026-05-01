#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "== Persian LLM Eval: local demo =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found. Please install Python 3 first."
  exit 1
fi

python3 -m unittest discover -s tests
python3 -m persian_eval.cli validate --dataset data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl
python3 -m persian_eval.cli leakage data/persian_eval_v1.dev.jsonl data/persian_eval_v1.public_eval.jsonl
python3 -m persian_eval.cli run --model smoke --backend mock --data data/persian_eval_v1.dev.jsonl --output results/smoke.json
python3 -m persian_eval.cli run --model smoke-public --backend mock --data data/persian_eval_v1.public_eval.jsonl --output results/smoke_public.json
python3 -m persian_eval.cli leaderboard build results/smoke.json results/smoke_public.json --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
python3 scripts/build_static_leaderboard.py

echo
echo "Done."
echo "Leaderboard JSON: leaderboard/leaderboard.json"
echo "Leaderboard CSV: leaderboard/leaderboard.csv"
echo "Leaderboard HTML: leaderboard/index.html"
echo
echo "You can close this window."
