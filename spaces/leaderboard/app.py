from __future__ import annotations

import json
import os
from pathlib import Path

import gradio as gr
import pandas as pd


def load_rows() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    path = Path(os.getenv("LEADERBOARD_PATH", "leaderboard.json"))
    if not path.exists():
        empty = pd.DataFrame(columns=["model_id", "overall_score"])
        return empty, empty, "No leaderboard artifact found."
    data = json.loads(path.read_text(encoding="utf-8"))
    main = pd.DataFrame(data.get("main", []))
    reference = pd.DataFrame(data.get("reference", []))
    return main, reference, f"Generated at: {data.get('generated_at', 'unknown')}"


with gr.Blocks(title="Persian LLM Eval") as demo:
    gr.Markdown("# Persian LLM Eval")
    status = gr.Markdown()
    main_table = gr.Dataframe(label="Open-weight leaderboard", interactive=False)
    reference_table = gr.Dataframe(label="API reference baselines", interactive=False)

    def refresh():
        main, reference, message = load_rows()
        return message, main, reference

    demo.load(refresh, outputs=[status, main_table, reference_table])


if __name__ == "__main__":
    demo.launch()
