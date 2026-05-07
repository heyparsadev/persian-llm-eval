"""Dataset loading and validation for Persian Eval JSONL files."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .normalize import strip_punctuation


class DatasetError(ValueError):
    """Raised when a dataset row does not match the v1 schema."""


@dataclass(frozen=True)
class DatasetRecord:
    id: str
    track: str
    prompt: str
    choices: list[str] | None
    answer: Any
    metadata: dict[str, Any]
    source: str
    split: str

    @classmethod
    def from_dict(cls, row: dict[str, Any], *, row_number: int | None = None) -> DatasetRecord:
        prefix = f"row {row_number}: " if row_number is not None else ""
        required = ["id", "track", "prompt", "answer", "metadata", "source", "split"]
        missing = [key for key in required if key not in row]
        if missing:
            raise DatasetError(f"{prefix}missing required field(s): {', '.join(missing)}")

        choices = row.get("choices")
        if choices is not None and (
            not isinstance(choices, list) or not all(isinstance(item, str) for item in choices)
        ):
            raise DatasetError(f"{prefix}choices must be null or a list of strings")

        metadata = row["metadata"]
        if not isinstance(metadata, dict):
            raise DatasetError(f"{prefix}metadata must be an object")

        record = cls(
            id=_require_str(row, "id", prefix),
            track=_require_str(row, "track", prefix),
            prompt=_require_str(row, "prompt", prefix),
            choices=choices,
            answer=row["answer"],
            metadata=metadata,
            source=_require_str(row, "source", prefix),
            split=_require_str(row, "split", prefix),
        )
        record.validate()
        return record

    def validate(self) -> None:
        if not self.id:
            raise DatasetError("id cannot be empty")
        if not self.track:
            raise DatasetError(f"{self.id}: track cannot be empty")
        if not self.prompt.strip():
            raise DatasetError(f"{self.id}: prompt cannot be empty")
        scoring = self.metadata.get("scoring")
        if scoring not in {"mcq", "exact", "f1", "instruction"}:
            raise DatasetError(
                f"{self.id}: metadata.scoring must be mcq, exact, f1, or instruction"
            )
        if scoring == "mcq":
            if not self.choices:
                raise DatasetError(f"{self.id}: mcq rows require choices")
            answer_index = self.metadata.get("answer_index")
            if answer_index is not None and not (
                isinstance(answer_index, int) and 0 <= answer_index < len(self.choices)
            ):
                raise DatasetError(f"{self.id}: metadata.answer_index is out of range")
        if scoring == "instruction" and not isinstance(self.answer, dict):
            raise DatasetError(f"{self.id}: instruction rows require an object answer")


def _require_str(row: dict[str, Any], key: str, prefix: str) -> str:
    value = row[key]
    if not isinstance(value, str):
        raise DatasetError(f"{prefix}{key} must be a string")
    return value


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for row_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise DatasetError(f"{path}: row {row_number}: invalid JSON: {exc}") from exc
    return rows


def load_records(
    paths: Iterable[str | Path],
    *,
    split: str | None = None,
    tasks: set[str] | None = None,
) -> list[DatasetRecord]:
    records: list[DatasetRecord] = []
    for path in paths:
        for row_number, row in enumerate(read_jsonl(path), start=1):
            record = DatasetRecord.from_dict(row, row_number=row_number)
            if split and record.split != split:
                continue
            if tasks and record.track not in tasks:
                continue
            records.append(record)
    validate_record_set(records)
    return records


def validate_record_set(records: list[DatasetRecord]) -> None:
    seen_ids: set[str] = set()
    for record in records:
        if record.id in seen_ids:
            raise DatasetError(f"duplicate id: {record.id}")
        seen_ids.add(record.id)


def duplicate_prompts(records: Iterable[DatasetRecord]) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    duplicates: list[tuple[str, str]] = []
    for record in records:
        prompt_key = strip_punctuation(record.prompt)
        if prompt_key in seen:
            duplicates.append((seen[prompt_key], record.id))
        else:
            seen[prompt_key] = record.id
    return duplicates
