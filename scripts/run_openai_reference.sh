#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

MODEL_ID="${1:-gpt-4.1-mini}"
OUTPUT_SAFE_NAME="$(echo "$MODEL_ID" | tr '/:' '__')"

if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is not set."
  echo "Set it first, then run: scripts/run_openai_reference.sh $MODEL_ID"
  exit 1
fi

python3 -m persian_eval.cli run \
  --model "$MODEL_ID" \
  --backend openai-compatible \
  --model-type api \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output "results/${OUTPUT_SAFE_NAME}.json"

python3 -m persian_eval.cli validate "results/${OUTPUT_SAFE_NAME}.json"
