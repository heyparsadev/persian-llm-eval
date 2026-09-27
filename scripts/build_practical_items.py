#!/usr/bin/env python3
"""Build the Persian Eval `practical` split: data/persian_eval_v1.practical.jsonl.

Six tracks x 25 items of everyday Persian work that people actually bring to an
assistant, plus constrained creative writing:

- practical_writing     letters, SMS, register shifts, support replies     (instruction)
- practical_editing     wrong keyboard layout, Finglish, spelling, ZWNJ     (exact / f1 / instruction)
- practical_numbers     Jalali calendar, cheque amounts, toman/rial, maths  (exact)
- practical_extraction  ads, bank SMS, tickets, receipts -> JSON            (json)
- practical_pragmatics  taarof, social formulas, natural translation        (mcq)
- practical_creative    acrostic, lipogram, rhyme, anagram, riddle, abjad   (instruction / exact)

Answers that can be computed are computed here (Jalali<->Gregorian conversion,
number words, keyboard-layout mapping, abjad) rather than typed by hand. Every
non-MCQ item carries metadata.reference_response and the build fails unless the
scorer gives each reference a perfect score, which proves the constraints are
satisfiable and the answer keys parse. Items are model-drafted, so they ship as
metadata.review.status = "pending_review" until a native speaker reviews them.

Usage:
    python scripts/build_practical_items.py           # (re)write the JSONL
    python scripts/build_practical_items.py --check   # fail if the file is stale
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from persian_eval.dataset import DatasetRecord  # noqa: E402
from persian_eval.scoring import score_record  # noqa: E402

OUTPUT = ROOT / "data" / "persian_eval_v1.practical.jsonl"
SOURCE = "curated:practical-v1"
REVIEW = {
    "author": "claude-code",
    "reviewers": [],
    "status": "pending_review",
    "notes": "Model-drafted for the practical split; needs native-speaker review.",
}
LABELS = ["الف", "ب", "پ", "ت"]
# Where the correct option lands, cycled per track so no position dominates.
ANSWER_POSITIONS = [1, 3, 0, 2, 2, 0, 3, 1, 0, 1, 3, 2]

# ---------------------------------------------------------------------------
# Jalali (Solar Hijri) calendar — the jalaali-js algorithm (Borkowski breaks).
# ---------------------------------------------------------------------------

_BREAKS = [
    -61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210,
    1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178,
]  # fmt: skip


def _div(a: int, b: int) -> int:
    quotient = abs(a) // abs(b)
    return quotient if (a >= 0) == (b > 0) else -quotient


def _mod(a: int, b: int) -> int:
    return a - _div(a, b) * b


def _jal_cal(jy: int) -> tuple[int, int, int]:
    gy = jy + 621
    leap_j = -14
    jp = _BREAKS[0]
    jump = 0
    if jy < jp or jy >= _BREAKS[-1]:
        raise ValueError(f"Jalali year out of range: {jy}")
    for jm in _BREAKS[1:]:
        jump = jm - jp
        if jy < jm:
            break
        leap_j += _div(jump, 33) * 8 + _div(_mod(jump, 33), 4)
        jp = jm
    n = jy - jp
    leap_j += _div(n, 33) * 8 + _div(_mod(n, 33) + 3, 4)
    if _mod(jump, 33) == 4 and jump - n == 4:
        leap_j += 1
    leap_g = _div(gy, 4) - _div((_div(gy, 100) + 1) * 3, 4) - 150
    march = 20 + leap_j - leap_g
    if jump - n < 6:
        n = n - jump + _div(jump + 4, 33) * 33
    leap = _mod(_mod(n + 1, 33) - 1, 4)
    if leap == -1:
        leap = 4
    return leap, gy, march


def _g2d(gy: int, gm: int, gd: int) -> int:
    d = (
        _div((gy + _div(gm - 8, 6) + 100100) * 1461, 4)
        + _div(153 * _mod(gm + 9, 12) + 2, 5)
        + gd
        - 34840408
    )
    return d - _div(_div(gy + 100100 + _div(gm - 8, 6), 100) * 3, 4) + 752


def _d2g(jdn: int) -> datetime.date:
    j = 4 * jdn + 139361631
    j = j + _div(_div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908
    i = _div(_mod(j, 1461), 4) * 5 + 308
    gd = _div(_mod(i, 153), 5) + 1
    gm = _mod(_div(i, 153), 12) + 1
    gy = _div(j, 1461) - 100100 + _div(8 - gm, 6)
    return datetime.date(gy, gm, gd)


def _j2d(jy: int, jm: int, jd: int) -> int:
    _, gy, march = _jal_cal(jy)
    return _g2d(gy, 3, march) + (jm - 1) * 31 - _div(jm, 7) * (jm - 7) + jd - 1


def _d2j(jdn: int) -> tuple[int, int, int]:
    gy = _d2g(jdn).year
    jy = gy - 621
    leap, _, march = _jal_cal(jy)
    k = jdn - _g2d(gy, 3, march)
    if k >= 0:
        if k <= 185:
            return jy, 1 + _div(k, 31), _mod(k, 31) + 1
        k -= 186
    else:
        jy -= 1
        k += 179
        if leap == 1:
            k += 1
    return jy, 7 + _div(k, 30), _mod(k, 30) + 1


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> datetime.date:
    return _d2g(_j2d(jy, jm, jd))


def gregorian_to_jalali(date: datetime.date) -> tuple[int, int, int]:
    return _d2j(_g2d(date.year, date.month, date.day))


def add_days_jalali(jy: int, jm: int, jd: int, days: int) -> tuple[int, int, int]:
    return _d2j(_j2d(jy, jm, jd) + days)


def is_leap_jalali(jy: int) -> bool:
    return _jal_cal(jy)[0] == 0


def _self_check_calendar() -> None:
    anchors = {
        (1399, 1, 1): datetime.date(2020, 3, 20),
        (1400, 1, 1): datetime.date(2021, 3, 21),
        (1403, 1, 1): datetime.date(2024, 3, 20),
        (1403, 12, 30): datetime.date(2025, 3, 20),
        (1404, 1, 1): datetime.date(2025, 3, 21),
        (1405, 1, 1): datetime.date(2026, 3, 21),
        (1357, 11, 22): datetime.date(1979, 2, 11),
    }
    for jalali, gregorian in anchors.items():
        assert jalali_to_gregorian(*jalali) == gregorian, jalali
        assert gregorian_to_jalali(gregorian) == jalali, gregorian
    assert [year for year in range(1395, 1410) if is_leap_jalali(year)] == [1395, 1399, 1403, 1408]


JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]  # fmt: skip
JALALI_MONTH_ALTERNATES = {5: ["امرداد"]}
GREGORIAN_MONTHS_FA = [
    "ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
    "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر",
]  # fmt: skip
GREGORIAN_MONTH_ALTERNATES = {4: ["آپریل"], 5: ["می"], 6: ["جون"], 7: ["جولای"], 8: ["آگوست"]}
GREGORIAN_MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]  # fmt: skip
# datetime.weekday(): Monday == 0.
WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
WEEKDAY_ALTERNATES = {
    "سه‌شنبه": ["سهشنبه"],
    "چهارشنبه": ["چهار‌شنبه"],
    "پنجشنبه": ["پنج‌شنبه"],
    "یکشنبه": ["یک‌شنبه"],
    "دوشنبه": ["دو‌شنبه"],
}

PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa(value: object) -> str:
    """Render digits in Persian script."""

    return str(value).translate(PERSIAN_DIGITS)


def fa_money(value: int) -> str:
    """Persian digits with the Arabic thousands separator: ۱٬۲۵۰٬۰۰۰."""

    return f"{value:,}".replace(",", "٬").translate(PERSIAN_DIGITS)


def jalali_text(jy: int, jm: int, jd: int) -> str:
    return fa(f"{jd} {JALALI_MONTHS[jm - 1]} {jy}")


def weekday_of_jalali(jy: int, jm: int, jd: int) -> str:
    return WEEKDAYS[jalali_to_gregorian(jy, jm, jd).weekday()]


def jalali_answers(jy: int, jm: int, jd: int) -> list[str]:
    names = [JALALI_MONTHS[jm - 1], *JALALI_MONTH_ALTERNATES.get(jm, [])]
    answers = [f"{jd} {name} {jy}" for name in names]
    answers += [f"{jy}/{jm:02d}/{jd:02d}", f"{jy}/{jm}/{jd}"]
    return list(dict.fromkeys(answers))


def gregorian_answers(date: datetime.date) -> list[str]:
    d, m, y = date.day, date.month, date.year
    names = [
        GREGORIAN_MONTHS_FA[m - 1],
        *GREGORIAN_MONTH_ALTERNATES.get(m, []),
        GREGORIAN_MONTHS_EN[m - 1],
    ]
    answers = [f"{d} {name} {y}" for name in names]
    answers += [
        f"{GREGORIAN_MONTHS_EN[m - 1]} {d}, {y}",
        f"{y}-{m:02d}-{d:02d}",
        f"{y}/{m:02d}/{d:02d}",
    ]
    return answers


def weekday_answers(name: str) -> list[str]:
    if name == "شنبه":
        # A bare «شنبه» is a token inside «یک‌شنبه»/«سه‌شنبه», so the exact
        # scorer's subsequence fallback cannot tell them apart. Avoid it.
        raise ValueError("pick a date that does not fall on Saturday")
    return [name, *WEEKDAY_ALTERNATES.get(name, [])]


# ---------------------------------------------------------------------------
# Persian number words (cheque style).
# ---------------------------------------------------------------------------

_ONES = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
_TEENS = [
    "ده", "یازده", "دوازده", "سیزده", "چهارده",
    "پانزده", "شانزده", "هفده", "هجده", "نوزده",
]  # fmt: skip
_TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
_HUNDREDS = ["", "صد", "دویست", "سیصد", "چهارصد", "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد"]
_SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون"]


def _three_digits(value: int) -> str:
    parts = []
    hundreds, rest = divmod(value, 100)
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if 10 <= rest < 20:
        parts.append(_TEENS[rest - 10])
    else:
        tens, ones = divmod(rest, 10)
        if tens:
            parts.append(_TENS[tens])
        if ones:
            parts.append(_ONES[ones])
    return " و ".join(parts)


def number_to_words(value: int) -> str:
    if value == 0:
        return "صفر"
    groups = []
    scale = 0
    while value:
        value, group = divmod(value, 1000)
        if group:
            words = _three_digits(group)
            groups.append(f"{words} {_SCALES[scale]}".strip())
        scale += 1
    return " و ".join(reversed(groups))


def number_word_variants(value: int) -> list[str]:
    canonical = number_to_words(value)
    variants = [canonical]
    if "هجده" in canonical:
        variants.append(canonical.replace("هجده", "هیجده"))
    return variants


# ---------------------------------------------------------------------------
# Keyboard layouts (ISIRI 9147 standard Persian vs US QWERTY), letters only.
# Letters whose key differs between the standard and the legacy Windows layout
# (پ, ژ, آ, ئ) are deliberately absent.
# ---------------------------------------------------------------------------

FA_TO_QWERTY = {
    "ض": "q", "ص": "w", "ث": "e", "ق": "r", "ف": "t", "غ": "y", "ع": "u",
    "ه": "i", "خ": "o", "ح": "p", "ج": "[", "چ": "]",
    "ش": "a", "س": "s", "ی": "d", "ب": "f", "ل": "g", "ا": "h", "ت": "j",
    "ن": "k", "م": "l", "ک": ";", "گ": "'",
    "ظ": "z", "ط": "x", "ز": "c", "ر": "v", "ذ": "b", "د": "n", "و": ",",
    " ": " ",
}  # fmt: skip
QWERTY_TO_FA = {key: letter for letter, key in FA_TO_QWERTY.items()}


def typed_with_english_layout(persian: str) -> str:
    return "".join(FA_TO_QWERTY[char] for char in persian)


def typed_with_persian_layout(english: str) -> str:
    return "".join(QWERTY_TO_FA[char] for char in english)


# ---------------------------------------------------------------------------
# Abjad (ابجد کبیر).
# ---------------------------------------------------------------------------

ABJAD = {
    "ا": 1, "آ": 1, "ب": 2, "پ": 2, "ج": 3, "چ": 3, "د": 4, "ه": 5, "و": 6,
    "ز": 7, "ژ": 7, "ح": 8, "ط": 9, "ی": 10, "ک": 20, "گ": 20, "ل": 30,
    "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90, "ق": 100, "ر": 200,
    "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800, "ظ": 900, "غ": 1000,
}  # fmt: skip


def abjad(word: str) -> int:
    return sum(ABJAD[char] for char in word)


# ---------------------------------------------------------------------------
# Item constructors.
# ---------------------------------------------------------------------------

TRACK_TOKENS = {
    "practical_writing": "writing",
    "practical_editing": "editing",
    "practical_numbers": "numbers",
    "practical_extraction": "extraction",
    "practical_pragmatics": "pragmatics",
    "practical_creative": "creative",
}


def _base(track: str, category: str, prompt: str, scoring: str) -> dict[str, Any]:
    return {
        "track": track,
        "prompt": prompt,
        "choices": None,
        "metadata": {"scoring": scoring, "category": category},
    }


def mcq(track: str, category: str, prompt: str, correct: str, distractors: list[str]) -> dict:
    item = _base(track, category, prompt, "mcq")
    item["mcq"] = (correct, distractors)
    return item


def exact(track: str, category: str, prompt: str, answers: list[str]) -> dict:
    item = _base(track, category, prompt, "exact")
    item["answer"] = answers
    item["metadata"]["reference_response"] = answers[0]
    return item


def f1(track: str, category: str, prompt: str, answers: list[str]) -> dict:
    item = _base(track, category, prompt, "f1")
    item["answer"] = answers
    item["metadata"]["reference_response"] = answers[0]
    return item


def instruction(
    track: str, category: str, prompt: str, constraints: dict[str, Any], reference: str
) -> dict:
    item = _base(track, category, prompt, "instruction")
    item["answer"] = constraints
    item["metadata"]["reference_response"] = reference
    return item


def extraction(category: str, text: str, keys: str, gold: dict[str, Any]) -> dict:
    prompt = (
        "از متن زیر اطلاعات خواسته‌شده را استخراج کن و یک شیء JSON با همین کلیدها برگردان:\n"
        f"{keys}\n"
        "عددها را بدون جداکننده و با رقم انگلیسی بنویس. اگر اطلاعاتی در متن نیامده، "
        "مقدار آن را null بگذار.\n\n"
        f"متن: «{text}»"
    )
    item = _base("practical_extraction", category, prompt, "json")
    item["answer"] = gold
    reference = {key: value[0] if isinstance(value, list) else value for key, value in gold.items()}
    item["metadata"]["reference_response"] = json.dumps(reference, ensure_ascii=False)
    return item


# ---------------------------------------------------------------------------
# practical_writing — everyday writing with checkable constraints.
# ---------------------------------------------------------------------------


def writing_items() -> list[dict]:
    t = "practical_writing"
    return [
        instruction(
            t,
            "formal_letter",
            "یک درخواست مرخصی یک‌روزه برای روز ۱۵ مهر خطاب به مدیرت بنویس. متن باید با "
            "«با سلام و احترام» شروع شود، با «با سپاس» تمام شود، عبارت «۱۵ مهر» و کلمه‌ی "
            "«مرخصی» در آن بیاید و بیشتر از ۶۰ کلمه نباشد.",
            {
                "starts_with": "با سلام و احترام",
                "ends_with": "با سپاس",
                "required_keywords": ["۱۵ مهر", "مرخصی"],
                "max_words": 70,
            },
            "با سلام و احترام\nاحتراماً به استحضار می‌رساند اینجانب برای رسیدگی به یک کار "
            "شخصی ضروری، به یک روز مرخصی در تاریخ ۱۵ مهر نیاز دارم. خواهشمندم با این درخواست "
            "موافقت فرمایید.\nبا سپاس",
        ),
        instruction(
            t,
            "sms",
            "یک پیامک کوتاه و مودبانه به منشی مطب دندان‌پزشکی بنویس و درخواست کن نوبتت از "
            "سه‌شنبه به پنج‌شنبه ساعت ۱۷ منتقل شود. هر دو روز را نام ببر، کلمه‌ی «لطفاً» را به "
            "کار ببر و حداکثر ۳۵ کلمه بنویس.",
            {
                "required_keywords": ["لطفاً"],
                "required_any": [
                    ["سه شنبه", "سهشنبه"],
                    ["پنج شنبه", "پنجشنبه"],
                    [
                        "17",
                        "پنج بعد از ظهر",
                        "پنج بعدازظهر",
                        "پنج عصر",
                        "5 عصر",
                        "5 بعد از ظهر",
                        "5 بعدازظهر",
                    ],
                ],
                "max_words": 42,
            },
            "سلام، وقت بخیر. لطفاً نوبت من را از سه‌شنبه به پنج‌شنبه ساعت ۱۷ منتقل کنید. "
            "از همکاری شما سپاسگزارم.",
        ),
        instruction(
            t,
            "register_formal",
            "این پیام محاوره‌ای را به فارسی رسمی و نوشتاری برگردان و فقط متن بازنویسی‌شده را "
            "بنویس: «سلام، فردا نمیتونم بیام سر کار چون مریضم. اگه میشه یه روز مرخصی بهم بدین.»",
            {
                "forbidden": ["نمیتونم", "نمی تونم", "بیام", "اگه", "مریضم"],
                "required_any": [
                    ["نمی توانم", "نمیتوانم", "قادر نیستم", "امکان حضور"],
                    ["بیمار", "کسالت", "ناخوش"],
                    ["مرخصی"],
                ],
                "max_words": 45,
            },
            "با سلام، به دلیل بیماری فردا نمی‌توانم در محل کار حاضر شوم. در صورت امکان، با یک "
            "روز مرخصی اینجانب موافقت فرمایید.",
        ),
        instruction(
            t,
            "register_colloquial",
            "این جمله‌ی رسمی را برای یک دوست صمیمی به زبان محاوره‌ای و خودمانی بازنویسی کن: "
            "«آیا امکان دارد فردا عصر به منزل ما تشریف بیاورید؟»",
            {
                "forbidden": ["تشریف", "منزل", "آیا", "امکان دارد"],
                "required_any": [
                    ["بیای", "میای", "می ای", "میایی", "می آی", "می آیی"],
                    ["خونه", "خونمون"],
                    ["فردا"],
                ],
                "max_words": 20,
            },
            "فردا عصر میای خونه‌ی ما؟",
        ),
        instruction(
            t,
            "customer_support",
            "مشتری عصبانی نوشته: «سفارشم یک هفته است نرسیده!». از طرف پشتیبانی فروشگاه یک پاسخ "
            "کوتاه و مودبانه بنویس که عذرخواهی کند و بگوید سفارش حداکثر تا ۴۸ ساعت آینده ارسال "
            "می‌شود. از کلمه‌های «مقصر» و «تقصیر» استفاده نکن و حداکثر ۵۰ کلمه بنویس.",
            {
                "required_any": [
                    ["عذرخواهی", "عذر میخواهیم", "پوزش", "متاسف", "ببخشید"],
                    ["48 ساعت", "چهل و هشت ساعت"],
                ],
                "forbidden": ["مقصر", "تقصیر"],
                "max_words": 58,
            },
            "مشتری گرامی، بابت تاخیر در ارسال سفارشتان صمیمانه عذرخواهی می‌کنیم. سفارش شما "
            "حداکثر تا ۴۸ ساعت آینده ارسال می‌شود و کد رهگیری برایتان پیامک خواهد شد. از صبر "
            "و شکیبایی شما سپاسگزاریم.",
        ),
        instruction(
            t,
            "summary",
            "این اطلاعیه را در یک جمله‌ی حداکثر ۲۵ کلمه‌ای خلاصه کن؛ نام محله، تاریخ و بازه‌ی "
            "ساعت قطعی حتماً در خلاصه بیاید:\n«به اطلاع ساکنان محترم محله‌ی نارمک می‌رساند که "
            "به دلیل تعمیر خط اصلی انتقال، آب منطقه در روز ۲۰ آبان از ساعت ۹ صبح تا ۳ "
            "بعدازظهر قطع خواهد بود. خواهشمند است آب مورد نیاز خود را از قبل ذخیره کنید. از "
            "صبر و شکیبایی شما سپاسگزاریم.»",
            {
                "required_any": [
                    ["نارمک"],
                    ["20 آبان", "بیستم آبان"],
                    ["ساعت 9", "9 صبح", "9 تا 3", "نه صبح", "نه تا سه"],
                    ["3 بعد", "تا 3", "سه بعد", "15"],
                ],
                "max_words": 30,
            },
            "آب محله‌ی نارمک روز ۲۰ آبان از ساعت ۹ صبح تا ۳ بعدازظهر به دلیل تعمیر خط اصلی "
            "قطع است.",
        ),
        instruction(
            t,
            "product_copy",
            "برای فروش یک کتری برقی در فروشگاه اینترنتی، توضیحی دقیقاً سه‌سطری بنویس که هر "
            "سطر یک ویژگی را بگوید. کلمه‌های «ظرفیت» و «گارانتی» باید در متن باشند.",
            {"line_count": 3, "required_keywords": ["ظرفیت", "گارانتی"], "max_words": 50},
            "ظرفیت ۱.۷ لیتر، مناسب برای خانواده‌های پرجمعیت\nخاموشی خودکار پس از جوش آمدن "
            "آب\nدارای ۱۸ ماه گارانتی رسمی",
        ),
        instruction(
            t,
            "academic_email",
            "یک ایمیل کوتاه و رسمی به استادی به نام دکتر رضایی بنویس و درخواست کن به‌عنوان "
            "دستیار پژوهشی در آزمایشگاهش همکاری کنی. ایمیل را با «استاد گرامی، جناب آقای دکتر "
            "رضایی» شروع کن، کلمه‌ی «رزومه» را به کار ببر و حداکثر ۷۰ کلمه بنویس.",
            {
                "starts_with": "استاد گرامی، جناب آقای دکتر رضایی",
                "required_keywords": ["رزومه", "دستیار"],
                "max_words": 80,
            },
            "استاد گرامی، جناب آقای دکتر رضایی\nبا سلام و احترام\nاینجانب مریم کریمی، دانشجوی "
            "کارشناسی ارشد مهندسی کامپیوتر، علاقه‌مندم به‌عنوان دستیار پژوهشی در آزمایشگاه "
            "شما همکاری کنم. رزومه‌ی خود را پیوست کرده‌ام و خوشحال می‌شوم در صورت امکان زمانی "
            "برای گفت‌وگو تعیین فرمایید.\nبا سپاس فراوان",
        ),
        instruction(
            t,
            "social_caption",
            "برای عکس یک کافه‌ی دنج در اصفهان یک کپشن اینستاگرامی حداکثر ۲۰ کلمه‌ای بنویس که "
            "دو هشتگ #اصفهان و #کافه در آن باشد.",
            {"required_keywords": ["#اصفهان", "#کافه"], "max_words": 25},
            "یک فنجان قهوه، بوی کتاب و آفتاب پاییزی؛ اینجا زمان آرام‌تر می‌گذرد. #اصفهان #کافه",
        ),
        instruction(
            t,
            "condolence",
            "پدر همکارت درگذشته است. یک پیام تسلیت کوتاه و رسمی برایش بنویس که کلمه‌ی «تسلیت» "
            "در آن باشد، حداکثر ۳۰ کلمه باشد و هیچ علامت تعجبی نداشته باشد.",
            {
                "required_keywords": ["تسلیت"],
                "required_any": [
                    ["روحشان شاد", "روحش شاد", "خدا رحمت", "خدا بیامرزد", "غم آخر", "صبر"]
                ],
                "forbidden": ["!"],
                "max_words": 36,
            },
            "درگذشت پدر گرامی‌تان را صمیمانه تسلیت می‌گویم. روحشان شاد و یادشان گرامی باد. "
            "برای شما و خانواده‌ی محترم صبر و آرامش آرزو می‌کنم.",
        ),
        instruction(
            t,
            "congratulation",
            "برای عروسی دوست صمیمی‌ات یک پیام تبریک خودمانی حداکثر ۲۵ کلمه‌ای بنویس که در آن "
            "آرزو کنی «به پای هم پیر شوند».",
            {"required_any": [["به پای هم پیر"], ["مبارک", "تبریک"]], "max_words": 30},
            "عروسیتون مبارک رفیق! کلی براتون خوشحالم. ان‌شاءالله به پای هم پیر بشید و همیشه "
            "دلتون شاد باشه.",
        ),
        instruction(
            t,
            "apology_email",
            "یک ایمیل کوتاه بنویس و بابت غیبت در جلسه‌ی امروز عذرخواهی کن. ایمیل با «با عرض "
            "پوزش» شروع شود، علت را «قطعی اینترنت» بگوید و جلسه‌ی جبرانی را برای «شنبه ساعت ۱۰» "
            "پیشنهاد بدهد. حداکثر ۴۵ کلمه.",
            {
                "starts_with": "با عرض پوزش",
                "required_keywords": ["قطعی اینترنت", "شنبه"],
                "required_any": [["ساعت 10", "ساعت ده", "10 صبح", "ده صبح"]],
                "max_words": 52,
            },
            "با عرض پوزش، به دلیل قطعی اینترنت نتوانستم در جلسه‌ی امروز شرکت کنم. اگر برایتان "
            "مقدور است، جلسه‌ی جبرانی را شنبه ساعت ۱۰ برگزار کنیم.\nبا سپاس",
        ),
        instruction(
            t,
            "sms",
            "به‌عنوان منشی کلینیک، یک پیامک یادآوری نوبت برای «خانم احمدی» بنویس: نوبت ایشان "
            "۲۶ آبان ساعت ۱۶:۳۰ است. در پایان پیامک بنویس که برای لغو نوبت عدد ۱ را ارسال "
            "کنند. حداکثر ۳۵ کلمه.",
            {
                "required_keywords": ["احمدی", "۲۶ آبان"],
                "required_any": [
                    ["16:30", "4:30", "چهار و نیم", "شانزده و سی", "16 و 30"],
                    ["لغو"],
                ],
                "max_words": 42,
            },
            "خانم احمدی گرامی، نوبت شما در کلینیک روز ۲۶ آبان ساعت ۱۶:۳۰ است. لطفاً سر وقت "
            "مراجعه کنید. برای لغو نوبت، عدد ۱ را ارسال کنید.",
        ),
        instruction(
            t,
            "classified_ad",
            "یک آگهی کوتاه برای اجاره‌ی یک آپارتمان ۷۵ متری دوخوابه در شیراز بنویس. متراژ، "
            "تعداد خواب و نام شهر حتماً ذکر شود، اما هیچ قیمتی نیاید و کلمه‌ی «فوری» به کار "
            "نرود. حداکثر ۳۰ کلمه.",
            {
                "required_any": [
                    ["75 متر"],
                    ["دوخوابه", "دو خوابه", "2 خوابه", "دو اتاق خواب", "2 اتاق خواب"],
                    ["شیراز"],
                ],
                "forbidden": ["فوری", "تومان", "میلیون", "قیمت", "ریال"],
                "max_words": 36,
            },
            "اجاره‌ی آپارتمان ۷۵ متری دوخوابه در شیراز؛ نورگیر، دارای آسانسور و پارکینگ، "
            "نزدیک به مترو. برای بازدید تماس بگیرید.",
        ),
        instruction(
            t,
            "complaint_letter",
            "یک نامه‌ی کوتاه و رسمی به شهرداری منطقه بنویس و گزارش بده که چراغ‌های «خیابان "
            "بهار» یک هفته است خاموش‌اند. نامه با «با سلام» شروع شود، هیچ علامت تعجبی نداشته "
            "باشد و حداکثر ۶۰ کلمه باشد.",
            {
                "starts_with": "با سلام",
                "required_keywords": ["خیابان بهار", "چراغ"],
                "forbidden": ["!"],
                "max_words": 70,
            },
            "با سلام\nاحتراماً به اطلاع می‌رساند چراغ‌های روشنایی خیابان بهار حدود یک هفته است "
            "خاموش‌اند و تردد شبانه، به‌ویژه برای سالمندان و کودکان، دشوار و ناامن شده است. "
            "خواهشمند است دستور فرمایید در اسرع وقت رسیدگی شود.\nبا تشکر، جمعی از ساکنان "
            "خیابان بهار",
        ),
        instruction(
            t,
            "resume",
            "برای بخش «درباره‌ی من» در رزومه‌ی یک حسابدار، یک جمله‌ی حرفه‌ای به صیغه‌ی اول شخص "
            "بنویس که عبارت «۵ سال سابقه» و کلمه‌ی «حسابداری» در آن آمده باشد. حداکثر ۲۵ کلمه.",
            {
                "required_any": [["5 سال سابقه", "پنج سال سابقه"]],
                "required_keywords": ["حسابداری"],
                "max_words": 30,
            },
            "حسابدار دقیق و منظمی هستم با ۵ سال سابقه در حسابداری شرکت‌های تولیدی و تسلط کامل "
            "بر گزارش‌های مالی.",
        ),
        instruction(
            t,
            "classified_ad",
            "برای آگهی فروش یک دوچرخه‌ی کوهستان سایز ۲۶، یک عنوان حداکثر ۶ کلمه‌ای بنویس که "
            "کلمه‌ی «دوچرخه» و عدد «۲۶» در آن باشد.",
            {"required_keywords": ["دوچرخه", "26"], "max_words": 7},
            "دوچرخه کوهستان سایز ۲۶ تمیز",
        ),
        instruction(
            t,
            "translation",
            'این جمله‌ی ایمیل کاری را به فارسی رسمی ترجمه کن: "Please find attached the '
            'invoice for September."',
            {
                "required_any": [
                    ["پیوست", "ضمیمه"],
                    ["فاکتور", "صورتحساب", "صورت حساب"],
                    ["سپتامبر"],
                ],
                "max_words": 20,
            },
            "فاکتور ماه سپتامبر به پیوست ارسال شده است.",
        ),
        instruction(
            t,
            "polite_refusal",
            "دوستت از تو ۲۰ میلیون تومان قرض خواسته و تو نمی‌توانی بدهی. یک پیام کوتاه، صمیمی "
            "و مودبانه بنویس که درخواستش را رد کنی بی‌آنکه دلخور شود. حداکثر ۴۰ کلمه.",
            {
                "required_any": [
                    ["شرمنده", "متاسف", "ببخش", "عذر"],
                    [
                        "نمی توانم",
                        "نمیتوانم",
                        "نمی تونم",
                        "نمیتونم",
                        "امکانش نیست",
                        "امکانش رو ندارم",
                        "در توانم نیست",
                        "از دستم برنمیاد",
                        "از دستم برنمی آید",
                    ],
                ],
                "max_words": 48,
            },
            "عزیزم، واقعاً شرمنده‌ام. این روزها خودم هم دستم تنگ است و نمی‌توانم این مبلغ را "
            "جور کنم. اگر کار دیگری از دستم بربیاید، حتماً کنارت هستم.",
        ),
        instruction(
            t,
            "how_to",
            "مراحل دم کردن چای ایرانی را دقیقاً در ۴ سطر بنویس (هر مرحله در یک سطر). کلمه‌ی "
            "«قوری» حتماً بیاید.",
            {
                "line_count": 4,
                "required_keywords": ["قوری"],
                "required_any": [["کتری", "سماور", "آب جوش"]],
                "max_words": 60,
            },
            "۱. آب را در کتری بجوشان.\n۲. قوری را با کمی آب جوش گرم کن و آبش را خالی کن.\n"
            "۳. چای خشک را در قوری بریز و روی آن آب جوش بریز.\n۴. قوری را روی کتری بگذار تا "
            "چای ده دقیقه دم بکشد.",
        ),
        instruction(
            t,
            "auto_reply",
            "یک پاسخ خودکار ایمیل برای دوران مرخصی‌ات بنویس: از ۲۰ تا ۳۰ آبان در دسترس نیستی "
            "و در این مدت باید با «آقای کریمی» تماس بگیرند. حداکثر ۴۰ کلمه.",
            {
                "required_keywords": ["کریمی"],
                "required_any": [
                    ["20 آبان", "20 تا 30", "بیستم آبان", "بیستم تا سی"],
                    ["30 آبان", "سی ام آبان", "سی آبان"],
                ],
                "max_words": 48,
            },
            "با سلام، از ۲۰ تا ۳۰ آبان در مرخصی هستم و به ایمیل‌ها دسترسی ندارم. در این مدت "
            "لطفاً برای امور فوری با آقای کریمی تماس بگیرید.\nبا سپاس",
        ),
        instruction(
            t,
            "tone_rewrite",
            "این پیام تند همسایه را مودبانه بازنویسی کن، بدون اینکه درخواست اصلی (کم کردن صدای "
            "موسیقی در شب) از بین برود و بدون علامت تعجب: «صدای آهنگتون رو کم کنید دیگه! نصف "
            "شبه!»",
            {
                "required_any": [
                    [
                        "لطفا",
                        "خواهش",
                        "ممنون می شوم",
                        "ممنون میشم",
                        "سپاسگزار",
                        "اگر امکان دارد",
                        "اگه امکانش هست",
                    ],
                    ["صدا"],
                    ["موسیقی", "آهنگ"],
                ],
                "forbidden": ["!", "دیگه"],
                "max_words": 40,
            },
            "سلام همسایه‌ی عزیز، اگر امکان دارد لطفاً شب‌ها صدای موسیقی را کمی کم کنید تا "
            "بتوانیم استراحت کنیم. خیلی ممنونم.",
        ),
        instruction(
            t,
            "plain_language",
            "این دستور پزشک را با زبانی ساده و خودمانی برای بیمار توضیح بده (حداکثر ۲۵ کلمه): "
            "«هر ۸ ساعت یک عدد کپسول پس از غذا میل شود.»",
            {
                "required_any": [
                    ["8 ساعت", "هشت ساعت", "سه بار", "3 بار"],
                    ["بعد از غذا", "پس از غذا", "بعد غذا", "بعد از خوردن غذا", "بعد از هر وعده"],
                ],
                "forbidden": ["میل شود"],
                "max_words": 30,
            },
            "هر ۸ ساعت، یعنی روزی سه بار، یک کپسول بخورید؛ همیشه بعد از غذا.",
        ),
        instruction(
            t,
            "greeting_card",
            "به مناسبت روز معلم، یک پیام تشکر دقیقاً دوسطری برای معلم سابقت بنویس. کلمه‌ی "
            "«معلم» باید در متن باشد.",
            {"line_count": 2, "required_keywords": ["معلم"], "max_words": 35},
            "روز معلم مبارک، خانم محمدی عزیز.\nهرچه دارم از صبر و مهربانی شما دارم؛ همیشه "
            "سپاسگزارتان هستم.",
        ),
        instruction(
            t,
            "invitation",
            "یک دعوت‌نامه‌ی رسمی کوتاه برای جشن شب یلدای شرکت بنویس: ۳۰ آذر، ساعت ۱۸، سالن "
            "اجتماعات. متن باید دقیقاً با جمله‌ی «منتظر حضور گرمتان هستیم» تمام شود و حداکثر "
            "۵۰ کلمه باشد.",
            {
                "required_keywords": ["یلدا", "۳۰ آذر", "سالن اجتماعات"],
                "required_any": [["18", "شش عصر", "6 عصر", "شش بعدازظهر", "شش بعد از ظهر"]],
                "ends_with": "منتظر حضور گرمتان هستیم",
                "max_words": 58,
            },
            "همکاران گرامی\nبه مناسبت شب یلدا، از شما دعوت می‌کنیم روز ۳۰ آذر ساعت ۱۸ در سالن "
            "اجتماعات شرکت، در جشن کوچک ما کنار هم باشیم. با انار و هندوانه و فال حافظ منتظر "
            "حضور گرمتان هستیم.",
        ),
    ]


# ---------------------------------------------------------------------------
# practical_editing — fixing text the way people actually mangle it.
# ---------------------------------------------------------------------------

KEYBOARD_PROMPT = (
    "این متن را کسی تایپ کرده که یادش رفته زبان کیبورد را از انگلیسی به فارسی تغییر "
    "دهد (چیدمان استاندارد کیبورد فارسی). متن فارسی‌ای را که می‌خواسته بنویسد، بنویس:\n{typed}"
)
REVERSE_KEYBOARD_PROMPT = (
    "کسی می‌خواسته یک کلمه‌ی انگلیسی تایپ کند اما کیبوردش روی فارسی (چیدمان استاندارد) "
    "بوده و این را نوشته: «{typed}». کلمه‌ی انگلیسی مورد نظرش چه بوده است؟"
)
FINGLISH_PROMPT = (
    "این پیام فینگلیش را به خط فارسی برگردان و همان لحن محاوره‌ای را نگه دار:\n{text}"
)
SPELLING_PROMPT = (
    "غلط‌های املایی این جمله را درست کن و فقط جمله‌ی درست‌شده را بنویس، بدون توضیح:\n«{text}»"
)
ZWNJ_PROMPT = (
    "این جمله را با رعایت درست نیم‌فاصله بازنویسی کن (جاهایی که باید نیم‌فاصله باشد اما "
    "فاصله‌ی کامل گذاشته شده) و فقط جمله‌ی درست‌شده را بنویس:\n«{text}»"
)


def editing_items() -> list[dict]:
    t = "practical_editing"
    items: list[dict] = []
    for sentence in [
        "سلام خوبی",
        "من فردا میام",
        "جلسه ساعت ده شروع میشه",
        "لطفا فایل را برای من بفرست",
        "کد تخفیف برای خرید بعدی شما ارسال شد",
        "امروز هوا خیلی سرد است",
    ]:
        typed = typed_with_english_layout(sentence)
        items.append(exact(t, "keyboard_layout", KEYBOARD_PROMPT.format(typed=typed), [sentence]))
    for english, persian in [("google", "گوگل"), ("password", "پسورد")]:
        typed = typed_with_persian_layout(english)
        prompt = REVERSE_KEYBOARD_PROMPT.format(typed=typed)
        items.append(exact(t, "keyboard_layout_reverse", prompt, [english, persian]))
    for text, answers in [
        (
            "salam, emrooz hava kheili garme",
            ["سلام، امروز هوا خیلی گرمه", "سلام امروز هوا خیلی گرم است"],
        ),
        (
            "mikham ye ghahve begiram, to chi mikhay?",
            ["می‌خوام یه قهوه بگیرم، تو چی می‌خوای؟", "میخوام یه قهوه بگیرم، تو چی میخوای؟"],
        ),
        (
            "farda saat 8 jolo-ye daneshgah montazeretam",
            ["فردا ساعت ۸ جلوی دانشگاه منتظرتم", "فردا ساعت هشت جلوی دانشگاه منتظرتم"],
        ),
        ("ghorbunet beram, dastet dard nakone", ["قربونت برم، دستت درد نکنه"]),
        (
            "ketabo yadet nare biyari",
            ["کتابو یادت نره بیاری", "کتاب رو یادت نره بیاری"],
        ),
    ]:
        items.append(f1(t, "finglish", FINGLISH_PROMPT.format(text=text), answers))
    for text, fixed, required, forbidden in [
        (
            "بچه‌ها در حیات مدرسه فوتبال بازی می‌کردند.",
            "بچه‌ها در حیاط مدرسه فوتبال بازی می‌کردند.",
            ["حیاط"],
            ["حیات"],
        ),
        (
            "او برای خاستگاری به منزل آنها رفت.",
            "او برای خواستگاری به منزل آنها رفت.",
            ["خواستگاری"],
            ["خاستگاری"],
        ),
        (
            "گذارش جلسه را روی میز مدیر گزاشتم.",
            "گزارش جلسه را روی میز مدیر گذاشتم.",
            ["گزارش", "گذاشتم"],
            ["گذارش", "گزاشتم"],
        ),
        (
            "این اطفاق برای همه‌ی ما درس عبرتی بود.",
            "این اتفاق برای همه‌ی ما درس عبرتی بود.",
            ["اتفاق"],
            ["اطفاق"],
        ),
        (
            "بعد از سخنرانی، همه از جایشان برخواستند.",
            "بعد از سخنرانی، همه از جایشان برخاستند.",
            ["برخاستند"],
            ["برخواستند"],
        ),
        (
            "این دستگاه نقض فنی دارد و استفاده از آن نقص قانون است.",
            "این دستگاه نقص فنی دارد و استفاده از آن نقض قانون است.",
            ["نقص فنی", "نقض قانون"],
            ["نقض فنی", "نقص قانون"],
        ),
    ]:
        constraints = {
            "required_keywords": required,
            "forbidden": forbidden,
            "max_words": len(fixed.split()) + 6,
        }
        prompt = SPELLING_PROMPT.format(text=text)
        items.append(instruction(t, "spelling", prompt, constraints, fixed))
    for text, fixed, required, forbidden in [
        (
            "ما می خواهیم کتاب ها را به کتابخانه ببریم.",
            "ما می‌خواهیم کتاب‌ها را به کتابخانه ببریم.",
            ["می‌خواهیم", ["کتاب‌ها", "کتابها"]],
            ["می خواهیم", "کتاب ها"],
        ),
        (
            "دانش آموزان در کلاس ها نشسته اند.",
            "دانش‌آموزان در کلاس‌ها نشسته‌اند.",
            ["دانش‌آموزان", ["کلاس‌ها", "کلاسها"], "نشسته‌اند"],
            ["دانش آموزان", "کلاس ها", "نشسته اند"],
        ),
        (
            "این بزرگ ترین مشکل ما در سال های اخیر است.",
            "این بزرگ‌ترین مشکل ما در سال‌های اخیر است.",
            [["بزرگ‌ترین", "بزرگترین"], ["سال‌های", "سالهای"]],
            ["بزرگ ترین", "سال های"],
        ),
        (
            "آن ها نمی توانند فردا بیایند.",
            "آن‌ها نمی‌توانند فردا بیایند.",
            [["آن‌ها", "آنها"], "نمی‌توانند"],
            ["آن ها", "نمی توانند"],
        ),
        (
            "خوش حال شدم که شما را دیدم.",
            "خوشحال شدم که شما را دیدم.",
            ["خوشحال"],
            ["خوش حال", "خوش‌حال"],
        ),
        (
            "پیام ها را خوانده ام و به زودی پاسخ می دهم.",
            "پیام‌ها را خوانده‌ام و به‌زودی پاسخ می‌دهم.",
            [["پیام‌ها", "پیامها"], "خوانده‌ام", "می‌دهم"],
            ["پیام ها", "خوانده ام", "می دهم"],
        ),
    ]:
        constraints = {
            "required_exact": required,
            "forbidden_exact": forbidden,
            "max_words": len(fixed.split()) + 8,
        }
        items.append(instruction(t, "zwnj", ZWNJ_PROMPT.format(text=text), constraints, fixed))
    return items


# ---------------------------------------------------------------------------
# practical_numbers — calendar, money, and everyday arithmetic.
# ---------------------------------------------------------------------------

DAY_MONTH_YEAR_FA = "پاسخ را به شکل «روز ماه سال» بنویس (مثلاً «۷ اردیبهشت ۱۴۰۳»)."
DAY_MONTH_YEAR_G = "پاسخ را به شکل «روز ماه سال» بنویس (مثلاً «۳ ژوئن ۲۰۲۴»)."


def numbers_items() -> list[dict]:
    t = "practical_numbers"
    items: list[dict] = []

    for jy, jm, jd in [(1405, 7, 15), (1404, 11, 22), (1403, 12, 30), (1405, 10, 1)]:
        prompt = (
            f"تاریخ {jalali_text(jy, jm, jd)} (هجری خورشیدی) معادل چه تاریخی در تقویم میلادی "
            f"است؟ {DAY_MONTH_YEAR_G}"
        )
        answers = gregorian_answers(jalali_to_gregorian(jy, jm, jd))
        items.append(exact(t, "jalali_to_gregorian", prompt, answers))

    for date in [datetime.date(2026, 12, 25), datetime.date(2027, 1, 1)]:
        g_text = fa(f"{date.day} {GREGORIAN_MONTHS_FA[date.month - 1]} {date.year}")
        prompt = (
            f"تاریخ {g_text} (میلادی) معادل چه تاریخی در تقویم هجری خورشیدی است؟ "
            f"{DAY_MONTH_YEAR_FA}"
        )
        items.append(exact(t, "gregorian_to_jalali", prompt, jalali_answers(*gregorian_to_jalali(date))))

    for start, days in [((1404, 12, 28), 5), ((1403, 12, 25), 10), ((1405, 6, 20), 45)]:
        prompt = (
            f"امروز {jalali_text(*start)} است. {fa(days)} روز بعد چه تاریخی است؟ "
            f"{DAY_MONTH_YEAR_FA}"
        )
        items.append(exact(t, "jalali_arithmetic", prompt, jalali_answers(*add_days_jalali(*start, days))))

    for jalali in [(1405, 8, 13), (1406, 1, 1)]:
        prompt = f"{jalali_text(*jalali)} چه روزی از هفته است؟ فقط نام روز را بنویس."
        items.append(exact(t, "weekday", prompt, weekday_answers(weekday_of_jalali(*jalali))))

    birth, today = (1378, 8, 15), (1405, 7, 5)
    age = today[0] - birth[0] - (1 if today[1:] < birth[1:] else 0)
    items.append(
        exact(
            t,
            "age",
            f"کسی که {jalali_text(*birth)} به دنیا آمده، در تاریخ {jalali_text(*today)} چند سال "
            "تمام دارد؟ فقط عدد را بنویس.",
            [str(age)],
        )
    )

    for amount in [1_250_000, 307_500, 2_048_000_000, 18_018]:
        prompt = (
            f"مبلغ {fa_money(amount)} تومان را برای نوشتن روی چک به حروف بنویس "
            "(فقط خود عدد را به حروف بنویس)."
        )
        items.append(exact(t, "number_to_words", prompt, number_word_variants(amount)))

    for amount in [675_402, 3_040_009]:
        prompt = f"عدد «{number_to_words(amount)}» را با رقم بنویس."
        items.append(exact(t, "words_to_number", prompt, [str(amount)]))

    items.append(
        exact(
            t,
            "rial_toman",
            f"قیمت یک کالا {fa_money(485_000)} ریال است. این مبلغ چند تومان است؟ فقط عدد را بنویس.",
            ["48500"],
        )
    )
    items.append(
        exact(
            t,
            "rial_toman",
            "۲۵۰ هزار تومان چند ریال است؟ فقط عدد را بنویس.",
            ["2500000"],
        )
    )
    items.append(
        exact(
            t,
            "shopping_math",
            f"قیمت یک جفت کفش {fa_money(2_400_000)} تومان است و ۱۵ درصد تخفیف دارد. قیمت "
            "نهایی چند تومان است؟ فقط عدد را بنویس.",
            [str(2_400_000 * 85 // 100)],
        )
    )
    items.append(
        exact(
            t,
            "shopping_math",
            f"قیمت یک کالا بدون مالیات {fa_money(850_000)} تومان است. اگر ۱۰ درصد مالیات بر "
            "ارزش افزوده به آن اضافه شود، مبلغ نهایی چند تومان می‌شود؟ فقط عدد را بنویس.",
            [str(850_000 * 110 // 100)],
        )
    )
    cheapest = min(750_000 // 5, 1_400_000 // 10)
    items.append(
        exact(
            t,
            "shopping_math",
            "بسته‌ی ۵ کیلویی برنج ۷۵۰ هزار تومان و بسته‌ی ۱۰ کیلویی یک میلیون و ۴۰۰ هزار "
            "تومان است. در بسته‌ای که به‌صرفه‌تر است، هر کیلو برنج چند تومان درمی‌آید؟ فقط "
            "عدد را بنویس.",
            [str(cheapest)],
        )
    )
    items.append(
        exact(
            t,
            "installments",
            "قیمت یک گوشی ۳۶ میلیون تومان است. ۱۲ میلیون تومان پیش‌پرداخت می‌دهی و بقیه را در "
            "۶ قسط مساوی و بدون سود می‌پردازی. هر قسط چند تومان است؟ فقط عدد را بنویس.",
            [str((36_000_000 - 12_000_000) // 6)],
        )
    )
    days_between = _j2d(1405, 7, 1) - _j2d(1405, 1, 1)
    items.append(
        exact(
            t,
            "jalali_arithmetic",
            "از ۱ فروردین ۱۴۰۵ تا ۱ مهر ۱۴۰۵ چند روز فاصله است؟ (روز شروع را حساب نکن.) فقط "
            "عدد را بنویس.",
            [str(days_between)],
        )
    )
    return items


# ---------------------------------------------------------------------------
# practical_extraction — messy everyday text to JSON.
# ---------------------------------------------------------------------------


def extraction_items() -> list[dict]:
    flight_day = weekday_of_jalali(1405, 7, 21)
    doctor_day = weekday_of_jalali(1405, 7, 23)
    party_day = weekday_of_jalali(1405, 8, 8)
    course_day = weekday_of_jalali(1405, 7, 19)
    trip_day = weekday_of_jalali(1405, 8, 6)
    checkout = add_days_jalali(1405, 8, 10, 3)
    return [
        extraction(
            "real_estate",
            "فروش آپارتمان ۸۵ متری در سعادت‌آباد تهران، دوخوابه، طبقه‌ی سوم با آسانسور. "
            "قیمت: هشت میلیارد و پانصد میلیون تومان. سند تک‌برگ.",
            "city (رشته)، neighbourhood (رشته)، area_m2 (عدد)، bedrooms (عدد)، floor (عدد)، "
            "elevator (true/false)، parking (true/false)، price_toman (عدد)",
            {
                "city": "تهران",
                "neighbourhood": ["سعادت‌آباد"],
                "area_m2": 85,
                "bedrooms": 2,
                "floor": 3,
                "elevator": True,
                "parking": None,
                "price_toman": 8_500_000_000,
            },
        ),
        extraction(
            "real_estate",
            "رهن و اجاره: واحد ۶۰ متری یک‌خوابه در اصفهان، خیابان چهارباغ. ودیعه ۳۰۰ میلیون، "
            "اجاره ماهی ۱۲ میلیون تومان. پارکینگ ندارد.",
            "city (رشته)، area_m2 (عدد)، bedrooms (عدد)، deposit_toman (عدد)، "
            "monthly_rent_toman (عدد)، parking (true/false)، elevator (true/false)",
            {
                "city": "اصفهان",
                "area_m2": 60,
                "bedrooms": 1,
                "deposit_toman": 300_000_000,
                "monthly_rent_toman": 12_000_000,
                "parking": False,
                "elevator": None,
            },
        ),
        extraction(
            "vehicle_ad",
            "پژو ۲۰۶ تیپ ۵، مدل ۱۳۹۹، سفید، کارکرد ۸۵ هزار کیلومتر، بدون رنگ، قیمت ۶۲۰ "
            "میلیون تومان.",
            "brand (رشته)، model (رشته)، model_year (عدد، سال شمسی)، color (رشته)، "
            "mileage_km (عدد)، price_toman (عدد)",
            {
                "brand": "پژو",
                "model": ["206", "206 تیپ 5", "پژو 206 تیپ 5"],
                "model_year": 1399,
                "color": "سفید",
                "mileage_km": 85_000,
                "price_toman": 620_000_000,
            },
        ),
        extraction(
            "bank_sms",
            "پیامک بانک | برداشت: ۱٬۲۵۰٬۰۰۰ ریال | مانده: ۳۴٬۸۰۰٬۰۰۰ ریال | "
            "۱۴۰۵/۰۷/۰۳ - ۱۸:۲۴",
            "type («برداشت» یا «واریز»)، amount_rial (عدد)، balance_rial (عدد)، "
            "date (به شکل YYYY/MM/DD)، time (به شکل HH:MM)",
            {
                "type": "برداشت",
                "amount_rial": 1_250_000,
                "balance_rial": 34_800_000,
                "date": ["1405/07/03", "1405/7/3"],
                "time": "18:24",
            },
        ),
        extraction(
            "bank_sms",
            "واریز به حساب: +۴۵٬۰۰۰٬۰۰۰ ریال | مانده: ۵۲٬۳۰۰٬۰۰۰ ریال | ۱۴۰۵/۰۶/۳۱ ساعت ۰۹:۱۵",
            "type («برداشت» یا «واریز»)، amount_toman (عدد، به تومان)، balance_toman (عدد، به "
            "تومان)، date (به شکل YYYY/MM/DD)",
            {
                "type": "واریز",
                "amount_toman": 4_500_000,
                "balance_toman": 5_230_000,
                "date": ["1405/06/31", "1405/6/31"],
            },
        ),
        extraction(
            "job_ad",
            "استخدام برنامه‌نویس پایتون (سطح میانی) در شیراز. حداقل ۳ سال سابقه. حقوق ۴۰ تا ۵۵ "
            "میلیون تومان. امکان دورکاری وجود ندارد.",
            "title (رشته)، city (رشته)، min_experience_years (عدد)، salary_min_toman (عدد)، "
            "salary_max_toman (عدد)، remote (true/false)، insurance (true/false)",
            {
                "title": ["برنامه‌نویس پایتون"],
                "city": "شیراز",
                "min_experience_years": 3,
                "salary_min_toman": 40_000_000,
                "salary_max_toman": 55_000_000,
                "remote": False,
                "insurance": None,
            },
        ),
        extraction(
            "ticket",
            f"پرواز شماره‌ی ۵۶۲۱ از مشهد به کیش، {flight_day} ۲۱ مهر ۱۴۰۵، ساعت حرکت ۰۶:۴۵، "
            "صندلی 14C.",
            "origin (رشته)، destination (رشته)، date (به شکل YYYY/MM/DD)، departure_time (به "
            "شکل HH:MM)، flight_number (رشته)، seat (رشته)",
            {
                "origin": "مشهد",
                "destination": "کیش",
                "date": ["1405/07/21", "1405/7/21"],
                "departure_time": ["06:45", "6:45"],
                "flight_number": "5621",
                "seat": "14C",
            },
        ),
        extraction(
            "ticket",
            "بلیت قطار تهران به مشهد، واگن ۴، کوپه‌ی ۳، صندلی ۱۲، قیمت ۸۹۰ هزار تومان، حرکت "
            "ساعت ۲۱:۳۰.",
            "origin (رشته)، destination (رشته)، wagon (عدد)، seat (عدد)، price_toman (عدد)، "
            "departure_time (به شکل HH:MM)",
            {
                "origin": "تهران",
                "destination": "مشهد",
                "wagon": 4,
                "seat": 12,
                "price_toman": 890_000,
                "departure_time": "21:30",
            },
        ),
        extraction(
            "receipt",
            "۲ پیتزا مخصوص، هر کدام ۴۲۰ هزار تومان؛ ۱ سالاد سزار ۲۱۰ هزار تومان؛ ۳ نوشابه، "
            "هر کدام ۳۵ هزار تومان. جمع: ۱٬۱۵۵٬۰۰۰ تومان. سرویس ۱۰٪: ۱۱۵٬۵۰۰ تومان. مبلغ قابل "
            "پرداخت: ۱٬۲۷۰٬۵۰۰ تومان.",
            "item_count (تعداد کل اقلام سفارش، عدد)، subtotal_toman (عدد)، service_percent "
            "(عدد)، total_toman (عدد)",
            {
                "item_count": 6,
                "subtotal_toman": 1_155_000,
                "service_percent": 10,
                "total_toman": 1_270_500,
            },
        ),
        extraction(
            "invoice",
            "فاکتور: ۳ عدد هارد اکسترنال، هر عدد ۲٬۸۰۰٬۰۰۰ تومان. ۱۰ درصد مالیات بر ارزش "
            "افزوده به جمع اضافه می‌شود.",
            "quantity (عدد)، subtotal_toman (جمع بدون مالیات، عدد)، vat_toman (مبلغ مالیات، "
            "عدد)، total_toman (مبلغ نهایی، عدد)",
            {
                "quantity": 3,
                "subtotal_toman": 8_400_000,
                "vat_toman": 840_000,
                "total_toman": 9_240_000,
            },
        ),
        extraction(
            "appointment",
            f"بیمار گرامی، نوبت شما نزد دکتر سپیده کاظمی (متخصص پوست) روز {doctor_day} ۲۳ مهر "
            "۱۴۰۵ ساعت ۱۷:۰۰ است. لطفاً ۱۵ دقیقه زودتر مراجعه کنید.",
            "doctor_name (رشته)، specialty (رشته)، date (به شکل YYYY/MM/DD)، time (به شکل "
            "HH:MM)، arrive_minutes_early (عدد)، fee_toman (عدد)",
            {
                "doctor_name": ["سپیده کاظمی"],
                "specialty": ["پوست"],
                "date": ["1405/07/23", "1405/7/23"],
                "time": ["17:00", "17"],
                "arrive_minutes_early": 15,
                "fee_toman": None,
            },
        ),
        extraction(
            "invitation",
            f"دعوت به جشن فارغ‌التحصیلی دانشکده‌ی مهندسی؛ {party_day} ۸ آبان ۱۴۰۵، ساعت ۱۶، "
            "تالار مولوی. ورود برای همراهان آزاد است.",
            "event (رشته)، date (به شکل YYYY/MM/DD)، time (به شکل HH:MM)، venue (رشته)، "
            "guests_allowed (true/false)",
            {
                "event": ["جشن فارغ‌التحصیلی", "فارغ‌التحصیلی"],
                "date": ["1405/08/08", "1405/8/8"],
                "time": ["16:00", "16"],
                "venue": ["تالار مولوی"],
                "guests_allowed": True,
            },
        ),
        extraction(
            "product_listing",
            "گوشی سامسونگ گلکسی A56، حافظه‌ی ۲۵۶ گیگ، رم ۸ گیگ، رنگ مشکی، ۱۸ ماه گارانتی.",
            "brand (رشته)، model (رشته)، storage_gb (عدد)، ram_gb (عدد)، color (رشته)، "
            "warranty_months (عدد)",
            {
                "brand": ["سامسونگ", "samsung"],
                "model": ["A56", "گلکسی A56", "Galaxy A56"],
                "storage_gb": 256,
                "ram_gb": 8,
                "color": "مشکی",
                "warranty_months": 18,
            },
        ),
        extraction(
            "contact",
            "مهندس آرش نیک‌نام | مدیر فنی | شرکت داده‌پردازان پارس | دفتر مرکزی: تبریز",
            "name (رشته، بدون عنوان «مهندس»)، job_title (رشته)، company (رشته)، city (رشته)، "
            "email (رشته)",
            {
                "name": ["آرش نیک‌نام"],
                "job_title": ["مدیر فنی"],
                "company": ["داده‌پردازان پارس", "شرکت داده‌پردازان پارس"],
                "city": "تبریز",
                "email": None,
            },
        ),
        extraction(
            "prescription",
            "آموکسی‌سیلین ۵۰۰ میلی‌گرم، هر ۸ ساعت یک کپسول، به مدت ۷ روز.",
            "drug (رشته)، dose_mg (عدد)، doses_per_day (عدد)، days (عدد)، total_capsules (تعداد "
            "کل کپسول‌های لازم، عدد)",
            {
                "drug": ["آموکسی‌سیلین", "amoxicillin"],
                "dose_mg": 500,
                "doses_per_day": 3,
                "days": 7,
                "total_capsules": 21,
            },
        ),
        extraction(
            "weather",
            "پیش‌بینی هوای فردا برای رشت: بارانی، کمینه‌ی دما ۱۴ و بیشینه‌ی ۲۱ درجه‌ی "
            "سانتی‌گراد. احتمال بارش ۸۰ درصد.",
            "city (رشته)، condition (رشته)، min_temp_c (عدد)، max_temp_c (عدد)، "
            "rain_chance_percent (عدد)، wind_kmh (عدد)",
            {
                "city": "رشت",
                "condition": ["بارانی", "باران"],
                "min_temp_c": 14,
                "max_temp_c": 21,
                "rain_chance_percent": 80,
                "wind_kmh": None,
            },
        ),
        extraction(
            "parcel_tracking",
            "مرسوله‌ی شما با کد رهگیری ۷۲۴۰۱۹۳۳۸۱ از مرکز پردازش تهران خارج شد و حداکثر تا "
            "۱۴۰۵/۰۷/۱۲ تحویل می‌شود.",
            "tracking_code (رشته)، origin_center (رشته)، delivery_deadline (به شکل YYYY/MM/DD)، "
            "recipient_name (رشته)",
            {
                "tracking_code": "7240193381",
                "origin_center": ["تهران"],
                "delivery_deadline": ["1405/07/12", "1405/7/12"],
                "recipient_name": None,
            },
        ),
        extraction(
            "utility_bill",
            "قبض برق دوره‌ی شهریور: مصرف ۳۸۵ کیلووات‌ساعت، مبلغ قابل پرداخت ۴٬۱۲۰٬۰۰۰ ریال، "
            "مهلت پرداخت ۱۴۰۵/۰۷/۱۰.",
            "period (رشته، نام ماه)، consumption_kwh (عدد)، amount_toman (عدد، به تومان)، "
            "due_date (به شکل YYYY/MM/DD)",
            {
                "period": "شهریور",
                "consumption_kwh": 385,
                "amount_toman": 412_000,
                "due_date": ["1405/07/10", "1405/7/10"],
            },
        ),
        extraction(
            "course",
            f"کارگاه «مقدمه‌ای بر یادگیری ماشین» با تدریس دکتر نرگس صدری، ۸ جلسه، شروع از "
            f"{course_day} ۱۹ مهر ۱۴۰۵. هزینه‌ی ثبت‌نام: ۳ میلیون و ۲۰۰ هزار تومان؛ دانشجویان "
            "۲۰ درصد تخفیف دارند.",
            "course (رشته)، instructor (رشته)، sessions (عدد)، start_date (به شکل YYYY/MM/DD)، "
            "fee_toman (عدد)، student_fee_toman (هزینه برای دانشجویان، عدد)",
            {
                "course": ["مقدمه‌ای بر یادگیری ماشین", "یادگیری ماشین"],
                "instructor": ["نرگس صدری"],
                "sessions": 8,
                "start_date": ["1405/07/19", "1405/7/19"],
                "fee_toman": 3_200_000,
                "student_fee_toman": 2_560_000,
            },
        ),
        extraction(
            "booking",
            "رزرو شما در هتل نگین اصفهان ثبت شد: ورود ۱۴۰۵/۰۸/۱۰، مدت اقامت ۳ شب، ۲ بزرگسال. "
            "صبحانه شامل می‌شود.",
            "hotel (رشته)، city (رشته)، check_in (به شکل YYYY/MM/DD)، nights (عدد)، "
            "check_out (به شکل YYYY/MM/DD)، adults (عدد)، breakfast_included (true/false)",
            {
                "hotel": ["هتل نگین", "نگین"],
                "city": "اصفهان",
                "check_in": ["1405/08/10", "1405/8/10"],
                "nights": 3,
                "check_out": [
                    f"{checkout[0]}/{checkout[1]:02d}/{checkout[2]:02d}",
                    f"{checkout[0]}/{checkout[1]}/{checkout[2]}",
                ],
                "adults": 2,
                "breakfast_included": True,
            },
        ),
        extraction(
            "classified_ad",
            "لپ‌تاپ لنوو ThinkPad T14، پردازنده‌ی Core i7 نسل ۱۲، رم ۱۶ گیگ، حافظه‌ی SSD ۵۱۲ "
            "گیگ، قیمت ۴۸ میلیون تومان، قیمت مقطوع است.",
            "brand (رشته)، ram_gb (عدد)، ssd_gb (عدد)، price_toman (عدد)، negotiable "
            "(true/false، آیا قیمت قابل چانه‌زنی است)",
            {
                "brand": ["لنوو", "lenovo"],
                "ram_gb": 16,
                "ssd_gb": 512,
                "price_toman": 48_000_000,
                "negotiable": False,
            },
        ),
        extraction(
            "news",
            "زلزله‌ای به بزرگی ۴٫۶ ریشتر بامداد امروز حوالی شهر خوی در آذربایجان غربی را "
            "لرزاند. تاکنون گزارشی از خسارت جانی منتشر نشده است.",
            "city (رشته)، province (رشته)، magnitude (عدد)، casualties_reported (true/false)، "
            "depth_km (عدد)",
            {
                "city": "خوی",
                "province": "آذربایجان غربی",
                "magnitude": 4.6,
                "casualties_reported": False,
                "depth_km": None,
            },
        ),
        extraction(
            "school_notice",
            f"اردوی یک‌روزه‌ی دانش‌آموزان پایه‌ی هشتم به باغ‌وحش ارم، {trip_day} ۶ آبان ۱۴۰۵. "
            "حرکت ساعت ۷:۳۰ از مدرسه. هزینه برای هر نفر ۴۵۰ هزار تومان.",
            "grade (عدد)، destination (رشته)، date (به شکل YYYY/MM/DD)، departure_time (به "
            "شکل HH:MM)، cost_toman (عدد)، lunch_included (true/false)",
            {
                "grade": 8,
                "destination": ["باغ‌وحش ارم"],
                "date": ["1405/08/06", "1405/8/6"],
                "departure_time": ["07:30", "7:30"],
                "cost_toman": 450_000,
                "lunch_included": None,
            },
        ),
        extraction(
            "payslip",
            "فیش حقوقی مهر: حقوق پایه ۲۸٬۰۰۰٬۰۰۰ تومان، اضافه‌کاری ۴٬۵۰۰٬۰۰۰ تومان، کسورات "
            "(بیمه و مالیات) ۳٬۷۰۰٬۰۰۰ تومان.",
            "base_salary_toman (عدد)، overtime_toman (عدد)، deductions_toman (عدد)، net_toman "
            "(خالص پرداختی، عدد)",
            {
                "base_salary_toman": 28_000_000,
                "overtime_toman": 4_500_000,
                "deductions_toman": 3_700_000,
                "net_toman": 28_800_000,
            },
        ),
        extraction(
            "sports",
            "در هفته‌ی ششم لیگ، استقلال در ورزشگاه آزادی میزبان سپاهان بود و بازی با نتیجه‌ی "
            "۲ بر ۱ به سود سپاهان تمام شد.",
            "home_team (رشته)، away_team (رشته)، home_goals (عدد)، away_goals (عدد)، winner "
            "(رشته)، stadium (رشته)",
            {
                "home_team": "استقلال",
                "away_team": "سپاهان",
                "home_goals": 1,
                "away_goals": 2,
                "winner": "سپاهان",
                "stadium": ["ورزشگاه آزادی", "آزادی"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# practical_pragmatics — what to say, when, and how it translates.
# ---------------------------------------------------------------------------


def pragmatics_items() -> list[dict]:
    t = "practical_pragmatics"
    return [
        mcq(
            t,
            "social_formula",
            "در پایان روز کاری به نگهبان ساختمان می‌گویید «خسته نباشید». او معمولاً چه پاسخی "
            "می‌دهد؟",
            "سلامت باشید، شما هم خسته نباشید",
            ["نوش جان، قابل شما را نداشت", "تسلیت می‌گویم", "مبارک باشد، به پای هم پیر شوید"],
        ),
        mcq(
            t,
            "social_formula",
            "از آرایشگاه برگشته‌اید و همکارتان می‌گوید «عافیت باشه». مناسب‌ترین پاسخ کدام است؟",
            "ممنون، سلامت باشید",
            ["نوش جان", "خدا رحمتش کند", "به سلامتی شما، بفرمایید"],
        ),
        mcq(
            t,
            "condolence",
            "پدر همکارتان درگذشته است. کدام پیام برای او مناسب‌تر است؟",
            "روحشان شاد، غم آخرتان باشد",
            [
                "مبارک باشد، ان‌شاءالله همیشه شاد باشید",
                "خسته نباشید، دستتان درد نکند",
                "عافیت باشد، خوش بگذرد",
            ],
        ),
        mcq(
            t,
            "social_formula",
            "گفتن «چشمتان روشن» در کدام موقعیت مناسب است؟",
            "وقتی عزیزی از سفر برگشته یا نوزادی به دنیا آمده است",
            ["وقتی کسی عینک تازه خریده است", "وقتی کسی بیمار شده است", "در مراسم ختم"],
        ),
        mcq(
            t,
            "taarof",
            "در تاکسی می‌پرسید کرایه چقدر شد و راننده می‌گوید «قابل نداره». معمولاً چه باید کرد؟",
            "تشکر می‌کنید، دوباره مبلغ را می‌پرسید و کرایه را می‌پردازید",
            [
                "تشکر می‌کنید و بدون پرداخت پیاده می‌شوید",
                "ناراحت می‌شوید و با راننده بحث می‌کنید",
                "دو برابر کرایه را می‌پردازید",
            ],
        ),
        mcq(
            t,
            "folk_belief",
            "طبق باور عامیانه‌ی ایرانی، اگر کسی درست هنگام شروع کاری یک بار عطسه کند، اطرافیان "
            "معمولاً چه می‌گویند؟",
            "صبر آمد",
            ["به سلامتی", "نوش جان", "چشمت روشن"],
        ),
        mcq(
            t,
            "politeness",
            "بزرگ‌تری از شما می‌پرسد «حالت چطوره؟». کدام پاسخ سنتی و محترمانه است؟",
            "زیر سایه‌ی شما خوبیم، ممنون",
            ["خدا بد ندهد", "نوش جان، شما هم", "غم آخرتان باشد"],
        ),
        mcq(
            t,
            "congratulation",
            "دوستتان تازه صاحب فرزند شده است. کدام جمله برای تبریک مناسب‌تر است؟",
            "قدمش مبارک، ان‌شاءالله زیر سایه‌ی شما بزرگ شود",
            ["خدا بیامرزدش", "عافیت باشد", "خسته نباشید، دستتان درد نکند"],
        ),
        mcq(
            t,
            "congratulation",
            "در جشن عروسی دوستتان، کدام جمله‌ی تبریک رایج و مناسب است؟",
            "مبارک باشد، ان‌شاءالله به پای هم پیر شوید",
            ["غم آخرتان باشد", "خدا بد ندهد", "عافیت باشد، خوش آمدید"],
        ),
        mcq(
            t,
            "taarof",
            "مهمانی برایتان هدیه آورده است. کدام پاسخ مودبانه‌ی رایج است؟",
            "چرا زحمت کشیدید؟ دستتان درد نکند",
            ["بله، منتظرش بودم", "قابل شما را ندارد", "خدا بد ندهد"],
        ),
        mcq(
            t,
            "taarof",
            "میزبان در پایان شام می‌گوید «ببخشید، چیز قابلی نبود». پاسخ مناسب کدام است؟",
            "دستتان درد نکند، خیلی خوشمزه بود",
            ["بله، واقعاً کم بود", "قابل شما را ندارد", "عافیت باشد"],
        ),
        mcq(
            t,
            "taarof",
            "دم در، میزبان تعارف می‌کند که شما اول وارد شوید. پاسخ رایج مهمان ایرانی چیست؟",
            "خواهش می‌کنم، شما بفرمایید",
            ["باشه، خداحافظ", "نوش جان", "دستتان درد نکند، خیلی خوشمزه بود"],
        ),
        mcq(
            t,
            "sympathy",
            "می‌شنوید پای همسایه‌تان شکسته است. رایج‌ترین جمله‌ی همدردی در لحظه‌ی اول کدام است؟",
            "خدا بد نده! ان‌شاءالله زودتر خوب شوید",
            ["مبارک باشد", "چشمتان روشن", "نوش جان"],
        ),
        mcq(
            t,
            "congratulation",
            "همکارتان می‌گوید «امروز تولدمه». کدام پاسخ طبیعی‌تر است؟",
            "تولدت مبارک! ان‌شاءالله صد و بیست ساله بشی",
            ["غم آخرت باشه", "خدا بد نده", "عافیت باشه"],
        ),
        mcq(
            t,
            "colloquial",
            "در گفت‌وگوی خودمانی، وقتی کسی کاری برای دوستش انجام داده و او می‌گوید «دمت گرم»، "
            "منظورش چیست؟",
            "تشکر و قدردانی صمیمانه",
            ["شکایت از گرمای هوا", "توصیه به نوشیدن چای داغ", "عذرخواهی بابت دیر آمدن"],
        ),
        mcq(
            t,
            "colloquial",
            "مادرتان از شما می‌خواهد نان بخرید و شما می‌گویید «چشم». منظورتان چیست؟",
            "باشه، حتماً انجام می‌دهم",
            ["چشمم درد می‌کند", "الان نمی‌توانم", "مطمئن نیستم"],
        ),
        mcq(
            t,
            "colloquial",
            "دوستتان می‌گوید «ماشین جدید خریدم!» و شما جواب می‌دهید «به سلامتی!». این جمله در "
            "اینجا چه معنایی دارد؟",
            "مبارک باشد، برایت خوشحالم",
            ["مراقب سلامتی‌ات باش", "بیا با هم نوشیدنی بخوریم", "امیدوارم زود خوب شوی"],
        ),
        mcq(
            t,
            "translation_en_fa",
            'کدام ترجمه‌ی فارسی برای جمله‌ی پایانی ایمیل "I\'m looking forward to hearing from '
            'you." طبیعی‌تر است؟',
            "منتظر پاسخ شما هستم.",
            [
                "من به جلو نگاه می‌کنم تا از شما بشنوم.",
                "به شنیدن صدای شما در آینده نگاه می‌کنم.",
                "امیدوارم هرگز از شما چیزی نشنوم.",
            ],
        ),
        mcq(
            t,
            "translation_en_fa",
            'دوستتان برای انتخاب رستوران نظر شما را می‌خواهد و شما می‌گویید "It\'s up to you.". '
            "کدام ترجمه‌ی فارسی طبیعی‌تر است؟",
            "هر طور خودت صلاح می‌دانی.",
            ["آن بالای سر توست.", "تا تو بالا بروی.", "به تو هیچ ربطی ندارد."],
        ),
        mcq(
            t,
            "translation_en_fa",
            'دوستتان پیش از اجرای نمایش روی صحنه است و کسی به او می‌گوید "Break a leg!". '
            "معادل طبیعی فارسی کدام است؟",
            "موفق باشی!",
            ["پایت را بشکن!", "مراقب باش پایت نشکند!", "خدا بد نده!"],
        ),
        mcq(
            t,
            "translation_en_fa",
            'کسی بابت تاخیر کوتاهی عذرخواهی می‌کند و شما می‌گویید "No worries.". معادل طبیعی '
            "فارسی کدام است؟",
            "اشکالی ندارد، پیش می‌آید.",
            [
                "هیچ نگرانی‌ای وجود ندارد که نگرانش باشم.",
                "نگرانی‌های من تمام شد.",
                "لطفاً نگران من باشید.",
            ],
        ),
        mcq(
            t,
            "translation_fa_en",
            "دوستتان در اسباب‌کشی کمکتان کرده و شما می‌گویید «دستت درد نکنه». بهترین معادل "
            "انگلیسی کدام است؟",
            "Thanks a lot, I really appreciate your help.",
            ["I hope your hand doesn't hurt.", "Take care of your hands.", "Sorry about your hand."],
        ),
        mcq(
            t,
            "translation_fa_en",
            "میزبان هنگام ورود مهمان می‌گوید «قدمتان روی چشم». بهترین معادل انگلیسی کدام است؟",
            "You're most welcome here.",
            ["Your feet are on my eyes.", "Please watch your step.", "Take your shoes off."],
        ),
        mcq(
            t,
            "translation_fa_en",
            "به کارگری که مشغول کار است می‌گویید «خدا قوت». بهترین معادل انگلیسی کدام است؟",
            "Keep up the good work!",
            ["God is powerful.", "You need more strength.", "Please work faster."],
        ),
        mcq(
            t,
            "register",
            "در ایمیل رسمی به مدیرتان، کدام شروع مناسب‌تر است؟",
            "با سلام و احترام،",
            ["سلام داداش،", "هی، چطوری؟", "سلام عزیزم،"],
        ),
    ]


# ---------------------------------------------------------------------------
# practical_creative — word play that is still machine-checkable.
# ---------------------------------------------------------------------------


def creative_items() -> list[dict]:
    t = "practical_creative"
    acrostic = (
        "یک متن {lines}‌سطری درباره‌ی {topic} بنویس که حرف اول سطرها به ترتیب کلمه‌ی «{word}» "
        "را بسازد. هر سطر یک جمله باشد و عنوان یا توضیح اضافه ننویس."
    )
    items = [
        instruction(
            t,
            "acrostic",
            acrostic.format(lines="سه", topic="مادر", word="مهر"),
            {"line_count": 3, "line_initials": ["م", "ه", "ر"], "required_any": [["مادر", "مامان"]]},
            "مادرم چراغ روشن خانه است\nهر روز با لبخندش بیدارمان می‌کند\nرنج‌هایش را هرگز به "
            "زبان نمی‌آورد",
        ),
        instruction(
            t,
            "acrostic",
            acrostic.format(lines="پنج", topic="وطن", word="ایران"),
            {"line_count": 5, "line_initials": ["ا", "ی", "ر", "ا", "ن"]},
            "ایران خانه‌ی مهربانی است\nیادش همیشه در دل ماست\nرودهایش پر از زندگی است\n"
            "آسمانش آبی و روشن است\nنامش بر زبان ما جاری است",
        ),
        instruction(
            t,
            "acrostic",
            acrostic.format(lines="پنج", topic="پاییز", word="باران"),
            {
                "line_count": 5,
                "line_initials": ["ب", "ا", "ر", "ا", "ن"],
                "required_any": [["پاییز", "برگ", "ابر", "باران"]],
            },
            "برگ‌ها آرام از شاخه می‌افتند\nابرها آسمان را خاکستری کرده‌اند\nرهگذران چترهایشان "
            "را باز می‌کنند\nانار سرخ بر سفره‌ها نشسته است\nنم‌نم باران پاییزی شروع شده است",
        ),
        instruction(
            t,
            "acrostic",
            acrostic.format(lines="چهار", topic="دوستی", word="دوست"),
            {"line_count": 4, "line_initials": ["د", "و", "س", "ت"]},
            "در روزهای سخت کنارم ماند\nوقتی خسته بودم دستم را گرفت\nسکوتم را بی‌کلام فهمید\n"
            "تنهایی را از یادم برد",
        ),
        instruction(
            t,
            "lipogram",
            "سه جمله درباره‌ی فصل بهار بنویس بدون اینکه حتی یک بار از حرف «ر» استفاده کنی (پس "
            "خود کلمه‌ی «بهار» را هم نمی‌توانی بنویسی). روی هم دست‌کم ۱۲ کلمه بنویس.",
            {
                "forbidden_chars": ["ر"],
                "min_words": 12,
                "required_any": [["شکوفه", "گل", "سبزه", "سبز", "جوانه"]],
            },
            "فصل شکوفه‌ها آمده است. گل‌ها باز شده‌اند و هوا دلنشین است. سبزه‌ها همه جا دیده "
            "می‌شوند.",
        ),
        instruction(
            t,
            "lipogram",
            "یک توصیف دست‌کم ۱۲ کلمه‌ای از صبحانه‌ی ایرانی بنویس که حرف «ن» در آن نباشد (یعنی "
            "کلمه‌هایی مثل «نان»، «پنیر» و «صبحانه» هم ممنوع‌اند).",
            {
                "forbidden_chars": ["ن"],
                "min_words": 12,
                "required_any": [["چای", "کره", "مربا", "تخم", "عسل", "گردو", "خرما"]],
            },
            "چای داغ با کره و مربا و تخم‌مرغ، هر روز صبح ما را شاد و سرحال می‌کرد.",
        ),
        instruction(
            t,
            "lipogram",
            "یک جمله‌ی دست‌کم ۸ کلمه‌ای درباره‌ی دریا بنویس که در آن هیچ «ا» یا «آ» نباشد (خود "
            "کلمه‌ی «دریا» هم ممنوع است).",
            {
                "forbidden_chars": ["ا", "آ"],
                "min_words": 8,
                "required_any": [["موج", "صدف", "شن", "نیلگون", "کشتی"]],
            },
            "موج نیلگون روی شن گرم می‌غلتد و صدف زیر نور خورشید می‌درخشد.",
        ),
        instruction(
            t,
            "lipogram",
            "یک جمله‌ی دست‌کم ۸ کلمه‌ای درباره‌ی مدرسه بنویس که حرف «ی» در آن به کار نرفته باشد.",
            {"forbidden_chars": ["ی"], "min_words": 8, "required_keywords": ["مدرسه"]},
            "صبح زود بچه‌ها با کوله به مدرسه رفتند و در کلاس درس خواندند.",
        ),
        instruction(
            t,
            "rhyme",
            "دو سطر شعرگونه درباره‌ی پاییز بنویس که آخرین کلمه‌ی هر سطر با «ار» تمام شود (مثل "
            "«انار» و «بهار»)، اما کلمه‌ی آخر دو سطر یکی نباشد.",
            {"line_count": 2, "lines_end_with": "ار", "distinct_line_endings": True},
            "برگ‌ها ریختند از شاخه‌ی چنار\nباد پاییزی آمد بی‌قرار",
        ),
        instruction(
            t,
            "rhyme",
            "دو سطر درباره‌ی شب بنویس که هر دو سطر با کلمه‌ی «است» تمام شوند و کلمه‌ی پیش از "
            "«است» در هر دو سطر با «ان» تمام شود (مثل «باران است»).",
            {"line_count": 2, "lines_end_with": "ان است"},
            "آسمان شب پر از ستارگان است\nماه آرام در دل آسمان است",
        ),
        instruction(
            t,
            "rhyme",
            "دو سطر درباره‌ی دوستی بنویس که آخرین کلمه‌ی هر سطر با «وست» تمام شود؛ کلمه‌ی آخر "
            "دو سطر نباید یکی باشد.",
            {"line_count": 2, "lines_end_with": "وست", "distinct_line_endings": True},
            "رفیق روزهای سخت و آسان، دوست\nکسی که دلش مهربان و نیکوست",
        ),
        instruction(
            t,
            "alliteration",
            "یک جمله‌ی دقیقاً پنج‌کلمه‌ای بنویس که همه‌ی کلمه‌هایش با حرف «س» شروع شوند.",
            {"word_initial": "س", "min_words": 5, "max_words": 5},
            "سهراب سحرگاه سرودی ساده سرود",
        ),
        instruction(
            t,
            "alliteration",
            "یک جمله‌ی دقیقاً شش‌کلمه‌ای بنویس که همه‌ی کلمه‌هایش با حرف «ب» شروع شوند.",
            {"word_initial": "ب", "min_words": 6, "max_words": 6},
            "بابک بعد باران به باغ برگشت",
        ),
        exact(
            t,
            "anagram",
            "با جابه‌جا کردن حروف کلمه‌ی «راهب» نام یکی از فصل‌های سال را بساز.",
            ["بهار"],
        ),
        exact(
            t,
            "anagram",
            "حروف «ز، ا، ر، ی، ش» را طوری مرتب کن که نام یک شهر مشهور ایران به دست آید.",
            ["شیراز"],
        ),
        exact(
            t,
            "anagram",
            "حروف «ن، ا، ر، ا، ی» را طوری مرتب کن که نام یک کشور به دست آید.",
            ["ایران"],
        ),
        exact(
            t,
            "anagram",
            "حروف «ر، ا، ن، ا» را طوری مرتب کن که نام یک میوه به دست آید.",
            ["انار"],
        ),
        exact(
            t,
            "riddle",
            "چیستان: آن چیست که پر از سوراخ است ولی باز هم آب را در خودش نگه می‌دارد؟",
            ["اسفنج"],
        ),
        exact(
            t,
            "riddle",
            "چیستان: آن چیست که هرچه بیشتر خشک می‌کند، خودش خیس‌تر می‌شود؟",
            ["حوله"],
        ),
        exact(
            t,
            "riddle",
            "چیستان: آن چیست که هرچه از آن برمی‌داری، بزرگ‌تر می‌شود؟",
            ["چاله", "گودال", "سوراخ", "حفره"],
        ),
        exact(
            t,
            "abjad",
            "در حساب ابجد (ابجد کبیر)، ارزش عددی کلمه‌ی «عشق» چند است؟ فقط عدد را بنویس.",
            [str(abjad("عشق"))],
        ),
        exact(
            t,
            "abjad",
            "در حساب ابجد (ابجد کبیر)، ارزش عددی کلمه‌ی «یلدا» چند است؟ فقط عدد را بنویس.",
            [str(abjad("یلدا"))],
        ),
        instruction(
            t,
            "idiom_paraphrase",
            "معنی اصطلاح «آب در هاون کوبیدن» را در یک جمله‌ی کوتاه (حداکثر ۱۵ کلمه) برای یک "
            "کودک توضیح بده، بدون اینکه کلمه‌های «آب»، «هاون» یا «کوبیدن» را به کار ببری.",
            {
                "forbidden": ["آب", "هاون", "کوبید"],
                "required_any": [
                    [
                        "بیهوده",
                        "بی فایده",
                        "بی نتیجه",
                        "فایده ای ندارد",
                        "فایده ندارد",
                        "نتیجه ای ندارد",
                        "نتیجه ندارد",
                        "بی ثمر",
                        "هدر",
                        "بیخود",
                        "بی خود",
                        "الکی",
                    ]
                ],
                "max_words": 20,
            },
            "یعنی کاری بیهوده انجام بدهی که هیچ نتیجه‌ای ندارد.",
        ),
        instruction(
            t,
            "idiom_paraphrase",
            "معنی «کار از کار گذشته» را در یک جمله‌ی کوتاه (حداکثر ۱۵ کلمه) توضیح بده، بدون "
            "اینکه کلمه‌های «کار» یا «گذشته» را به کار ببری.",
            {
                "forbidden": ["کار", "گذشت"],
                "required_any": [["دیر", "فرصت", "جبران", "چاره", "برگشت"]],
                "max_words": 20,
            },
            "یعنی دیگر دیر شده و فرصتی برای جبران باقی نمانده است.",
        ),
        instruction(
            t,
            "headline",
            "یک تیتر خبری طنز حداکثر ۸ کلمه‌ای درباره‌ی ترافیک تهران بنویس که کلمه‌ی «ترافیک» "
            "در آن باشد و با علامت «؟» تمام شود.",
            {"required_keywords": ["ترافیک"], "required_suffix": "؟", "max_words": 10},
            "آیا ترافیک تهران بالاخره به مقصد رسید؟",
        ),
    ]
    return items


# ---------------------------------------------------------------------------
# Assembly.
# ---------------------------------------------------------------------------


def build_rows() -> list[dict[str, Any]]:
    _self_check_calendar()
    assert number_to_words(1_250_000) == "یک میلیون و دویست و پنجاه هزار"
    assert typed_with_english_layout("سلام خوبی") == "sghl o,fd"
    assert typed_with_persian_layout("google") == "لخخلمث"
    assert abjad("عشق") == 470

    groups = [
        writing_items(),
        editing_items(),
        numbers_items(),
        extraction_items(),
        pragmatics_items(),
        creative_items(),
    ]
    rows: list[dict[str, Any]] = []
    for group in groups:
        mcq_seen = 0
        for index, item in enumerate(group, start=1):
            track = item["track"]
            row: dict[str, Any] = {
                "id": f"peval-practical-{TRACK_TOKENS[track]}-{index:03d}",
                "track": track,
                "prompt": item["prompt"],
                "choices": None,
                "answer": item.get("answer"),
                "metadata": dict(item["metadata"]),
                "source": SOURCE,
                "split": "practical",
            }
            if "mcq" in item:
                correct, distractors = item["mcq"]
                position = ANSWER_POSITIONS[mcq_seen % len(ANSWER_POSITIONS)]
                mcq_seen += 1
                choices = list(distractors)
                choices.insert(position, correct)
                row["choices"] = choices
                row["answer"] = correct
                row["metadata"]["answer_index"] = position
                row["metadata"]["reference_response"] = LABELS[position]
            row["metadata"]["review"] = dict(REVIEW)
            rows.append(row)
    _verify(rows)
    return rows


def _verify(rows: list[dict[str, Any]]) -> None:
    failures = []
    for row in rows:
        record = DatasetRecord.from_dict(row)
        score, details = score_record(record, row["metadata"]["reference_response"])
        if score != 1.0:
            failures.append(f"{row['id']}: reference scores {score}: {details}")
    if failures:
        raise SystemExit("reference responses must score 1.0:\n" + "\n".join(failures))


def render(rows: list[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if the JSONL is out of date")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)

    content = render(build_rows())
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != content:
            print(f"{args.output} is out of date; rerun this script", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date")
        return 0
    args.output.write_text(content, encoding="utf-8")
    print(f"wrote {args.output} ({content.count(chr(10))} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
