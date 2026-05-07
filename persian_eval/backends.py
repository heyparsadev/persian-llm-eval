"""Generation backends for the Persian Eval runner."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any

from .dataset import DatasetRecord

SYSTEM_PROMPT = "شما یک دستیار دقیق فارسی هستید. پاسخ را کوتاه، مستقیم و به زبان فارسی بدهید."


def format_prompt(record: DatasetRecord) -> str:
    scoring = record.metadata.get("scoring")
    if scoring == "mcq" and record.choices:
        labels = (
            record.metadata.get("choice_labels")
            or ["الف", "ب", "پ", "ت", "ث", "ج", "چ", "ح"][: len(record.choices)]
        )
        rendered_choices = "\n".join(
            f"{label}) {choice}" for label, choice in zip(labels, record.choices)
        )
        return f"{record.prompt}\n\nگزینه ها:\n{rendered_choices}\n\nفقط برچسب گزینه درست را بنویس."
    if scoring in {"exact", "f1"}:
        return f"{record.prompt}\n\nپاسخ کوتاه:"
    return record.prompt


@dataclass
class GenerationConfig:
    max_new_tokens: int = 96
    temperature: float = 0.0
    base_url: str | None = None
    dtype: str = "bfloat16"
    quantization: str | None = None


class BaseBackend:
    name = "base"

    def generate(self, record: DatasetRecord) -> str:
        raise NotImplementedError


class MockBackend(BaseBackend):
    """A deterministic backend for smoke tests. It does not inspect answer keys."""

    name = "mock"

    def generate(self, record: DatasetRecord) -> str:
        if record.metadata.get("scoring") == "mcq":
            return "الف"
        if record.metadata.get("scoring") == "instruction":
            return "این یک پاسخ کوتاه آزمایشی برای سنجش مسیر اجرا است."
        return "پاسخ آزمایشی"


class HFBackend(BaseBackend):
    name = "hf"

    def __init__(self, model_id: str, *, revision: str | None, config: GenerationConfig):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        except ImportError as exc:
            raise RuntimeError(
                "Install the Hugging Face backend with: pip install -e '.[hf]'"
            ) from exc

        self.torch = torch
        self.model_id = model_id
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, revision=revision, trust_remote_code=True
        )
        load_kwargs: dict[str, Any] = {
            "revision": revision,
            "device_map": "auto",
            "trust_remote_code": True,
        }
        dtype = self._resolve_dtype(config.dtype)
        if dtype is not None:
            load_kwargs["torch_dtype"] = dtype
        if config.quantization == "4bit":
            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=dtype or torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif config.quantization == "8bit":
            load_kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **load_kwargs)

    def _resolve_dtype(self, dtype_name: str) -> Any:
        if dtype_name == "auto":
            return None
        if dtype_name == "float16":
            return self.torch.float16
        if dtype_name == "bfloat16":
            return self.torch.bfloat16
        if dtype_name == "float32":
            return self.torch.float32
        raise ValueError(f"Unsupported dtype: {dtype_name}")

    def generate(self, record: DatasetRecord) -> str:
        prompt = format_prompt(record)
        if getattr(self.tokenizer, "chat_template", None):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
            template_kwargs = {
                "add_generation_prompt": True,
                "return_tensors": "pt",
                "return_dict": True,
            }
            if "qwen3" in self.model_id.lower():
                template_kwargs["enable_thinking"] = False
            try:
                encoded = self.tokenizer.apply_chat_template(messages, **template_kwargs)
            except TypeError:
                template_kwargs.pop("enable_thinking", None)
                encoded = self.tokenizer.apply_chat_template(messages, **template_kwargs)
        else:
            encoded = self.tokenizer(f"{SYSTEM_PROMPT}\n\n{prompt}", return_tensors="pt")

        encoded = encoded.to(self.model.device)
        input_ids = encoded["input_ids"]

        do_sample = self.config.temperature > 0
        generate_kwargs = {
            "max_new_tokens": self.config.max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.eos_token_id,
            "attention_mask": encoded.get("attention_mask"),
        }
        generate_kwargs = {
            key: value for key, value in generate_kwargs.items() if value is not None
        }
        if do_sample:
            generate_kwargs["temperature"] = self.config.temperature
        with self.torch.no_grad():
            output_ids = self.model.generate(input_ids, **generate_kwargs)
        generated = output_ids[0][input_ids.shape[-1] :]
        return self.tokenizer.decode(generated, skip_special_tokens=True).strip()


class OpenAICompatibleBackend(BaseBackend):
    name = "openai-compatible"

    def __init__(self, model_id: str, *, config: GenerationConfig):
        self.model_id = model_id
        self.config = config
        self.base_url = (
            config.base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the openai-compatible backend")

    def generate(self, record: DatasetRecord) -> str:
        payload: dict[str, Any] = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": format_prompt(record)},
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_new_tokens,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()


def create_backend(
    backend_name: str,
    model_id: str,
    *,
    revision: str | None,
    config: GenerationConfig,
) -> BaseBackend:
    if backend_name == "mock":
        return MockBackend()
    if backend_name == "hf":
        return HFBackend(model_id, revision=revision, config=config)
    if backend_name == "openai-compatible":
        return OpenAICompatibleBackend(model_id, config=config)
    raise ValueError(f"Unsupported backend: {backend_name}")
