#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mkdir -p hf/dataset
cp data/persian_eval_v1.dev.jsonl hf/dataset/persian_eval_v1.dev.jsonl
cp data/persian_eval_v1.public_eval.jsonl hf/dataset/persian_eval_v1.public_eval.jsonl
cp data/external_sources.yml hf/dataset/external_sources.yml

echo "Prepared hf/dataset for upload to Hugging Face Datasets."
