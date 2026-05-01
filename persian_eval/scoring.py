"""Deterministic scorers for Persian Eval v1."""

from __future__ import annotations

from typing import Any

from .dataset import DatasetRecord
from .normalize import normalize_persian, strip_punctuation, tokenize

DEFAULT_LABELS = ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح"]


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
    raise ValueError(f"Unsupported scoring type: {scoring}")


def score_mcq(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    labels = record.metadata.get("choice_labels") or DEFAULT_LABELS[: len(record.choices or [])]
    answer_index = record.metadata.get("answer_index")
    if answer_index is None:
        answer_index = _find_answer_index(record)
    predicted_index = extract_choice_index(prediction, record.choices or [], labels)
    score = 1.0 if predicted_index == answer_index else 0.0
    return score, {"predicted_index": predicted_index, "answer_index": answer_index}


def score_exact(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    accepted = _accepted_answers(record.answer)
    normalized_prediction = strip_punctuation(prediction)
    normalized_accepted = [strip_punctuation(item) for item in accepted]
    score = 1.0 if normalized_prediction in normalized_accepted else 0.0
    return score, {"accepted": accepted, "normalized_prediction": normalized_prediction}


def score_f1(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    accepted = _accepted_answers(record.answer)
    prediction_tokens = tokenize(prediction)
    best = 0.0
    best_answer = ""
    for answer in accepted:
        current = token_f1(prediction_tokens, tokenize(answer))
        if current > best:
            best = current
            best_answer = answer
    return best, {"best_answer": best_answer}


def score_instruction(record: DatasetRecord, prediction: str) -> tuple[float, dict[str, Any]]:
    constraints = dict(record.answer)
    normalized_prediction = normalize_persian(prediction)
    checks: dict[str, bool] = {}

    required_keywords = constraints.get("required_keywords", [])
    if required_keywords:
        checks["required_keywords"] = all(normalize_persian(keyword) in normalized_prediction for keyword in required_keywords)

    forbidden = constraints.get("forbidden", [])
    if forbidden:
        checks["forbidden"] = all(normalize_persian(item) not in normalized_prediction for item in forbidden)

    words = tokenize(prediction)
    if "min_words" in constraints:
        checks["min_words"] = len(words) >= int(constraints["min_words"])
    if "max_words" in constraints:
        checks["max_words"] = len(words) <= int(constraints["max_words"])
    if "required_prefix" in constraints:
        checks["required_prefix"] = normalized_prediction.startswith(normalize_persian(constraints["required_prefix"]))
    if "required_suffix" in constraints:
        checks["required_suffix"] = normalized_prediction.endswith(normalize_persian(constraints["required_suffix"]))

    if not checks:
        return 0.0, {"checks": checks, "constraint_score": 0.0}
    passed = sum(1 for value in checks.values() if value)
    constraint_score = passed / len(checks)
    strict_score = 1.0 if passed == len(checks) else 0.0
    return strict_score, {"checks": checks, "constraint_score": constraint_score}


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
