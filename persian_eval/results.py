"""Result schema helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ResultError(ValueError):
    """Raised when a result artifact does not match the v1 schema."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def validate_result(data: dict[str, Any]) -> None:
    required = ["model_id", "model_type", "revision", "backend", "task_scores", "overall_score", "run_config", "timestamp"]
    missing = [key for key in required if key not in data]
    if missing:
        raise ResultError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(data["model_id"], str) or not data["model_id"]:
        raise ResultError("model_id must be a non-empty string")
    if data["model_type"] not in {"open-weight", "open-source", "api", "mock", "other"}:
        raise ResultError("model_type must be open-weight, open-source, api, mock, or other")
    if not isinstance(data["backend"], str) or not data["backend"]:
        raise ResultError("backend must be a non-empty string")
    if not isinstance(data["task_scores"], dict) or not data["task_scores"]:
        raise ResultError("task_scores must be a non-empty object")
    if not isinstance(data["overall_score"], (int, float)):
        raise ResultError("overall_score must be numeric")
    if not isinstance(data["run_config"], dict):
        raise ResultError("run_config must be an object")
    for track, score_data in data["task_scores"].items():
        if not isinstance(score_data, dict):
            raise ResultError(f"task_scores.{track} must be an object")
        if "score" not in score_data or "n" not in score_data:
            raise ResultError(f"task_scores.{track} requires score and n")
        if not isinstance(score_data["score"], (int, float)):
            raise ResultError(f"task_scores.{track}.score must be numeric")
        if not isinstance(score_data["n"], int) or score_data["n"] < 0:
            raise ResultError(f"task_scores.{track}.n must be a non-negative integer")


def load_result(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    validate_result(data)
    return data


def write_result(path: str | Path, data: dict[str, Any]) -> None:
    validate_result(data)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
