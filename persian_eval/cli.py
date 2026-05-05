"""Command-line interface for Persian LLM Eval."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backends import GenerationConfig, create_backend
from .dataset import DatasetError, duplicate_prompts, load_records
from .leaderboard import build_leaderboard, write_csv, write_leaderboard
from .results import ResultError, load_result, write_result
from .runner import default_dataset_path, run_records


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return run_command(args)
        if args.command == "validate":
            return validate_command(args)
        if args.command == "leaderboard":
            return leaderboard_command(args)
        if args.command == "leakage":
            return leakage_command(args)
    except (DatasetError, ResultError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="persian-eval")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a model on a Persian Eval JSONL dataset")
    run_parser.add_argument("--model", required=True, help="Model ID or API model name")
    run_parser.add_argument("--backend", default="mock", choices=["mock", "hf", "openai-compatible"])
    run_parser.add_argument("--model-type", default=None, choices=["open-weight", "open-source", "api", "mock", "other"])
    run_parser.add_argument("--revision", default=None)
    run_parser.add_argument("--tasks", default="all", help="all or comma-separated track names")
    run_parser.add_argument("--split", default=None)
    run_parser.add_argument("--data", nargs="+", default=[str(default_dataset_path())])
    run_parser.add_argument("--output", required=True)
    run_parser.add_argument("--max-new-tokens", type=int, default=96)
    run_parser.add_argument("--temperature", type=float, default=0.0)
    run_parser.add_argument("--base-url", default=None, help="OpenAI-compatible base URL")
    run_parser.add_argument("--dtype", default="bfloat16", choices=["auto", "bfloat16", "float16", "float32"])
    run_parser.add_argument("--quantization", default=None, choices=["4bit", "8bit"], help="Optional HF bitsandbytes quantization")
    run_parser.add_argument("--no-samples", action="store_true", help="Do not include sample-level predictions")

    validate_parser = subparsers.add_parser("validate", help="Validate result JSON or dataset JSONL")
    validate_parser.add_argument("paths", nargs="+")
    validate_parser.add_argument("--dataset", action="store_true")

    leakage_parser = subparsers.add_parser("leakage", help="Check duplicate prompts across JSONL datasets")
    leakage_parser.add_argument("paths", nargs="+")

    leaderboard_parser = subparsers.add_parser("leaderboard", help="Leaderboard operations")
    leaderboard_subparsers = leaderboard_parser.add_subparsers(dest="leaderboard_command", required=True)
    build = leaderboard_subparsers.add_parser("build", help="Build leaderboard artifacts from result JSON files")
    build.add_argument("results", nargs="+")
    build.add_argument("--output", default="leaderboard/leaderboard.json")
    build.add_argument("--csv", default=None)

    return parser


def run_command(args: argparse.Namespace) -> int:
    tasks = parse_tasks(args.tasks)
    records = load_records(args.data, split=args.split, tasks=tasks)
    if not records:
        raise DatasetError("no records matched the requested split/tasks")

    model_type = args.model_type or infer_model_type(args.backend)
    config = GenerationConfig(
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        base_url=args.base_url,
        dtype=args.dtype,
        quantization=args.quantization,
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
    }
    result = run_records(
        records,
        backend=backend,
        model_id=args.model,
        model_type=model_type,
        revision=args.revision,
        run_config=run_config,
        include_samples=not args.no_samples,
    )
    write_result(args.output, result)
    print(f"wrote {args.output} | overall={result['overall_score']:.4f} | records={len(records)}")
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
        f"wrote {args.output} | main={len(leaderboard['main'])} | reference={len(leaderboard['reference'])}"
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
    if backend == "openai-compatible":
        return "api"
    if backend == "mock":
        return "mock"
    return "open-weight"


if __name__ == "__main__":
    raise SystemExit(main())
