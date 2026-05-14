"""Evaluation runner."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from .backends import BaseBackend
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
) -> dict[str, Any]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    samples: list[dict[str, Any]] = []

    total_records = len(records)
    for index, record in enumerate(records, start=1):
        print(
            f"[{index}/{total_records}] {record.id} ({record.track})", file=sys.stderr, flush=True
        )
        prediction = backend.generate(record)
        score, details = score_record(record, prediction)
        totals[record.track] += score
        counts[record.track] += 1
        if include_samples:
            samples.append(
                {
                    "id": record.id,
                    "track": record.track,
                    "prediction": prediction,
                    "score": score,
                    "details": details,
                }
            )

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
    if include_samples:
        result["samples"] = samples
    return result


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
        )
    ]
    paths = [path for path in paths if Path(path).exists()]
    records = {record.id: record for record in load_records(paths)}

    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    new_samples: list[dict[str, Any]] = []
    for sample in samples:
        record = records.get(sample["id"])
        if record is None:
            raise ValueError(f"rescore: dataset record not found for {sample['id']}")
        score, details = score_record(record, sample.get("prediction", ""))
        totals[record.track] += score
        counts[record.track] += 1
        new_samples.append(
            {
                "id": record.id,
                "track": record.track,
                "prediction": sample.get("prediction", ""),
                "score": score,
                "details": details,
            }
        )

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
    return rescored


def default_dataset_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    candidate = root / "data" / "persian_eval_v1.public_eval.jsonl"
    if candidate.exists():
        return candidate
    cwd_candidate = Path.cwd() / "data" / "persian_eval_v1.public_eval.jsonl"
    return cwd_candidate
