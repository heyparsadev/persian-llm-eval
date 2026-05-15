#!/usr/bin/env python3
"""Summarise review_proposals.jsonl into a human-readable markdown report.

Reads:
  data/review_proposals.jsonl   (output of review_pending_items.py)
  data/persian_eval_v1.public_eval.jsonl
  data/persian_eval_v1.hard.jsonl

Writes:
  docs/REVIEW_PROPOSALS.md

The report groups items by recommendation (rejected → revise → accepted) and
within each group by track. For each item it shows the prompt (truncated),
the current answer/constraints, the model's rubric scores, the issues it
flagged, and any concrete proposed change. Designed for a human to skim and
mark what to apply.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "data" / "review_proposals.jsonl"
DATASETS = [
    ROOT / "data" / "persian_eval_v1.public_eval.jsonl",
    ROOT / "data" / "persian_eval_v1.hard.jsonl",
]
OUTPUT = ROOT / "docs" / "REVIEW_PROPOSALS.md"


def main() -> int:
    if not PROPOSALS.exists():
        print(f"error: {PROPOSALS} does not exist", file=sys.stderr)
        return 1

    items = _load_items()
    proposals = _load_proposals()

    by_rec: dict[str, list[dict[str, Any]]] = {"rejected": [], "revise": [], "accepted": []}
    parse_errors: list[dict[str, Any]] = []
    for proposal in proposals:
        if "parse_error" in proposal:
            parse_errors.append(proposal)
            continue
        rec = proposal.get("recommendation", "?")
        by_rec.setdefault(rec, []).append(proposal)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        f.write("# Persian Eval v1.1 — review proposals\n\n")
        f.write(
            f"Auto-generated from `data/review_proposals.jsonl`. "
            f"Total proposals: {len(proposals)}. "
            f"Rejected: {len(by_rec['rejected'])}. "
            f"Revise: {len(by_rec['revise'])}. "
            f"Accepted: {len(by_rec['accepted'])}. "
            f"Parse errors: {len(parse_errors)}.\n\n"
        )
        f.write(
            "Use this file to triage what to apply. The reviewer is "
            "claude-sonnet-4-6, which is strict about Persian phrasing and "
            "constraint solvability. Take its 'reject' calls seriously; treat "
            "'revise' as a useful suggestion to skim, not a requirement.\n\n"
        )

        for rec_name in ("rejected", "revise", "accepted"):
            f.write(f"## {rec_name.title()} ({len(by_rec[rec_name])})\n\n")
            by_track: dict[str, list[dict[str, Any]]] = {}
            for proposal in by_rec[rec_name]:
                by_track.setdefault(proposal.get("track", "?"), []).append(proposal)
            for track in sorted(by_track):
                f.write(f"### `{track}` — {len(by_track[track])} items\n\n")
                for proposal in sorted(by_track[track], key=lambda p: p["id"]):
                    item = items.get(proposal["id"])
                    _write_item(f, proposal, item)
            f.write("\n")

        if parse_errors:
            f.write("## Parse errors\n\n")
            f.write("The reviewer's reply could not be parsed for these items. ")
            f.write("Re-running `scripts/review_pending_items.py` may fix them.\n\n")
            for err in parse_errors:
                f.write(f"- `{err.get('id', '?')}`\n")
            f.write("\n")

    print(f"wrote {OUTPUT}")
    return 0


def _load_items() -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    for path in DATASETS:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                items[row["id"]] = row
    return items


def _load_proposals() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with PROPOSALS.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _write_item(f, proposal: dict[str, Any], item: dict[str, Any] | None) -> None:
    item_id = proposal["id"]
    rubric = proposal.get("rubric") or {}
    issues = proposal.get("issues") or []
    changes = proposal.get("proposed_changes")

    f.write(f"#### `{item_id}`\n\n")
    if item is None:
        f.write("*Item missing from dataset files.*\n\n")
        return

    prompt = (item.get("prompt") or "").replace("\n", " ")
    if len(prompt) > 240:
        prompt = prompt[:237] + "..."
    f.write(f"**Prompt:** {prompt}\n\n")

    if item.get("choices"):
        labels = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح"]
        for idx, choice in enumerate(item["choices"]):
            mark = " ← labelled answer" if idx == item.get("metadata", {}).get(
                "answer_index"
            ) else ""
            f.write(f"  - {labels[idx] if idx < len(labels) else idx}) {choice}{mark}\n")
        f.write("\n")
    else:
        ans = item.get("answer")
        if isinstance(ans, list):
            f.write(f"**Accepted answers:** {ans}\n\n")
        elif isinstance(ans, dict):
            f.write(f"**Constraints:** `{json.dumps(ans, ensure_ascii=False)}`\n\n")
        else:
            f.write(f"**Answer:** {ans}\n\n")

    if rubric:
        rubric_str = ", ".join(f"{k}={v}" for k, v in rubric.items())
        f.write(f"**Rubric:** {rubric_str}\n\n")
    if issues:
        f.write("**Issues:**\n")
        for issue in issues:
            f.write(f"  - {issue}\n")
        f.write("\n")
    if changes and isinstance(changes, dict):
        non_null = {k: v for k, v in changes.items() if v not in (None, [], {})}
        if non_null:
            f.write("**Proposed changes:**\n")
            f.write("```json\n")
            f.write(json.dumps(non_null, ensure_ascii=False, indent=2))
            f.write("\n```\n\n")
    f.write("---\n\n")


if __name__ == "__main__":
    raise SystemExit(main())
