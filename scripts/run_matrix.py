#!/usr/bin/env python3
"""Run a model matrix (configs/*_models.json) over the benchmark splits.

Each enabled config row is one model setting, and each run writes
results/<label>.<split>.json. The config's "backend" picks the route:
configs/openrouter_models.json sends every model through OpenRouter with one
OPENROUTER_API_KEY; configs/anthropic_models.json sends Claude models through
Anthropic's own API with ANTHROPIC_API_KEY. Existing result files are skipped
(use --force to redo them), and an interrupted run resumes from its
.partial.jsonl checkpoint.

OpenRouter slugs are checked against OpenRouter's public model catalogue
before anything is spent: unknown slugs are skipped and live prices shown.
Every run prints a cost estimate first (--estimate prints only that).

Rows with "batch": true (Anthropic only) go out as Message Batches at half
price. The script submits every batch first and then collects them, so the
whole matrix takes about as long as its slowest batch.

Usage:
    python scripts/run_matrix.py --estimate            # OpenRouter matrix cost, no key needed
    python scripts/run_matrix.py --config configs/anthropic_models.json --estimate
    export OPENROUTER_API_KEY=sk-or-...
    python scripts/run_matrix.py --dry-run             # plan + estimate
    python scripts/run_matrix.py                       # run everything
    python scripts/run_matrix.py --only opus,gpt-6 --splits practical
    python scripts/run_matrix.py --config configs/anthropic_models.json \\
        --splits challenge --max-items 20 --results-dir results/pilot   # cheap pilot
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
API_KEYS = {"openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}
BATCH_DISCOUNT = 0.5  # Message Batches API price relative to standard

# Persian characters per token, measured on this repo's prompts (Sep 2026) with
# the o200k tokenizer (GPT-4o/5 family) and the public legacy Claude tokenizer.
# The current Claude tokenizer is not public, so the Claude figure is an
# assumption; thinking tokens dominate, so a 30% error here moves a Claude row
# by under 8%. Other providers get a middle assumption.
CHARS_PER_TOKEN = {"openai/": 2.9, "anthropic/": 1.0, "claude-": 1.0}
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


def backend_of(model: dict[str, Any]) -> str:
    backend = str(model.get("backend", "openrouter"))
    if backend not in API_KEYS:
        raise ValueError(f"{model['label']}: backend must be one of {', '.join(API_KEYS)}")
    return backend


def fetch_catalogue() -> dict[str, dict[str, Any]] | None:
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base_url}/models", timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"warning: could not fetch the OpenRouter catalogue ({exc})", file=sys.stderr)
        return None
    return {item["id"]: item for item in data.get("data", []) if isinstance(item, dict)}


def split_profile(split: str, max_items: int | None = None) -> dict[str, float]:
    """Item count plus prompt and expected-answer characters for one split."""

    records = load_records([ROOT / "data" / f"persian_eval_v1.{split}.jsonl"])
    prompt_chars = sum(len(SYSTEM_PROMPT) + len(format_prompt(record)) for record in records)
    answer_chars = sum(
        len(str(record.metadata.get("reference_response") or ""))
        or ANSWER_CHARS.get(str(record.metadata.get("scoring")), 80)
        for record in records
    )
    share = min(1.0, max_items / len(records)) if max_items else 1.0
    return {
        "items": len(records) * share,
        "prompt_chars": prompt_chars * share,
        "answer_chars": answer_chars * VERBOSITY * share,
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
    cost = (input_tokens * price_in + output_tokens * price_out) / 1_000_000
    return cost * BATCH_DISCOUNT if model.get("batch") else cost


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
    max_items: int | None = None,
) -> float:
    profiles = {split: split_profile(split, max_items) for split in splits}
    header = " | ".join(f"{split} ({round(profiles[split]['items'])})" for split in splits)
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
    if any(model.get("batch") for model in models):
        print("\nRows with batch=true are priced at the Message Batches discount (50% off).")
    print(
        f"\nEstimated total: ${grand:.2f} (${low:.2f}-${high:.2f} if thinking runs 0.5x-2x the "
        "assumed length). Actual cost is recorded per run in usage.cost_usd."
    )
    return grand


def build_command(
    model: dict[str, Any], split: str, output: Path, max_items: int | None = None
) -> list[str]:
    command = [
        "run",
        "--model",
        model["slug"],
        "--backend",
        backend_of(model),
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
    if model.get("batch"):
        command.append("--batch")
    if max_items:
        command += ["--max-items", str(max_items)]
    return command


def summarize(paths: list[Path]) -> None:
    rows = []
    for path in paths:
        if not path.exists():
            continue
        result = json.loads(path.read_text(encoding="utf-8"))
        usage = result.get("usage", {})
        calls = usage.get("calls") or 0
        tokens_out = usage.get("completion_tokens")
        rows.append(
            (
                path.stem,
                result["overall_score"],
                usage.get("cost_usd"),
                round(tokens_out / calls) if calls and tokens_out else None,
                usage.get("empty_predictions", 0),
                usage.get("truncated", 0),
                usage.get("item_errors", 0),
            )
        )
    if not rows:
        return
    print("\n| run | overall | cost (USD) | output tokens/item | empty | truncated | errors |")
    print("|---|:---:|:---:|:---:|:---:|:---:|:---:|")
    for name, overall, cost, per_item, empty, truncated, errors in sorted(
        rows, key=lambda row: -row[1]
    ):
        cost_text = f"{cost:.3f}" if isinstance(cost, (int, float)) else "-"
        per_item_text = str(per_item) if per_item is not None else "-"
        print(
            f"| {name} | {overall:.4f} | {cost_text} | {per_item_text} | {empty} | "
            f"{truncated} | {errors} |"
        )


def preflight(
    models: list[dict[str, Any]],
    catalogue: dict[str, dict[str, Any]] | None,
    listed: dict[str, list[float]],
) -> list[dict[str, Any]]:
    """Print each row's prices; drop OpenRouter slugs missing from a reachable catalogue."""

    runnable = []
    print("| label | model | effort | $/M in | $/M out |")
    print("|---|---|---|---:|---:|")
    for model in models:
        effort = model.get("reasoning_effort") or "default"
        row = f"| {model['label']} | {model['slug']} | {effort} |"
        on_openrouter = backend_of(model) == "openrouter"
        if on_openrouter and catalogue is not None and model["slug"] not in catalogue:
            print(f"{row} not in catalogue | skipped |")
            continue
        prices = model_prices(model, catalogue, listed)
        print(f"{row} " + (f"${prices[0]:g} | ${prices[1]:g} |" if prices else "? | ? |"))
        runnable.append(model)
    return runnable


def run_all(
    todo: list[tuple[dict[str, Any], str, Path]], max_items: int | None = None
) -> list[str]:
    failures = []
    collect = []
    # Submit every batch first so they all process at once, then collect them.
    for model, split, path in todo:
        if not model.get("batch"):
            continue
        print(f"\n=== {model['label']} / {split}: submit batch ===", flush=True)
        if persian_eval([*build_command(model, split, path, max_items), "--no-wait"]) != 0:
            failures.append(f"{model['label']}/{split}")
        elif Path(f"{path}.partial.jsonl").exists():
            collect.append((model, split, path))  # Still running; else already collected.
    direct = [item for item in todo if not item[0].get("batch")]
    for model, split, path in direct + collect:
        print(f"\n=== {model['label']} / {split} ===", flush=True)
        code = persian_eval(build_command(model, split, path, max_items))
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
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="pilot: run N items per split, spread over its tracks (use another --results-dir)",
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

    on_openrouter = any(backend_of(model) == "openrouter" for model in models)
    catalogue = fetch_catalogue() if on_openrouter and not args.skip_preflight else None
    runnable = preflight(models, catalogue, listed_prices)
    print_estimate(runnable, splits, catalogue, listed_prices, args.max_items)
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
            print("persian-eval " + " ".join(build_command(model, split, path, args.max_items)))
        return 0
    needed = {API_KEYS[backend_of(model)] for model, _, _ in todo}
    missing = sorted(key for key in needed if not os.getenv(key))
    if missing:
        print(f"{', '.join(missing)} is not set; export it and rerun.", file=sys.stderr)
        return 1

    failures = run_all(todo, args.max_items)
    summarize([path for _, _, path in plan])
    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
