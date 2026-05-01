#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m persian_eval.cli leaderboard build results/*.json --output leaderboard/leaderboard.json --csv leaderboard/leaderboard.csv
python3 scripts/build_static_leaderboard.py
python3 -m persian_eval.cli leaderboard build results/*.json --output spaces/leaderboard/leaderboard.json --csv spaces/leaderboard/leaderboard.csv
