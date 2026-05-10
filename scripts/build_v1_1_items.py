#!/usr/bin/env python3
"""Generate Persian Eval v1.1 items and append them to the JSONL splits.

This is a deterministic, one-shot generator: running it twice on a clean
checkout produces an identical diff. New items are appended in-order with
deterministic IDs. Each row carries a `metadata.review` block with status
`pending_review` so human reviewers can promote them via PRs as described
in CONTRIBUTING_DATASET.md.

Run from repo root:

    python scripts/build_v1_1_items.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
SOURCE = "curated:v1.1"
AUTHOR = "claude-review"


def review_block(
    *,
    clarity: int = 5,
    ambiguity: int = 1,
    cultural_fit: int = 5,
    leakage_risk: int = 1,
    difficulty: int = 3,
    notes: str = "",
) -> dict[str, Any]:
    block: dict[str, Any] = {
        "author": AUTHOR,
        "reviewers": [],
        "status": "pending_review",
        "rubric": {
            "clarity": clarity,
            "ambiguity": ambiguity,
            "cultural_fit": cultural_fit,
            "leakage_risk": leakage_risk,
            "difficulty": difficulty,
        },
    }
    if notes:
        block["notes"] = notes
    return block


def mcq(
    qid: str,
    *,
    track: str,
    split: str,
    prompt: str,
    choices: list[str],
    answer_index: int,
    category: str,
    difficulty: int = 3,
) -> dict[str, Any]:
    return {
        "id": qid,
        "track": track,
        "prompt": prompt,
        "choices": choices,
        "answer": choices[answer_index],
        "metadata": {
            "scoring": "mcq",
            "answer_index": answer_index,
            "category": category,
            "review": review_block(difficulty=difficulty),
        },
        "source": SOURCE,
        "split": split,
    }


def exact(
    qid: str,
    *,
    track: str,
    split: str,
    prompt: str,
    answers: list[str],
    category: str,
    difficulty: int = 3,
) -> dict[str, Any]:
    return {
        "id": qid,
        "track": track,
        "prompt": prompt,
        "choices": None,
        "answer": answers,
        "metadata": {
            "scoring": "exact",
            "category": category,
            "review": review_block(difficulty=difficulty),
        },
        "source": SOURCE,
        "split": split,
    }


def f1(
    qid: str,
    *,
    track: str,
    split: str,
    prompt: str,
    answers: list[str],
    category: str,
    difficulty: int = 3,
) -> dict[str, Any]:
    return {
        "id": qid,
        "track": track,
        "prompt": prompt,
        "choices": None,
        "answer": answers,
        "metadata": {
            "scoring": "f1",
            "category": category,
            "review": review_block(difficulty=difficulty),
        },
        "source": SOURCE,
        "split": split,
    }


def instr(
    qid: str,
    *,
    track: str,
    split: str,
    prompt: str,
    constraints: dict[str, Any],
    category: str,
    difficulty: int = 3,
) -> dict[str, Any]:
    return {
        "id": qid,
        "track": track,
        "prompt": prompt,
        "choices": None,
        "answer": constraints,
        "metadata": {
            "scoring": "instruction",
            "category": category,
            "review": review_block(difficulty=difficulty),
        },
        "source": SOURCE,
        "split": split,
    }


def public_knowledge() -> list[dict[str, Any]]:
    items = [
        mcq(
            "peval-public-knowledge-005",
            track="knowledge",
            split="public_eval",
            prompt="دومین شهر پرجمعیت ایران بعد از تهران معمولا کدام شهر است؟",
            choices=["مشهد", "اصفهان", "شیراز", "تبریز"],
            answer_index=0,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-006",
            track="knowledge",
            split="public_eval",
            prompt="کدام کشور همسایه شرقی ایران است؟",
            choices=["ترکیه", "ارمنستان", "افغانستان", "آذربایجان"],
            answer_index=2,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-007",
            track="knowledge",
            split="public_eval",
            prompt="مرکز استان فارس کدام شهر است؟",
            choices=["یزد", "اهواز", "کرمان", "شیراز"],
            answer_index=3,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-008",
            track="knowledge",
            split="public_eval",
            prompt="دریاچه ارومیه در کدام منطقه ایران قرار دارد؟",
            choices=["شمال‌غرب", "جنوب", "شرق", "مرکز"],
            answer_index=0,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-009",
            track="knowledge",
            split="public_eval",
            prompt="کوه دماوند در کدام رشته‌کوه قرار دارد؟",
            choices=["زاگرس", "البرز", "هندوکش", "کپه‌داغ"],
            answer_index=1,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-010",
            track="knowledge",
            split="public_eval",
            prompt="ماه پایانی فصل تابستان در تقویم هجری شمسی چیست؟",
            choices=["مرداد", "شهریور", "مهر", "تیر"],
            answer_index=1,
            category="calendar",
        ),
        mcq(
            "peval-public-knowledge-011",
            track="knowledge",
            split="public_eval",
            prompt="آذر چندمین ماه تقویم هجری شمسی است؟",
            choices=["هشتم", "نهم", "دهم", "یازدهم"],
            answer_index=1,
            category="calendar",
        ),
        mcq(
            "peval-public-knowledge-012",
            track="knowledge",
            split="public_eval",
            prompt="اولین روز فصل پاییز در تقویم هجری شمسی معمولا در کدام ماه است؟",
            choices=["شهریور", "مهر", "آبان", "آذر"],
            answer_index=1,
            category="calendar",
        ),
        mcq(
            "peval-public-knowledge-013",
            track="knowledge",
            split="public_eval",
            prompt="در سیستم بین‌المللی یکاها، یکای پایه برای دما کدام است؟",
            choices=["سلسیوس", "فارنهایت", "کلوین", "رانکین"],
            answer_index=2,
            category="science",
        ),
        mcq(
            "peval-public-knowledge-014",
            track="knowledge",
            split="public_eval",
            prompt="نماد شیمیایی Au به کدام عنصر اشاره دارد؟",
            choices=["نقره", "طلا", "مس", "آهن"],
            answer_index=1,
            category="science",
        ),
        mcq(
            "peval-public-knowledge-015",
            track="knowledge",
            split="public_eval",
            prompt="بخش عمده جرم خورشید را کدام عنصر تشکیل می‌دهد؟",
            choices=["هلیوم", "هیدروژن", "اکسیژن", "کربن"],
            answer_index=1,
            category="science",
        ),
        mcq(
            "peval-public-knowledge-016",
            track="knowledge",
            split="public_eval",
            prompt="سرعت نور در خلا تقریبا چقدر است؟",
            choices=[
                "سیصد کیلومتر بر ثانیه",
                "سه‌هزار کیلومتر بر ثانیه",
                "سیصد هزار کیلومتر بر ثانیه",
                "سی‌میلیون کیلومتر بر ثانیه",
            ],
            answer_index=2,
            category="science",
        ),
        mcq(
            "peval-public-knowledge-017",
            track="knowledge",
            split="public_eval",
            prompt="کدام پروتکل پایه‌ای انتقال صفحه‌های وب در اینترنت است؟",
            choices=["FTP", "HTTP", "SMTP", "IMAP"],
            answer_index=1,
            category="technology",
        ),
        mcq(
            "peval-public-knowledge-018",
            track="knowledge",
            split="public_eval",
            prompt="زبان نشانه‌گذاری اصلی برای ساخت ساختار صفحه‌های وب کدام است؟",
            choices=["CSS", "HTML", "JSON", "XML"],
            answer_index=1,
            category="technology",
        ),
        mcq(
            "peval-public-knowledge-019",
            track="knowledge",
            split="public_eval",
            prompt="سیستم‌عامل اوبونتو بر پایه کدام خانواده ساخته شده است؟",
            choices=["لینوکس", "ویندوز", "مک‌اواس", "بی‌اس‌دی"],
            answer_index=0,
            category="technology",
        ),
        mcq(
            "peval-public-knowledge-020",
            track="knowledge",
            split="public_eval",
            prompt="کدام واحد ذخیره‌سازی از کیلوبایت کوچک‌تر است؟",
            choices=["مگابایت", "گیگابایت", "بایت", "ترابایت"],
            answer_index=2,
            category="technology",
        ),
        mcq(
            "peval-public-knowledge-021",
            track="knowledge",
            split="public_eval",
            prompt="جنبش مشروطه در ایران رسما در دوره کدام سلسله اعلام شد؟",
            choices=["صفویه", "افشاریه", "زندیه", "قاجاریه"],
            answer_index=3,
            category="history",
        ),
        mcq(
            "peval-public-knowledge-022",
            track="knowledge",
            split="public_eval",
            prompt="کوروش بزرگ بنیان‌گذار کدام سلسله ایرانی شناخته می‌شود؟",
            choices=["ساسانی", "اشکانی", "هخامنشی", "ماد"],
            answer_index=2,
            category="history",
        ),
        mcq(
            "peval-public-knowledge-023",
            track="knowledge",
            split="public_eval",
            prompt="شاهنامه اثر کدام شاعر است؟",
            choices=["سعدی", "نظامی", "فردوسی", "خاقانی"],
            answer_index=2,
            category="literature",
        ),
        mcq(
            "peval-public-knowledge-024",
            track="knowledge",
            split="public_eval",
            prompt="مثنوی معنوی اثر کدام شاعر است؟",
            choices=["مولوی", "عطار", "رودکی", "هاتف"],
            answer_index=0,
            category="literature",
        ),
        mcq(
            "peval-public-knowledge-025",
            track="knowledge",
            split="public_eval",
            prompt="رودکی معمولا با کدام عنوان شناخته می‌شود؟",
            choices=["لسان‌الغیب", "پدر شعر فارسی", "خداوندگار غزل", "حکیم طوس"],
            answer_index=1,
            category="literature",
        ),
        mcq(
            "peval-public-knowledge-026",
            track="knowledge",
            split="public_eval",
            prompt="رود کارون عمدتا در کدام استان جریان دارد؟",
            choices=["خوزستان", "گلستان", "گیلان", "همدان"],
            answer_index=0,
            category="geography",
        ),
        mcq(
            "peval-public-knowledge-027",
            track="knowledge",
            split="public_eval",
            prompt="یک ربع ساعت چند دقیقه است؟",
            choices=["پنج", "ده", "پانزده", "بیست"],
            answer_index=2,
            category="units",
        ),
        mcq(
            "peval-public-knowledge-028",
            track="knowledge",
            split="public_eval",
            prompt="کدام جانور پستاندار است؟",
            choices=["مار", "نهنگ", "تمساح", "قورباغه"],
            answer_index=1,
            category="biology",
        ),
        mcq(
            "peval-public-knowledge-029",
            track="knowledge",
            split="public_eval",
            prompt="در کدام عنصر، پیشوند «اکسی» به‌طور غالب در نام ترکیب‌ها دیده می‌شود؟",
            choices=["نیتروژن", "کربن", "اکسیژن", "گوگرد"],
            answer_index=2,
            category="science",
        ),
        mcq(
            "peval-public-knowledge-030",
            track="knowledge",
            split="public_eval",
            prompt="آیا گزاره زیر درست است؟ «خط استوا از داخل خاک ایران می‌گذرد.»",
            choices=["درست است", "نادرست است", "تنها از جزیره‌های جنوبی می‌گذرد", "تنها از خلیج فارس می‌گذرد"],
            answer_index=1,
            category="geography",
        ),
    ]
    return items


def public_short_qa() -> list[dict[str, Any]]:
    items = [
        exact(
            "peval-public-shortqa-005",
            track="short_qa",
            split="public_eval",
            prompt="بلندترین قله رشته‌کوه البرز چه نام دارد؟",
            answers=["دماوند", "قله دماوند"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-006",
            track="short_qa",
            split="public_eval",
            prompt="پایتخت استان خراسان رضوی چه نام دارد؟",
            answers=["مشهد"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-007",
            track="short_qa",
            split="public_eval",
            prompt="نام دیگر آبراهی که خلیج فارس را به دریای عمان متصل می‌کند چیست؟",
            answers=["تنگه هرمز"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-008",
            track="short_qa",
            split="public_eval",
            prompt="بزرگ‌ترین جزیره ایران در خلیج فارس چه نام دارد؟",
            answers=["قشم", "جزیره قشم"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-009",
            track="short_qa",
            split="public_eval",
            prompt="در کدام شهر ایران میدان نقش جهان واقع شده است؟",
            answers=["اصفهان"],
            category="culture",
        ),
        exact(
            "peval-public-shortqa-010",
            track="short_qa",
            split="public_eval",
            prompt="نخستین ماه تقویم هجری شمسی چه نام دارد؟",
            answers=["فروردین"],
            category="calendar",
        ),
        exact(
            "peval-public-shortqa-011",
            track="short_qa",
            split="public_eval",
            prompt="چندمین روز فروردین معمولا با سیزده‌بدر شناخته می‌شود؟",
            answers=["سیزدهم", "۱۳", "13"],
            category="calendar",
        ),
        exact(
            "peval-public-shortqa-012",
            track="short_qa",
            split="public_eval",
            prompt="نام مرکز استان آذربایجان شرقی چیست؟",
            answers=["تبریز"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-013",
            track="short_qa",
            split="public_eval",
            prompt="در فارسی، گرم‌ترین فصل سال چه نامیده می‌شود؟",
            answers=["تابستان"],
            category="general",
        ),
        exact(
            "peval-public-shortqa-014",
            track="short_qa",
            split="public_eval",
            prompt="کدام رنگ معمولا در میانه پرچم سه‌رنگ ایران قرار دارد؟",
            answers=["سفید"],
            category="general",
        ),
        exact(
            "peval-public-shortqa-015",
            track="short_qa",
            split="public_eval",
            prompt="یک کیلومتر چند متر است؟",
            answers=["هزار", "هزار متر", "۱۰۰۰", "1000"],
            category="units",
        ),
        exact(
            "peval-public-shortqa-016",
            track="short_qa",
            split="public_eval",
            prompt="قطب جنوب در کدام نیم‌کره زمین قرار دارد؟",
            answers=["نیم‌کره جنوبی", "جنوبی"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-017",
            track="short_qa",
            split="public_eval",
            prompt="بزرگ‌ترین سیاره منظومه شمسی چه نام دارد؟",
            answers=["مشتری", "سیاره مشتری"],
            category="science",
        ),
        exact(
            "peval-public-shortqa-018",
            track="short_qa",
            split="public_eval",
            prompt="در زبان فارسی، مخالف کلمه «روز» چیست؟",
            answers=["شب"],
            category="language",
        ),
        exact(
            "peval-public-shortqa-019",
            track="short_qa",
            split="public_eval",
            prompt="چه عددی را اگر در صفر ضرب کنیم، حاصل صفر می‌شود؟",
            answers=["هر عدد", "همه اعداد", "هر عددی"],
            category="math",
        ),
        exact(
            "peval-public-shortqa-020",
            track="short_qa",
            split="public_eval",
            prompt="نام مرکز استان گیلان چیست؟",
            answers=["رشت"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-021",
            track="short_qa",
            split="public_eval",
            prompt="کدام رنگ از ترکیب آبی و زرد به دست می‌آید؟",
            answers=["سبز"],
            category="science",
        ),
        exact(
            "peval-public-shortqa-022",
            track="short_qa",
            split="public_eval",
            prompt="در دستگاه گردش خون انسان، خون پاک از کدام بطن قلب به آئورت می‌رود؟",
            answers=["بطن چپ", "چپ"],
            category="science",
        ),
        exact(
            "peval-public-shortqa-023",
            track="short_qa",
            split="public_eval",
            prompt="نام پل قدیمی معروف اصفهان روی زاینده‌رود که از دوره صفویه به‌جا مانده چیست؟",
            answers=["سی و سه پل", "سی‌و‌سه پل", "پل سی و سه پل"],
            category="culture",
        ),
        exact(
            "peval-public-shortqa-024",
            track="short_qa",
            split="public_eval",
            prompt="جشن چهارشنبه‌سوری در آستانه کدام جشن بزرگ ایرانی برگزار می‌شود؟",
            answers=["نوروز", "عید نوروز"],
            category="culture",
        ),
        exact(
            "peval-public-shortqa-025",
            track="short_qa",
            split="public_eval",
            prompt="در ایران، روز معلم در کدام ماه شمسی است؟",
            answers=["اردیبهشت"],
            category="calendar",
        ),
        exact(
            "peval-public-shortqa-026",
            track="short_qa",
            split="public_eval",
            prompt="در کدام استان ایران، شهر کیش قرار دارد؟",
            answers=["هرمزگان"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-027",
            track="short_qa",
            split="public_eval",
            prompt="در صفحه‌کلید استاندارد، حرف «ش» معمولا روی کدام ردیف قرار دارد؟",
            answers=["ردیف بالا", "ردیف بالای حروف"],
            category="technology",
            difficulty=2,
        ),
        exact(
            "peval-public-shortqa-028",
            track="short_qa",
            split="public_eval",
            prompt="نام بزرگ‌ترین اقیانوس جهان چیست؟",
            answers=["اقیانوس آرام", "آرام"],
            category="geography",
        ),
        exact(
            "peval-public-shortqa-029",
            track="short_qa",
            split="public_eval",
            prompt="در زبان فارسی، فعل «رفتن» در زمان حال ساده اول‌شخص مفرد چیست؟",
            answers=["می‌روم", "میروم"],
            category="language",
        ),
        exact(
            "peval-public-shortqa-030",
            track="short_qa",
            split="public_eval",
            prompt="کدام فلز در دمای اتاق به حالت مایع است؟",
            answers=["جیوه"],
            category="science",
        ),
    ]
    return items


def public_reading() -> list[dict[str, Any]]:
    items = [
        f1(
            "peval-public-reading-005",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: نسرین صبح به آزمایشگاه رفت تا نمونه‌ی آبی را که "
                "از رودخانه گرفته بود بررسی کند. او می‌خواست بفهمد چرا ماهی‌های منطقه کم شده‌اند. "
                "بعد از چند ساعت آزمایش، نتیجه نشان داد که اکسیژن محلول در آب پایین است. "
                "نسرین تصمیم گرفت گزارشی برای شهرداری بنویسد. سوال: نسرین تصمیم گرفت برای چه نهادی گزارش بنویسد؟"
            ),
            answers=["شهرداری", "برای شهرداری"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-006",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: کیان هر شب پیش از خواب کمی کتاب می‌خواند تا "
                "ذهنش از کارهای روز فاصله بگیرد. او متوجه شد در روزهایی که این کار را انجام می‌دهد، "
                "صبح راحت‌تر بیدار می‌شود. سوال: کیان متوجه چه نتیجه‌ای از خواندن شبانه شد؟"
            ),
            answers=["راحت‌تر بیدار شدن صبح", "بیدار شدن آسان‌تر در صبح"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-007",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: روستای پیرانه چند سال پیش بدون آب لوله‌کشی بود. "
                "اهالی با کمک گروهی داوطلب، چاه عمیقی حفر کردند و لوله‌ها را تا خانه‌ها رساندند. "
                "حالا همه به آب سالم دسترسی دارند. سوال: مشکل اصلی روستا پیش از این کار چه بود؟"
            ),
            answers=["نبود آب لوله‌کشی", "نداشتن آب لوله‌کشی"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-008",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مهسا یک کارگاه کوچک سفال دارد. او ابتدا گل را "
                "ورز می‌دهد، بعد آن را روی چرخ شکل می‌دهد و در نهایت ظرف‌ها را در کوره می‌پزد. "
                "سوال: گام پایانی در کار مهسا چیست؟"
            ),
            answers=["پختن ظرف‌ها در کوره", "پختن در کوره"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-009",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک باغبان جوان متوجه شد در گوشه‌ای از باغ، "
                "گل‌ها زودتر از بقیه پژمرده می‌شوند. او بررسی کرد و دید آن گوشه آفتاب کمتری "
                "می‌گیرد. سوال: علت پژمرده شدن زودتر گل‌ها چه بود؟"
            ),
            answers=["کم بودن آفتاب", "نور آفتاب کم"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-010",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک شرکت کوچک تصمیم گرفت برای کاهش هزینه‌ها، "
                "جلسه‌های هفتگی را به صورت آنلاین برگزار کند. بعد از سه ماه، هزینه ایاب و ذهاب "
                "به نصف رسید. سوال: تصمیم شرکت چه اثری بر هزینه‌ها داشت؟"
            ),
            answers=["نصف شدن هزینه ایاب و ذهاب", "نصف شدن هزینه‌های جابه‌جایی"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-011",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: ساسان همیشه دیر به مدرسه می‌رسید. معلمش پیشنهاد "
                "کرد لباس‌های روز بعد را شب قبل آماده کند. ساسان این کار را انجام داد و از هفته بعد "
                "به‌موقع به کلاس رسید. سوال: راه‌حلی که معلم پیشنهاد کرد چه بود؟"
            ),
            answers=["آماده کردن لباس شب قبل", "آماده کردن لباس‌ها در شب پیش"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-012",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پژوهشگر دید که در خانه‌هایی که گیاه آپارتمانی "
                "وجود دارد، رطوبت هوا کمی بیشتر است. او این موضوع را در یک مقاله کوتاه گزارش کرد. "
                "سوال: یافته اصلی پژوهشگر چه بود؟"
            ),
            answers=["بالاتر بودن رطوبت در خانه‌های دارای گیاه", "افزایش رطوبت در خانه‌های با گیاه"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-013",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: تیم توسعه نرم‌افزار متوجه شد بیشتر گزارش‌های خطا "
                "از یک صفحه خاص می‌آید. آن‌ها آن صفحه را بازنویسی کردند و تعداد گزارش‌ها به یک‌سوم "
                "رسید. سوال: نتیجه بازنویسی صفحه چه بود؟"
            ),
            answers=["کاهش گزارش خطا به یک‌سوم", "یک‌سوم شدن گزارش‌های خطا"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-014",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: در یک مدرسه روستایی، دانش‌آموزان با کمک معلم خود "
                "یک کتابخانه کوچک ساختند. کتاب‌ها از اهالی روستا هدیه گرفته شد. حالا هر بچه می‌تواند "
                "هفته‌ای یک کتاب امانت بگیرد. سوال: کتاب‌های کتابخانه از کجا تامین شدند؟"
            ),
            answers=["از اهالی روستا", "هدیه اهالی روستا"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-015",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک کارمند بانک دید که اگر صبح‌ها به‌جای فهرست بلند، "
                "فقط سه کار مهم را یادداشت کند، تا ظهر آن‌ها را تمام می‌کند. این روش به بقیه همکارانش هم "
                "پیشنهاد داد. سوال: روش کارمند چه بود؟"
            ),
            answers=["یادداشت سه کار مهم در صبح", "نوشتن سه کار مهم در آغاز روز"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-016",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: در یک محله، مردم برای کاهش مصرف آب، شیرهای آب "
                "خانه‌ها را با شیرهای جدیدی عوض کردند که هوا را با آب مخلوط می‌کنند. مصرف آب در سه ماه "
                "اول حدود ده درصد کم شد. سوال: علت کاهش مصرف چه بود؟"
            ),
            answers=["تعویض شیرها با شیرهای مخلوط‌کن هوا", "نصب شیرهای جدید مخلوط‌کننده هوا"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-017",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک کافه کوچک تصمیم گرفت لیوان‌های یک‌بار مصرف را "
                "بردارد و به مشتری‌های همیشگی لیوان شخصی بدهد. بعد از شش ماه، هزینه خرید لیوان "
                "کاغذی به یک‌چهارم رسید. سوال: تغییر چه اثری بر هزینه داشت؟"
            ),
            answers=["یک‌چهارم شدن هزینه لیوان کاغذی", "کاهش هزینه لیوان کاغذی به یک‌چهارم"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-018",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک کشاورز دید زمینش در یک گوشه نمک بالایی دارد و "
                "گندم در آن قسمت رشد نمی‌کند. او در آن گوشه به‌جای گندم گیاه مقاوم به شوری کاشت. "
                "سوال: کشاورز در آن گوشه چه نوع گیاهی کاشت؟"
            ),
            answers=["گیاه مقاوم به شوری", "مقاوم به شوری"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-019",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر یک کتابفروشی متوجه شد بیشتر مشتری‌ها صبح "
                "زود می‌آیند. او تصمیم گرفت ساعت کاری را زودتر آغاز کند. سوال: تصمیم مدیر بر چه پایه‌ای "
                "گرفته شد؟"
            ),
            answers=["زمان حضور بیشتر مشتری‌ها", "آمدن مشتری‌ها در صبح زود"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-020",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: گروهی از همسایه‌ها هر هفته به‌نوبت زباله بازیافتی "
                "ساختمان را به مرکز بازیافت می‌برند. این کار باعث شده زباله‌ای که در سطل عمومی می‌رود "
                "نصف شود. سوال: نوبت‌بندی همسایه‌ها چه نتیجه‌ای داده است؟"
            ),
            answers=["نصف شدن زباله سطل عمومی", "کاهش نصف زباله عمومی ساختمان"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-021",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پزشک به بیمارش گفت که دلیل سردرد مکرر، کم‌خوابی "
                "و کم‌نوشیدن آب است. بیمار سعی کرد هر شب هفت ساعت بخوابد و روزی شش لیوان آب بنوشد. "
                "بعد از یک ماه سردردها کم شد. سوال: پزشک چه دو علتی برای سردرد بیمار ذکر کرد؟"
            ),
            answers=["کم‌خوابی و کم‌نوشیدن آب", "کم خوابیدن و کم آب نوشیدن"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-022",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: در یک کارخانه، خط تولید قبلا با ۱۲ نفر کار می‌کرد. "
                "بعد از خرید یک دستگاه جدید بسته‌بندی، با ۸ نفر هم کار خط انجام می‌شود. سوال: تعداد "
                "نفرات لازم برای کار خط بعد از تغییر چقدر شده است؟"
            ),
            answers=["هشت نفر", "۸ نفر", "8 نفر"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-023",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک معلم تصمیم گرفت در کلاس به‌جای امتحان نهایی "
                "کتبی، از هر دانش‌آموز یک پروژه عملی بخواهد. والدین گفتند بچه‌ها انگیزه بیشتری "
                "گرفته‌اند. سوال: معلم به‌جای امتحان نهایی چه چیزی خواست؟"
            ),
            answers=["پروژه عملی", "یک پروژه عملی از هر دانش‌آموز"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-024",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک رستوران کوچک سفارش‌ها را از طریق پیامک می‌گرفت. "
                "بعد از راه‌اندازی یک اپلیکیشن ساده، تعداد سفارش‌ها در روز دو برابر شد. سوال: تغییر "
                "چه اثری بر سفارش‌ها داشت؟"
            ),
            answers=["دو برابر شدن تعداد سفارش روزانه", "افزایش دو برابری سفارش روزانه"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-025",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: شهرداری یک شهر کوچک تصمیم گرفت در پارک‌ها چراغ‌های "
                "خورشیدی نصب کند. هزینه برق روشنایی پارک‌ها در سال اول حدود ۳۰ درصد کاهش یافت. "
                "سوال: نصب چراغ خورشیدی چه اثری بر هزینه برق پارک‌ها داشت؟"
            ),
            answers=["حدود ۳۰ درصد کاهش", "کاهش حدود سی درصد", "کاهش حدود 30 درصد"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-026",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک شرکت حمل‌ونقل، مسیر روزانه کامیون‌ها را با یک "
                "نرم‌افزار جدید بهینه کرد. زمان رسیدن به انبار به‌طور میانگین یک ساعت کم شد. "
                "سوال: کاهش زمان رسیدن چقدر بود؟"
            ),
            answers=["یک ساعت", "۱ ساعت", "1 ساعت", "میانگین یک ساعت"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-027",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک خبرنگار از معلمی گزارش گرفت که سال‌هاست در "
                "روستایی دورافتاده درس می‌دهد. معلم گفت تنها انگیزه‌اش دیدن پیشرفت بچه‌هاست. "
                "سوال: انگیزه معلم برای ادامه کار چیست؟"
            ),
            answers=["دیدن پیشرفت بچه‌ها", "پیشرفت بچه‌ها"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-028",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک گروه پژوهشی از دانش‌آموزان دبیرستانی خواست هر "
                "روز سی دقیقه پیاده‌روی کنند. بعد از دو ماه، نمره‌های درس‌های نظری در میانگین کلاس "
                "اندکی بهتر شد. سوال: پژوهشگران از دانش‌آموزان چه چیزی خواستند؟"
            ),
            answers=["پیاده‌روی روزانه سی دقیقه", "روزی سی دقیقه پیاده‌روی"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-029",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک مغازه‌دار محله، خرید نسیه را برای مشتری‌های "
                "همیشگی محدود به مبلغ مشخصی کرد. این کار از بدهی‌های معوق او در یک سال جلوگیری "
                "کرد. سوال: تصمیم مغازه‌دار چه بود؟"
            ),
            answers=["محدود کردن خرید نسیه به مبلغ مشخص", "تعیین سقف برای خرید نسیه"],
            category="reading_comprehension",
        ),
        f1(
            "peval-public-reading-030",
            track="reading",
            split="public_eval",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: گروهی از داوطلبان یک پل چوبی قدیمی روستا را تعمیر "
                "کردند. حالا بچه‌های روستا برای رفتن به مدرسه دیگر مجبور به دور زدن از مسیر طولانی "
                "نیستند. سوال: نتیجه تعمیر پل برای بچه‌های روستا چه شد؟"
            ),
            answers=["نیاز نداشتن به دور زدن از مسیر طولانی", "حذف دور زدن از مسیر طولانی"],
            category="reading_comprehension",
        ),
    ]
    return items


def public_instruction() -> list[dict[str, Any]]:
    items = [
        instr(
            "peval-public-instruction-005",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام کوتاه فارسی برای دعوت دوستت به یک پیاده‌روی صبحگاهی بنویس که شامل "
                "کلمات «صبح» و «پارک» باشد و بین ۸ تا ۲۵ کلمه طول داشته باشد."
            ),
            constraints={
                "required_keywords": ["صبح", "پارک"],
                "min_words": 8,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-006",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک توصیه کوتاه برای صرفه‌جویی در برق بنویس. پاسخ نباید شامل کلمه «همیشه» باشد و "
                "باید کلمه «لامپ» را داشته باشد. طول پاسخ بین ۶ تا ۳۰ کلمه."
            ),
            constraints={
                "required_keywords": ["لامپ"],
                "forbidden": ["همیشه"],
                "min_words": 6,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-007",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله کوتاه فارسی بنویس که با «اگر» شروع شود و کلمه «تمرین» را داشته باشد. "
                "طول بین ۶ تا ۲۵ کلمه."
            ),
            constraints={
                "required_prefix": "اگر",
                "required_keywords": ["تمرین"],
                "min_words": 6,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-008",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله فارسی درباره فایده مطالعه بنویس که با «کتاب» پایان یابد و کلمه «دانش» را "
                "داشته باشد. حداکثر ۲۰ کلمه."
            ),
            constraints={
                "required_suffix": "کتاب",
                "required_keywords": ["دانش"],
                "min_words": 5,
                "max_words": 20,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-009",
            track="instruction",
            split="public_eval",
            prompt=(
                "در یک پاراگراف کوتاه درباره صرفه‌جویی در آب بنویس. پاسخ باید شامل کلمات «آب» و "
                "«شیر» باشد و علامت سوال نداشته باشد. طول بین ۱۲ تا ۴۰ کلمه."
            ),
            constraints={
                "required_keywords": ["آب", "شیر"],
                "forbidden": ["؟", "?"],
                "min_words": 12,
                "max_words": 40,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-010",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام کوتاه برای تشکر از یک همکار بنویس که شامل کلمه «همکاری» باشد و طول آن "
                "بین ۸ تا ۲۵ کلمه باشد. از کلمه «خیلی» استفاده نکن."
            ),
            constraints={
                "required_keywords": ["همکاری"],
                "forbidden": ["خیلی"],
                "min_words": 8,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-011",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک توضیح کوتاه برای یک کودک هفت ساله درباره چرخه آب بنویس. باید کلمات «ابر» و "
                "«باران» را داشته باشد و طول بین ۱۰ تا ۳۵ کلمه."
            ),
            constraints={
                "required_keywords": ["ابر", "باران"],
                "min_words": 10,
                "max_words": 35,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-012",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک معرفی کوتاه از خودت برای یک کلاس آنلاین فارسی بنویس که با «سلام» شروع شود و "
                "کلمه «هدف» را داشته باشد. طول بین ۱۰ تا ۳۰ کلمه."
            ),
            constraints={
                "required_prefix": "سلام",
                "required_keywords": ["هدف"],
                "min_words": 10,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-013",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله انگیزشی برای یک دوست که در حال درس خواندن است بنویس. باید کلمه «امروز» "
                "را داشته باشد و کوتاه باشد. حداکثر ۱۸ کلمه."
            ),
            constraints={
                "required_keywords": ["امروز"],
                "min_words": 5,
                "max_words": 18,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-014",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک توضیح کوتاه درباره فایده پیاده‌روی روزانه بنویس. پاسخ باید شامل کلمه «سلامت» "
                "باشد، نباید کلمه «همیشه» داشته باشد و طول بین ۸ تا ۳۰ کلمه باشد."
            ),
            constraints={
                "required_keywords": ["سلامت"],
                "forbidden": ["همیشه"],
                "min_words": 8,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-015",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک متن سه‌جمله‌ای کوتاه برای معرفی یک کتاب موردعلاقه بنویس که شامل کلمه «داستان» "
                "باشد. طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_keywords": ["داستان"],
                "min_words": 15,
                "max_words": 45,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-016",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام کوتاه برای رزرو یک قرار ملاقات کاری بنویس. پاسخ باید شامل «جلسه» و یک "
                "ساعت مشخص (مثل «ساعت ۱۰») باشد. از کلمه «شاید» استفاده نکن. حداکثر ۳۰ کلمه."
            ),
            constraints={
                "required_keywords": ["جلسه", "ساعت"],
                "forbidden": ["شاید"],
                "min_words": 8,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-017",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک توضیح کوتاه درباره کاربرد ایمیل در محیط کار بنویس که با «ایمیل» شروع شود و "
                "کلمه «ارتباط» را داشته باشد. طول بین ۸ تا ۲۸ کلمه."
            ),
            constraints={
                "required_prefix": "ایمیل",
                "required_keywords": ["ارتباط"],
                "min_words": 8,
                "max_words": 28,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-018",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام تبریک کوتاه برای موفقیت یک دوست بنویس که با «تبریک» شروع شود و با «است» "
                "تمام شود. حداکثر ۲۰ کلمه."
            ),
            constraints={
                "required_prefix": "تبریک",
                "required_suffix": "است",
                "min_words": 5,
                "max_words": 20,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-019",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک یادداشت کوتاه برای آشپز خانه بنویس که سفارش غذای فردا را توضیح می‌دهد. باید "
                "کلمه «ناهار» و کلمه «ساعت» را داشته باشد. طول بین ۱۰ تا ۳۰ کلمه."
            ),
            constraints={
                "required_keywords": ["ناهار", "ساعت"],
                "min_words": 10,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-020",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله درباره فایده زود خوابیدن بنویس که با «اگر» شروع شود و با «بهتر است» "
                "پایان یابد. حداکثر ۲۰ کلمه."
            ),
            constraints={
                "required_prefix": "اگر",
                "required_suffix": "بهتر است",
                "min_words": 6,
                "max_words": 20,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-021",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک توضیح کوتاه درباره مفهوم «تیم‌ورک» در محیط اداری بنویس. باید شامل «همکار» و "
                "«هدف مشترک» باشد. حداکثر ۳۵ کلمه."
            ),
            constraints={
                "required_keywords": ["همکار", "هدف مشترک"],
                "min_words": 10,
                "max_words": 35,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-022",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک متن کوتاه راهنما برای استفاده از یک نان‌توستر بنویس. باید مرحله‌ای باشد و "
                "حداقل سه فعل امری داشته باشد. طول بین ۱۵ تا ۴۵ کلمه. از کلمه «خطر» استفاده نکن."
            ),
            constraints={
                "required_keywords": ["نان"],
                "forbidden": ["خطر"],
                "min_words": 15,
                "max_words": 45,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-023",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک یادداشت کوتاه برای یک همکار بنویس که توضیح می‌دهد امروز چرا دیر آمده‌ای. باید "
                "شامل کلمه «ترافیک» باشد و علامت تعجب نداشته باشد. حداکثر ۲۵ کلمه."
            ),
            constraints={
                "required_keywords": ["ترافیک"],
                "forbidden": ["!"],
                "min_words": 6,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-024",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام کوتاه برای دعوت به یک نشست خانوادگی بنویس که با «خانواده» شروع شود و "
                "کلمه «جمعه» را داشته باشد. حداکثر ۲۵ کلمه."
            ),
            constraints={
                "required_prefix": "خانواده",
                "required_keywords": ["جمعه"],
                "min_words": 6,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-025",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله کوتاه درباره فایده یادگیری زبان دوم بنویس که شامل کلمه «فرصت» باشد. "
                "از کلمه «همیشه» استفاده نکن. حداکثر ۳۰ کلمه."
            ),
            constraints={
                "required_keywords": ["فرصت"],
                "forbidden": ["همیشه"],
                "min_words": 7,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-026",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پاسخ کوتاه و مودب برای رد یک دعوت ناهار بنویس. باید شامل «ممنون» و یک "
                "علت کوتاه باشد. حداکثر ۲۰ کلمه."
            ),
            constraints={
                "required_keywords": ["ممنون"],
                "min_words": 6,
                "max_words": 20,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-027",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک یادداشت کوتاه برای معلم فرزندت بنویس که توضیح می‌دهد فردا فرزندت غایب است. "
                "باید با «سلام» شروع شود و کلمه «بیمار» را داشته باشد. حداکثر ۳۰ کلمه."
            ),
            constraints={
                "required_prefix": "سلام",
                "required_keywords": ["بیمار"],
                "min_words": 8,
                "max_words": 30,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-028",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام تشکر کوتاه از پزشک خانوادگی بنویس که شامل کلمه «صبر» باشد. حداکثر ۲۵ کلمه. "
                "نباید علامت سوال داشته باشد."
            ),
            constraints={
                "required_keywords": ["صبر"],
                "forbidden": ["؟", "?"],
                "min_words": 6,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-029",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک جمله درباره فایده ورزش صبحگاهی بنویس که با «ورزش» شروع شود و کلمه «انرژی» "
                "را داشته باشد. حداکثر ۲۵ کلمه."
            ),
            constraints={
                "required_prefix": "ورزش",
                "required_keywords": ["انرژی"],
                "min_words": 6,
                "max_words": 25,
            },
            category="instruction_following",
        ),
        instr(
            "peval-public-instruction-030",
            track="instruction",
            split="public_eval",
            prompt=(
                "یک پیام کوتاه برای راهنمایی نشانی به یک تاکسی‌اینترنتی بنویس. پاسخ باید شامل "
                "کلمه «خیابان» و «پلاک» باشد. حداکثر ۳۰ کلمه."
            ),
            constraints={
                "required_keywords": ["خیابان", "پلاک"],
                "min_words": 8,
                "max_words": 30,
            },
            category="instruction_following",
        ),
    ]
    return items


def public_culture() -> list[dict[str, Any]]:
    items = [
        mcq(
            "peval-public-culture-005",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ ایرانی، سفره هفت‌سین معمولا با کدام جشن همراه است؟",
            choices=["یلدا", "نوروز", "مهرگان", "سده"],
            answer_index=1,
            category="nowruz",
        ),
        mcq(
            "peval-public-culture-006",
            track="culture",
            split="public_eval",
            prompt="در سفره هفت‌سین، کدام مورد یکی از هفت «س» سنتی محسوب می‌شود؟",
            choices=["شیرینی", "سنجد", "شمع", "نان"],
            answer_index=1,
            category="nowruz",
        ),
        mcq(
            "peval-public-culture-007",
            track="culture",
            split="public_eval",
            prompt="چهارشنبه‌سوری معمولا در شب آخرین چهارشنبه کدام ماه برگزار می‌شود؟",
            choices=["دی", "بهمن", "اسفند", "فروردین"],
            answer_index=2,
            category="nowruz",
        ),
        mcq(
            "peval-public-culture-008",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ عامه ایرانی، خواندن دیوان حافظ برای فال گرفتن بیشتر در کدام شب رواج دارد؟",
            choices=["شب یلدا", "شب چهارشنبه‌سوری", "شب جمعه", "شب نوروز"],
            answer_index=0,
            category="yalda",
        ),
        mcq(
            "peval-public-culture-009",
            track="culture",
            split="public_eval",
            prompt="کدام یک از خوراکی‌های زیر بیشتر در سفره شب یلدا دیده می‌شود؟",
            choices=["کاهو", "آناناس", "انار", "موز"],
            answer_index=2,
            category="yalda",
        ),
        mcq(
            "peval-public-culture-010",
            track="culture",
            split="public_eval",
            prompt="کدام شاعر ایرانی به «شیخ اجل» معروف است؟",
            choices=["حافظ", "سعدی", "رودکی", "نظامی"],
            answer_index=1,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-011",
            track="culture",
            split="public_eval",
            prompt="کدام شاعر ایرانی با لقب «لسان‌الغیب» شناخته می‌شود؟",
            choices=["مولوی", "خیام", "حافظ", "فردوسی"],
            answer_index=2,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-012",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ ایرانی، «عیدی» معمولا در کدام مناسبت داده می‌شود؟",
            choices=["نوروز", "روز مادر", "شب یلدا", "روز معلم"],
            answer_index=0,
            category="nowruz",
        ),
        mcq(
            "peval-public-culture-013",
            track="culture",
            split="public_eval",
            prompt="کدام نوع موسیقی ایرانی بر پایه «دستگاه» سامان یافته است؟",
            choices=["موسیقی پاپ", "موسیقی محلی شمالی", "موسیقی سنتی", "موسیقی راک"],
            answer_index=2,
            category="music",
        ),
        mcq(
            "peval-public-culture-014",
            track="culture",
            split="public_eval",
            prompt="کدام ساز ایرانی با چوب نازکی به نام «مضراب» نواخته می‌شود و بدنه‌ای ذوزنقه‌ای دارد؟",
            choices=["تار", "دف", "سنتور", "نی"],
            answer_index=2,
            category="music",
        ),
        mcq(
            "peval-public-culture-015",
            track="culture",
            split="public_eval",
            prompt="در آشپزی سنتی ایرانی، کدام غذا با برنج و گوشت و سبزی پخته می‌شود؟",
            choices=["قورمه‌سبزی", "ماکارونی", "پیتزا", "سوشی"],
            answer_index=0,
            category="food",
        ),
        mcq(
            "peval-public-culture-016",
            track="culture",
            split="public_eval",
            prompt="آش رشته معمولا در کدام مناسبت‌ها بیشتر پخته می‌شود؟",
            choices=["نوروز و نذر", "تولد", "مهمانی شام رسمی", "صبحانه"],
            answer_index=0,
            category="food",
        ),
        mcq(
            "peval-public-culture-017",
            track="culture",
            split="public_eval",
            prompt="در ادب فارسی، «دیوان» معمولا به چه چیز اشاره دارد؟",
            choices=[
                "فقط مجموعه نامه‌های یک پادشاه",
                "مجموعه شعرهای یک شاعر",
                "کتاب آشپزی",
                "کتاب مرجع تاریخی",
            ],
            answer_index=1,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-018",
            track="culture",
            split="public_eval",
            prompt="در سفره ایرانی، نان «بربری» معمولا چه شکلی دارد؟",
            choices=["گرد و کوچک", "بیضی و کشیده", "مکعب", "مثلث"],
            answer_index=1,
            category="food",
        ),
        mcq(
            "peval-public-culture-019",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ گفتاری فارسی، عبارت «سلامتی شما» معمولا کجا گفته می‌شود؟",
            choices=[
                "هنگام نوشیدن چای یا نوشیدنی در جمع",
                "هنگام خداحافظی از تلفن کار",
                "هنگام شروع جلسه رسمی",
                "هنگام شروع خواندن نماز",
            ],
            answer_index=0,
            category="etiquette",
        ),
        mcq(
            "peval-public-culture-020",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ ایرانی، «سیزده‌بدر» معمولا به چه شکلی برگزار می‌شود؟",
            choices=[
                "ماندن در خانه و خواندن قرآن",
                "رفتن به طبیعت و گذراندن روز در فضای باز",
                "روزه گرفتن از صبح تا شب",
                "خرید لباس عید",
            ],
            answer_index=1,
            category="nowruz",
        ),
        mcq(
            "peval-public-culture-021",
            track="culture",
            split="public_eval",
            prompt="کدام یک از موارد زیر یکی از «هنرهای دستی» سنتی ایران به شمار می‌آید؟",
            choices=["برنامه‌نویسی", "قالی‌بافی", "دوبله فیلم", "جرنالیسم"],
            answer_index=1,
            category="handicrafts",
        ),
        mcq(
            "peval-public-culture-022",
            track="culture",
            split="public_eval",
            prompt="در ادب فارسی، عبارت «ای دل غافل» معمولا چه حسی را منتقل می‌کند؟",
            choices=["شادی شدید", "افسوس و هشدار", "خشم", "تعجب علمی"],
            answer_index=1,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-023",
            track="culture",
            split="public_eval",
            prompt="در ضرب‌المثل فارسی «از این ستون به آن ستون فرج است» منظور چیست؟",
            choices=[
                "گذر زمان ممکن است گشایش بیاورد",
                "باید همیشه سرجای خود ایستاد",
                "ستون‌های بنا را باید کم کرد",
                "دو ستون بهتر از یکی است",
            ],
            answer_index=0,
            category="proverb",
            difficulty=3,
        ),
        mcq(
            "peval-public-culture-024",
            track="culture",
            split="public_eval",
            prompt="در آداب میهمانی ایرانی، رسم «تعارف» معمولا به چه معناست؟",
            choices=[
                "اصرار مودبانه در پذیرایی یا گرفتن چیزی",
                "نوعی موسیقی محلی",
                "نوعی غذای محلی",
                "نوعی رقص جمعی",
            ],
            answer_index=0,
            category="etiquette",
        ),
        mcq(
            "peval-public-culture-025",
            track="culture",
            split="public_eval",
            prompt="کدام یک از این جشن‌ها ریشه پیشااسلامی در فرهنگ ایرانی دارد؟",
            choices=["مهرگان", "روز مادر", "روز کارگر", "روز پزشک"],
            answer_index=0,
            category="festival",
        ),
        mcq(
            "peval-public-culture-026",
            track="culture",
            split="public_eval",
            prompt="در فرهنگ گفتاری ایرانی، گفتن «قابل شما را ندارد» معمولا کجا به‌کار می‌رود؟",
            choices=[
                "هنگام تعارف در فروش یا هدیه دادن",
                "هنگام عذرخواهی در محل کار",
                "هنگام تبریک گفتن",
                "هنگام پایان سخنرانی رسمی",
            ],
            answer_index=0,
            category="etiquette",
        ),
        mcq(
            "peval-public-culture-027",
            track="culture",
            split="public_eval",
            prompt="در ادبیات فارسی، «رباعی» قالب شعری با چند مصراع است؟",
            choices=["دو", "سه", "چهار", "پنج"],
            answer_index=2,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-028",
            track="culture",
            split="public_eval",
            prompt="کدام شاعر بیشتر با رباعیات خود در جهان شناخته می‌شود؟",
            choices=["خیام", "سنایی", "هاتف", "اوحدی"],
            answer_index=0,
            category="literature_culture",
        ),
        mcq(
            "peval-public-culture-029",
            track="culture",
            split="public_eval",
            prompt="کدام بنای تاریخی در شیراز قرار دارد و آرامگاه یک شاعر بزرگ فارسی است؟",
            choices=["تخت جمشید", "حافظیه", "ارگ بم", "میدان نقش جهان"],
            answer_index=1,
            category="culture",
        ),
        mcq(
            "peval-public-culture-030",
            track="culture",
            split="public_eval",
            prompt="در زبان فارسی، «خط نستعلیق» بیشتر برای چه کاری استفاده می‌شود؟",
            choices=[
                "نوشتن متون کامپیوتری",
                "خوش‌نویسی شعر و ادبیات",
                "نقشه‌برداری مهندسی",
                "نوشتن فرمول ریاضی",
            ],
            answer_index=1,
            category="culture",
        ),
    ]
    return items


def hard_reasoning() -> list[dict[str, Any]]:
    items = [
        mcq(
            "peval-hard-reasoning-005",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر کارمندی که به سرور دسترسی دارد، رمز عبور دو مرحله‌ای فعال کرده باشد و "
                "علی به سرور دسترسی دارد، کدام نتیجه قطعی است؟"
            ),
            choices=[
                "علی رمز عبور دو مرحله‌ای فعال کرده است",
                "علی رمز عبور دو مرحله‌ای ندارد",
                "هیچ نتیجه‌ای نمی‌توان گرفت",
                "علی به سرور دسترسی ندارد",
            ],
            answer_index=0,
            category="modus_ponens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-006",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "همه پزشکان دانشگاه‌رفته‌اند. مریم دانشگاه نرفته است. کدام نتیجه قطعی است؟"
            ),
            choices=[
                "مریم پزشک است",
                "مریم پزشک نیست",
                "مریم ممکن است پزشک باشد",
                "هیچ نتیجه‌ای نمی‌توان گرفت",
            ],
            answer_index=1,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-007",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "چهار نفر به نام‌های نازنین، بهرام، کاوه و سارا در صف ایستاده‌اند. نازنین دقیقا قبل از "
                "بهرام است. سارا آخرین نفر صف نیست. کاوه پشت سر بهرام است. ترتیب از اول به آخر کدام است؟"
            ),
            choices=[
                "نازنین، بهرام، کاوه، سارا",
                "نازنین، بهرام، سارا، کاوه",
                "بهرام، نازنین، کاوه، سارا",
                "نازنین، سارا، بهرام، کاوه",
            ],
            answer_index=1,
            category="ordering_logic",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-008",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هیچ ماشین برقی به بنزین نیاز ندارد و خودروی شرکت ما برقی نیست، چه نتیجه قطعی "
                "می‌توان گرفت؟"
            ),
            choices=[
                "خودروی شرکت ما به بنزین نیاز دارد",
                "خودروی شرکت ما به بنزین نیاز ندارد",
                "نمی‌توان قطعا تصمیم گرفت",
                "هیچ خودرویی به بنزین نیاز ندارد",
            ],
            answer_index=2,
            category="logical_quantifier",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-009",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "علی می‌گوید: «اگر فردا باران ببارد، در خانه می‌مانم.» فردا علی در خانه نماند. "
                "چه نتیجه قطعی می‌توان گرفت؟"
            ),
            choices=[
                "فردا باران بارید",
                "فردا باران نبارید",
                "هیچ نتیجه‌ای نمی‌توان گرفت",
                "علی همیشه در خانه می‌ماند",
            ],
            answer_index=1,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-010",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "گروهی شامل شش دانش‌آموز است. سه نفر فوتبال بازی می‌کنند، چهار نفر شطرنج بازی می‌کنند، "
                "و دو نفر هر دو را بازی می‌کنند. چند نفر هیچ‌کدام را بازی نمی‌کنند؟"
            ),
            choices=["صفر", "یک", "دو", "سه"],
            answer_index=1,
            category="set_logic",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-011",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر گزاره «هر دانشجوی فلسفه کتاب کانت را خوانده» درست باشد، کدام گزاره معادل آن است؟"
            ),
            choices=[
                "هر کس کتاب کانت را خوانده، دانشجوی فلسفه است",
                "هر کس کتاب کانت را نخوانده، دانشجوی فلسفه نیست",
                "هیچ دانشجوی فلسفه‌ای کتاب کانت را نخوانده",
                "هیچ‌کس به‌جز دانشجویان فلسفه کانت را نمی‌خواند",
            ],
            answer_index=1,
            category="contrapositive",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-012",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "یک قفسه پنج کتاب دارد. کتاب آبی دقیقا کنار کتاب قرمز است. کتاب سبز سمت چپ کتاب آبی "
                "نیست. کتاب زرد دقیقا در وسط است. اگر کتاب قرمز سمت چپ کتاب آبی باشد، کدام چینش "
                "ممکن است؟"
            ),
            choices=[
                "سبز، قرمز، زرد، آبی، سفید",
                "سفید، قرمز، آبی، زرد، سبز",
                "قرمز، آبی، زرد، سبز، سفید",
                "سفید، سبز، زرد، قرمز، آبی",
            ],
            answer_index=3,
            category="ordering_logic",
            difficulty=5,
        ),
        mcq(
            "peval-hard-reasoning-013",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر کس که زبان عربی می‌داند بتواند ترجمه کند و سینا بتواند ترجمه کند، آیا "
                "می‌توان نتیجه گرفت سینا زبان عربی می‌داند؟"
            ),
            choices=[
                "بله، حتما",
                "خیر، این نتیجه‌گیری نادرست است",
                "بله، فقط در صورت وجود یک ترجمه کتبی",
                "هیچ نتیجه‌ای نمی‌توان گرفت",
            ],
            answer_index=1,
            category="affirming_consequent",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-014",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "دو دوست به نام مینا و رضا با هم آشنا هستند. مینا می‌گوید: «من از رضا بزرگ‌ترم.» "
                "رضا می‌گوید: «من از مینا کوچک‌ترم.» اگر یکی از این دو دروغ بگوید، چه نتیجه می‌گیریم؟"
            ),
            choices=[
                "رضا از مینا بزرگ‌تر است",
                "مینا از رضا بزرگ‌تر است",
                "هر دو هم‌سن‌اند",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=2,
            category="logical_consistency",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-015",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "در یک جعبه ۳ توپ قرمز و ۲ توپ آبی است. اگر یک توپ بدون نگاه برداریم و آن توپ آبی "
                "نباشد، کدام جمله درست است؟"
            ),
            choices=[
                "توپ‌های جعبه باقی‌مانده ۲ قرمز و ۲ آبی است",
                "توپ‌های جعبه باقی‌مانده ۳ قرمز و ۱ آبی است",
                "توپ‌های جعبه باقی‌مانده ۲ قرمز و ۱ آبی است",
                "توپ‌های جعبه باقی‌مانده ۳ قرمز و ۲ آبی است",
            ],
            answer_index=2,
            category="conditional_reasoning",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-016",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر سه‌گوش متساوی‌الاضلاع متساوی‌الزاویه باشد و یک سه‌گوش متساوی‌الزاویه نباشد، "
                "آن سه‌گوش چه ویژگی قطعی دارد؟"
            ),
            choices=[
                "متساوی‌الاضلاع نیست",
                "متساوی‌الاضلاع هست",
                "نمی‌توان نتیجه گرفت",
                "قائم‌الزاویه است",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-017",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "در یک شرکت، هیچ کارمند جدیدی به اطلاعات حسابداری دسترسی ندارد. آرش به اطلاعات "
                "حسابداری دسترسی دارد. کدام نتیجه قطعی است؟"
            ),
            choices=[
                "آرش حسابدار است",
                "آرش کارمند جدید نیست",
                "آرش رئیس شرکت است",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=1,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-018",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر کس که در جلسه دیروز بوده دستور جلسه را گرفته باشد و سارا دستور جلسه را "
                "نگرفته، چه نتیجه قطعی می‌گیریم؟"
            ),
            choices=[
                "سارا در جلسه دیروز نبوده است",
                "سارا در جلسه دیروز بوده ولی دستور را گم کرده",
                "سارا دستور را به‌زودی می‌گیرد",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-019",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "گروهی متشکل از هفت نفر است. حداقل چهار نفر زبان فرانسه می‌دانند و حداقل پنج نفر "
                "زبان انگلیسی می‌دانند. حداقل چند نفر هر دو زبان را می‌دانند؟"
            ),
            choices=["یک نفر", "دو نفر", "سه نفر", "چهار نفر"],
            answer_index=1,
            category="pigeonhole",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-020",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر گزاره «هر کارمندی که آموزش امنیت دیده، می‌تواند به سامانه وصل شود» درست باشد، "
                "و حسن نتواند به سامانه وصل شود، چه نتیجه قطعی می‌گیریم؟"
            ),
            choices=[
                "حسن آموزش امنیت ندیده است",
                "حسن آموزش امنیت دیده ولی فراموش کرده",
                "حسن کارمند نیست",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-021",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "علی، بابک و سارا هر کدام یا فقط راست‌گو یا فقط دروغ‌گو هستند. علی می‌گوید: «بابک "
                "دروغ‌گوست.» بابک می‌گوید: «سارا راست‌گوست.» سارا می‌گوید: «من دروغ‌گو نیستم.» "
                "اگر دقیقا یک نفر دروغ‌گو باشد، چه کسی است؟"
            ),
            choices=["علی", "بابک", "سارا", "نمی‌توان تعیین کرد"],
            answer_index=1,
            category="liar_truth",
            difficulty=5,
        ),
        mcq(
            "peval-hard-reasoning-022",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر روز که جلسه برگزار می‌شود، گزارش جلسه در همان روز ارسال می‌شود، و پنجشنبه "
                "هیچ گزارشی ارسال نشد، چه نتیجه قطعی می‌گیریم؟"
            ),
            choices=[
                "پنجشنبه جلسه‌ای برگزار نشد",
                "پنجشنبه جلسه برگزار شد ولی گزارش به فردا موکول شد",
                "هیچ‌گاه پنجشنبه جلسه برگزار نمی‌شود",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-023",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "گزاره‌های زیر با هم سازگارند یا ناسازگار؟ ۱) همه طوطی‌ها سخن می‌گویند. ۲) تونی "
                "یک طوطی است. ۳) تونی سخن نمی‌گوید."
            ),
            choices=[
                "گزاره‌ها با هم سازگارند",
                "گزاره‌ها با هم ناسازگارند",
                "گزاره ۲ بی‌اثر است",
                "تنها در صورت دانستن گونه طوطی می‌توان قضاوت کرد",
            ],
            answer_index=1,
            category="logical_consistency",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-024",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر مدیر فروش باید گزارش هفتگی بدهد و تقی گزارش هفتگی نداده، چه نتیجه قطعی "
                "می‌گیریم؟"
            ),
            choices=[
                "تقی مدیر فروش نیست",
                "تقی مدیر فروش است ولی گزارش گم شده",
                "تقی هفته آینده گزارش می‌دهد",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-025",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "در یک کلاس ۲۰ نفری، حداقل هر دانش‌آموز یک ورزش دوست دارد. ۱۲ نفر فوتبال، ۹ نفر "
                "والیبال و ۵ نفر هر دو را دوست دارند. چند نفر فقط یکی از این دو ورزش را دوست "
                "دارند؟"
            ),
            choices=["یازده", "شانزده", "هفده", "نوزده"],
            answer_index=0,
            category="set_logic",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-026",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر بدانیم «بعضی پزشکان دانشمندند» و «همه دانشمندان مقاله می‌نویسند»، کدام نتیجه "
                "قطعی است؟"
            ),
            choices=[
                "همه پزشکان مقاله می‌نویسند",
                "بعضی پزشکان مقاله می‌نویسند",
                "هیچ پزشکی مقاله نمی‌نویسد",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=1,
            category="syllogism",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-027",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "سه برادر به ترتیب سن از بزرگ به کوچک نام دارند: امیر، علی، آرش. اگر امیر بیست و هشت "
                "ساله و آرش بیست‌وچهار ساله باشد، سن علی می‌تواند کدام عدد نباشد؟"
            ),
            choices=["بیست و پنج", "بیست و شش", "بیست و هفت", "بیست و سه"],
            answer_index=3,
            category="bounded_inference",
            difficulty=3,
        ),
        mcq(
            "peval-hard-reasoning-028",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر نشست بدون دستور کار به اضافه‌کار منجر شود و امروز اضافه‌کاری نشد، چه نتیجه "
                "قطعی می‌گیریم؟"
            ),
            choices=[
                "نشست امروز دستور کار داشت یا نشستی برگزار نشد",
                "هر نشست با دستور کار خوب پیش می‌رود",
                "نشستی برگزار نشد",
                "نشست با دستور کار برگزار شد",
            ],
            answer_index=0,
            category="modus_tollens",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-029",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "گفته شده «اگر بازاریابی تکمیل شود، فروش ماه آینده افزایش می‌یابد.» همچنین گفته "
                "شده «اگر فروش افزایش یابد، شرکت پاداش می‌دهد.» اگر شرکت پاداش نداد، چه نتیجه می‌گیریم؟"
            ),
            choices=[
                "بازاریابی حتما تکمیل نشده",
                "فروش حتما افزایش یافته",
                "هر دو گزاره نقض می‌شوند",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="chain_inference",
            difficulty=4,
        ),
        mcq(
            "peval-hard-reasoning-030",
            track="hard_reasoning",
            split="hard",
            prompt=(
                "اگر هر کاربر با اشتراک طلایی به بخش پیشرفته دسترسی دارد و هیچ مهمانی به بخش "
                "پیشرفته دسترسی ندارد، چه نتیجه قطعی می‌گیریم؟"
            ),
            choices=[
                "هیچ مهمانی اشتراک طلایی ندارد",
                "هر مهمان اشتراک طلایی دارد",
                "هر کاربر طلایی مهمان است",
                "نمی‌توان نتیجه گرفت",
            ],
            answer_index=0,
            category="syllogism",
            difficulty=4,
        ),
    ]
    return items


def hard_math() -> list[dict[str, Any]]:
    items = [
        exact(
            "peval-hard-math-005",
            track="hard_math",
            split="hard",
            prompt=(
                "یک کالا قیمت اولیه ۲۵۰ هزار تومان دارد. ابتدا ۱۰ درصد گران می‌شود و سپس از قیمت "
                "جدید ۲۰ درصد تخفیف می‌خورد. قیمت نهایی به تومان چقدر است؟"
            ),
            answers=["۲۲۰۰۰۰", "220000", "۲۲۰ هزار", "220 هزار", "دویست و بیست هزار"],
            category="percentage",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-006",
            track="hard_math",
            split="hard",
            prompt=(
                "میانگین چهار عدد ۱۵ است. اگر عدد پنجمی به‌نام x به آنها اضافه شود تا میانگین "
                "پنج عدد ۱۸ شود، x چند است؟"
            ),
            answers=["۳۰", "30"],
            category="mean",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-007",
            track="hard_math",
            split="hard",
            prompt=(
                "سه نفر در ساختن یک دیوار همکاری می‌کنند. نفر اول به‌تنهایی این کار را در ۶ ساعت "
                "انجام می‌دهد، نفر دوم در ۸ ساعت و نفر سوم در ۱۲ ساعت. اگر هر سه با هم کار کنند، "
                "چند ساعت طول می‌کشد؟ پاسخ را به ساعت بنویس."
            ),
            answers=["۸/۳", "8/3", "۲ و ۲/۳", "2 و 2/3"],
            category="work_rate",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-008",
            track="hard_math",
            split="hard",
            prompt=(
                "یک قطار ۱۲۰ کیلومتر را با سرعت ۸۰ کیلومتر بر ساعت طی می‌کند و سپس ۸۰ کیلومتر را "
                "با سرعت ۴۰ کیلومتر بر ساعت. سرعت میانگین کل مسیر چند کیلومتر بر ساعت است؟"
            ),
            answers=["۵۷.۱۴", "۵۷.۱", "57.1", "57.14", "حدود ۵۷"],
            category="weighted_speed",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-009",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر سه ضلع یک مثلث ۳، ۴ و ۵ سانتی‌متر باشد، مساحت آن مثلث چند سانتی‌متر مربع است؟"
            ),
            answers=["۶", "6", "شش"],
            category="geometry",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-010",
            track="hard_math",
            split="hard",
            prompt=(
                "در یک کیسه ۴ مهره قرمز و ۶ مهره آبی است. اگر دو مهره بدون جایگذاری برداریم، احتمال "
                "اینکه هر دو قرمز باشند چقدر است؟ پاسخ را به‌صورت کسر ساده‌شده بنویس."
            ),
            answers=["۲/۱۵", "2/15"],
            category="probability",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-011",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر ۲ به توان x برابر ۳۲ باشد، x چند است؟"
            ),
            answers=["۵", "5", "پنج"],
            category="exponent",
            difficulty=2,
        ),
        exact(
            "peval-hard-math-012",
            track="hard_math",
            split="hard",
            prompt=(
                "محیط یک دایره ۱۰ سانتی‌متر است. اگر شعاع آن دو برابر شود، محیط چند سانتی‌متر می‌شود؟"
            ),
            answers=["۲۰", "20", "بیست"],
            category="geometry",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-013",
            track="hard_math",
            split="hard",
            prompt=(
                "علی ۵ ساله است و پدرش ۳۵ ساله. چند سال دیگر سن پدر دقیقا دو برابر سن علی می‌شود؟"
            ),
            answers=["۲۵", "25", "بیست و پنج"],
            category="age_problem",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-014",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر مجموع سه عدد متوالی ۴۸ باشد، عدد وسط چند است؟"
            ),
            answers=["۱۶", "16", "شانزده"],
            category="arithmetic_sequence",
            difficulty=2,
        ),
        exact(
            "peval-hard-math-015",
            track="hard_math",
            split="hard",
            prompt=(
                "یک کتاب در یک فروشگاه ۲۰ درصد تخفیف خورد و قیمت آن به ۸۰ هزار تومان رسید. قیمت "
                "اصلی کتاب چقدر بود (به تومان)؟"
            ),
            answers=["۱۰۰۰۰۰", "100000", "۱۰۰ هزار", "100 هزار", "صد هزار"],
            category="percentage",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-016",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر یک کالا را با ۲۵٪ سود بفروشیم و قیمت فروش ۱۲۵ هزار تومان شود، قیمت خرید آن "
                "چقدر بوده است (به تومان)؟"
            ),
            answers=["۱۰۰۰۰۰", "100000", "۱۰۰ هزار", "100 هزار", "صد هزار"],
            category="profit_loss",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-017",
            track="hard_math",
            split="hard",
            prompt=(
                "نسبت سن دو نفر ۲ به ۳ است. اگر مجموع سن آن‌ها ۵۰ باشد، سن نفر بزرگ‌تر چند است؟"
            ),
            answers=["۳۰", "30", "سی"],
            category="ratio",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-018",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر شعاع یک دایره ۷ سانتی‌متر باشد و عدد پی را ۲۲/۷ بگیریم، مساحت دایره چند "
                "سانتی‌متر مربع است؟"
            ),
            answers=["۱۵۴", "154", "صد و پنجاه و چهار"],
            category="geometry",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-019",
            track="hard_math",
            split="hard",
            prompt=(
                "احتمال اینکه با پرتاب یک تاس عددی بزرگ‌تر از ۴ بیاید چقدر است؟ پاسخ را به‌صورت "
                "کسر ساده‌شده بنویس."
            ),
            answers=["۱/۳", "1/3"],
            category="probability",
            difficulty=2,
        ),
        exact(
            "peval-hard-math-020",
            track="hard_math",
            split="hard",
            prompt=(
                "تعداد مقسوم‌علیه‌های مثبت عدد ۱۲ چند تا است؟"
            ),
            answers=["۶", "6", "شش"],
            category="number_theory",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-021",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر در یک خانواده ۳ فرزند باشد و هر فرزند به‌طور مستقل با احتمال یک‌دوم پسر یا دختر "
                "باشد، احتمال اینکه دقیقا دو پسر باشند چقدر است؟ پاسخ را به‌صورت کسر بنویس."
            ),
            answers=["۳/۸", "3/8"],
            category="probability",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-022",
            track="hard_math",
            split="hard",
            prompt=(
                "میانگین ۵ عدد ۲۰ است. اگر یکی از این اعداد، که برابر ۱۵ بود، حذف شود، میانگین "
                "چهار عدد باقی‌مانده چند است؟"
            ),
            answers=["۲۱.۲۵", "21.25", "بیست و یک و یک‌چهارم"],
            category="mean",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-023",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر x در معادله ۳x − ۷ = ۲x + ۵ صدق کند، مقدار x چند است؟"
            ),
            answers=["۱۲", "12", "دوازده"],
            category="algebra",
            difficulty=2,
        ),
        exact(
            "peval-hard-math-024",
            track="hard_math",
            split="hard",
            prompt=(
                "یک مخزن آب در ۶ ساعت با شیر اول پر می‌شود و در ۹ ساعت با شیر دوم. اگر هر دو شیر "
                "همزمان باز باشند، مخزن در چند ساعت پر می‌شود؟ پاسخ را به ساعت بنویس."
            ),
            answers=["۱۸/۵", "18/5", "۳ و ۳/۵", "3 و 3/5", "۳.۶", "3.6"],
            category="work_rate",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-025",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر طول یک مستطیل ۴ متر و عرض آن ۳ متر باشد، طول قطر آن چند متر است؟"
            ),
            answers=["۵", "5", "پنج"],
            category="geometry",
            difficulty=2,
        ),
        exact(
            "peval-hard-math-026",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر امروز دوشنبه باشد، ۲۰۰ روز دیگر چه روزی از هفته است؟"
            ),
            answers=["شنبه"],
            category="modular_arithmetic",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-027",
            track="hard_math",
            split="hard",
            prompt=(
                "از یک عدد دو رقمی، اگر رقم‌هایش را جابه‌جا کنیم، عدد جدید ۲۷ بیشتر از عدد اصلی "
                "می‌شود. اگر مجموع رقم‌های عدد ۹ باشد، عدد اصلی چیست؟"
            ),
            answers=["۳۶", "36", "سی و شش"],
            category="digit_problem",
            difficulty=4,
        ),
        exact(
            "peval-hard-math-028",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر یک کارگر در ۸ روز یک کار را انجام دهد و کارگر دیگر همان کار را در ۱۲ روز، "
                "اگر هر دو با هم کار کنند، چند روز طول می‌کشد؟ پاسخ را به روز بنویس."
            ),
            answers=["۲۴/۵", "24/5", "۴.۸", "4.8"],
            category="work_rate",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-029",
            track="hard_math",
            split="hard",
            prompt=(
                "اگر مجموع n عدد طبیعی اول برابر ۵۵ باشد، n چند است؟"
            ),
            answers=["۱۰", "10", "ده"],
            category="number_theory",
            difficulty=3,
        ),
        exact(
            "peval-hard-math-030",
            track="hard_math",
            split="hard",
            prompt=(
                "احتمال اینکه با پرتاب همزمان دو تاس، مجموع برابر ۷ شود چقدر است؟ پاسخ را به‌صورت "
                "کسر ساده‌شده بنویس."
            ),
            answers=["۱/۶", "1/6"],
            category="probability",
            difficulty=3,
        ),
    ]
    return items


def hard_reading() -> list[dict[str, Any]]:
    items = [
        f1(
            "peval-hard-reading-005",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: تیم محصول دو ایده برای صفحه ورود داشت: یکی صفحه‌ای "
                "بسیار ساده با یک دکمه و دیگری صفحه‌ای با چندین انتخاب. تست‌ها نشان داد کاربران "
                "با صفحه ساده، در مرحله بعد بیشتر گم می‌شوند و در صفحه پر، اول معطل می‌مانند ولی در "
                "نهایت کار را تمام می‌کنند. سوال: چرا صفحه ساده، با وجود سرعت اولیه بیشتر، "
                "نهایتا انتخاب نشد؟"
            ),
            answers=["گم شدن کاربر در مرحله بعد", "سردرگمی در گام بعد"],
            category="ux_reasoning",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-006",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پژوهش در میان دانش‌آموزان نشان داد کسانی که "
                "صبحانه می‌خورند نمره‌های بهتری دارند. اما بررسی دقیق‌تر نشان داد این دانش‌آموزان "
                "معمولا از خانواده‌هایی هستند که شب زود می‌خوابند و حمایت تحصیلی بیشتری دارند. "
                "سوال: عامل پنهانی که نتیجه ساده «صبحانه = نمره بهتر» را تردیدآمیز می‌کند چیست؟"
            ),
            answers=["حمایت خانوادگی و خواب کافی", "حمایت خانواده و خواب زود"],
            category="confounding",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-007",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک کارخانه دو خط تولید دارد. خط الف سرعت بیشتر اما "
                "نرخ خرابی هشت درصد دارد، خط ب سرعت کم‌تر و نرخ خرابی دو درصد. مدیریت تصمیم گرفت "
                "از خط ب استفاده کند چون هزینه‌های تعمیر و پشتیبانی نهایتا کل سود را می‌خورد. سوال: "
                "چرا با وجود سرعت کمتر، خط ب انتخاب شد؟"
            ),
            answers=["پایین بودن نرخ خرابی و هزینه تعمیر", "کمتر بودن هزینه پشتیبانی"],
            category="decision_reasoning",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-008",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر یک رستوران دو پیشخدمت داشت. پیشخدمت اول هر "
                "روز فرم رضایت مشتریان را خودش پر می‌کرد. پیشخدمت دوم فرم را به مشتری می‌داد. در "
                "گزارش پایان ماه، رضایت پیشخدمت اول کمی بالاتر بود. مدیر نتیجه گرفت پیشخدمت اول "
                "بهتر کار می‌کند. سوال: ضعف اصلی این نتیجه‌گیری چیست؟"
            ),
            answers=["تعارض منافع در پر کردن فرم", "سوگیری در جمع‌آوری داده توسط خود پیشخدمت"],
            category="bias",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-009",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر مدرسه گفت اگر سرویس مدرسه به‌موقع برسد، اردو "
                "ساعت ۸ برگزار می‌شود. صبح روز اردو بچه‌ها دیدند هرچند سرویس به‌موقع رسید، اردو "
                "ساعت ۹ آغاز شد چون قفل در ورودی پارک نیم‌ساعت دیر باز شد. سوال: علت اصلی تاخیر "
                "اردو چه بود؟"
            ),
            answers=["دیر باز شدن قفل در ورودی پارک", "تاخیر در باز شدن در پارک"],
            category="causal_reading",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-010",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک شهرداری برای کاهش تصادف، در سه چهارراه دوربین "
                "نصب کرد. یک سال بعد، تعداد تصادفات در آن سه چهارراه نصف شد. اما در گزارش سراسری "
                "شهر، عدد کل تصادف فقط ۵٪ کم شد. سوال: چه احتمالی توضیح می‌دهد که چرا کاهش "
                "محلی به کاهش متناسب در کل شهر منجر نشد؟"
            ),
            answers=[
                "جابه‌جایی تصادف به چهارراه‌های دیگر",
                "انتقال رفتار رانندگی به نقاط بدون دوربین",
            ],
            category="displacement_effect",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-011",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: کمیته بودجه پروژه‌ای را رد کرد چون تنها ۲۰٪ اعضا "
                "موافق بودند، در حالی‌که آیین‌نامه نیاز به ۵۰٪+ یک رای دارد. کاربر بعد از یک ماه "
                "مطلع شد که در همان جلسه فقط نیمی از اعضا حاضر بودند. سوال: نتیجه رد پروژه از نظر "
                "آیین‌نامه چه ایرادی دارد؟"
            ),
            answers=[
                "نبود نصاب برای تصمیم‌گیری",
                "حضور نیمی از اعضا و عدم حد نصاب",
            ],
            category="procedural_reasoning",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-012",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک تیم پزشکی دو روش درمان آزمایش کرد. روش الف در "
                "نمونه ۲۰۰ نفری ۸۰٪ بهبودی نشان داد، روش ب در نمونه ۲۰ نفری ۹۰٪. تیم نوشت روش ب "
                "بهتر است. سوال: چه ضعفی در این نتیجه‌گیری وجود دارد؟"
            ),
            answers=[
                "کوچک بودن نمونه روش ب",
                "حجم نمونه کوچک و عدم تعمیم",
            ],
            category="sample_size",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-013",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر یک سایت دید پس از تغییر رنگ دکمه خرید از آبی "
                "به نارنجی، فروش ۲٪ بالا رفت. اما همان روز یک کمپین تلویزیونی هم آغاز شده بود. "
                "سوال: چرا نمی‌توان مطمئن بود رشد فروش از تغییر رنگ دکمه است؟"
            ),
            answers=[
                "همزمانی با کمپین تلویزیونی",
                "اثر کمپین به‌عنوان متغیر مزاحم",
            ],
            category="confounding",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-014",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک شهر سه راه دارد: راه شمال، راه مرکز، راه جنوب. "
                "کارگزار شهر گفت اگر در راه شمال سد ساخته شود، آب در راه مرکز به‌حد کافی می‌رسد. "
                "ولی پس از ساخت سد، آب در راه مرکز کم شد چون تامین مرکز مستقل از شمال بود. "
                "سوال: ادعای کارگزار در پی کدام خطای نگرشی شکل گرفت؟"
            ),
            answers=[
                "فرض غلط رابطه علی بین شمال و مرکز",
                "نسبت دادن نادرست علت",
            ],
            category="false_causation",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-015",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: تیم نگه‌داری بنا گفت اگر گزارش تخلف امضا شود، آسانسور "
                "تعمیر می‌شود. ساکنان امضا کردند، ولی آسانسور تعمیر نشد چون قطعه یدکی در بازار "
                "موجود نبود. سوال: علت قطعی نقض وعده تیم چه بود؟"
            ),
            answers=[
                "نبود قطعه یدکی در بازار",
                "موجود نبودن قطعه",
            ],
            category="causal_reading",
            difficulty=3,
        ),
        f1(
            "peval-hard-reading-016",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پژوهش نشان داد در یک منطقه، شهرهایی که میزان "
                "بستنی‌فروشی بیشتری دارند، آمار غرق‌شدگی بالاتری هم دارند. پژوهشگر نتیجه گرفت "
                "بستنی باعث غرق‌شدن می‌شود. سوال: چه متغیر مزاحم احتمالی توضیح بهتری می‌دهد؟"
            ),
            answers=[
                "گرما و فصل تابستان",
                "هوای گرم و رفتن به آب",
            ],
            category="confounding",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-017",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر یک پروژه دید زمان جلسه‌های هفتگی هر هفته "
                "طولانی‌تر می‌شود. بررسی کرد و دید چون دستور جلسه نوشته نمی‌شود، بحث‌های فرعی زیاد "
                "می‌شوند. تصمیم گرفت دستور جلسه از قبل ارسال شود. سوال: ریشه ناکارآمدی جلسه‌ها چه بود؟"
            ),
            answers=[
                "نبود دستور جلسه از پیش",
                "نداشتن دستور جلسه",
            ],
            category="root_cause",
            difficulty=3,
        ),
        f1(
            "peval-hard-reading-018",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک مدیر بازاریابی داده‌ها را فقط از ۲۵٪ مشتریان "
                "وفادار جمع می‌کرد، چون پاسخ‌گوتر بودند. سپس بر اساس همین داده‌ها برای کل بازار "
                "تصمیم می‌گرفت. سوال: نام این خطا چیست؟"
            ),
            answers=[
                "سوگیری انتخاب نمونه",
                "سوگیری انتخاب",
            ],
            category="selection_bias",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-019",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: کمیته آموزش گفت اگر نرخ قبولی دانش‌آموزان از ۸۰٪ "
                "بالاتر برود، معلم برتر معرفی می‌شود. در سال آینده نرخ قبولی به ۸۵٪ رسید، ولی "
                "معلم برتر معرفی نشد چون ضوابط جدیدی برای ارزیابی اضافه شد. سوال: علت معرفی نشدن "
                "معلم برتر چه بود؟"
            ),
            answers=[
                "اضافه شدن ضوابط جدید ارزیابی",
                "تغییر ضوابط ارزیابی",
            ],
            category="changed_criteria",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-020",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک معلم دید نمره‌های امتحان نهایی در کلاس دخترانه "
                "بهتر از کلاس پسرانه است. در همان مدرسه، تعداد ساعت تدریس کلاس دخترانه دو برابر "
                "بوده. سوال: چرا نمی‌توان از این آمار نتیجه گرفت دختران در آن درس قوی‌ترند؟"
            ),
            answers=[
                "تفاوت در ساعت تدریس",
                "متغیر مزاحم ساعت تدریس",
            ],
            category="confounding",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-021",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پژوهشگر گفت سکه‌ای را ۱۰ بار پرت کرده و هر بار "
                "شیر آمده، پس بار یازدهم احتمالا خط می‌آید. سوال: نام این خطای استدلال چیست؟"
            ),
            answers=[
                "خطای قمارباز",
                "خطای قماربازی",
            ],
            category="gamblers_fallacy",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-022",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: تیم محصول گفت اگر دکمه ثبت‌نام بزرگ‌تر شود، تعداد "
                "کاربر دو برابر می‌شود. آن‌ها دکمه را بزرگ کردند و در عرض یک ماه تعداد کاربر دو برابر "
                "شد. اما همزمان قیمت محصول هم نصف شده بود. سوال: کدام عامل ممکن است نقش اصلی در "
                "افزایش کاربر داشته باشد؟"
            ),
            answers=[
                "نصف شدن قیمت محصول",
                "کاهش قیمت به نصف",
            ],
            category="confounding",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-023",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک مدیر گفت چون ده درصد کارمندان از کافه شکایت "
                "دارند، باید کافه را تعطیل کنیم. اعضای تیم گفتند بهتر است نظر ۹۰ درصد بقیه را هم "
                "پرسید. سوال: ضعف تصمیم اولیه مدیر چه بود؟"
            ),
            answers=[
                "بی‌توجهی به نظر اکثریت",
                "تصمیم بر مبنای اقلیت",
            ],
            category="base_rate",
            difficulty=3,
        ),
        f1(
            "peval-hard-reading-024",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: شهردار یک شهر گفت چون پارک سرسبزتر شد، تعداد "
                "شکایت‌های ساکنان نزدیک پارک کم شد، پس کیفیت زندگی بهتر شده. اما بررسی نشان داد "
                "خیلی از همان ساکنان قبلا اسباب‌کشی کرده‌اند. سوال: چرا نتیجه شهردار قابل اعتماد نیست؟"
            ),
            answers=[
                "جابه‌جایی ساکنان شاکی",
                "خروج معترضان از منطقه",
            ],
            category="survivor_bias",
            difficulty=5,
        ),
        f1(
            "peval-hard-reading-025",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک سایت خبری دید کاربران در صفحه‌هایی که عنوان "
                "آن‌ها سوالی است بیشتر می‌مانند. مدیر دستور داد همه عنوان‌ها سوالی شوند. بعد از یک ماه "
                "میانگین زمان ماندن کاربر در صفحه بدون تغییر بود. سوال: چه دلیلی توضیح می‌دهد چرا "
                "نتیجه پیش‌بینی‌شده محقق نشد؟"
            ),
            answers=[
                "از بین رفتن جذابیت ویژه عنوان سوالی",
                "اشباع شدن کاربر از عناوین سوالی",
            ],
            category="generalization_failure",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-026",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: کاربر گفت سایت خیلی کند است. تیم فنی متوجه شد فقط "
                "صفحه پروفایل کند است. تیم محصول می‌خواست همه صفحات را بازنویسی کند. سوال: کدام "
                "تصمیم اقتصادی‌تر است؟"
            ),
            answers=[
                "بازنویسی فقط صفحه پروفایل",
                "تمرکز بر صفحه پروفایل",
            ],
            category="scope_reasoning",
            difficulty=3,
        ),
        f1(
            "peval-hard-reading-027",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک پژوهش گفت در شهرهایی که قهوه بیشتری مصرف می‌شود، "
                "آمار سکته بالاتر است. بررسی نشان داد در همان شهرها میانگین سن جمعیت هم بیشتر است. "
                "سوال: متغیر مزاحم احتمالی چیست؟"
            ),
            answers=[
                "میانگین سن بالاتر",
                "بیشتر بودن سن جمعیت",
            ],
            category="confounding",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-028",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: کمیته انتخاب گفت اگر کسی هم آلمانی و هم سوئدی بداند، "
                "اولویت دارد. مهتاب فقط آلمانی می‌داند. کمیته او را پذیرفت. سوال: این تصمیم با ضابطه "
                "اعلام‌شده چه تناسبی دارد؟"
            ),
            answers=[
                "ناسازگار با ضابطه اعلام‌شده",
                "خلاف ضابطه اولویت",
            ],
            category="rule_violation",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-029",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: مدیر یک کارخانه گفت چون درآمد امسال نسبت به پارسال "
                "بیشتر شده، عملکرد ما خوب بوده. اما گزارش حسابدار نشان داد قیمت محصول دو برابر "
                "شده ولی تعداد فروش به نصف رسیده. سوال: چرا قضاوت اولیه مدیر کافی نیست؟"
            ),
            answers=[
                "افت تعداد فروش با وجود رشد درآمد",
                "کاهش حجم فروش پشت رشد درآمد",
            ],
            category="metric_reasoning",
            difficulty=4,
        ),
        f1(
            "peval-hard-reading-030",
            track="hard_reading",
            split="hard",
            prompt=(
                "متن را بخوان و پاسخ کوتاه بده: یک تیم بازی، در سه ماه گذشته همه بازی‌های خانگی را "
                "برده ولی همه بازی‌های خارج از خانه را باخته. مربی نتیجه گرفت زمین خانگی برای تیم "
                "حیاتی است. سوال: چه احتمال جایگزینی، توضیحی متفاوت برای این الگو می‌دهد؟"
            ),
            answers=[
                "تفاوت قدرت حریفان در دو دسته",
                "حریفان خارج از خانه قوی‌تر",
            ],
            category="alternative_explanation",
            difficulty=4,
        ),
    ]
    return items


def hard_instruction() -> list[dict[str, Any]]:
    items = [
        instr(
            "peval-hard-instruction-005",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی برای کاربری که از قطعی اینترنت شکایت دارد بنویس. باید با «درک می‌کنم» "
                "شروع شود، شامل کلمات «پیگیری» و «راهکار» باشد، علامت سوال نداشته باشد و بین ۱۲ تا "
                "۴۰ کلمه باشد."
            ),
            constraints={
                "required_prefix": "درک می‌کنم",
                "required_keywords": ["پیگیری", "راهکار"],
                "forbidden": ["؟", "?"],
                "min_words": 12,
                "max_words": 40,
            },
            category="support_response",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-006",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاراگراف فارسی درباره مزایای کار تیمی بنویس. پاسخ باید شامل «بازخورد» و «هدف "
                "مشترک» باشد، نباید کلمه «خیلی» را داشته باشد و دقیقا با کلمه «همکاری» شروع شود. "
                "طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_prefix": "همکاری",
                "required_keywords": ["بازخورد", "هدف مشترک"],
                "forbidden": ["خیلی"],
                "min_words": 15,
                "max_words": 45,
            },
            category="multi_constraint",
            difficulty=5,
        ),
        instr(
            "peval-hard-instruction-007",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی درباره اهمیت رمز عبور قوی بنویس. باید شامل «رمز عبور» و «احراز هویت» "
                "باشد، هیچ رقم انگلیسی یا فارسی نداشته باشد، با «از نظر امنیتی» شروع شود و بین "
                "۱۵ تا ۵۰ کلمه باشد."
            ),
            constraints={
                "required_prefix": "از نظر امنیتی",
                "required_keywords": ["رمز عبور", "احراز هویت"],
                "forbidden": [
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "۰",
                    "۱",
                    "۲",
                    "۳",
                    "۴",
                    "۵",
                    "۶",
                    "۷",
                    "۸",
                    "۹",
                ],
                "min_words": 15,
                "max_words": 50,
            },
            category="security_instruction",
            difficulty=5,
        ),
        instr(
            "peval-hard-instruction-008",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی درباره فایده مدیریت زمان برای دانشجوها بنویس که با «اگر» شروع شود، "
                "شامل «اولویت» و «تقویم» باشد، نباید نقطه بیاید و باید با «می‌شود» تمام شود. طول "
                "بین ۱۰ تا ۳۵ کلمه."
            ),
            constraints={
                "required_prefix": "اگر",
                "required_suffix": "می‌شود",
                "required_keywords": ["اولویت", "تقویم"],
                "forbidden": ["."],
                "min_words": 10,
                "max_words": 35,
            },
            category="suffix_control",
            difficulty=5,
        ),
        instr(
            "peval-hard-instruction-009",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک ایمیل کوتاه فارسی برای رد مودبانه یک پیشنهاد همکاری بنویس. باید با «با سلام» "
                "شروع شود، شامل «قدردانی» و «در حال حاضر» باشد، نباید کلمه «هرگز» داشته باشد، و "
                "طول بین ۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "با سلام",
                "required_keywords": ["قدردانی", "در حال حاضر"],
                "forbidden": ["هرگز"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-010",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پیام پشتیبانی برای کاربری که شکایت دارد سفارشش دیر رسیده بنویس. باید با «درست "
                "می‌فرمایید» شروع شود، شامل «جبران» باشد، علامت تعجب نداشته باشد، و طول بین ۱۰ تا "
                "۳۵ کلمه."
            ),
            constraints={
                "required_prefix": "درست می‌فرمایید",
                "required_keywords": ["جبران"],
                "forbidden": ["!"],
                "min_words": 10,
                "max_words": 35,
            },
            category="support_response",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-011",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن کوتاه برای دعوت به یک کارگاه آنلاین بنویس. باید شامل «ثبت‌نام» و یک «لینک» "
                "باشد، با «دعوت می‌کنیم» شروع شود، علامت سوال نداشته باشد و طول بین ۱۵ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "دعوت می‌کنیم",
                "required_keywords": ["ثبت‌نام", "لینک"],
                "forbidden": ["؟", "?"],
                "min_words": 15,
                "max_words": 40,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-012",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک خلاصه فارسی از مزایای ورزش روزانه بنویس. باید با «به‌طور کلی» شروع شود، شامل "
                "«قلب» و «خواب» باشد، نباید عدد داشته باشد و طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_prefix": "به‌طور کلی",
                "required_keywords": ["قلب", "خواب"],
                "forbidden": [
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "۰",
                    "۱",
                    "۲",
                    "۳",
                    "۴",
                    "۵",
                    "۶",
                    "۷",
                    "۸",
                    "۹",
                ],
                "min_words": 15,
                "max_words": 45,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-013",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی برای رد ادب‌مند درخواست تخفیف بنویس. باید با «از پیشنهاد» شروع شود، "
                "شامل «سیاست شرکت» باشد، نباید نقطه‌ویرگول داشته باشد و طول بین ۱۲ تا ۳۵ کلمه."
            ),
            constraints={
                "required_prefix": "از پیشنهاد",
                "required_keywords": ["سیاست شرکت"],
                "forbidden": ["؛"],
                "min_words": 12,
                "max_words": 35,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-014",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک خلاصه فارسی برای پروفایل لینکدین یک مهندس نرم‌افزار جوان بنویس. باید با «مهندس» "
                "شروع شود، شامل «بک‌اند» و «همکاری تیمی» باشد، علامت تعجب نداشته باشد و طول بین "
                "۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "مهندس",
                "required_keywords": ["بک‌اند", "همکاری تیمی"],
                "forbidden": ["!"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-015",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پیام تشکر رسمی فارسی به یک استاد بعد از پایان نیمسال بنویس. باید با «استاد گرامی» "
                "شروع شود، شامل «راهنمایی» و «این نیمسال» باشد، نباید کلمه «بد» داشته باشد و با "
                "«ارادتمند شما» تمام شود. طول بین ۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "استاد گرامی",
                "required_suffix": "ارادتمند شما",
                "required_keywords": ["راهنمایی", "این نیمسال"],
                "forbidden": ["بد"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=5,
        ),
        instr(
            "peval-hard-instruction-016",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک هشدار فارسی برای یک کاربر که از مرورگر قدیمی استفاده می‌کند بنویس. باید با "
                "«برای امنیت بیشتر» شروع شود، شامل «به‌روزرسانی» و «مرورگر» باشد، نباید کلمه "
                "«حتما» داشته باشد و طول بین ۱۰ تا ۳۵ کلمه."
            ),
            constraints={
                "required_prefix": "برای امنیت بیشتر",
                "required_keywords": ["به‌روزرسانی", "مرورگر"],
                "forbidden": ["حتما"],
                "min_words": 10,
                "max_words": 35,
            },
            category="security_instruction",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-017",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ به سوال یک کاربر درباره علت تاخیر در پاسخ‌گویی پشتیبانی بنویس. باید با "
                "«در حال حاضر» شروع شود، شامل «نوبت‌بندی» و «اولویت‌بندی» باشد، نباید کلمه «شاید» "
                "داشته باشد و طول بین ۱۲ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "در حال حاضر",
                "required_keywords": ["نوبت‌بندی", "اولویت‌بندی"],
                "forbidden": ["شاید"],
                "min_words": 12,
                "max_words": 40,
            },
            category="support_response",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-018",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن فارسی برای فراخوان یک مسابقه عکاسی بنویس. باید با «مسابقه عکاسی» شروع شود، "
                "شامل «داوری» و «جایزه» باشد، نباید نقطه‌ویرگول داشته باشد و طول بین ۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "مسابقه عکاسی",
                "required_keywords": ["داوری", "جایزه"],
                "forbidden": ["؛"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-019",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک یادداشت داخلی برای کارمندان درباره تغییر ساعت کاری بنویس. باید با «به اطلاع» "
                "شروع شود، شامل «ساعت کاری جدید» و «از هفته آینده» باشد، علامت سوال نداشته باشد و "
                "طول بین ۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "به اطلاع",
                "required_keywords": ["ساعت کاری جدید", "از هفته آینده"],
                "forbidden": ["؟", "?"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-020",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پیام برای مشتری وفادار بنویس که از او دعوت می‌کنی در نظرسنجی شرکت کند. باید "
                "با «مشتری گرامی» شروع شود، شامل «نظر شما» و «بهبود خدمات» باشد، نباید عدد "
                "داشته باشد و طول بین ۱۵ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "مشتری گرامی",
                "required_keywords": ["نظر شما", "بهبود خدمات"],
                "forbidden": [
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "۰",
                    "۱",
                    "۲",
                    "۳",
                    "۴",
                    "۵",
                    "۶",
                    "۷",
                    "۸",
                    "۹",
                ],
                "min_words": 15,
                "max_words": 40,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-021",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن فارسی درباره فایده پشتیبان‌گیری منظم از داده‌ها بنویس. باید با «پشتیبان‌گیری» "
                "شروع شود، شامل «از دست رفتن» و «بازیابی» باشد، نباید کلمه «همیشه» داشته باشد و "
                "طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_prefix": "پشتیبان‌گیری",
                "required_keywords": ["از دست رفتن", "بازیابی"],
                "forbidden": ["همیشه"],
                "min_words": 15,
                "max_words": 45,
            },
            category="security_instruction",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-022",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی به یک خبرنگار درباره علت رشد فروش شرکت بنویس. باید با «رشد فروش» "
                "شروع شود، شامل «بازار جدید» و «خدمات پس از فروش» باشد، نباید کلمه «صرفا» داشته "
                "باشد و طول بین ۱۸ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "رشد فروش",
                "required_keywords": ["بازار جدید", "خدمات پس از فروش"],
                "forbidden": ["صرفا"],
                "min_words": 18,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-023",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پیام کوتاه برای دعوت یک متخصص به یک گفت‌وگوی پادکست بنویس. باید با «جناب آقای» "
                "یا «سرکار خانم» شروع شود (یکی به انتخاب)، شامل «گفت‌وگو» و «پادکست» باشد، نباید "
                "علامت تعجب داشته باشد و طول بین ۱۸ تا ۴۵ کلمه."
            ),
            constraints={
                "required_keywords": ["گفت‌وگو", "پادکست"],
                "forbidden": ["!"],
                "min_words": 18,
                "max_words": 45,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-024",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی برای یک کاربر که شکایت دارد فاکتورش با مبلغ سفارش نمی‌خواند بنویس. "
                "باید با «از تماس شما» شروع شود، شامل «بررسی فاکتور» و «پیگیری» باشد، نباید کلمه "
                "«قطعا» داشته باشد و طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_prefix": "از تماس شما",
                "required_keywords": ["بررسی فاکتور", "پیگیری"],
                "forbidden": ["قطعا"],
                "min_words": 15,
                "max_words": 45,
            },
            category="support_response",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-025",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن فارسی برای راهنمای کاربری ساده برای جست‌وجو در یک وب‌سایت بنویس. باید با "
                "«برای جست‌وجو» شروع شود، شامل «کادر بالا» و «دکمه جست‌وجو» باشد، علامت سوال نداشته "
                "باشد و طول بین ۱۵ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "برای جست‌وجو",
                "required_keywords": ["کادر بالا", "دکمه جست‌وجو"],
                "forbidden": ["؟", "?"],
                "min_words": 15,
                "max_words": 40,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-026",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک هشدار فارسی برای کاربری که قصد ارسال اطلاعات حساس از طریق ایمیل دارد بنویس. "
                "باید با «هشدار» شروع شود، شامل «اطلاعات حساس» و «رمزنگاری» باشد، نباید کلمه «هرگز» "
                "داشته باشد و طول بین ۱۲ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "هشدار",
                "required_keywords": ["اطلاعات حساس", "رمزنگاری"],
                "forbidden": ["هرگز"],
                "min_words": 12,
                "max_words": 40,
            },
            category="security_instruction",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-027",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن کوتاه برای معرفی محصول یک استارتاپ نوپا بنویس. باید با «معرفی می‌کنیم» شروع "
                "شود، شامل «راه‌حل» و «کاربر» باشد، نباید کلمه «بهترین» داشته باشد و طول بین ۱۵ تا "
                "۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "معرفی می‌کنیم",
                "required_keywords": ["راه‌حل", "کاربر"],
                "forbidden": ["بهترین"],
                "min_words": 15,
                "max_words": 40,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-028",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ فارسی به یک ایمیل که خواستار اطلاعات بیشتر از یک گزارش است بنویس. باید با "
                "«پیرو ایمیل» شروع شود، شامل «جزئیات تکمیلی» و «پیوست» باشد، نباید علامت سوال "
                "داشته باشد و طول بین ۱۵ تا ۴۵ کلمه."
            ),
            constraints={
                "required_prefix": "پیرو ایمیل",
                "required_keywords": ["جزئیات تکمیلی", "پیوست"],
                "forbidden": ["؟", "?"],
                "min_words": 15,
                "max_words": 45,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-029",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک متن کوتاه برای دعوت همکاران به یک نشست هم‌فکری درباره فرهنگ سازمانی بنویس. "
                "باید با «همکاران گرامی» شروع شود، شامل «هم‌فکری» و «فرهنگ سازمانی» باشد، نباید کلمه "
                "«اجباری» داشته باشد و طول بین ۲۰ تا ۵۰ کلمه."
            ),
            constraints={
                "required_prefix": "همکاران گرامی",
                "required_keywords": ["هم‌فکری", "فرهنگ سازمانی"],
                "forbidden": ["اجباری"],
                "min_words": 20,
                "max_words": 50,
            },
            category="multi_constraint",
            difficulty=4,
        ),
        instr(
            "peval-hard-instruction-030",
            track="hard_instruction",
            split="hard",
            prompt=(
                "یک پاسخ کوتاه و دیپلماتیک به یک پیام انتقادی از یک مشتری بنویس. باید با «انتقاد شما» "
                "شروع شود، شامل «بازنگری» و «بهبود» باشد، نباید کلمه «اشتباه» داشته باشد و طول "
                "بین ۱۵ تا ۴۰ کلمه."
            ),
            constraints={
                "required_prefix": "انتقاد شما",
                "required_keywords": ["بازنگری", "بهبود"],
                "forbidden": ["اشتباه"],
                "min_words": 15,
                "max_words": 40,
            },
            category="support_response",
            difficulty=4,
        ),
    ]
    return items


def hard_culture() -> list[dict[str, Any]]:
    items = [
        mcq(
            "peval-hard-culture-005",
            track="hard_culture",
            split="hard",
            prompt=(
                "وقتی کسی در فارسی می‌گوید «دلش با ما نیست»، نزدیک‌ترین معنی محاوره‌ای کدام است؟"
            ),
            choices=[
                "از نظر فکری در جای دیگری است یا تمایلی ندارد",
                "خانه‌اش از ما دور است",
                "بیمار است",
                "دل‌درد دارد",
            ],
            answer_index=0,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-006",
            track="hard_culture",
            split="hard",
            prompt="عبارت «خاک تو سرم» در گفت‌وگوی روزمره فارسی معمولا چه حسی را منتقل می‌کند؟",
            choices=[
                "تشویق و تحسین",
                "افسوس یا سرزنش خود",
                "سلام و خوش‌آمد",
                "تشکر",
            ],
            answer_index=1,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-007",
            track="hard_culture",
            split="hard",
            prompt=(
                "وقتی میزبان ایرانی پس از غذا می‌گوید «نوش جان»، پاسخ ادب‌مند رایج چه می‌تواند باشد؟"
            ),
            choices=[
                "خواهش می‌کنم، شما هم نوش جان",
                "دست شما درد نکند",
                "خدا حافظ",
                "ممنون از وقت‌تان",
            ],
            answer_index=1,
            category="etiquette",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-008",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر در یک محیط رسمی، یک همکار به شما می‌گوید «قابل شما را ندارد»، مناسب‌ترین پاسخ "
                "ادب‌مند کدام است؟"
            ),
            choices=[
                "نه ممنون، نمی‌خواهم",
                "بسیار ممنون، اگر زحمتی نیست لطف کنید",
                "چقدر می‌شود؟",
                "هر طور خودتان مایل هستید",
            ],
            answer_index=1,
            category="taarof",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-009",
            track="hard_culture",
            split="hard",
            prompt=(
                "در زبان عامیانه فارسی، عبارت «سرت به کار خودت باشد» معمولا چه پیامی دارد؟"
            ),
            choices=[
                "تشویق به یادگیری",
                "خواست محترمانه برای دخالت نکردن",
                "احوال‌پرسی",
                "پیشنهاد همکاری",
            ],
            answer_index=1,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-010",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر در فارسی کسی به دیگری بگوید «روی حرفش نمی‌ایستد»، نزدیک‌ترین مفهوم چیست؟"
            ),
            choices=[
                "بسیار رسمی صحبت می‌کند",
                "به وعده و گفته خودش پایبند نیست",
                "پشت میز ایستاده صحبت می‌کند",
                "صدایش بالا نمی‌رود",
            ],
            answer_index=1,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-011",
            track="hard_culture",
            split="hard",
            prompt=(
                "در فرهنگ کاری ایران، اگر همکاری بگوید «در خدمتم»، چه برداشت محتمل‌تری دارد؟"
            ),
            choices=[
                "بیان آمادگی برای کمک یا گفت‌وگو",
                "خداحافظی نهایی از سازمان",
                "اعلام بازنشستگی",
                "اعلام انتقال به شعبه دیگر",
            ],
            answer_index=0,
            category="politeness",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-012",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر کسی بگوید «سرش را زیر آب کرد»، در زبان فارسی محاوره‌ای معمولا چه برداشت می‌شود؟"
            ),
            choices=[
                "خود را پنهان کرد یا غیب شد",
                "شنا یاد گرفت",
                "زیر باران ایستاد",
                "حمام کرد",
            ],
            answer_index=0,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-013",
            track="hard_culture",
            split="hard",
            prompt=(
                "وقتی در پیامی رسمی فارسی نوشته می‌شود «در صورت صلاحدید»، نزدیک‌ترین معنی آن چیست؟"
            ),
            choices=[
                "اگر مفید بدانید",
                "حتما این کار را بکنید",
                "ما نمی‌دانیم چه کار کنیم",
                "اگر بودجه کافی داشته باشید",
            ],
            answer_index=0,
            category="formal_register",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-014",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر در فارسی کسی به دیگری بگوید «از این ستون به آن ستون فرج است»، چه پیامی دارد؟"
            ),
            choices=[
                "هیچ راهی وجود ندارد",
                "گذر زمان ممکن است گشایش بیاورد",
                "باید جای ستون‌ها را عوض کرد",
                "ساختمان نیاز به تعمیر دارد",
            ],
            answer_index=1,
            category="proverb",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-015",
            track="hard_culture",
            split="hard",
            prompt=(
                "در رسم تعارف ایرانی، اگر مهمان به اصرار میزبان برای پذیرایی بیشتر بگوید «سیر سیرم، "
                "واقعا»، مفهوم رایج اجتماعی این پاسخ چیست؟"
            ),
            choices=[
                "میزبان باید حتما تعارف را تمام کند",
                "میزبان معمولا یک یا دو بار دیگر تعارف می‌کند",
                "مهمان عصبانی شده است",
                "مهمان درخواست غذا دارد",
            ],
            answer_index=1,
            category="taarof",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-016",
            track="hard_culture",
            split="hard",
            prompt=(
                "ضرب‌المثل «کوزه‌گر از کوزه شکسته آب می‌خورد» معمولا برای چه موقعیتی به کار می‌رود؟"
            ),
            choices=[
                "کسی که برای دیگران کاری می‌کند ولی خودش از آن بی‌بهره است",
                "کوزه‌ها همیشه می‌شکنند",
                "آب گرم بهتر از سرد است",
                "هنر کوزه‌گری در حال نابودی است",
            ],
            answer_index=0,
            category="proverb",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-017",
            track="hard_culture",
            split="hard",
            prompt=(
                "وقتی فردی در فارسی می‌گوید «گرد و خاک کردن»، در گفت‌وگوی روزمره معمولا چه برداشت می‌شود؟"
            ),
            choices=[
                "نظافت اتاق",
                "ایجاد سر و صدا یا غوغا",
                "گذاشتن گل و گلدان",
                "رفت و آمد دوستانه",
            ],
            answer_index=1,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-018",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر کسی در فارسی بگوید «کلاهش پس معرکه است»، نزدیک‌ترین معنی محاوره‌ای چیست؟"
            ),
            choices=[
                "کلاه او گم شده است",
                "موقعیتش ضعیف یا کار از دستش رفته است",
                "در میدان شلوغ است",
                "کلاهش جدید است",
            ],
            answer_index=1,
            category="idiom",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-019",
            track="hard_culture",
            split="hard",
            prompt=(
                "در یک ایمیل کاری رسمی فارسی، کدام بسته شدن مودب‌تر تلقی می‌شود؟"
            ),
            choices=[
                "خداحافظ",
                "با احترام",
                "بای",
                "تا بعد",
            ],
            answer_index=1,
            category="formal_register",
            difficulty=2,
        ),
        mcq(
            "peval-hard-culture-020",
            track="hard_culture",
            split="hard",
            prompt=(
                "در فارسی محاوره‌ای، عبارت «جا انداخته» برای یک کلاس درس معمولا چه معنی می‌دهد؟"
            ),
            choices=[
                "موضوع به‌خوبی توضیح داده شده و فهمیده شده",
                "صندلی‌های کلاس جابه‌جا شده‌اند",
                "غذا در کلاس پخش شده",
                "کلاس تاخیر داشته است",
            ],
            answer_index=0,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-021",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر یک سرپرست در محیط کار رسمی به کارمند بگوید «اگر زحمتی نیست، گزارش را تا فردا "
                "ببینم»، نزدیک‌ترین خوانش این جمله کدام است؟"
            ),
            choices=[
                "درخواست انجام تا فردا با لحن مودبانه",
                "اعلام تعطیلی فردا",
                "اعلام عدم نیاز به گزارش",
                "تشکر از گزارش قبلی",
            ],
            answer_index=0,
            category="politeness",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-022",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر مهمان ایرانی پس از پایان مهمانی بگوید «خانه‌تان آباد»، نزدیک‌ترین مفهوم چیست؟"
            ),
            choices=[
                "خداحافظ به سبک رسمی و دعای خیر برای میزبان",
                "اعلام علاقه به خرید خانه",
                "گله از کیفیت پذیرایی",
                "درخواست بازگشت به مهمانی",
            ],
            answer_index=0,
            category="taarof",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-023",
            track="hard_culture",
            split="hard",
            prompt=(
                "در فارسی محاوره‌ای، اگر کسی بگوید «دستش به دهنش می‌رسد»، نزدیک‌ترین معنی چیست؟"
            ),
            choices=[
                "از نظر مالی نسبتا تامین است",
                "بسیار گرسنه است",
                "نمی‌تواند غذا بخورد",
                "خیلی قد بلند است",
            ],
            answer_index=0,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-024",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر یک کارمند به مدیر بگوید «در خدمت شما هستم»، در یک گفت‌وگوی کاری معمول چه می‌رساند؟"
            ),
            choices=[
                "بیان احترام و آمادگی برای انجام کار",
                "اعلام تعلیق از کار",
                "اعلام مرخصی",
                "انکار مسئولیت",
            ],
            answer_index=0,
            category="politeness",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-025",
            track="hard_culture",
            split="hard",
            prompt=(
                "ضرب‌المثل «گر صبر کنی ز غوره حلوا سازی» چه پیامی دارد؟"
            ),
            choices=[
                "صبر و پشتکار به نتیجه شیرین می‌رسد",
                "غوره خوش‌مزه‌تر از حلوا است",
                "حلوا را باید فورا خورد",
                "آشپزی نیاز به صبر ندارد",
            ],
            answer_index=0,
            category="proverb",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-026",
            track="hard_culture",
            split="hard",
            prompt=(
                "در گفت‌وگوی روزمره ایرانی، عبارت «خسته نباشید» معمولا کجا گفته می‌شود؟"
            ),
            choices=[
                "هنگام دیدن کسی که در حال کار است",
                "هنگام تشویق در یک مسابقه",
                "هنگام شروع روز اداری",
                "هنگام آغاز سفر",
            ],
            answer_index=0,
            category="etiquette",
            difficulty=2,
        ),
        mcq(
            "peval-hard-culture-027",
            track="hard_culture",
            split="hard",
            prompt=(
                "وقتی کسی می‌گوید «این کار از من برمی‌آید»، نزدیک‌ترین معنی محاوره‌ای چیست؟"
            ),
            choices=[
                "این کار را می‌توانم انجام دهم",
                "این کار از من گرفته شد",
                "این کار را بلد نیستم",
                "این کار را امروز انجام می‌دهم",
            ],
            answer_index=0,
            category="idiom",
            difficulty=2,
        ),
        mcq(
            "peval-hard-culture-028",
            track="hard_culture",
            split="hard",
            prompt=(
                "در فارسی، عبارت «یخ کسی را شکستن» در مکالمه‌ای دوستانه معمولا چه معنی می‌دهد؟"
            ),
            choices=[
                "از حالت سکوت یا خجالت اولیه بیرون آوردن",
                "بستنی خوردن با یکدیگر",
                "یک نوشیدنی سرد سفارش دادن",
                "یخچال را تعمیر کردن",
            ],
            answer_index=0,
            category="idiom",
            difficulty=3,
        ),
        mcq(
            "peval-hard-culture-029",
            track="hard_culture",
            split="hard",
            prompt=(
                "اگر یک ایرانی در پاسخ به سوال «حال شما چطور است؟» بگوید «شکر، می‌گذرد»، نزدیک‌ترین "
                "برداشت ادب‌مند چیست؟"
            ),
            choices=[
                "بیان نسبتا مودبانه و خودداری از شکایت",
                "نشان دادن خشم پنهان",
                "اعلام استعفا",
                "درخواست کمک فوری",
            ],
            answer_index=0,
            category="politeness",
            difficulty=4,
        ),
        mcq(
            "peval-hard-culture-030",
            track="hard_culture",
            split="hard",
            prompt=(
                "در فرهنگ ایرانی، اگر مهمانی به میزبان بگوید «دست‌ شما درد نکند»، نزدیک‌ترین مفهوم "
                "اجتماعی این عبارت چیست؟"
            ),
            choices=[
                "تشکر بابت زحمت پذیرایی",
                "نگرانی از سلامت میزبان",
                "درخواست غذای بیشتر",
                "اعلام پایان مهمانی به‌صورت رسمی",
            ],
            answer_index=0,
            category="etiquette",
            difficulty=3,
        ),
    ]
    return items


SECTIONS: list[tuple[str, str, callable[..., list[dict[str, Any]]]]] = [
    ("data/persian_eval_v1.public_eval.jsonl", "knowledge", public_knowledge),
    ("data/persian_eval_v1.public_eval.jsonl", "short_qa", public_short_qa),
    ("data/persian_eval_v1.public_eval.jsonl", "reading", public_reading),
    ("data/persian_eval_v1.public_eval.jsonl", "instruction", public_instruction),
    ("data/persian_eval_v1.public_eval.jsonl", "culture", public_culture),
    ("data/persian_eval_v1.hard.jsonl", "hard_reasoning", hard_reasoning),
    ("data/persian_eval_v1.hard.jsonl", "hard_math", hard_math),
    ("data/persian_eval_v1.hard.jsonl", "hard_reading", hard_reading),
    ("data/persian_eval_v1.hard.jsonl", "hard_instruction", hard_instruction),
    ("data/persian_eval_v1.hard.jsonl", "hard_culture", hard_culture),
]


def _balance_answer_positions(items: list[dict[str, Any]]) -> None:
    """Spread MCQ answer positions uniformly within each track.

    The hand-written items in some tracks naturally cluster on position 0
    (correct option written first). We post-process them so the validator's
    skew check stays under 50% per track without forcing the author to
    bookkeep positions while drafting.
    """

    import re

    id_num_re = re.compile(r"-(\d+)$")
    by_track: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        if item["metadata"].get("scoring") != "mcq":
            continue
        by_track.setdefault(item["track"], []).append(item)

    for track_items in by_track.values():
        for item in track_items:
            choices = item.get("choices") or []
            if len(choices) != 4:
                continue
            match = id_num_re.search(item["id"])
            if not match:
                continue
            num = int(match.group(1))
            target = (num - 5) % 4
            current = item["metadata"].get("answer_index")
            if not isinstance(current, int) or current == target:
                continue
            choices = list(choices)
            choices[current], choices[target] = choices[target], choices[current]
            item["choices"] = choices
            item["metadata"]["answer_index"] = target
            item["answer"] = choices[target]


def main() -> int:
    files: dict[str, list[dict[str, Any]]] = {}
    for path, _, generator in SECTIONS:
        files.setdefault(path, []).extend(generator())

    for path, new_items in files.items():
        _balance_answer_positions(new_items)
        target = ROOT / path
        existing = target.read_text(encoding="utf-8")
        existing_ids = {
            json.loads(line)["id"] for line in existing.splitlines() if line.strip()
        }
        with target.open("a", encoding="utf-8") as handle:
            written = 0
            for item in new_items:
                if item["id"] in existing_ids:
                    continue
                handle.write(json.dumps(item, ensure_ascii=False))
                handle.write("\n")
                existing_ids.add(item["id"])
                written += 1
        print(f"appended {written} items to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
