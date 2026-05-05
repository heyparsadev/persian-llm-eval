#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m persian_eval.cli run \
  --model deepseek-ai/DeepSeek-R1-Distill-Llama-8B \
  --backend hf \
  --model-type open-weight \
  --data data/persian_eval_v1.hard.jsonl \
  --max-new-tokens 48 \
  --output results/deepseek_r1_distill_llama_8b_hard.json

python3 -m persian_eval.cli validate results/deepseek_r1_distill_llama_8b_hard.json
scripts/build_leaderboard.sh
