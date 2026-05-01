# انتشار پروژه

این فایل برای وقتی است که بخواهیم پروژه را عمومی کنیم.

## GitHub

اگر GitHub CLI نصب و login شده باشد:

```bash
scripts/publish_github.sh persian-llm-eval
```

اگر نصب نیست، کافی است کل این پوشه را در یک repo جدید GitHub upload کنیم.

## Hugging Face Dataset

اول فایل‌های dataset را آماده کن:

```bash
scripts/prepare_hf_dataset.sh
```

بعد پوشه `hf/dataset` را در یک Hugging Face Dataset repo آپلود کن.

## Hugging Face Space

اول leaderboard Space را آماده کن:

```bash
scripts/prepare_hf_space.sh
```

بعد پوشه `hf/space` را به عنوان یک Hugging Face Space از نوع Gradio آپلود کن.

## اجرای مدل واقعی

برای مدل‌های Hugging Face:

```bash
pip install -e ".[hf]"
persian-eval run --model MODEL_ID --backend hf --model-type open-weight --data data/persian_eval_v1.public_eval.jsonl --output results/model.json
```

برای API:

```bash
export OPENAI_API_KEY=...
scripts/run_openai_reference.sh gpt-4.1-mini
```
