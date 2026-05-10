"""Leaderboard artifact generation."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from .results import load_result, utc_now

# Bootstrap defaults. Iterations are intentionally modest so leaderboard
# generation stays sub-second for typical run counts.
DEFAULT_BOOTSTRAP_ITERATIONS = 1000
DEFAULT_BOOTSTRAP_CONFIDENCE = 0.95
DEFAULT_BOOTSTRAP_SEED = 1729


def build_leaderboard(
    result_paths: list[str | Path],
    *,
    bootstrap_iterations: int = DEFAULT_BOOTSTRAP_ITERATIONS,
    bootstrap_confidence: float = DEFAULT_BOOTSTRAP_CONFIDENCE,
    bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED,
) -> dict[str, Any]:
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
        ci = compute_bootstrap_ci(
            result,
            iterations=bootstrap_iterations,
            confidence=bootstrap_confidence,
            seed=bootstrap_seed,
        )
        if ci is not None:
            row["overall_score_ci_low"] = round(ci["low"], 6)
            row["overall_score_ci_high"] = round(ci["high"], 6)
            row["overall_score_ci_method"] = ci["method"]
            row["overall_score_ci_confidence"] = ci["confidence"]
            row["overall_score_ci_iterations"] = ci["iterations"]
        rows.append(row)

    rows.sort(key=lambda item: item["overall_score"], reverse=True)
    main = [
        row for row in rows if row["model_type"] != "api" and row["backend"] != "openai-compatible"
    ]
    reference = [
        row for row in rows if row["model_type"] == "api" or row["backend"] == "openai-compatible"
    ]
    return {"generated_at": utc_now(), "main": main, "reference": reference}


def compute_bootstrap_ci(
    result: dict[str, Any],
    *,
    iterations: int,
    confidence: float,
    seed: int,
) -> dict[str, Any] | None:
    """Return a non-parametric bootstrap CI on the macro-averaged overall score.

    Uses sample-level scores when present (preferred), and falls back to a
    track-level normal-approximation CI built from per-track means and
    sample counts. Returns None when neither path is available.
    """

    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must lie in (0, 1)")
    if iterations <= 0:
        raise ValueError("iterations must be positive")

    samples = result.get("samples")
    track_scores: dict[str, list[float]] = defaultdict(list)
    if isinstance(samples, list) and samples:
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            track = sample.get("track")
            score = sample.get("score")
            if isinstance(track, str) and isinstance(score, (int, float)):
                track_scores[track].append(float(score))

    alpha = (1.0 - confidence) / 2.0
    if track_scores and all(track_scores.values()):
        rng = random.Random(seed)
        track_arrays: dict[str, list[float]] = {
            track: list(scores) for track, scores in track_scores.items()
        }
        overalls: list[float] = []
        for _ in range(iterations):
            track_means: list[float] = []
            for scores in track_arrays.values():
                n = len(scores)
                resampled = (rng.choice(scores) for _ in range(n))
                total = 0.0
                for value in resampled:
                    total += value
                track_means.append(total / n)
            overalls.append(sum(track_means) / len(track_means))
        overalls.sort()
        low = overalls[max(0, math.floor(alpha * len(overalls)) - 1)]
        high = overalls[min(len(overalls) - 1, math.ceil((1 - alpha) * len(overalls)) - 1)]
        return {
            "low": low,
            "high": high,
            "method": "bootstrap_sample",
            "confidence": confidence,
            "iterations": iterations,
        }

    return _normal_approx_ci(result, alpha=alpha, confidence=confidence)


def _normal_approx_ci(
    result: dict[str, Any],
    *,
    alpha: float,
    confidence: float,
) -> dict[str, Any] | None:
    z = _z_for_alpha(alpha)
    task_scores = result.get("task_scores") or {}
    if not isinstance(task_scores, dict) or not task_scores:
        return None
    variances: list[float] = []
    for score_data in task_scores.values():
        if not isinstance(score_data, dict):
            return None
        score = score_data.get("score")
        n = score_data.get("n")
        if not isinstance(score, (int, float)) or not isinstance(n, int) or n <= 0:
            return None
        # Bernoulli-like variance for a per-track mean of 0/1 sample scores;
        # an upper bound for f1/instruction means in [0, 1].
        p = max(0.0, min(1.0, float(score)))
        variances.append(p * (1.0 - p) / n)
    if not variances:
        return None
    track_count = len(variances)
    overall_variance = sum(variances) / (track_count * track_count)
    if overall_variance <= 0:
        return None
    margin = z * math.sqrt(overall_variance)
    overall = float(result.get("overall_score", 0.0))
    return {
        "low": max(0.0, overall - margin),
        "high": min(1.0, overall + margin),
        "method": "normal_approx",
        "confidence": confidence,
        "iterations": 0,
    }


def _z_for_alpha(alpha: float) -> float:
    # Inverse standard normal CDF lookup for common confidence levels,
    # avoiding a SciPy dependency. Falls back to an Acklam-style
    # rational approximation for arbitrary alphas.
    table = {
        0.025: 1.959963984540054,  # 95%
        0.05: 1.6448536269514722,  # 90%
        0.005: 2.5758293035489,  # 99%
    }
    if alpha in table:
        return table[alpha]
    return _inverse_normal_cdf(1 - alpha)


def _inverse_normal_cdf(p: float) -> float:
    # Acklam's algorithm; accurate to ~1e-9 for p in (0, 1).
    if not 0.0 < p < 1.0:
        raise ValueError("p must lie in (0, 1)")
    a = [
        -3.969683028665376e1,
        2.209460984245205e2,
        -2.759285104469687e2,
        1.383577518672690e2,
        -3.066479806614716e1,
        2.506628277459239,
    ]
    b = [
        -5.447609879822406e1,
        1.615858368580409e2,
        -1.556989798598866e2,
        6.680131188771972e1,
        -1.328068155288572e1,
    ]
    c = [
        -7.784894002430293e-3,
        -3.223964580411365e-1,
        -2.400758277161838,
        -2.549732539343734,
        4.374664141464968,
        2.938163982698783,
    ]
    d = [
        7.784695709041462e-3,
        3.224671290700398e-1,
        2.445134137142996,
        3.754408661907416,
    ]
    plow = 0.02425
    phigh = 1 - plow
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
        )
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return ((((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q) / (
            ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1
        )
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
        (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1
    )


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
    fieldnames = (
        sorted({key for row in rows for key in row})
        if rows
        else ["table", "model_id", "overall_score"]
    )
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
