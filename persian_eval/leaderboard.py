"""Leaderboard artifact generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .results import load_result, utc_now


def build_leaderboard(result_paths: list[str | Path]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in result_paths:
        result = load_result(path)
        row = {
            "model_id": result["model_id"],
            "model_type": result["model_type"],
            "backend": result["backend"],
            "revision": result["revision"],
            "overall_score": round(float(result["overall_score"]), 6),
            "timestamp": result["timestamp"],
            "artifact": str(path),
        }
        for track, score_data in result["task_scores"].items():
            row[f"{track}_score"] = round(float(score_data["score"]), 6)
            row[f"{track}_n"] = int(score_data["n"])
        rows.append(row)

    rows.sort(key=lambda item: item["overall_score"], reverse=True)
    main = [row for row in rows if row["model_type"] != "api" and row["backend"] != "openai-compatible"]
    reference = [row for row in rows if row["model_type"] == "api" or row["backend"] == "openai-compatible"]
    return {"generated_at": utc_now(), "main": main, "reference": reference}


def write_leaderboard(path: str | Path, leaderboard: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(leaderboard, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_csv(path: str | Path, leaderboard: dict[str, Any]) -> None:
    rows = []
    for table_name in ("main", "reference"):
        for row in leaderboard.get(table_name, []):
            rows.append({"table": table_name, **row})

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["table", "model_id", "overall_score"]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
