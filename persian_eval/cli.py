"""Command-line interface for Persian LLM Eval."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backends import GenerationConfig, create_backend
from .dataset import DatasetError, duplicate_prompts, load_records
from .leaderboard import build_leaderboard, write_csv, write_leaderboard
from .results import ResultError, load_result, write_result
from .runner import (
    BatchPending,
    default_dataset_path,
    rescore_result,
    run_records,
    spread_sample,
)

COMMANDS = {
    "run": "run_command",
    "validate": "validate_command",
    "leaderboard": "leaderboard_command",
    "leakage": "leakage_command",
    "rescore": "rescore_command",
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = globals().get(COMMANDS.get(args.command, ""))
    if handler is None:
        return 0
    try:
        return handler(args)
    except (DatasetError, ResultError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="persian-eval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a model on a Persian Eval JSONL dataset")
    run_parser.add_argument("--model", required=True, help="Model ID or API model name")
    run_parser.add_argument(
        "--backend",
        default="mock",
        choices=["mock", "hf", "openai-compatible", "openai-responses", "anthropic", "openrouter"],
    )
    run_parser.add_argument(
        "--model-type", default=None, choices=["open-weight", "open-source", "api", "mock", "other"]
    )
    run_parser.add_argument("--revision", default=None)
    run_parser.add_argument("--tasks", default="all", help="all or comma-separated track names")
    run_parser.add_argument("--split", default=None)
    run_parser.add_argument("--data", nargs="+", default=[str(default_dataset_path())])
    run_parser.add_argument("--output", required=True)
    run_parser.add_argument("--max-new-tokens", type=int, default=96)
    run_parser.add_argument("--temperature", type=float, default=0.0)
    run_parser.add_argument("--base-url", default=None, help="OpenAI-compatible base URL")
    run_parser.add_argument(
        "--reasoning-effort",
        default=None,
        choices=["none", "minimal", "low", "medium", "high", "xhigh", "max"],
        help="Optional reasoning/effort level for reasoning models",
    )
    run_parser.add_argument(
        "--thinking",
        default=None,
        choices=["adaptive", "enabled", "disabled"],
        help="Optional Anthropic thinking mode",
    )
    run_parser.add_argument(
        "--thinking-budget-tokens",
        type=int,
        default=None,
        help="Optional Anthropic manual thinking token budget",
    )
    run_parser.add_argument(
        "--dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"]
    )
    run_parser.add_argument(
        "--quantization",
        default=None,
        choices=["4bit", "8bit"],
        help="Optional HF bitsandbytes quantization",
    )
    run_parser.add_argument(
        "--no-samples", action="store_true", help="Do not include sample-level predictions"
    )
    run_parser.add_argument(
        "--provider",
        default=None,
        help="OpenRouter: comma-separated provider order to pin, e.g. 'anthropic,google-vertex'",
    )
    run_parser.add_argument(
        "--no-fallbacks",
        action="store_true",
        help="OpenRouter: fail instead of routing outside --provider",
    )
    run_parser.add_argument(
        "--data-collection",
        default=None,
        choices=["allow", "deny"],
        help="OpenRouter: 'deny' only routes to providers that do not store/train on prompts",
    )
    run_parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Parallel API requests (API backends only; results keep dataset order)",
    )
    run_parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue an interrupted run from <output>.partial.jsonl instead of starting over",
    )
    run_parser.add_argument(
        "--max-item-errors",
        type=int,
        default=0,
        help="Let up to N items whose API call keeps failing score 0 instead of aborting",
    )
    run_parser.add_argument(
        "--batch",
        action="store_true",
        help="anthropic: send the items as one Message Batch at half price "
        "(most finish within an hour, at most 24h); the batch id is kept in the checkpoint",
    )
    run_parser.add_argument(
        "--no-wait",
        action="store_true",
        help="With --batch: submit the batch, or check it, and exit if it has not ended; "
        "rerun with --resume to collect the results",
    )
    run_parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="Pilot run: only N items, spread evenly over the selected data",
    )

    validate_parser = subparsers.add_parser(
        "validate", help="Validate result JSON or dataset JSONL"
    )
    validate_parser.add_argument("paths", nargs="+")
    validate_parser.add_argument("--dataset", action="store_true")

    leakage_parser = subparsers.add_parser(
        "leakage", help="Check duplicate prompts across JSONL datasets"
    )
    leakage_parser.add_argument("paths", nargs="+")

    rescore_parser = subparsers.add_parser(
        "rescore",
        help="Re-apply current scoring to a result file's saved sample predictions",
    )
    rescore_parser.add_argument("input", help="Path to existing result JSON")
    rescore_parser.add_argument("--output", required=True, help="Path to write rescored result")
    rescore_parser.add_argument(
        "--data",
        nargs="+",
        default=None,
        help="Dataset JSONL files (defaults to every persian_eval_v1.*.jsonl split in data/)",
    )

    leaderboard_parser = subparsers.add_parser("leaderboard", help="Leaderboard operations")
    leaderboard_subparsers = leaderboard_parser.add_subparsers(
        dest="leaderboard_command", required=True
    )
    build = leaderboard_subparsers.add_parser(
        "build", help="Build leaderboard artifacts from result JSON files"
    )
    build.add_argument("results", nargs="+")
    build.add_argument("--output", default="leaderboard/leaderboard.json")
    build.add_argument("--csv", default=None)

    return parser


def run_command(args: argparse.Namespace) -> int:
    tasks = parse_tasks(args.tasks)
    records = load_records(args.data, split=args.split, tasks=tasks)
    if not records:
        raise DatasetError("no records matched the requested split/tasks")
    if args.max_items is not None:
        if args.max_items < 1:
            raise ValueError("--max-items must be at least 1")
        records = spread_sample(records, args.max_items)

    if args.concurrency > 1 and args.backend == "hf":
        raise ValueError("--concurrency > 1 is only supported for API backends")
    if args.batch and args.backend != "anthropic":
        raise ValueError("--batch is only supported for the anthropic backend")
    if args.no_wait and not args.batch:
        raise ValueError("--no-wait only applies to --batch")
    model_type = args.model_type or infer_model_type(args.backend)
    provider_order = [item.strip() for item in (args.provider or "").split(",") if item.strip()]
    config = GenerationConfig(
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        base_url=args.base_url,
        dtype=args.dtype,
        quantization=args.quantization,
        reasoning_effort=args.reasoning_effort,
        thinking_type=args.thinking,
        thinking_budget_tokens=args.thinking_budget_tokens,
        provider_order=provider_order or None,
        allow_fallbacks=not args.no_fallbacks,
        data_collection=args.data_collection,
    )
    backend = create_backend(args.backend, args.model, revision=args.revision, config=config)
    run_config = {
        "data": [str(Path(path)) for path in args.data],
        "tasks": "all" if tasks is None else sorted(tasks),
        "split": args.split,
        "max_new_tokens": args.max_new_tokens,
        "temperature": args.temperature,
        "dtype": args.dtype,
        "quantization": args.quantization,
        "reasoning_effort": args.reasoning_effort,
        "thinking": args.thinking,
        "thinking_budget_tokens": args.thinking_budget_tokens,
    }
    if args.backend == "openrouter":
        run_config["provider_order"] = provider_order or None
        run_config["allow_fallbacks"] = not args.no_fallbacks
        run_config["data_collection"] = args.data_collection
    if args.batch:
        run_config["batch"] = True
    if args.max_items is not None:
        run_config["max_items"] = args.max_items
    checkpoint = Path(f"{args.output}.partial.jsonl")
    try:
        result = run_records(
            records,
            backend=backend,
            model_id=args.model,
            model_type=model_type,
            revision=args.revision,
            run_config=run_config,
            include_samples=not args.no_samples,
            concurrency=args.concurrency,
            checkpoint_path=checkpoint,
            resume=args.resume,
            max_item_errors=args.max_item_errors,
            batch=args.batch,
            wait_for_batch=not args.no_wait,
        )
    except BatchPending as pending:
        counts = ", ".join(f"{value} {key}" for key, value in pending.counts.items())
        print(
            f"batch {pending.batch_id} is still running ({counts}); "
            "rerun the same command with --resume to collect it"
        )
        return 0
    write_result(args.output, result)
    checkpoint.unlink(missing_ok=True)
    summary = (
        f"wrote {args.output} | overall={result['overall_score']:.4f} | records={len(records)}"
    )
    cost = result.get("usage", {}).get("cost_usd")
    if cost is not None:
        summary += f" | cost=${cost:.4f}"
    print(summary)
    return 0


def validate_command(args: argparse.Namespace) -> int:
    if args.dataset:
        records = load_records(args.paths)
        duplicates = duplicate_prompts(records)
        print(f"dataset ok | records={len(records)} | duplicate_prompts={len(duplicates)}")
        return 0
    for path in args.paths:
        load_result(path)
        print(f"result ok | {path}")
    return 0


def leaderboard_command(args: argparse.Namespace) -> int:
    if args.leaderboard_command != "build":
        raise ValueError(f"unsupported leaderboard command: {args.leaderboard_command}")
    leaderboard = build_leaderboard(args.results)
    write_leaderboard(args.output, leaderboard)
    if args.csv:
        write_csv(args.csv, leaderboard)
    print(
        f"wrote {args.output} | main={len(leaderboard['main'])} | "
        f"reference={len(leaderboard['reference'])}"
    )
    return 0


def rescore_command(args: argparse.Namespace) -> int:
    original = load_result(args.input)
    rescored = rescore_result(original, data_paths=args.data)
    write_result(args.output, rescored)
    print(
        f"rescored {args.input} -> {args.output} | "
        f"overall {original['overall_score']:.4f} -> {rescored['overall_score']:.4f}"
    )
    return 0


def leakage_command(args: argparse.Namespace) -> int:
    records = load_records(args.paths)
    duplicates = duplicate_prompts(records)
    if duplicates:
        for first, second in duplicates:
            print(f"duplicate_prompt: {first} == {second}")
        return 1
    print(f"leakage check ok | records={len(records)} | duplicate_prompts=0")
    return 0


def parse_tasks(value: str) -> set[str] | None:
    if value == "all":
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def infer_model_type(backend: str) -> str:
    if backend in {"openai-compatible", "openai-responses", "anthropic", "openrouter"}:
        return "api"
    if backend == "mock":
        return "mock"
    return "open-weight"


if __name__ == "__main__":
    raise SystemExit(main())
