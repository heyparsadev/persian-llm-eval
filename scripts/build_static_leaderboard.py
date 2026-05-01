#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "leaderboard" / "leaderboard.json"
OUTPUT = ROOT / "leaderboard" / "index.html"


def fmt_score(value: object) -> str:
    try:
        return f"{float(value) * 100:.1f}"
    except (TypeError, ValueError):
        return ""


def render_table(rows: list[dict[str, object]]) -> str:
    if not rows:
        return "<p class=\"empty\">هنوز نتیجه‌ای ثبت نشده است.</p>"

    track_keys = sorted({
        key for row in rows for key in row if key.endswith("_score") and key != "overall_score"
    })
    headers = ["Model", "Type", "Overall"] + [key.replace("_score", "") for key in track_keys]
    body = []
    for row in rows:
        cells = [
            html.escape(str(row.get("model_id", ""))),
            html.escape(str(row.get("model_type", ""))),
            fmt_score(row.get("overall_score")),
        ]
        cells.extend(fmt_score(row.get(key)) for key in track_keys)
        body.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>")

    header_html = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def main() -> int:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    main_rows = data.get("main", [])
    reference_rows = data.get("reference", [])
    generated_at = html.escape(str(data.get("generated_at", "unknown")))
    document = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Persian LLM Eval Leaderboard</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f7f7f4;
      color: #1d1d1b;
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      letter-spacing: 0;
    }}
    h2 {{
      margin-top: 32px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    p {{
      line-height: 1.8;
    }}
    .meta {{
      color: #60635f;
      direction: ltr;
      text-align: left;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid #deded8;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #ededeb;
      text-align: left;
      direction: ltr;
      white-space: nowrap;
    }}
    th {{
      background: #ecece6;
      font-weight: 700;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .empty {{
      color: #60635f;
      background: white;
      border: 1px solid #deded8;
      padding: 14px;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Persian LLM Eval</h1>
    <p>Leaderboard محلی برای دمو و بررسی سریع. امتیازها به درصد نمایش داده شده‌اند.</p>
    <p class="meta">Generated at: {generated_at}</p>
    <h2>مدل‌های open-weight</h2>
    {render_table(main_rows)}
    <h2>API reference baselines</h2>
    {render_table(reference_rows)}
  </main>
</body>
</html>
"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
