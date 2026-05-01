# وضعیت پروژه

پروژه‌ی Persian LLM Eval v1 آماده‌ی اجرای محلی است.

## انجام شده

- CLI ساخته شد.
- dataset نمونه فارسی ساخته شد.
- scoring خودکار برای MCQ، QA کوتاه، reading، instruction و culture ساخته شد.
- خروجی JSON استاندارد ساخته شد.
- leaderboard builder ساخته شد.
- Hugging Face Space ساده ساخته شد.
- خروجی HTML محلی برای دیدن leaderboard ساخته شد.
- CI برای GitHub ساخته شد.
- راهنمای submission و deployment اضافه شد.
- فایل `RUN_ME.command` برای اجرای ساده اضافه شد.

## هنوز برای نسخه عمومی واقعی لازم است

- اجرای مدل‌های واقعی و پر کردن leaderboard.
- تصمیم درباره نام رسمی پروژه و repo.
- ساخت GitHub repo عمومی.
- ساخت Hugging Face Dataset و Space.
- اگر leaderboard رسمی می‌خواهیم، ساخت hidden split بزرگ‌تر و نگهداری امن آن.

## محدودیت فعلی

روی این سیستم فعلاً GitHub CLI و Hugging Face CLI در دسترس نیستند، بنابراین publish واقعی از همین‌جا انجام نشد. پروژه برای publish آماده است.
