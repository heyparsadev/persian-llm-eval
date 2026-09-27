#!/usr/bin/env python3
"""Run the OpenRouter model matrix (configs/openrouter_models.json) over the benchmark splits.

One OPENROUTER_API_KEY covers every model. For each enabled model and split the
script calls `persian-eval run --backend openrouter` and writes
results/<label>.<split>.json. Existing result files are skipped (use --force to
redo them), and an interrupted run resumes from its .partial.jsonl checkpoint.

Before spending anything it checks every slug against OpenRouter's public model
catalogue and prints per-million-token prices; unknown slugs are skipped.

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python scripts/run_openrouter_matrix.py --dry-run            # show the plan
    python scripts/run_openrouter_matrix.py                      # run everything
    python scripts/run_openrouter_matrix.py --only opus,gpt-6 --splits practical
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from persian_eval.cli import main as persian_eval  # noqa: E402

DEFAULT_CONFIG = ROOT / "configs" / "openrouter_models.json"


def load_config(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    defaults = config.get("defaults", {})
    models = []
    for entry in config["models"]:
        merged = {**defaults, **entry}
        if merged.get("enabled", True):
            models.append(merged)
    return defaults, models


def fetch_catalogue() -> dict[str, dict[str, Any]] | None:
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: could not fetch the OpenRouter catalogue ({exc})", file=sys.stderr)
        return None
    return {item["id"]: item for item in data.get("data", []) if isinstance(item, dict)}


def per_million(price: Any) -> str:
    try:
        return f"${float(price) * 1_000_000:.2f}"
    except (TypeError, ValueError):
        return "?"


def build_command(model: dict[str, Any], split: str, output: Path) -> list[str]:
    command = [
        "run",
        "--model",
        model["slug"],
        "--backend",
        "openrouter",
        "--model-type",
        model.get("model_type", "api"),
        "--data",
        f"data/persian_eval_v1.{split}.jsonl",
        "--output",
        str(output),
        "--max-new-tokens",
        str(model.get("max_new_tokens", 1024)),
        "--temperature",
        str(model.get("temperature", 0.0)),
        "--concurrency",
        str(model.get("concurrency", 4)),
        "--max-item-errors",
        str(model.get("max_item_errors", 0)),
        "--resume",
    ]
    if model.get("reasoning_effort"):
        command += ["--reasoning-effort", model["reasoning_effort"]]
    if model.get("thinking_budget_tokens"):
        command += ["--thinking-budget-tokens", str(model["thinking_budget_tokens"])]
    if model.get("provider"):
        command += ["--provider", model["provider"]]
    if model.get("data_collection"):
        command += ["--data-collection", model["data_collection"]]
    return command


def summarize(paths: list[Path]) -> None:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        usage = result.get("usage", {})
        rows.append(
            (
                path.stem,
                result["overall_score"],
                usage.get("cost_usd"),
                usage.get("empty_predictions", 0),
                usage.get("truncated", 0),
                usage.get("item_errors", 0),
            )
        )
    if not rows:
        return
    print("\n| run | overall | cost (USD) | empty | truncated | errors |")
    print("|---|:---:|:---:|:---:|:---:|:---:|")
    for name, overall, cost, empty, truncated, errors in sorted(rows, key=lambda row: -row[1]):
        cost_text = f"{cost:.3f}" if isinstance(cost, (int, float)) else "-"
        print(f"| {name} | {overall:.4f} | {cost_text} | {empty} | {truncated} | {errors} |")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--only", default=None, help="comma-separated substrings of labels")
    parser.add_argument("--splits", default=None, help="comma-separated splits to run")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--force", action="store_true", help="re-run even if the result exists")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    parser.add_argument(
        "--skip-preflight", action="store_true", help="do not check slugs against the catalogue"
    )
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    results_dir = args.results_dir.resolve()
    # Dataset paths are recorded in each result's run_config; keep them repo-relative.
    os.chdir(ROOT)

    defaults, models = load_config(config_path)
    if args.only:
        needles = [item.strip() for item in args.only.split(",") if item.strip()]
        models = [model for model in models if any(needle in model["label"] for needle in needles)]
    splits = (
        [item.strip() for item in args.splits.split(",") if item.strip()]
        if args.splits
        else defaults.get("splits", ["practical"])
    )
    if not models:
        print("no models selected", file=sys.stderr)
        return 1

    catalogue = None if args.skip_preflight else fetch_catalogue()
    runnable = []
    print("| label | slug | effort | $/M in | $/M out |")
    print("|---|---|---|---:|---:|")
    for model in models:
        entry = catalogue.get(model["slug"]) if catalogue else None
        pricing = (entry or {}).get("pricing", {})
        effort = model.get("reasoning_effort") or "default"
        prices = f"{per_million(pricing.get('prompt'))} | {per_million(pricing.get('completion'))}"
        if catalogue is not None and entry is None:
            print(f"| {model['label']} | {model['slug']} | {effort} | not in catalogue | skipped |")
            continue
        print(f"| {model['label']} | {model['slug']} | {effort} | {prices} |")
        runnable.append(model)

    plan = [
        (model, split, results_dir / f"{model['label']}.{split}.json")
        for model in runnable
        for split in splits
    ]
    todo = [(model, split, path) for model, split, path in plan if args.force or not path.exists()]
    print(f"\n{len(todo)} run(s) to do, {len(plan) - len(todo)} already done")
    if args.dry_run:
        for model, split, path in todo:
            print("persian-eval " + " ".join(build_command(model, split, path)))
        return 0
    if todo and not os.getenv("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY is not set; export it and rerun.", file=sys.stderr)
        return 1

    failures = []
    for model, split, path in todo:
        print(f"\n=== {model['label']} / {split} ===", flush=True)
        code = persian_eval(build_command(model, split, path))
        if code != 0:
            failures.append(f"{model['label']}/{split}")
            print(f"failed: {model['label']}/{split} (rerun to resume)", file=sys.stderr)

    summarize([path for _, _, path in plan])
    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
