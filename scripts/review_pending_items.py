#!/usr/bin/env python3
"""Model-assisted review pass over Persian Eval pending_review items.

For every JSONL row whose metadata.review.status is "pending_review", call a
strong Anthropic model and ask it to evaluate the item against the
CONTRIBUTING_DATASET rubric, judge any track-specific concerns
(narrow accepted-answer lists, unsolvable instruction constraints, MCQ answer
correctness), and emit a recommendation: accept / revise / reject, with a
concrete proposed change when applicable.

Output is written to data/review_proposals.jsonl, one JSON object per item,
keyed by id. The script is idempotent: re-running skips items already in
the output file.

Usage:

    python scripts/review_pending_items.py \\
        --model claude-sonnet-4-6 \\
        data/persian_eval_v1.public_eval.jsonl \\
        data/persian_eval_v1.hard.jsonl
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_OUTPUT = ROOT / "data" / "review_proposals.jsonl"

REVIEW_INSTRUCTIONS = """You are a Persian-language benchmark item reviewer.

You will be given one item from the Persian Eval v1.1 dataset and must judge
its quality, then return a single JSON object on the last line of your reply.

Rate each rubric dimension on the 1–5 scale defined in CONTRIBUTING_DATASET.md:

- clarity (5 = unambiguous, 1 = confusing)
- ambiguity (1 = single correct answer, 5 = many defensible answers)
- cultural_fit (5 = idiomatic Iranian Persian, 1 = stilted/translated)
- leakage_risk (1 = original wording, 5 = likely scraped from a public source)
- difficulty (1 = trivial, 5 = expert)

Then, depending on the item's `metadata.scoring`:

- mcq: confirm the labelled answer is correct, flag any distractor that is
  also defensibly correct, or any distractor that is laughably wrong.
- exact / f1: judge whether the `answer` list is complete. Propose
  additional accepted Persian phrasings (synonyms, equivalent ways of
  expressing the answer in Iranian Persian). For numbers, both Persian
  digits and Arabic digits should be accepted.
- instruction: judge whether the constraints are jointly satisfiable in
  Persian within the word bounds. Specifically check whether `max_words`
  is realistic for the topic and whether `forbidden` lists conflict with
  `required_keywords`.

Recommend a status:

- accepted: item is good, no changes needed.
- revise: item is salvageable but needs concrete fix(es). Provide them.
- rejected: fundamental issue (wrong answer, unsolvable constraints,
  duplicate, contamination, ambiguity that no edit can fix).

Output format — your reply MUST end with a single line containing valid
JSON of this shape (no markdown fences, just the JSON):

{
  "rubric": {"clarity": 5, "ambiguity": 1, "cultural_fit": 5, "leakage_risk": 1, "difficulty": 3},
  "recommendation": "accepted" | "revise" | "rejected",
  "issues": ["short bullet 1", "short bullet 2"],
  "proposed_changes": {
      "answer_additions": ["..."],          // for exact/f1 items only
      "answer_replacement": "...",           // if labelled answer is wrong
      "answer_index_replacement": 2,         // for mcq items only
      "constraint_changes": {"max_words": 80}, // for instruction items only
      "rewrite_prompt": "...",               // optional, only if prompt itself needs editing
      "notes": "free-text rationale"
  }
}

Set unused proposed_changes fields to null. If recommendation is
"accepted", proposed_changes may be null entirely.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="JSONL input files")
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Anthropic model id (default: claude-sonnet-4-6)",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output JSONL path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N pending items (debug)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List items that would be reviewed; do not call the API",
    )
    args = parser.parse_args(argv)

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("error: ANTHROPIC_API_KEY is required", file=sys.stderr)
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pending = list(_iter_pending(args.paths))
    if args.limit:
        pending = pending[: args.limit]

    already = _load_existing_ids(output_path)
    todo = [item for item in pending if item["id"] not in already]
    print(
        f"pending={len(pending)} | already_reviewed={len(already)} | "
        f"todo={len(todo)} | model={args.model}",
        file=sys.stderr,
    )
    if args.dry_run:
        for item in todo[:20]:
            print(f"  would review {item['id']} ({item['track']})", file=sys.stderr)
        if len(todo) > 20:
            print(f"  ...and {len(todo) - 20} more", file=sys.stderr)
        return 0

    base_url = (os.getenv("ANTHROPIC_BASE_URL") or "https://api.anthropic.com").rstrip("/")
    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    with output_path.open("a", encoding="utf-8") as out:
        for index, item in enumerate(todo, start=1):
            print(f"[{index}/{len(todo)}] {item['id']} ({item['track']})", file=sys.stderr)
            try:
                response = _review_one(item, args.model, api_key, base_url)
            except Exception as exc:  # noqa: BLE001 - log and continue
                print(f"  error: {exc}", file=sys.stderr)
                continue
            response["id"] = item["id"]
            response["track"] = item["track"]
            response["model"] = args.model
            out.write(json.dumps(response, ensure_ascii=False) + "\n")
            out.flush()
    return 0


def _iter_pending(paths: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                review = row.get("metadata", {}).get("review", {})
                if review.get("status") == "pending_review":
                    items.append(row)
    return items


def _load_existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    seen: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            item_id = row.get("id")
            if isinstance(item_id, str):
                seen.add(item_id)
    return seen


def _review_one(
    item: dict[str, Any], model: str, api_key: str, base_url: str
) -> dict[str, Any]:
    user_content = "Review this item:\n\n" + json.dumps(item, ensure_ascii=False, indent=2)
    payload = {
        "model": model,
        "max_tokens": 1500,
        "system": REVIEW_INSTRUCTIONS,
        "messages": [{"role": "user", "content": user_content}],
        "temperature": 0.0,
    }
    request = urllib.request.Request(
        f"{base_url}/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    text = _post_with_retries(request)
    return _parse_review(text)


def _post_with_retries(request: urllib.request.Request, max_attempts: int = 4) -> str:
    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
            chunks = []
            for block in payload.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text")
                    if isinstance(text, str):
                        chunks.append(text)
            if chunks:
                return "\n".join(chunks).strip()
            raise RuntimeError("no text content in response")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {429, 500, 502, 503, 504} and attempt < max_attempts - 1:
                time.sleep(2**attempt)
                continue
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {body[:500]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < max_attempts - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"transport error: {exc}") from exc
    raise RuntimeError(f"all retries exhausted: {last_error}")


def _parse_review(text: str) -> dict[str, Any]:
    """Extract the trailing JSON object from the model's reply.

    The model is asked to end with a JSON object containing rubric/
    recommendation/etc. The surrounding markdown often also contains
    nested-looking braces (e.g. an inner rubric dict shown for emphasis),
    so a naïve rfind on '{' picks up the inner object. Walk backward from
    the last '}' with bracket matching to find the matching outer '{'.
    """

    cleaned = text.strip()
    end = cleaned.rfind("}")
    if end == -1:
        return {"raw": text, "parse_error": "no closing brace found"}

    depth = 0
    start = -1
    for index in range(end, -1, -1):
        ch = cleaned[index]
        if ch == "}":
            depth += 1
        elif ch == "{":
            depth -= 1
            if depth == 0:
                start = index
                break
    if start == -1:
        return {"raw": text, "parse_error": "no balanced JSON object found"}

    snippet = cleaned[start : end + 1]
    try:
        parsed = json.loads(snippet)
    except json.JSONDecodeError as exc:
        return {"raw": text, "parse_error": f"JSON decode error: {exc}"}
    if not isinstance(parsed, dict):
        return {"raw": text, "parse_error": "JSON is not an object"}
    if "rubric" not in parsed and "recommendation" not in parsed:
        return {
            "raw": text,
            "parse_error": "JSON object lacks 'rubric'/'recommendation' fields",
        }
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
