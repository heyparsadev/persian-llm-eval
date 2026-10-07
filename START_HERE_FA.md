# از اینجا شروع کن

این پروژه یک بنچمارک فارسی ایرانی برای مدل‌های زبانی است: ۵۴۴ سوال در
۲۱ تِرَک (دانش عمومی، فرهنگ، خوانش متن، پیروی از دستور، استدلال، ریاضی،
تعارف، اصطلاحات، و حالا کارهای روزمره، خلاقانه و چالشی)، اسکورینگ خودکار و
یک leaderboard فعال با نتایج مدل‌های فرانتیر مثل Claude 4.x و GPT-5/5.5.

## ساده‌ترین راه اجرا

روی macOS کافیست روی این فایل دابل‌کلیک کنی:

```text
RUN_ME.command
```

این کار خودش تست‌ها را اجرا می‌کند، دیتاست را اعتبارسنجی می‌کند، یک
اجرای آزمایشی با backend ساختگی (`mock`) می‌سازد، و یک leaderboard
نمونه تولید می‌کند. اگر همه چیز درست باشد، در ترمینال پیام موفقیت
می‌بینی.

## نتایج فعلی

نسخه‌ی فعلی دیتاست **v1.1** است (۱۵۰ سوال در split عمومی + ۱۵۰ سوال در
split سخت). تا الان ۲۳ ران از مدل‌های فرانتیر منتشر شده‌اند. خلاصه و
جدول کامل اینجا:

- [`docs/BENCHMARK_REPORT.md`](docs/BENCHMARK_REPORT.md) — گزارش کامل
  با per-track و bootstrap CI.
- [`leaderboard/leaderboard.csv`](leaderboard/leaderboard.csv) — جدول
  قابل باز کردن در اکسل.

## split جدید: «کاربردی» (practical)

۱۵۰ سوال تازه در ۶ ترک که به کارهای واقعی کاربر ایرانی نزدیک‌ترند:
نامه و پیامک و تغییر لحن رسمی/محاوره، متن تایپ‌شده با کیبورد اشتباه،
فینگلیش، غلط املایی و نیم‌فاصله، تاریخ شمسی و میلادی، مبلغ چک به حروف،
تومان و ریال، استخراج اطلاعات از آگهی دیوار و پیامک بانک به JSON، تعارف
و جمله‌های اجتماعی، ترجمه‌ی طبیعی اصطلاح‌ها، و بازی‌های زبانی مثل توشیح،
حذف یک حرف، قافیه، جابه‌جایی حروف، چیستان و حساب ابجد.

## split جدید: «چالشی» (challenge)

۱۰۰ سوال در ۵ ترک که برای مدل‌های نسل جدید هم سخت بمانند و آگاهی را
بسنجند، نه فقط حافظه را:

- پرسش با پیش‌فرض غلط: «چرا فردوسی گلستان را نوشت؟»
- پرسشی که جوابش در متن نیست
- همه‌ی معناهای «شیر» و «مهر» بدون اِعراب، و تشخیص طعنه
- دانش زنجیروار درباره‌ی ادبیات و تاریخ و جغرافیای ایران، و نسبت‌هایی مثل
  جاری و باجناق
- بازی‌های سخت با کلمه: جمله‌ای که از آخر به اول همان باشد، توشیح همراه با
  قافیه، و شمردن نقطه‌ها

سوال‌های هر دو split فعلاً در وضعیت `pending_review` هستند و باید یک
فارسی‌زبان آن‌ها را بازبینی کند. جزئیات، تخمین هزینه و برنامه‌ی بعدی در
[`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md).

## اجرای مدل‌ها با OpenRouter (پیشنهادی)

با یک کلید OpenRouter به همه‌ی مدل‌ها دسترسی داری (Claude Fable 5.1 و
Opus 5.5، GPT-6 Astra و Sol و Luna، Gemini، Grok، DeepSeek و …):

```bash
pip install -e .
export OPENROUTER_API_KEY=sk-or-...

# یک مدل روی split کاربردی
persian-eval run --model anthropic/claude-opus-5.5 --backend openrouter \
  --data data/persian_eval_v1.practical.jsonl --max-new-tokens 4096 \
  --concurrency 6 --output results/claude-opus-5.5.practical.json

# کل ماتریس مدل‌ها (configs/openrouter_models.json)
python scripts/run_matrix.py --estimate  # تخمین هزینه، بدون کلید
python scripts/run_matrix.py --dry-run   # برنامه و قیمت‌های زنده
python scripts/run_matrix.py
```

اگر اجرا وسط کار قطع شد، همان دستور را دوباره بزن؛ سوال‌هایی که جواب
گرفته‌اند دوباره پرسیده نمی‌شوند. هزینه‌ی واقعی هر اجرا (به دلار) در
فایل نتیجه ثبت می‌شود.

## فقط Claude، مستقیم با API انتروپیک (Batch، نصف قیمت)

ماتریس [`configs/anthropic_models.json`](configs/anthropic_models.json)
مدل Opus 5.5 را در سطح‌های فکر low، medium، high و max و Sonnet 5.5 را بدون
فکر و در همین چهار سطح اجرا می‌کند. هر اجرا یک Message Batch است که نصف قیمت حساب
می‌شود:

```bash
export ANTHROPIC_API_KEY=...
python scripts/run_matrix.py --config configs/anthropic_models.json --estimate
# اول یک اجرای آزمایشی ارزان (۲۰ سوال چالشی برای هر ردیف، حدود ۷ دلار)
python scripts/run_matrix.py --config configs/anthropic_models.json \
  --splits challenge --max-items 20 --results-dir results/pilot
python scripts/run_matrix.py --config configs/anthropic_models.json
```

تخمین هزینه و جزئیات در بخش ۴ [`docs/ROADMAP_FA.md`](docs/ROADMAP_FA.md).

## اجرای مستقیم با API یا GPU خودت

با کلید Anthropic یا OpenAI:

```bash
export ANTHROPIC_API_KEY=...
persian-eval run --model claude-sonnet-4-6 --backend anthropic \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/claude-sonnet-4-6.public_eval.json
```

با مدل open-weight روی GPU خودت (نیاز به `pip install -e ".[hf]"`):

```bash
persian-eval run --model PartAI/Dorna2-Llama3.1-8B-Instruct --backend hf \
  --data data/persian_eval_v1.public_eval.jsonl \
  --output results/dorna2.json
```

## مشارکت

- اضافه‌کردن سوال جدید یا اصلاح موجود:
  [`CONTRIBUTING_DATASET.md`](CONTRIBUTING_DATASET.md)
- اضافه‌کردن کد یا backend جدید:
  [`CONTRIBUTING.md`](CONTRIBUTING.md)
- ارسال نتیجه‌ی مدل خودت برای leaderboard:
  [`SUBMISSION.md`](SUBMISSION.md)
