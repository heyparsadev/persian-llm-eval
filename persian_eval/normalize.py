"""Persian text normalization utilities used by deterministic scorers."""

from __future__ import annotations

import re
import string
import unicodedata

ARABIC_TO_PERSIAN = str.maketrans(
    {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "آ": "آ",
    }
)

DIGITS = str.maketrans(
    {
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    }
)

DIACRITICS_RE = re.compile(r"[\u064b-\u065f\u0670]")
WHITESPACE_RE = re.compile(r"\s+")
PERSIAN_PUNCTUATION = "،؛؟«»٪٫٬…ـ"
PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation + PERSIAN_PUNCTUATION)


def normalize_persian(text: object) -> str:
    """Normalize Persian/Arabic variants, digits, diacritics, and whitespace."""

    if text is None:
        return ""
    value = unicodedata.normalize("NFKC", str(text))
    value = value.translate(ARABIC_TO_PERSIAN)
    value = value.translate(DIGITS)
    value = value.replace("\u200c", " ")
    value = value.replace("\u200f", " ")
    value = DIACRITICS_RE.sub("", value)
    value = WHITESPACE_RE.sub(" ", value)
    return value.strip().lower()


def strip_punctuation(text: object) -> str:
    """Normalize text and remove punctuation."""

    return WHITESPACE_RE.sub(" ", normalize_persian(text).translate(PUNCTUATION_TABLE)).strip()


def tokenize(text: object) -> list[str]:
    """Tokenize normalized Persian text with a whitespace baseline."""

    cleaned = strip_punctuation(text)
    if not cleaned:
        return []
    return cleaned.split()
