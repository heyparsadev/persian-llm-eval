"""Build benchmark visualisations from results/ JSONs.

Produces five PNG charts in docs/charts/:
  1. overall_hard.png      — headline bar chart with bootstrap CI
  2. track_heatmap.png     — model × track heatmap on hard split
  3. opus_thinking.png     — Opus 4.7 thinking-effort sweep
  4. public_vs_hard.png    — generalisation scatter plot
  5. top_models_tracks.png — top-5 models across hard tracks

Requires matplotlib (install via `pip install -e ".[viz]"`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
CHARTS = ROOT / "docs" / "charts"
LEADERBOARD = ROOT / "leaderboard" / "leaderboard.json"

HARD_TRACKS = [
    "hard_culture",
    "hard_instruction",
    "hard_knowledge",
    "hard_math",
    "hard_reading",
    "hard_reasoning",
    "hard_short_qa",
]

PUBLIC_TRACKS = [
    "culture",
    "instruction",
    "knowledge",
    "reading",
    "short_qa",
]

TRACK_DISPLAY = {
    "culture": "Culture",
    "instruction": "Instruction",
    "knowledge": "Knowledge",
    "reading": "Reading",
    "short_qa": "ShortQA",
    "hard_culture": "Culture",
    "hard_instruction": "Instruction",
    "hard_knowledge": "Knowledge",
    "hard_math": "Math",
    "hard_reading": "Reading",
    "hard_reasoning": "Reasoning",
    "hard_short_qa": "ShortQA",
}


def display_name(stem: str) -> str:
    """Map result-file stem to a short label for charts."""
    s = stem.replace(".hard", "").replace(".public_eval", "")
    mapping = {
        "claude-haiku-4-5": "Claude Haiku 4.5",
        "claude-sonnet-4-6": "Claude Sonnet 4.6",
        "claude-opus-4-7": "Claude Opus 4.7",
        "claude-opus-4-7-thinking": "Claude Opus 4.7 +T(low)",
        "claude-opus-4-7-thinking-medium": "Claude Opus 4.7 +T(med)",
        "claude-opus-4-7-thinking-high": "Claude Opus 4.7 +T(high)",
        "gpt-5-nano": "GPT-5 nano",
        "gpt-5-mini": "GPT-5 mini",
        "gpt-5": "GPT-5",
        "gpt-5-thinking-medium": "GPT-5 +T(med)",
        "gpt-5.5": "GPT-5.5",
        "gpt-5.5-thinking-medium": "GPT-5.5 +T(med)",
        "gpt-5.5-thinking-high": "GPT-5.5 +T(high)",
    }
    return mapping.get(s, s)


def family_color(label: str) -> str:
    """Return a matplotlib colour for a model family."""
    if "Claude" in label:
        if "Haiku" in label:
            return "#f5a572"
        if "Sonnet" in label:
            return "#e8804d"
        return "#c45a2c"  # Opus
    if "GPT" in label:
        if "nano" in label:
            return "#7fcdbb"
        if "mini" in label:
            return "#41b6c4"
        if "5.5" in label:
            return "#1d6f87"
        return "#2c7fb8"  # GPT-5
    return "#888888"


def load_result(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def load_leaderboard() -> dict[str, dict[str, Any]]:
    """Return artifact path -> leaderboard row, for CI lookup."""
    data = json.load(LEADERBOARD.open())
    out: dict[str, dict[str, Any]] = {}
    for row in data.get("main", []) + data.get("reference", []):
        out[row["artifact"]] = row
    return out


def chart1_overall_hard(leaderboard: dict[str, dict[str, Any]]) -> None:
    """Horizontal bar chart of overall hard scores with bootstrap CI."""
    rows = []
    for path in sorted(RESULTS.glob("*.hard.json")):
        r = load_result(path)
        artifact = f"results/{path.name}"
        lb = leaderboard.get(artifact, {})
        rows.append(
            {
                "label": display_name(path.stem),
                "score": r["overall_score"],
                "ci_low": lb.get("overall_score_ci_low", r["overall_score"]),
                "ci_high": lb.get("overall_score_ci_high", r["overall_score"]),
            }
        )
    rows.sort(key=lambda x: x["score"])

    labels = [r["label"] for r in rows]
    scores = np.array([r["score"] for r in rows])
    lo = np.array([r["ci_low"] for r in rows])
    hi = np.array([r["ci_high"] for r in rows])
    err = np.vstack([scores - lo, hi - scores])
    colors = [family_color(l) for l in labels]

    fig, ax = plt.subplots(figsize=(10, 0.45 * len(labels) + 1.2))
    bars = ax.barh(labels, scores, xerr=err, color=colors, edgecolor="#222", linewidth=0.5,
                   error_kw={"ecolor": "#444", "elinewidth": 1.0, "capsize": 3})
    for bar, score in zip(bars, scores, strict=False):
        ax.text(score + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{score:.3f}", va="center", fontsize=9)

    ax.set_xlim(0.5, 1.02)
    ax.set_xlabel("Overall score (hard split)")
    ax.set_title("Persian LLM Eval v1.1 — hard split\nbootstrap 95% CI on overall",
                 fontsize=12, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)

    legend_elements = [
        Patch(facecolor="#c45a2c", label="Claude Opus"),
        Patch(facecolor="#e8804d", label="Claude Sonnet"),
        Patch(facecolor="#f5a572", label="Claude Haiku"),
        Patch(facecolor="#1d6f87", label="GPT-5.5"),
        Patch(facecolor="#2c7fb8", label="GPT-5"),
        Patch(facecolor="#41b6c4", label="GPT-5 mini"),
        Patch(facecolor="#7fcdbb", label="GPT-5 nano"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=8, frameon=False)

    fig.tight_layout()
    fig.savefig(CHARTS / "overall_hard.png", dpi=150)
    plt.close(fig)


def chart2_track_heatmap() -> None:
    """Heatmap of per-track scores on hard split."""
    rows = []
    for path in sorted(RESULTS.glob("*.hard.json")):
        r = load_result(path)
        rows.append(
            {
                "label": display_name(path.stem),
                "overall": r["overall_score"],
                "tracks": r["task_scores"],
            }
        )
    rows.sort(key=lambda x: -x["overall"])

    tracks_present = sorted({t for r in rows for t in r["tracks"]})
    labels = [r["label"] for r in rows]
    matrix = np.array(
        [[r["tracks"].get(t, {}).get("score", np.nan) for t in tracks_present] for r in rows]
    )

    fig, ax = plt.subplots(figsize=(1.3 * len(tracks_present) + 2, 0.4 * len(labels) + 1.5))
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0.5, vmax=1.0, aspect="auto")

    ax.set_xticks(range(len(tracks_present)))
    ax.set_xticklabels([TRACK_DISPLAY.get(t, t) for t in tracks_present],
                       rotation=30, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            if np.isnan(v):
                continue
            colour = "white" if v < 0.7 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=8, color=colour)

    cb = fig.colorbar(im, ax=ax, shrink=0.7)
    cb.set_label("Track score")

    ax.set_title("Per-track scores — hard split (sorted by overall)",
                 fontsize=12, loc="left")
    fig.tight_layout()
    fig.savefig(CHARTS / "track_heatmap.png", dpi=150)
    plt.close(fig)


def chart3_opus_thinking() -> None:
    """Opus 4.7 thinking-effort sweep across tracks."""
    files = [
        ("Standard", "claude-opus-4-7.hard.json"),
        ("+T(low)", "claude-opus-4-7-thinking.hard.json"),
        ("+T(med)", "claude-opus-4-7-thinking-medium.hard.json"),
        ("+T(high)", "claude-opus-4-7-thinking-high.hard.json"),
    ]
    data: dict[str, list[float]] = {}
    efforts: list[str] = []
    overall_scores: list[float] = []
    for label, fname in files:
        r = load_result(RESULTS / fname)
        efforts.append(label)
        overall_scores.append(r["overall_score"])
        for track, td in r["task_scores"].items():
            data.setdefault(track, []).append(td["score"])

    fig, ax = plt.subplots(figsize=(9, 5.5))
    palette = plt.cm.tab10(np.linspace(0, 1, len(data) + 1))

    for i, (track, scores) in enumerate(sorted(data.items())):
        ax.plot(efforts, scores, marker="o", linewidth=1.5,
                color=palette[i + 1], label=TRACK_DISPLAY.get(track, track),
                alpha=0.85)

    ax.plot(efforts, overall_scores, marker="s", linewidth=2.8, color="#222",
            label="Overall", zorder=5)
    for i, s in enumerate(overall_scores):
        ax.text(i, s + 0.01, f"{s:.3f}", ha="center", fontsize=9,
                fontweight="bold")

    ax.set_ylim(0.55, 1.02)
    ax.set_ylabel("Score")
    ax.set_xlabel("Thinking effort")
    ax.set_title("Claude Opus 4.7 — thinking effort sweep on hard split\n"
                 "more thinking → longer answers → max_words penalties on Instruction",
                 fontsize=11, loc="left")
    ax.grid(alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower left", fontsize=8, ncol=2, frameon=False)

    fig.tight_layout()
    fig.savefig(CHARTS / "opus_thinking.png", dpi=150)
    plt.close(fig)


def _family_key(label: str) -> str:
    if "Haiku" in label:
        return "Claude Haiku"
    if "Sonnet" in label:
        return "Claude Sonnet"
    if "Claude Opus" in label:
        return "Claude Opus"
    if "GPT-5 nano" in label:
        return "GPT-5 nano"
    if "GPT-5 mini" in label:
        return "GPT-5 mini"
    if "GPT-5.5" in label:
        return "GPT-5.5"
    if "GPT-5" in label:
        return "GPT-5"
    return label


def chart4_public_vs_hard() -> None:
    """Scatter: best variant per family on public_eval vs hard."""
    pubs = {}
    for path in RESULTS.glob("*.public_eval.json"):
        stem = path.stem.replace(".public_eval", "")
        pubs[stem] = load_result(path)["overall_score"]
    hards = {}
    for path in RESULTS.glob("*.hard.json"):
        stem = path.stem.replace(".hard", "")
        hards[stem] = load_result(path)["overall_score"]

    keys = sorted(set(pubs) & set(hards))
    raw = [(pubs[k], hards[k], display_name(k)) for k in keys]

    best: dict[str, tuple[float, float, str]] = {}
    for x, y, label in raw:
        fam = _family_key(label)
        if fam not in best or (x + y) / 2 > (best[fam][0] + best[fam][1]) / 2:
            best[fam] = (x, y, label)

    points = sorted(best.values(), key=lambda p: -(p[0] + p[1]))

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.plot([0.5, 1.0], [0.5, 1.0], color="#aaa", linestyle="--",
            linewidth=1, label="y = x (perfect generalisation)")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    labels = [p[2] for p in points]
    colors = [family_color(l) for l in labels]
    ax.scatter(xs, ys, c=colors, s=180, edgecolors="#222", linewidths=0.6, zorder=3)

    for x, y, label in zip(xs, ys, labels, strict=False):
        ax.annotate(label, (x, y), xytext=(10, -4), textcoords="offset points",
                    fontsize=10.5)

    lo = min(min(xs), min(ys)) - 0.02
    ax.set_xlim(lo, 1.01)
    ax.set_ylim(lo, 1.01)
    ax.set_xlabel("Overall score on public_eval")
    ax.set_ylabel("Overall score on hard")
    ax.set_title("Public-eval vs hard — generalisation of frontier models\n"
                 "all points sit below y=x → hard split is genuinely harder",
                 fontsize=11, loc="left")
    ax.grid(alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", fontsize=9, frameon=False)
    ax.set_aspect("equal")

    fig.tight_layout()
    fig.savefig(CHARTS / "public_vs_hard.png", dpi=150)
    plt.close(fig)


def chart5_top_models_tracks() -> None:
    """Grouped bars: best variant per model family on hard tracks."""
    rows = []
    for path in sorted(RESULTS.glob("*.hard.json")):
        r = load_result(path)
        rows.append(
            {
                "label": display_name(path.stem),
                "overall": r["overall_score"],
                "tracks": r["task_scores"],
            }
        )

    best_per_family: dict[str, dict[str, Any]] = {}
    for r in rows:
        fam = _family_key(r["label"])
        if fam not in best_per_family or r["overall"] > best_per_family[fam]["overall"]:
            best_per_family[fam] = r

    top = sorted(best_per_family.values(), key=lambda x: -x["overall"])

    tracks_present = sorted({t for r in top for t in r["tracks"]})
    n_tracks = len(tracks_present)
    n_models = len(top)
    bar_w = 0.8 / n_models
    x = np.arange(n_tracks)

    fig, ax = plt.subplots(figsize=(max(9, 1.6 * n_tracks), 5.5))
    for i, row in enumerate(top):
        scores = [row["tracks"].get(t, {}).get("score", 0.0) for t in tracks_present]
        offset = (i - (n_models - 1) / 2) * bar_w
        bars = ax.bar(x + offset, scores, bar_w,
                      label=row["label"], color=family_color(row["label"]),
                      edgecolor="#222", linewidth=0.4)
        for b, s in zip(bars, scores, strict=False):
            if s > 0:
                ax.text(b.get_x() + b.get_width() / 2, s + 0.005,
                        f"{s:.2f}", ha="center", fontsize=7, rotation=0)

    ax.set_xticks(x)
    ax.set_xticklabels([TRACK_DISPLAY.get(t, t) for t in tracks_present],
                       rotation=15, ha="right")
    ax.set_ylim(0.4, 1.07)
    ax.set_ylabel("Score")
    ax.set_title("Best variant per model family — hard tracks",
                 fontsize=12, loc="left")
    ax.grid(axis="y", alpha=0.25, linestyle="--")
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", fontsize=8, frameon=False, ncol=1)

    fig.tight_layout()
    fig.savefig(CHARTS / "top_models_tracks.png", dpi=150)
    plt.close(fig)


def main() -> int:
    CHARTS.mkdir(parents=True, exist_ok=True)
    leaderboard = load_leaderboard()

    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["axes.titleweight"] = "semibold"

    chart1_overall_hard(leaderboard)
    chart2_track_heatmap()
    chart3_opus_thinking()
    chart4_public_vs_hard()
    chart5_top_models_tracks()

    for path in sorted(CHARTS.glob("*.png")):
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
