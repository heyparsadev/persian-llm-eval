"""Evaluation runner."""

from __future__ import annotations

import json
import sys
import threading
from collections import Counter, defaultdict
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

from .backends import APIError, BaseBackend
from .dataset import DatasetRecord, load_records
from .results import utc_now
from .scoring import score_record


def run_records(
    records: list[DatasetRecord],
    *,
    backend: BaseBackend,
    model_id: str,
    model_type: str,
    revision: str | None,
    run_config: dict[str, Any],
    include_samples: bool = True,
    concurrency: int = 1,
    checkpoint_path: str | Path | None = None,
    resume: bool = False,
    max_item_errors: int = 0,
) -> dict[str, Any]:
    """Generate, score, and aggregate predictions for ``records``.

    With ``checkpoint_path`` every finished generation is appended to a JSONL
    checkpoint as soon as it returns, so an interrupted API run can continue
    with ``resume=True`` instead of paying for the same calls again. The
    caller deletes the checkpoint once the final result is written.

    ``max_item_errors`` lets up to that many items whose API call failed
    (for example a provider refusing one prompt) score 0 with the error kept
    in the sample's ``meta``, instead of aborting the run. Authentication and
    credit errors always abort. Failed items are retried on ``resume``.
    """

    if concurrency < 1:
        raise ValueError("concurrency must be at least 1")
    done: dict[str, dict[str, Any]] = {}
    checkpoint = Path(checkpoint_path) if checkpoint_path else None
    if checkpoint is not None:
        # The header ties a checkpoint to one model and configuration, so a
        # resumed run can never mix predictions from two different setups.
        fingerprint = json.loads(
            json.dumps(
                {"model_id": model_id, "backend": backend.name, "run_config": run_config},
                ensure_ascii=False,
            )
        )
        if resume and checkpoint.exists():
            header, saved = read_checkpoint(checkpoint)
            if header is not None and header != fingerprint:
                raise ValueError(
                    f"{checkpoint} was written by a different model or configuration; "
                    "delete it or run without --resume"
                )
            wanted = {record.id for record in records}
            done = {key: value for key, value in saved.items() if key in wanted}
            if done:
                print(f"resuming: {len(done)} saved predictions", file=sys.stderr)
        else:
            checkpoint.parent.mkdir(parents=True, exist_ok=True)
            header_line = json.dumps({"checkpoint": fingerprint}, ensure_ascii=False)
            checkpoint.write_text(header_line + "\n", encoding="utf-8")

    pending = [record for record in records if record.id not in done]
    _generate_pending(
        pending,
        backend,
        done,
        checkpoint,
        concurrency,
        total=len(records),
        max_item_errors=max_item_errors,
    )

    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    samples: list[dict[str, Any]] = []
    metas: list[dict[str, Any]] = []
    for record in records:
        prediction = done[record.id]["prediction"]
        meta = done[record.id].get("meta") or {}
        metas.append(meta)
        score, details = score_record(record, prediction)
        totals[record.track] += score
        counts[record.track] += 1
        if include_samples:
            sample: dict[str, Any] = {
                "id": record.id,
                "track": record.track,
                "prediction": prediction,
                "score": score,
                "details": details,
            }
            if meta:
                sample["meta"] = meta
            samples.append(sample)

    task_scores = {
        track: {"score": totals[track] / counts[track], "n": counts[track]}
        for track in sorted(counts)
        if counts[track] > 0
    }
    overall_score = (
        sum(item["score"] for item in task_scores.values()) / len(task_scores)
        if task_scores
        else 0.0
    )

    result: dict[str, Any] = {
        "model_id": model_id,
        "model_type": model_type,
        "revision": revision,
        "backend": backend.name,
        "task_scores": task_scores,
        "overall_score": overall_score,
        "run_config": run_config,
        "timestamp": utc_now(),
    }
    usage = summarize_usage(metas, [done[record.id]["prediction"] for record in records])
    if usage:
        result["usage"] = usage
    if include_samples:
        result["samples"] = samples
    return result


def _generate_pending(
    pending: list[DatasetRecord],
    backend: BaseBackend,
    done: dict[str, dict[str, Any]],
    checkpoint: Path | None,
    concurrency: int,
    *,
    total: int,
    max_item_errors: int = 0,
) -> None:
    lock = threading.Lock()
    finished = len(done)
    item_errors = 0

    def generate(record: DatasetRecord) -> tuple[str, dict[str, Any]]:
        nonlocal item_errors
        try:
            return backend.generate_with_meta(record)
        except APIError as exc:
            if exc.status in {401, 402}:
                raise
            with lock:
                item_errors += 1
                if item_errors > max_item_errors:
                    raise
            print(f"item error {record.id}: {exc}", file=sys.stderr, flush=True)
            return "", {"error": str(exc)[:500]}

    def progress(position: int, record: DatasetRecord) -> None:
        print(f"[{position}/{total}] {record.id} ({record.track})", file=sys.stderr, flush=True)

    def record_result(record: DatasetRecord, prediction: str, meta: dict[str, Any]) -> None:
        nonlocal finished
        entry = {"prediction": prediction, "meta": meta}
        with lock:
            done[record.id] = entry
            finished += 1
            if checkpoint is not None:
                line = json.dumps({"id": record.id, **entry}, ensure_ascii=False)
                with checkpoint.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            if concurrency > 1:
                progress(finished, record)

    if concurrency == 1:
        for record in pending:
            progress(finished + 1, record)
            prediction, meta = generate(record)
            record_result(record, prediction, meta)
        return

    def work(record: DatasetRecord) -> None:
        prediction, meta = generate(record)
        record_result(record, prediction, meta)

    executor = ThreadPoolExecutor(max_workers=concurrency)
    try:
        futures = [executor.submit(work, record) for record in pending]
        finished_futures, _ = wait(futures, return_when=FIRST_EXCEPTION)
        for future in finished_futures:
            future.result()
    finally:
        # On failure, drop queued work; in-flight calls still land in the checkpoint.
        executor.shutdown(wait=True, cancel_futures=True)


def read_checkpoint(path: Path) -> tuple[dict[str, Any] | None, dict[str, dict[str, Any]]]:
    """Return the checkpoint's run fingerprint (if any) and its saved predictions."""

    header: dict[str, Any] | None = None
    entries: dict[str, dict[str, Any]] = {}
    if not path.exists():
        return header, entries
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # A torn final line from a killed process.
        if isinstance(row, dict) and isinstance(row.get("checkpoint"), dict):
            header = row["checkpoint"]
            continue
        if isinstance(row, dict) and isinstance(row.get("id"), str):
            if (row.get("meta") or {}).get("error"):
                continue  # Failed calls are retried on resume.
            entries[row["id"]] = {
                "prediction": str(row.get("prediction") or ""),
                "meta": row.get("meta") or {},
            }
    return header, entries


def summarize_usage(metas: list[dict[str, Any]], predictions: list[str]) -> dict[str, Any] | None:
    """Aggregate per-call metadata (tokens, cost, provider) into a result-level block."""

    if not any(metas):
        return None
    usage: dict[str, Any] = {"calls": len(metas)}
    for key in ("prompt_tokens", "completion_tokens", "reasoning_tokens"):
        values = [meta[key] for meta in metas if isinstance(meta.get(key), (int, float))]
        if values:
            usage[key] = int(sum(values))
    costs = [meta["cost_usd"] for meta in metas if isinstance(meta.get("cost_usd"), (int, float))]
    if costs:
        usage["cost_usd"] = round(sum(costs), 6)
    latencies = [
        meta["latency_s"] for meta in metas if isinstance(meta.get("latency_s"), (int, float))
    ]
    if latencies:
        usage["mean_latency_s"] = round(sum(latencies) / len(latencies), 3)
    usage["empty_predictions"] = sum(1 for prediction in predictions if not prediction.strip())
    usage["truncated"] = sum(1 for meta in metas if meta.get("finish_reason") == "length")
    usage["item_errors"] = sum(1 for meta in metas if meta.get("error"))
    for key, label in (("provider", "providers"), ("served_model", "served_models")):
        counter = Counter(str(meta[key]) for meta in metas if meta.get(key))
        if counter:
            usage[label] = dict(counter.most_common())
    return usage


def rescore_result(
    result: dict[str, Any], *, data_paths: list[str | Path] | None = None
) -> dict[str, Any]:
    """Re-apply current scoring rules to the saved predictions of a result file."""

    samples = result.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("result has no samples; cannot rescore")

    paths = data_paths or [
        str(default_dataset_path().parent / name)
        for name in (
            "persian_eval_v1.dev.jsonl",
            "persian_eval_v1.public_eval.jsonl",
            "persian_eval_v1.hard.jsonl",
            "persian_eval_v1.practical.jsonl",
            "persian_eval_v1.challenge.jsonl",
        )
    ]
    paths = [path for path in paths if Path(path).exists()]
    records = {record.id: record for record in load_records(paths)}

    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    new_samples: list[dict[str, Any]] = []
    dropped: list[str] = []
    for sample in samples:
        record = records.get(sample["id"])
        if record is None:
            # Item was removed from the dataset (e.g. rejected during review).
            # Drop it from the rescored result rather than aborting the pass.
            dropped.append(sample["id"])
            continue
        score, details = score_record(record, sample.get("prediction", ""))
        totals[record.track] += score
        counts[record.track] += 1
        new_sample = {
            "id": record.id,
            "track": record.track,
            "prediction": sample.get("prediction", ""),
            "score": score,
            "details": details,
        }
        if sample.get("meta"):
            new_sample["meta"] = sample["meta"]
        new_samples.append(new_sample)

    task_scores = {
        track: {"score": totals[track] / counts[track], "n": counts[track]}
        for track in sorted(counts)
        if counts[track] > 0
    }
    overall_score = (
        sum(item["score"] for item in task_scores.values()) / len(task_scores)
        if task_scores
        else 0.0
    )

    rescored = dict(result)
    rescored["task_scores"] = task_scores
    rescored["overall_score"] = overall_score
    rescored["samples"] = new_samples
    rescored["timestamp"] = utc_now()
    if dropped:
        rescored["dropped_samples"] = dropped
    return rescored


def default_dataset_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    candidate = root / "data" / "persian_eval_v1.public_eval.jsonl"
    if candidate.exists():
        return candidate
    cwd_candidate = Path.cwd() / "data" / "persian_eval_v1.public_eval.jsonl"
    return cwd_candidate
