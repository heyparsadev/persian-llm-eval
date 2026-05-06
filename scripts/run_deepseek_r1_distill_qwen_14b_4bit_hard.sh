#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m persian_eval.cli run \
  --model deepseek-ai/DeepSeek-R1-Distill-Qwen-14B \
  --backend hf \
  --model-type open-weight \
  --data data/persian_eval_v1.hard.jsonl \
  --max-new-tokens 64 \
  --quantization 4bit \
  --dtype bfloat16 \
  --output results/deepseek_r1_distill_qwen_14b_4bit_hard.json

python3 -m persian_eval.cli validate results/deepseek_r1_distill_qwen_14b_4bit_hard.json
scripts/build_leaderboard.sh
