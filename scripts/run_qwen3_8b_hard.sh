#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m persian_eval.cli run \
  --model Qwen/Qwen3-8B \
  --backend hf \
  --model-type open-weight \
  --data data/persian_eval_v1.hard.jsonl \
  --max-new-tokens 32 \
  --output results/qwen3_8b_hard.json

python3 -m persian_eval.cli validate results/qwen3_8b_hard.json
scripts/build_leaderboard.sh
