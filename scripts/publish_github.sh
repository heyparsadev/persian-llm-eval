#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

REPO_NAME="${1:-persian-llm-eval}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is not installed or not available."
  echo "Install/login to gh, then run: scripts/publish_github.sh $REPO_NAME"
  exit 1
fi

if [ ! -d .git ]; then
  git init
fi

git add .
git commit -m "Initial Persian LLM Eval benchmark" || true
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
