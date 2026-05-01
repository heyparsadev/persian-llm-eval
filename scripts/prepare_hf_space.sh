#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

scripts/build_leaderboard.sh

mkdir -p hf/space
cp spaces/leaderboard/app.py hf/space/app.py
cp spaces/leaderboard/requirements.txt hf/space/requirements.txt
cp spaces/leaderboard/README.md hf/space/README.md
cp spaces/leaderboard/leaderboard.json hf/space/leaderboard.json
cp spaces/leaderboard/leaderboard.csv hf/space/leaderboard.csv

echo "Prepared hf/space for upload to a Hugging Face Space."
