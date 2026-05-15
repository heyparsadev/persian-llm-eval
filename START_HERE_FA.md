# از اینجا شروع کن

این پروژه یک بنچمارک فارسی ایرانی برای مدل‌های زبانی است: ۳۰۰ سوال، ۱۰ تِرَک
موضوعی (دانش عمومی، فرهنگ، خوانش متن، پیروی از دستور، استدلال، ریاضی،
تعارف، اصطلاحات و …)، اسکورینگ خودکار و یک leaderboard فعال با نتایج
مدل‌های فرانتیر مثل Claude 4.x و GPT-5/5.5.

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

## مدل واقعی روی این بنچمارک اجرا کن

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
