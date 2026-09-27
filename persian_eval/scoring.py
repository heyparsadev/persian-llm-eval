"""Deterministic scorers for Persian Eval v1."""

from __future__ import annotations

import json
import re
from typing import Any

from .dataset import DatasetRecord
from .normalize import (
    DIGITS,
    normalize_keep_zwnj,
    normalize_persian,
    strip_punctuation,
    tokenize,
)

DEFAULT_LABELS = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح"]

# Leading list markers, numbering, quotes, and markdown that may precede the
# first real letter of a line (acrostic checks look past them).
LINE_MARKER_RE = re.compile(r"^[\s\d\-\*•#>\.\)\(:،؛«»\"'`_~|\[\]]+")


def score_record(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    scoring = record.metadata.get("scoring")
    if scoring == "mcq":
        return score_mcq(record, prediction)
    if scoring == "exact":
        return score_exact(record, prediction)
    if scoring == "f1":
        return score_f1(record, prediction)
    if scoring == "instruction":
        return score_instruction(record, prediction)
    if scoring == "json":
        return score_json(record, prediction)
    raise ValueError(f"Unsupported scoring type: {scoring}")


def score_mcq(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    labels = record.metadata.get("choice_labels") or DEFAULT_LABELS[: len(record.choices or [])]
    answer_index = record.metadata.get("answer_index")
    if answer_index is None:
        answer_index = _find_answer_index(record)
    predicted_index = None
    scored_candidate = ""
    for candidate in prediction_candidates(prediction):
        predicted_index = extract_choice_index(candidate, record.choices or [], labels)
        if predicted_index is not None:
            scored_candidate = candidate
            break
    score = 1.0 if predicted_index == answer_index else 0.0
    return score, {
        "predicted_index": predicted_index,
        "answer_index": answer_index,
        "scored_candidate": scored_candidate,
    }


def score_exact(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    accepted = _accepted_answers(record.answer)
    normalized_accepted = [strip_punctuation(item) for item in accepted]
    accepted_token_lists = [tokenize(item) for item in accepted]
    for candidate in prediction_candidates(prediction):
        normalized_prediction = strip_punctuation(candidate)
        if normalized_prediction in normalized_accepted:
            return 1.0, {
                "accepted": accepted,
                "normalized_prediction": normalized_prediction,
                "scored_candidate": candidate,
                "match_kind": "exact",
            }
        candidate_tokens = tokenize(candidate)
        for accepted_tokens in accepted_token_lists:
            if accepted_tokens and _contains_subsequence(candidate_tokens, accepted_tokens):
                return 1.0, {
                    "accepted": accepted,
                    "normalized_prediction": normalized_prediction,
                    "scored_candidate": candidate,
                    "match_kind": "subsequence",
                }
    normalized_prediction = strip_punctuation(strip_reasoning(prediction))
    return 0.0, {
        "accepted": accepted,
        "normalized_prediction": normalized_prediction,
        "scored_candidate": strip_reasoning(prediction),
        "match_kind": "none",
    }


def _contains_subsequence(haystack: list[str], needle: list[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    for index in range(len(haystack) - len(needle) + 1):
        if haystack[index : index + len(needle)] == needle:
            return True
    return False


def score_f1(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    accepted = _accepted_answers(record.answer)
    best = 0.0
    best_answer = ""
    best_candidate = ""
    for candidate in prediction_candidates(prediction):
        prediction_tokens = tokenize(candidate)
        for answer in accepted:
            answer_tokens = tokenize(answer)
            current = token_f1(prediction_tokens, answer_tokens)
            window = _best_window_f1(prediction_tokens, answer_tokens)
            current = max(current, window)
            if current > best:
                best = current
                best_answer = answer
                best_candidate = candidate
    return best, {"best_answer": best_answer, "scored_candidate": best_candidate}


def _best_window_f1(prediction_tokens: list[str], answer_tokens: list[str]) -> float:
    """Best F1 across all sliding windows of size |answer_tokens| in the prediction."""

    if not prediction_tokens or not answer_tokens:
        return 0.0
    size = len(answer_tokens)
    if size > len(prediction_tokens):
        return 0.0
    best = 0.0
    for start in range(len(prediction_tokens) - size + 1):
        window = prediction_tokens[start : start + size]
        score = token_f1(window, answer_tokens)
        best = max(best, score)
    return best


def score_instruction(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    constraints = dict(record.answer)
    prediction = strip_reasoning(prediction)
    normalized_prediction = normalize_persian(prediction)
    checks: dict[str, bool] = {}

    required_keywords = constraints.get("required_keywords", [])
    if required_keywords:
        checks["required_keywords"] = all(
            normalize_persian(keyword) in normalized_prediction for keyword in required_keywords
        )

    forbidden = constraints.get("forbidden", [])
    if forbidden:
        checks["forbidden"] = all(
            normalize_persian(item) not in normalized_prediction for item in forbidden
        )

    words = tokenize(prediction)
    if "min_words" in constraints:
        checks["min_words"] = len(words) >= int(constraints["min_words"])
    if "max_words" in constraints:
        checks["max_words"] = len(words) <= int(constraints["max_words"])
    if "required_prefix" in constraints:
        checks["required_prefix"] = normalized_prediction.startswith(
            normalize_persian(constraints["required_prefix"])
        )
    if "required_suffix" in constraints:
        checks["required_suffix"] = normalized_prediction.endswith(
            normalize_persian(constraints["required_suffix"])
        )

    checks.update(_extended_instruction_checks(constraints, prediction, normalized_prediction))

    if not checks:
        return 0.0, {"checks": checks, "constraint_score": 0.0}
    passed = sum(1 for value in checks.values() if value)
    constraint_score = passed / len(checks)
    strict_score = 1.0 if passed == len(checks) else 0.0
    return strict_score, {"checks": checks, "constraint_score": constraint_score}


def _extended_instruction_checks(
    constraints: dict[str, Any], prediction: str, normalized_prediction: str
) -> dict[str, bool]:
    """Constraint types added for the practical split (all optional, all strict).

    - ``required_any``: list of groups; each group needs at least one option present.
    - ``forbidden_chars``: characters that must not appear (lipograms).
    - ``required_exact`` / ``forbidden_exact``: substrings matched with ZWNJ kept
      significant, so «می‌خواهم» and «می خواهم» are different strings. A
      ``required_exact`` entry may be a list of acceptable spellings.
    - ``starts_with`` / ``ends_with``: like ``required_prefix``/``required_suffix``
      but ignoring punctuation, so a closing period or opening quote is harmless.
    - ``line_count``: exact number of non-empty lines.
    - ``line_initials``: first letter of each non-empty line, in order (acrostic).
    - ``lines_end_with``: every non-empty line ends with this suffix (or any of a list).
    - ``distinct_line_endings``: the last word of every line is different.
    - ``word_initial``: every word starts with this letter.
    """

    checks: dict[str, bool] = {}
    required_any = constraints.get("required_any", [])
    if required_any:
        checks["required_any"] = all(
            any(normalize_persian(option) in normalized_prediction for option in group)
            for group in required_any
        )

    forbidden_chars = constraints.get("forbidden_chars", [])
    if forbidden_chars:
        checks["forbidden_chars"] = all(
            normalize_persian(char) not in normalized_prediction for char in forbidden_chars
        )

    loose_prediction = strip_punctuation(prediction)
    if "starts_with" in constraints:
        checks["starts_with"] = loose_prediction.startswith(
            strip_punctuation(constraints["starts_with"])
        )
    if "ends_with" in constraints:
        checks["ends_with"] = loose_prediction.endswith(strip_punctuation(constraints["ends_with"]))

    exact_prediction = normalize_keep_zwnj(prediction)
    required_exact = constraints.get("required_exact", [])
    if required_exact:
        checks["required_exact"] = all(
            any(normalize_keep_zwnj(option) in exact_prediction for option in _options(item))
            for item in required_exact
        )
    forbidden_exact = constraints.get("forbidden_exact", [])
    if forbidden_exact:
        checks["forbidden_exact"] = all(
            normalize_keep_zwnj(item) not in exact_prediction for item in forbidden_exact
        )

    lines = [line.strip() for line in prediction.splitlines() if strip_punctuation(line)]
    if "line_count" in constraints:
        checks["line_count"] = len(lines) == int(constraints["line_count"])
    if "line_initials" in constraints:
        expected = [_fold_letter(letter) for letter in constraints["line_initials"]]
        actual = [_first_letter(line) for line in lines]
        checks["line_initials"] = actual == expected
    if "lines_end_with" in constraints:
        suffixes = constraints["lines_end_with"]
        if isinstance(suffixes, str):
            suffixes = [suffixes]
        normalized_suffixes = [strip_punctuation(item) for item in suffixes]
        checks["lines_end_with"] = bool(lines) and all(
            any(strip_punctuation(line).endswith(suffix) for suffix in normalized_suffixes)
            for line in lines
        )
    if constraints.get("distinct_line_endings"):
        last_words = [tokenize(line)[-1] for line in lines if tokenize(line)]
        checks["distinct_line_endings"] = len(last_words) == len(set(last_words))
    if "word_initial" in constraints:
        letter = _fold_letter(constraints["word_initial"])
        words = tokenize(prediction)
        checks["word_initial"] = bool(words) and all(
            _fold_letter(word[0]) == letter for word in words
        )
    return checks


def _options(item: Any) -> list[Any]:
    return item if isinstance(item, list) else [item]


def _first_letter(line: str) -> str:
    stripped = LINE_MARKER_RE.sub("", normalize_persian(line))
    return _fold_letter(stripped[:1])


def _fold_letter(letter: str) -> str:
    # Alef with madda counts as alef for acrostics and alliteration.
    value = normalize_persian(letter)[:1]
    return "ا" if value == "آ" else value


def score_json(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    """Field-level accuracy of a JSON object extracted from the prediction.

    ``record.answer`` maps each expected key to its gold value. A list value
    means "any of these". ``null`` gold values are satisfied by null, an empty
    string, or a missing key (this is how items test for hallucinated fields).
    Numbers compare numerically, so ``"8,500,000"`` and ``8500000`` both match.
    """

    expected = record.answer
    parsed = extract_json_object(prediction)
    if parsed is None:
        return 0.0, {"parsed": False, "fields": {}, "field_accuracy": 0.0}
    fields = {
        key: _json_value_matches(gold, parsed.get(key, _MISSING)) for key, gold in expected.items()
    }
    accuracy = sum(1 for ok in fields.values() if ok) / len(fields) if fields else 0.0
    return accuracy, {
        "parsed": True,
        "fields": fields,
        "field_accuracy": accuracy,
        "extra_keys": sorted(key for key in parsed if key not in expected),
    }


class _Missing:
    pass


_MISSING = _Missing()


def extract_json_object(prediction: str) -> dict[str, Any] | None:
    """Return the first JSON object found in a response, tolerating fences and prose."""

    text = strip_reasoning(prediction).translate(DIGITS)
    candidates = [
        match.group(1) for match in re.finditer(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    ]
    candidates.append(text)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        for start in [index for index, char in enumerate(candidate) if char == "{"]:
            try:
                value, _ = decoder.raw_decode(candidate, start)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    return None


def _json_value_matches(gold: Any, value: Any) -> bool:
    if isinstance(gold, list):
        return any(_json_value_matches(option, value) for option in gold)
    if gold is None:
        return value is _MISSING or value is None or (isinstance(value, str) and not value.strip())
    if value is _MISSING or value is None:
        return False
    if isinstance(gold, bool):
        # JSON booleans, or the strings "true"/"false"; never 0/1.
        text = value.strip().lower() if isinstance(value, str) else None
        return value is gold or text == str(gold).lower()
    if isinstance(gold, (int, float)):
        number = _as_number(value)
        return number is not None and abs(number - float(gold)) <= 1e-6 * max(1.0, abs(gold))
    return _text_matches(str(gold), value)


def _text_matches(gold: str, value: Any) -> bool:
    # Exact after normalisation, or the gold phrase inside a slightly longer value
    # ("محله سعادت‌آباد" for "سعادت آباد").
    gold_tokens = tokenize(gold)
    value_tokens = tokenize(value)
    return value_tokens == gold_tokens or (
        bool(gold_tokens)
        and len(value_tokens) <= len(gold_tokens) + 2
        and _contains_subsequence(value_tokens, gold_tokens)
    )


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[\s,٬_']", "", normalize_persian(value)).replace("٫", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def token_f1(prediction_tokens: list[str], answer_tokens: list[str]) -> float:
    if not prediction_tokens or not answer_tokens:
        return 1.0 if prediction_tokens == answer_tokens else 0.0
    common = 0
    remaining = answer_tokens.copy()
    for token in prediction_tokens:
        if token in remaining:
            common += 1
            remaining.remove(token)
    if common == 0:
        return 0.0
    precision = common / len(prediction_tokens)
    recall = common / len(answer_tokens)
    return 2 * precision * recall / (precision + recall)


def extract_choice_index(prediction: str, choices: list[str], labels: list[str]) -> int | None:
    normalized = strip_punctuation(prediction)
    prediction_tokens = normalized.split()
    if prediction_tokens:
        first = prediction_tokens[0]
        if first in labels:
            return labels.index(first)
        if first == "گزینه" and len(prediction_tokens) > 1:
            label_token = prediction_tokens[1]
            if label_token == "ی" and len(prediction_tokens) > 2:
                label_token = prediction_tokens[2]
            if label_token in labels:
                return labels.index(label_token)

    matched: list[int] = []
    for index, choice in enumerate(choices):
        normalized_choice = strip_punctuation(choice)
        if normalized_choice and normalized_choice in normalized:
            matched.append(index)
    if len(matched) == 1:
        return matched[0]
    return None


def strip_reasoning(prediction: str) -> str:
    """Remove common hidden/visible reasoning wrappers before deterministic scoring."""

    value = str(prediction or "").strip()
    if "</think>" in value:
        value = value.split("</think>")[-1].strip()
    value = re.sub(r"<think>.*?</think>", "", value, flags=re.DOTALL | re.IGNORECASE).strip()
    return value


def prediction_candidates(prediction: str) -> list[str]:
    """Return likely final-answer snippets, ordered from most to least specific."""

    stripped = strip_reasoning(prediction)
    candidates: list[str] = []
    marker_patterns = [
        r"(?:پاسخ\s*نهایی|جواب\s*نهایی|نتیجه\s*نهایی|پاسخ|جواب|نتیجه)\s*[:：]\s*(.+)",
        r"(?:final\s*answer|answer|therefore)\s*[:：]\s*(.+)",
    ]
    for pattern in marker_patterns:
        for match in re.finditer(pattern, stripped, flags=re.IGNORECASE | re.DOTALL):
            candidates.append(match.group(1).strip())
    for match in re.finditer(r"\\boxed\{([^{}]+)\}", stripped):
        candidates.append(match.group(1).strip())
    for line in reversed([item.strip() for item in stripped.splitlines() if item.strip()]):
        candidates.append(line)
    candidates.append(stripped)
    candidates.append(str(prediction or "").strip())

    deduped: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        cleaned = candidate.strip()
        if not cleaned:
            continue
        key = normalize_persian(cleaned)
        if key and key not in seen:
            seen.add(key)
            deduped.append(cleaned)
    return deduped


def _find_answer_index(record: DatasetRecord) -> int:
    answer = strip_punctuation(record.answer)
    for index, choice in enumerate(record.choices or []):
        if strip_punctuation(choice) == answer:
            return index
    raise ValueError(f"{record.id}: cannot infer answer_index from answer")


def _accepted_answers(answer: Any) -> list[str]:
    if isinstance(answer, list):
        return [str(item) for item in answer]
    return [str(answer)]
