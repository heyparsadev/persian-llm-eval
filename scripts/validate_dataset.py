#!/usr/bin/env python3
"""Mechanical quality validator for Persian Eval JSONL datasets.

Runs in CI on every push and is also exposed for local use:

    python scripts/validate_dataset.py data/persian_eval_v1.*.jsonl

It enforces rules described in CONTRIBUTING_DATASET.md section 6.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

# Allow `python scripts/validate_dataset.py …` without an editable install.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from persian_eval.dataset import DatasetRecord, load_records  # noqa: E402
from persian_eval.normalize import normalize_persian, strip_punctuation, tokenize  # noqa: E402
from persian_eval.scoring import score_record  # noqa: E402

PUBLIC_TRACKS = {"knowledge", "short_qa", "reading", "instruction", "culture"}
HARD_TRACKS = {
    "hard_reasoning",
    "hard_math",
    "hard_reading",
    "hard_instruction",
    "hard_culture",
}
DEV_TRACKS = PUBLIC_TRACKS  # dev mirrors public tracks at smaller scale.
PRACTICAL_TRACKS = {
    "practical_writing",
    "practical_editing",
    "practical_numbers",
    "practical_extraction",
    "practical_pragmatics",
    "practical_creative",
}

CHALLENGE_TRACKS = {
    "challenge_premise",
    "challenge_grounding",
    "challenge_ambiguity",
    "challenge_multihop",
    "challenge_wordplay",
}
# Splits whose track names are `<split>_<id token>`.
PREFIXED_SPLITS = {"practical", "challenge"}

PER_SPLIT_TRACKS: dict[str, set[str]] = {
    "dev": DEV_TRACKS,
    "public_eval": PUBLIC_TRACKS,
    "hard": HARD_TRACKS,
    "practical": PRACTICAL_TRACKS,
    "challenge": CHALLENGE_TRACKS,
}

# Minimum number of items per (split, track). dev is intentionally tiny;
# the real benchmark splits must have enough items to reduce per-track
# noise below ±15% with bootstrap confidence intervals.
PER_TRACK_MIN: dict[str, int] = {
    "dev": 2,
    "public_eval": 20,
    "hard": 20,
    "practical": 20,
    "challenge": 20,
}

# Minimum prompt length per track (in characters of the normalized prompt).
PROMPT_MIN_CHARS: dict[str, int] = {
    "knowledge": 12,
    "short_qa": 8,
    "reading": 60,
    "instruction": 30,
    "culture": 12,
    "hard_reasoning": 30,
    "hard_math": 30,
    "hard_reading": 70,
    "hard_instruction": 40,
    "hard_culture": 20,
    "practical_writing": 60,
    "practical_editing": 40,
    "practical_numbers": 25,
    "practical_extraction": 80,
    "practical_pragmatics": 30,
    "practical_creative": 30,
    "challenge_premise": 25,
    "challenge_grounding": 80,
    "challenge_ambiguity": 25,
    "challenge_multihop": 25,
    "challenge_wordplay": 25,
}

ID_PATTERN = re.compile(r"^peval-(dev|public|hard|practical|challenge)-([a-z]+)-(\d{3,})$")
# Some legacy IDs spell tracks without an underscore (e.g. `shortqa` for
# `short_qa`). The mapping below is the source of truth for id-token →
# canonical track name within a split.
ID_TRACK_ALIASES: dict[str, str] = {
    "knowledge": "knowledge",
    "shortqa": "short_qa",
    "reading": "reading",
    "instruction": "instruction",
    "culture": "culture",
    "reasoning": "hard_reasoning",
    "math": "hard_math",
}
ARABIC_LETTER_RE = re.compile(r"[يكةؤإأ]")
READING_LEAD = "متن را بخوان"


class DatasetQualityError(ValueError):
    """Raised when a mechanical quality check fails."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="JSONL files to validate")
    parser.add_argument(
        "--strict-min-count",
        action="store_true",
        help="Fail if any (split, track) bucket is below its minimum (default: warn only).",
    )
    args = parser.parse_args(argv)

    records = load_records(args.paths)
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(check_id_format(records))
    errors.extend(check_split_track_consistency(records))
    errors.extend(check_arabic_letters(records))
    errors.extend(check_no_answer_leakage(records))
    errors.extend(check_choice_leakage(records))
    errors.extend(check_mcq_structure(records))
    errors.extend(check_instruction_structure(records))
    errors.extend(check_json_structure(records))
    errors.extend(check_reference_responses(records))
    errors.extend(check_prompt_lengths(records))

    count_messages = check_per_track_counts(records)
    if args.strict_min_count:
        errors.extend(count_messages)
    else:
        warnings.extend(count_messages)

    warnings.extend(check_answer_position_skew(records))

    for warning in warnings:
        print(f"warn: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)

    print(
        f"validate_dataset | records={len(records)} | "
        f"errors={len(errors)} | warnings={len(warnings)}",
        file=sys.stderr,
    )
    return 1 if errors else 0


def check_id_format(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        match = ID_PATTERN.match(record.id)
        if not match:
            errors.append(f"{record.id}: id must match peval-{{split}}-{{track}}-{{NNN}}")
            continue
        split_token, track_token, _ = match.groups()
        expected_split = {
            "dev": "dev",
            "public": "public_eval",
            "hard": "hard",
            "practical": "practical",
            "challenge": "challenge",
        }[split_token]
        if record.split != expected_split:
            errors.append(
                f"{record.id}: id split token {split_token!r} does not match "
                f"row split {record.split!r}"
            )
        # Track token may be a prefix subset of the actual track (e.g. id uses
        # `knowledge` while the row track is `knowledge`). Just require that
        # the id token be contained in the row track for hard rows
        # (e.g. `peval-hard-reasoning-001` for track `hard_reasoning`).
        canonical_track = _resolve_track_alias(track_token, expected_split)
        if expected_split == "hard" and not record.track.startswith("hard_"):
            errors.append(f"{record.id}: hard split rows require a hard_* track")
        elif expected_split in PREFIXED_SPLITS and record.track != f"{expected_split}_{track_token}":
            errors.append(
                f"{record.id}: id track token {track_token!r} does not match "
                f"row track {record.track!r}"
            )
        elif canonical_track and canonical_track != record.track:
            errors.append(
                f"{record.id}: id track token {track_token!r} resolves to "
                f"{canonical_track!r}, does not match row track {record.track!r}"
            )
    return errors


def check_split_track_consistency(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        allowed = PER_SPLIT_TRACKS.get(record.split)
        if allowed is None:
            errors.append(f"{record.id}: unknown split {record.split!r}")
            continue
        if record.track not in allowed:
            errors.append(
                f"{record.id}: track {record.track!r} not allowed in split {record.split!r}"
            )
    return errors


def check_arabic_letters(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        if ARABIC_LETTER_RE.search(record.prompt):
            errors.append(f"{record.id}: prompt contains Arabic letter (use Persian ی/ک/ه)")
        for choice in record.choices or []:
            if ARABIC_LETTER_RE.search(choice):
                errors.append(f"{record.id}: choice contains Arabic letter")
                break
    return errors


def check_no_answer_leakage(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        scoring = record.metadata.get("scoring")
        # MCQ items: the answer text is by construction one of the choices
        # and the choice-leakage check covers that. Skip here to avoid
        # double-flagging puzzle prompts that legitimately mention choice
        # text (liar/truth, ordering, etc.).
        if scoring not in {"exact", "f1"}:
            continue
        if record.track in {"reading", "hard_reading", "challenge_grounding"}:
            # Reading answers come from the passage by design.
            continue
        prompt_tokens = tokenize(record.prompt)
        for accepted in _iter_accepted_strings(record.answer):
            answer_tokens = tokenize(accepted)
            if len(answer_tokens) < 1:
                continue
            joined = "".join(answer_tokens)
            if len(joined) < 3:
                continue
            if _contains_subsequence(prompt_tokens, answer_tokens):
                errors.append(
                    f"{record.id}: answer tokens {answer_tokens!r} appear verbatim in prompt"
                )
                break
    return errors


def check_choice_leakage(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        if not record.choices:
            continue
        if READING_LEAD in record.prompt:
            continue
        prompt_tokens = tokenize(record.prompt)
        # The correct answer's text appearing in prompt is the only real
        # leak; siblings in choices repeating prompt words is fine for
        # logic puzzles. We compare against the canonical answer choice.
        answer_index = record.metadata.get("answer_index")
        if not isinstance(answer_index, int) or answer_index >= len(record.choices):
            continue
        choice_tokens = tokenize(record.choices[answer_index])
        if len(choice_tokens) < 2:
            # Single-token choices (e.g. اعداد) are too short to flag
            # without false positives in puzzle prompts.
            continue
        if _contains_subsequence(prompt_tokens, choice_tokens):
            errors.append(
                f"{record.id}: correct choice tokens {choice_tokens!r} appear verbatim in prompt"
            )
    return errors


def _contains_subsequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return True
    return False


def check_mcq_structure(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        if record.metadata.get("scoring") != "mcq":
            continue
        choices = record.choices or []
        if not 3 <= len(choices) <= 5:
            errors.append(f"{record.id}: mcq must have 3–5 choices, got {len(choices)}")
            continue
        normalized = [strip_punctuation(choice) for choice in choices]
        if len(set(normalized)) != len(normalized):
            errors.append(f"{record.id}: mcq choices must be unique after normalization")
            continue
        answer_index = record.metadata.get("answer_index")
        if isinstance(answer_index, int):
            if answer_index >= len(choices):
                errors.append(f"{record.id}: answer_index out of range")
                continue
            answer_choice = strip_punctuation(choices[answer_index])
            answer_text = strip_punctuation(_canonical_answer(record.answer))
            if answer_text and answer_text != answer_choice:
                errors.append(
                    f"{record.id}: answer text does not match choices[answer_index]"
                )
    return errors


def check_instruction_structure(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        if record.metadata.get("scoring") != "instruction":
            continue
        if not isinstance(record.answer, dict):
            errors.append(f"{record.id}: instruction answer must be an object")
            continue
        active = [key for key in INSTRUCTION_KEYS if key in record.answer]
        unknown = sorted(set(record.answer) - set(INSTRUCTION_KEYS))
        if unknown:
            errors.append(f"{record.id}: unknown instruction constraint(s): {unknown}")
        if not active:
            errors.append(f"{record.id}: instruction item has no active constraints")
            continue
        min_words = record.answer.get("min_words")
        max_words = record.answer.get("max_words")
        if (
            isinstance(min_words, int)
            and isinstance(max_words, int)
            and min_words > max_words
        ):
            errors.append(f"{record.id}: min_words > max_words")
    return errors


INSTRUCTION_KEYS = (
    "required_keywords",
    "forbidden",
    "min_words",
    "max_words",
    "required_prefix",
    "required_suffix",
    "required_any",
    "forbidden_chars",
    "required_exact",
    "forbidden_exact",
    "starts_with",
    "ends_with",
    "line_count",
    "line_initials",
    "lines_end_with",
    "distinct_line_endings",
    "words_per_line",
    "word_initial",
    "word_final",
    "word_palindrome",
    "letter_palindrome",
    "min_letters",
    "word_length_step",
)


def check_json_structure(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    scalar = (str, int, float, bool, type(None))
    for record in records:
        if record.metadata.get("scoring") != "json":
            continue
        for key, value in record.answer.items():
            options = value if isinstance(value, list) else [value]
            if not options or not all(isinstance(option, scalar) for option in options):
                errors.append(
                    f"{record.id}: json field {key!r} must be a scalar or a list of scalars"
                )
    return errors


def check_reference_responses(records: Iterable[DatasetRecord]) -> list[str]:
    """Items that ship a reference response must give it a perfect score.

    This proves instruction constraints are jointly satisfiable and that answer
    keys parse the way the author intended.
    """

    errors: list[str] = []
    for record in records:
        reference = record.metadata.get("reference_response")
        if reference is None:
            continue
        score, details = score_record(record, str(reference))
        if score != 1.0:
            errors.append(f"{record.id}: reference_response scores {score:.3f}: {details}")
    return errors


def check_prompt_lengths(records: Iterable[DatasetRecord]) -> list[str]:
    errors: list[str] = []
    for record in records:
        minimum = PROMPT_MIN_CHARS.get(record.track)
        if minimum is None:
            continue
        normalized = normalize_persian(record.prompt)
        if len(normalized) < minimum:
            errors.append(
                f"{record.id}: prompt too short for track {record.track!r} "
                f"({len(normalized)} < {minimum} chars)"
            )
    return errors


def check_per_track_counts(records: list[DatasetRecord]) -> list[str]:
    bucket: dict[tuple[str, str], int] = defaultdict(int)
    for record in records:
        bucket[(record.split, record.track)] += 1
    present_splits = {record.split for record in records}
    messages: list[str] = []
    for split, tracks in PER_SPLIT_TRACKS.items():
        if split not in present_splits:
            continue
        minimum = PER_TRACK_MIN.get(split, 0)
        for track in tracks:
            count = bucket.get((split, track), 0)
            if count < minimum:
                messages.append(
                    f"split={split!r} track={track!r}: {count} items "
                    f"(< minimum {minimum})"
                )
    return messages


def check_answer_position_skew(records: Iterable[DatasetRecord]) -> list[str]:
    by_track: dict[str, Counter[int]] = defaultdict(Counter)
    for record in records:
        if record.metadata.get("scoring") != "mcq":
            continue
        index = record.metadata.get("answer_index")
        if isinstance(index, int):
            by_track[record.track][index] += 1
    messages: list[str] = []
    for track, counter in by_track.items():
        total = sum(counter.values())
        if total < 12:
            continue
        most_common_index, most_common_count = counter.most_common(1)[0]
        ratio = most_common_count / total
        if ratio > 0.5:
            messages.append(
                f"track={track!r}: answer position {most_common_index} "
                f"appears in {ratio:.0%} of items (> 50%)"
            )
    return messages


def _resolve_track_alias(token: str, expected_split: str) -> str | None:
    canonical = ID_TRACK_ALIASES.get(token)
    if canonical is None:
        return None
    if expected_split == "hard" and not canonical.startswith("hard_"):
        return f"hard_{canonical}" if f"hard_{canonical}" in HARD_TRACKS else canonical
    if expected_split != "hard" and canonical.startswith("hard_"):
        return None
    return canonical


def _iter_accepted_strings(answer: object) -> Iterable[str]:
    if isinstance(answer, list):
        for item in answer:
            if isinstance(item, str):
                yield item
    elif isinstance(answer, str):
        yield answer


def _canonical_answer(answer: object) -> str:
    if isinstance(answer, list):
        return next((item for item in answer if isinstance(item, str)), "")
    if isinstance(answer, str):
        return answer
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
