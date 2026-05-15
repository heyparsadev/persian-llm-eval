#!/usr/bin/env python3
"""Apply review decisions from data/review_proposals.jsonl to the dataset.

Three operations:

1. `--auto-clear`: for items with recommendation == "accepted", set
   metadata.review.status = "accepted" (carry over the rubric). For items
   with recommendation == "rejected", remove them from the JSONL entirely
   (git history preserves the original). Print a summary.

2. `--interactive`: walk through every "revise" item, show the proposed
   change, ask y/n/s/q, and apply the change if accepted. Resumable: the
   apply log goes to data/review_decisions.jsonl so re-running the tool
   skips items already decided.

3. Default (no flag): run --auto-clear, then --interactive.

Usage examples:

    python scripts/apply_review_decisions.py --auto-clear      # only the easy ones
    python scripts/apply_review_decisions.py --interactive      # only the y/n loop
    python scripts/apply_review_decisions.py --track reading    # filter to one track
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROPOSALS = ROOT / "data" / "review_proposals.jsonl"
DECISIONS = ROOT / "data" / "review_decisions.jsonl"
SPLITS = {
    "public_eval": ROOT / "data" / "persian_eval_v1.public_eval.jsonl",
    "hard": ROOT / "data" / "persian_eval_v1.hard.jsonl",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--auto-clear", action="store_true", help="Apply accepted+rejected only")
    parser.add_argument("--interactive", action="store_true", help="Walk through revise items")
    parser.add_argument("--track", default=None, help="Only process one track (filter)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing files",
    )
    args = parser.parse_args(argv)

    if not (args.auto_clear or args.interactive):
        args.auto_clear = True
        args.interactive = True

    proposals = _load_proposals()
    if args.track:
        proposals = [p for p in proposals if p.get("track") == args.track]

    if args.auto_clear:
        _apply_auto_clear(proposals, dry_run=args.dry_run)
    if args.interactive:
        _apply_interactive(proposals, dry_run=args.dry_run)
    return 0


def _load_proposals() -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in PROPOSALS.read_text(encoding="utf-8").splitlines() if line
    ]


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_dataset(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _split_for_id(item_id: str) -> str:
    # peval-{split}-{track}-{nnn} where split is dev/public/hard.
    parts = item_id.split("-")
    if len(parts) < 4:
        return "?"
    return {"public": "public_eval", "hard": "hard", "dev": "dev"}.get(parts[1], "?")


def _apply_auto_clear(proposals: list[dict[str, Any]], *, dry_run: bool) -> None:
    accepted = {p["id"]: p for p in proposals if p.get("recommendation") == "accepted"}
    rejected = {p["id"]: p for p in proposals if p.get("recommendation") == "rejected"}

    print(f"auto-clear: accepted={len(accepted)} rejected={len(rejected)}", file=sys.stderr)
    if not accepted and not rejected:
        return

    for split_name, path in SPLITS.items():
        rows = _load_dataset(path)
        out: list[dict[str, Any]] = []
        applied_accept = 0
        removed = 0
        for row in rows:
            if row["id"] in rejected:
                print(f"  remove   {row['id']:35} ({rejected[row['id']].get('track')})", file=sys.stderr)
                removed += 1
                continue
            if row["id"] in accepted:
                meta = row.setdefault("metadata", {})
                review = meta.setdefault("review", {})
                old = review.get("status", "<missing>")
                review["status"] = "accepted"
                review.setdefault("reviewers", []).append("claude-sonnet-4-6")
                # Update rubric if the proposal supplied a non-trivial one
                proposed_rubric = accepted[row["id"]].get("rubric")
                if isinstance(proposed_rubric, dict):
                    review["rubric"] = proposed_rubric
                applied_accept += 1
                if applied_accept <= 3:
                    print(
                        f"  accept   {row['id']:35} status {old} -> accepted",
                        file=sys.stderr,
                    )
            out.append(row)
        print(
            f"  {split_name}: applied_accept={applied_accept} removed={removed}",
            file=sys.stderr,
        )
        if not dry_run:
            _write_dataset(path, out)


def _load_decisions() -> dict[str, str]:
    if not DECISIONS.exists():
        return {}
    out: dict[str, str] = {}
    for line in DECISIONS.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("id"):
            out[row["id"]] = row.get("decision", "?")
    return out


def _apply_interactive(proposals: list[dict[str, Any]], *, dry_run: bool) -> None:
    revise = [p for p in proposals if p.get("recommendation") == "revise"]
    if not revise:
        print("interactive: nothing to do (0 revise items)", file=sys.stderr)
        return

    decisions = _load_decisions()
    todo = [p for p in revise if p["id"] not in decisions]
    done = len(decisions)
    print(
        f"interactive: {len(todo)} revise items todo ({done} already decided)",
        file=sys.stderr,
    )
    if not todo:
        return

    # Load all dataset rows by id.
    rows_by_split: dict[str, list[dict[str, Any]]] = {
        name: _load_dataset(path) for name, path in SPLITS.items()
    }
    by_id: dict[str, dict[str, Any]] = {}
    for rows in rows_by_split.values():
        for row in rows:
            by_id[row["id"]] = row

    # Group todo by track for easier navigation.
    todo.sort(key=lambda p: (p.get("track", ""), p["id"]))

    print(
        "\nKeys:\n  y = apply proposed change, mark item accepted\n"
        "  n = skip (item stays pending_review)\n"
        "  s = skip this whole track for now\n"
        "  q = quit and save what you've done so far\n",
        file=sys.stderr,
    )

    skip_tracks: set[str] = set()
    for index, proposal in enumerate(todo, start=1):
        if proposal.get("track") in skip_tracks:
            continue
        item = by_id.get(proposal["id"])
        if item is None:
            print(f"  warn: dataset row missing for {proposal['id']}, skipping", file=sys.stderr)
            continue

        print("\n" + "=" * 72)
        print(f"[{index}/{len(todo)}] {proposal['id']} ({proposal.get('track')})")
        print("-" * 72)
        _show_item(item, proposal)
        decision = _prompt()
        if decision == "q":
            print("quit; decisions saved.", file=sys.stderr)
            return
        if decision == "s":
            skip_tracks.add(proposal.get("track", ""))
            print(f"skipping track {proposal.get('track')}", file=sys.stderr)
            continue
        if decision == "n":
            _record_decision(proposal["id"], "skipped", dry_run=dry_run)
            continue
        # "y": apply
        if _apply_one(item, proposal):
            _record_decision(proposal["id"], "applied", dry_run=dry_run)
            if not dry_run:
                # Persist the JSONL split this item lives in.
                split_name = _split_for_id(proposal["id"])
                if split_name in rows_by_split:
                    _write_dataset(SPLITS[split_name], rows_by_split[split_name])
        else:
            print("  (no concrete change to apply; recorded as skipped)", file=sys.stderr)
            _record_decision(proposal["id"], "skipped_no_change", dry_run=dry_run)


def _show_item(item: dict[str, Any], proposal: dict[str, Any]) -> None:
    prompt = (item.get("prompt") or "").replace("\n", " ")
    if len(prompt) > 220:
        prompt = prompt[:217] + "..."
    print(f"prompt: {prompt}")
    if item.get("choices"):
        labels = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح"]
        for idx, choice in enumerate(item["choices"]):
            mark = " ← answer" if idx == item.get("metadata", {}).get("answer_index") else ""
            print(f"  {labels[idx]}) {choice}{mark}")
    elif isinstance(item.get("answer"), list):
        print(f"accepted: {item['answer']}")
    elif isinstance(item.get("answer"), dict):
        print(f"constraints: {json.dumps(item['answer'], ensure_ascii=False)}")
    else:
        print(f"answer: {item.get('answer')}")
    issues = proposal.get("issues") or []
    if issues:
        print("issues:")
        for issue in issues:
            print(f"  - {issue}")
    changes = proposal.get("proposed_changes")
    if isinstance(changes, dict):
        non_null = {k: v for k, v in changes.items() if v not in (None, [], {}) and k != "notes"}
        if non_null:
            print("proposed:")
            print(json.dumps(non_null, ensure_ascii=False, indent=2))


def _prompt() -> str:
    while True:
        try:
            choice = input("apply? [y/n/s/q]: ").strip().lower()
        except EOFError:
            return "q"
        if choice in {"y", "n", "s", "q"}:
            return choice


def _record_decision(item_id: str, decision: str, *, dry_run: bool) -> None:
    line = json.dumps({"id": item_id, "decision": decision}, ensure_ascii=False)
    if dry_run:
        print(f"  (dry-run) would record: {line}", file=sys.stderr)
        return
    with DECISIONS.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _apply_one(item: dict[str, Any], proposal: dict[str, Any]) -> bool:
    changes = proposal.get("proposed_changes")
    if not isinstance(changes, dict):
        return False
    applied = False

    # 1. Extra accepted-answer phrasings (exact/f1 only).
    additions = changes.get("answer_additions")
    if additions and isinstance(item.get("answer"), list):
        existing = list(item["answer"])
        new = [s for s in additions if isinstance(s, str) and s not in existing]
        if new:
            item["answer"] = existing + new
            applied = True

    # 2. Replace the canonical answer text outright.
    replacement = changes.get("answer_replacement")
    if isinstance(replacement, str) and replacement.strip():
        if isinstance(item.get("answer"), list):
            if replacement not in item["answer"]:
                item["answer"] = [replacement, *item["answer"]]
        else:
            item["answer"] = replacement
        applied = True

    # 3. Replace MCQ answer_index.
    idx = changes.get("answer_index_replacement")
    if isinstance(idx, int):
        meta = item.setdefault("metadata", {})
        meta["answer_index"] = idx
        if item.get("choices") and 0 <= idx < len(item["choices"]):
            item["answer"] = item["choices"][idx]
        applied = True

    # 4. Tweak instruction constraints.
    constraint_changes = changes.get("constraint_changes")
    if isinstance(constraint_changes, dict) and isinstance(item.get("answer"), dict):
        for key, value in constraint_changes.items():
            item["answer"][key] = value
        applied = True

    # 5. Prompt rewrite.
    new_prompt = changes.get("rewrite_prompt")
    if isinstance(new_prompt, str) and new_prompt.strip():
        item["prompt"] = new_prompt.strip()
        applied = True

    if applied:
        meta = item.setdefault("metadata", {})
        review = meta.setdefault("review", {})
        review["status"] = "accepted"
        reviewers = review.setdefault("reviewers", [])
        if "claude-sonnet-4-6" not in reviewers:
            reviewers.append("claude-sonnet-4-6")
        if "human-applied" not in reviewers:
            reviewers.append("human-applied")
    return applied


if __name__ == "__main__":
    raise SystemExit(main())
