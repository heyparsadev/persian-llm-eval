#!/usr/bin/env python3
"""Run the OpenRouter model matrix (configs/openrouter_models.json) over the benchmark splits.

One OPENROUTER_API_KEY covers every model. For each enabled model and split the
script calls `persian-eval run --backend openrouter` and writes
results/<label>.<split>.json. Existing result files are skipped (use --force to
redo them), and an interrupted run resumes from its .partial.jsonl checkpoint.

Before spending anything it checks every slug against OpenRouter's public model
catalogue, prints per-million-token prices, skips unknown slugs, and estimates
the cost of the planned runs (--estimate prints only the estimate).

Usage:
    python scripts/run_openrouter_matrix.py --estimate           # cost estimate, no key needed
    export OPENROUTER_API_KEY=sk-or-...
    python scripts/run_openrouter_matrix.py --dry-run            # plan + estimate
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

from persian_eval.backends import SYSTEM_PROMPT, format_prompt  # noqa: E402
from persian_eval.cli import main as persian_eval  # noqa: E402
from persian_eval.dataset import load_records  # noqa: E402

DEFAULT_CONFIG = ROOT / "configs" / "openrouter_models.json"

# Persian characters per token, measured on this repo's prompts (Sep 2026) with
# the o200k tokenizer (GPT-4o/5 family) and the public legacy Claude tokenizer.
# The current Claude tokenizer is not public, so the Claude figure is a
# conservative bound. Other providers get a middle assumption.
CHARS_PER_TOKEN = {"openai/": 2.9, "anthropic/": 1.0}
DEFAULT_CHARS_PER_TOKEN = 2.0
# Assumed thinking tokens per item for these short tasks, by reasoning effort.
REASONING_TOKENS = {
    "none": 0,
    "minimal": 150,
    "low": 600,
    "medium": 1500,
    "high": 4000,
    "xhigh": 8000,
    "max": 16000,
}
# Visible answer length in characters for items without a reference response.
ANSWER_CHARS = {"mcq": 40, "exact": 40, "f1": 80, "instruction": 300, "json": 250}
VERBOSITY = 1.5  # real answers run longer than the minimal reference
MESSAGE_OVERHEAD_TOKENS = 15  # chat-format tokens per request


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


def split_profile(split: str) -> dict[str, float]:
    """Item count plus prompt and expected-answer characters for one split."""

    records = load_records([ROOT / "data" / f"persian_eval_v1.{split}.jsonl"])
    prompt_chars = sum(len(SYSTEM_PROMPT) + len(format_prompt(record)) for record in records)
    answer_chars = sum(
        len(str(record.metadata.get("reference_response") or ""))
        or ANSWER_CHARS.get(str(record.metadata.get("scoring")), 80)
        for record in records
    )
    return {
        "items": len(records),
        "prompt_chars": prompt_chars,
        "answer_chars": answer_chars * VERBOSITY,
    }


def chars_per_token(model: dict[str, Any]) -> float:
    if model.get("chars_per_token"):
        return float(model["chars_per_token"])
    for prefix, value in CHARS_PER_TOKEN.items():
        if model["slug"].startswith(prefix):
            return value
    return DEFAULT_CHARS_PER_TOKEN


def reasoning_tokens(model: dict[str, Any]) -> float:
    if model.get("thinking_budget_tokens"):
        return float(model["thinking_budget_tokens"]) / 2
    effort = model.get("reasoning_effort")
    if effort:
        return float(REASONING_TOKENS.get(effort, 1500))
    return float(model.get("assumed_reasoning_tokens", 0))


def estimate_cost(
    model: dict[str, Any],
    profile: dict[str, float],
    prices: tuple[float, float],
    *,
    reasoning_scale: float = 1.0,
) -> float:
    """USD for one model on one split: prompt, visible answer, and thinking tokens."""

    per_token = chars_per_token(model)
    input_tokens = profile["prompt_chars"] / per_token + MESSAGE_OVERHEAD_TOKENS * profile["items"]
    output_tokens = profile["answer_chars"] / per_token
    output_tokens += reasoning_tokens(model) * reasoning_scale * profile["items"]
    price_in, price_out = prices
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def model_prices(
    model: dict[str, Any],
    catalogue: dict[str, dict[str, Any]] | None,
    listed: dict[str, list[float]],
) -> tuple[float, float] | None:
    """Live catalogue prices per million tokens, else the prices listed in the config."""

    pricing = ((catalogue or {}).get(model["slug"]) or {}).get("pricing") or {}
    try:
        return float(pricing["prompt"]) * 1_000_000, float(pricing["completion"]) * 1_000_000
    except (KeyError, TypeError, ValueError):
        pass
    if model["slug"] in listed:
        price_in, price_out = listed[model["slug"]]
        return float(price_in), float(price_out)
    return None


def print_estimate(
    models: list[dict[str, Any]],
    splits: list[str],
    catalogue: dict[str, dict[str, Any]] | None,
    listed: dict[str, list[float]],
) -> float:
    profiles = {split: split_profile(split) for split in splits}
    header = " | ".join(f"{split} ({int(profiles[split]['items'])})" for split in splits)
    print(f"\n| label | chars/token | thinking tokens/item | $/M in / out | {header} | total |")
    print("|---|:---:|:---:|:---:|" + "---:|" * (len(splits) + 1))
    grand = low = high = 0.0
    for model in models:
        prices = model_prices(model, catalogue, listed)
        if prices is None:
            cells = " | ".join("?" for _ in splits)
            print(f"| {model['label']} | | | no price | {cells} | ? |")
            continue
        costs = [estimate_cost(model, profiles[split], prices) for split in splits]
        total = sum(costs)
        grand += total
        low += sum(estimate_cost(model, profiles[s], prices, reasoning_scale=0.5) for s in splits)
        high += sum(estimate_cost(model, profiles[s], prices, reasoning_scale=2.0) for s in splits)
        cells = " | ".join(f"${cost:.2f}" for cost in costs)
        print(
            f"| {model['label']} | {chars_per_token(model):.1f} | {reasoning_tokens(model):.0f} | "
            f"${prices[0]:g} / ${prices[1]:g} | {cells} | ${total:.2f} |"
        )
    print(
        f"\nEstimated total: ${grand:.2f} (${low:.2f}-${high:.2f} if thinking runs 0.5x-2x the "
        "assumed length). Actual cost is recorded per run in usage.cost_usd."
    )
    return grand


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


def preflight(
    models: list[dict[str, Any]], catalogue: dict[str, dict[str, Any]] | None
) -> list[dict[str, Any]]:
    """Print live prices per model; drop slugs missing from a reachable catalogue."""

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
    return runnable


def run_all(todo: list[tuple[dict[str, Any], str, Path]]) -> list[str]:
    failures = []
    for model, split, path in todo:
        print(f"\n=== {model['label']} / {split} ===", flush=True)
        code = persian_eval(build_command(model, split, path))
        if code != 0:
            failures.append(f"{model['label']}/{split}")
            print(f"failed: {model['label']}/{split} (rerun to resume)", file=sys.stderr)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--only", default=None, help="comma-separated substrings of labels")
    parser.add_argument("--splits", default=None, help="comma-separated splits to run")
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--force", action="store_true", help="re-run even if the result exists")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit")
    parser.add_argument(
        "--estimate", action="store_true", help="print the cost estimate and exit (no key needed)"
    )
    parser.add_argument(
        "--skip-preflight", action="store_true", help="do not check slugs against the catalogue"
    )
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    results_dir = args.results_dir.resolve()
    # Dataset paths are recorded in each result's run_config; keep them repo-relative.
    os.chdir(ROOT)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    listed_prices = config.get("prices_usd_per_million", {})
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
    runnable = preflight(models, catalogue)
    print_estimate(runnable, splits, catalogue, listed_prices)
    if args.estimate:
        return 0

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

    failures = run_all(todo)
    summarize([path for _, _, path in plan])
    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
