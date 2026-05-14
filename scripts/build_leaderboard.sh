#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Glob only top-level results/, skipping results/legacy/.
shopt -s nullglob
RESULTS=(results/*.json)
shopt -u nullglob

python3 -m persian_eval.cli leaderboard build "${RESULTS[@]}" --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
python3 scripts/build_static_leaderboard.py
python3 -m persian_eval.cli leaderboard build "${RESULTS[@]}" --output spaces/leaderboard/leaderboard.json --csv spaces/leaderboard/leaderboard.csv
