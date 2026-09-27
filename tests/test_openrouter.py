import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from unittest import mock

from persian_eval.backends import (
    GenerationConfig,
    OpenRouterBackend,
    OpenRouterUpstreamError,
    create_backend,
    extract_openrouter_text,
    openrouter_call_meta,
)
from persian_eval.cli import main as cli_main
from persian_eval.dataset import DatasetRecord
from persian_eval.results import load_result

ROOT = Path(__file__).resolve().parents[1]

RECORD = DatasetRecord.from_dict(
    {
        "id": "q",
        "track": "short_qa",
        "prompt": "پایتخت ایران کجاست؟",
        "choices": None,
        "answer": ["تهران"],
        "metadata": {"scoring": "exact"},
        "source": "test",
        "split": "dev",
    }
)

RESPONSE = {
    "id": "gen-1",
    "model": "anthropic/claude-opus-5.5",
    "provider": "Anthropic",
    "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": " تهران "}}],
    "usage": {
        "prompt_tokens": 120,
        "completion_tokens": 8,
        "completion_tokens_details": {"reasoning_tokens": 0},
        "cost": 0.00064,
    },
}


def _backend(**overrides):
    with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        return OpenRouterBackend(
            "anthropic/claude-opus-5.5", config=GenerationConfig(max_new_tokens=512, **overrides)
        )


class OpenRouterPayloadTests(unittest.TestCase):
    def test_requires_api_key(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(RuntimeError):
            OpenRouterBackend("openai/gpt-6-sol", config=GenerationConfig())

    def test_create_backend_knows_openrouter(self):
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "k"}):
            backend = create_backend(
                "openrouter", "openai/gpt-6-sol", revision=None, config=GenerationConfig()
            )
        self.assertEqual(backend.name, "openrouter")

    def test_default_payload_sends_temperature_and_no_reasoning(self):
        payload = _backend().build_payload(RECORD)
        self.assertEqual(payload["model"], "anthropic/claude-opus-5.5")
        self.assertEqual(payload["max_tokens"], 512)
        self.assertEqual(payload["temperature"], 0.0)
        self.assertNotIn("reasoning", payload)
        self.assertNotIn("provider", payload)
        self.assertIn("فقط پاسخ نهایی", payload["messages"][1]["content"])

    def test_reasoning_effort_adds_headroom_and_drops_temperature(self):
        payload = _backend(reasoning_effort="low").build_payload(RECORD)
        self.assertEqual(payload["reasoning"], {"effort": "low", "exclude": True})
        self.assertEqual(payload["max_tokens"], 512 + 4096)
        self.assertNotIn("temperature", payload)

    def test_reasoning_none_disables_thinking(self):
        payload = _backend(reasoning_effort="none").build_payload(RECORD)
        self.assertEqual(payload["reasoning"], {"effort": "none"})
        self.assertEqual(payload["max_tokens"], 512)
        self.assertIn("temperature", payload)

    def test_thinking_budget_maps_to_reasoning_max_tokens(self):
        payload = _backend(thinking_budget_tokens=2000).build_payload(RECORD)
        self.assertEqual(payload["reasoning"], {"max_tokens": 2000, "exclude": True})
        self.assertEqual(payload["max_tokens"], 2512)

    def test_provider_preferences(self):
        payload = _backend(
            provider_order=["anthropic", "google-vertex"],
            allow_fallbacks=False,
            data_collection="deny",
        ).build_payload(RECORD)
        self.assertEqual(
            payload["provider"],
            {
                "order": ["anthropic", "google-vertex"],
                "allow_fallbacks": False,
                "data_collection": "deny",
            },
        )


class OpenRouterResponseTests(unittest.TestCase):
    def test_extract_text_and_meta(self):
        self.assertEqual(extract_openrouter_text(RESPONSE), "تهران")
        meta = openrouter_call_meta(RESPONSE)
        self.assertEqual(meta["provider"], "Anthropic")
        self.assertEqual(meta["served_model"], "anthropic/claude-opus-5.5")
        self.assertEqual(meta["prompt_tokens"], 120)
        self.assertEqual(meta["reasoning_tokens"], 0)
        self.assertAlmostEqual(meta["cost_usd"], 0.00064)
        self.assertEqual(meta["finish_reason"], "stop")

    def test_content_parts_are_joined(self):
        data = {"choices": [{"message": {"content": [{"type": "text", "text": "الف"}]}}]}
        self.assertEqual(extract_openrouter_text(data), "الف")

    def test_null_content_scores_as_empty(self):
        data = {"choices": [{"finish_reason": "length", "message": {"content": None}}]}
        self.assertEqual(extract_openrouter_text(data), "")

    def test_missing_choices_is_an_upstream_error(self):
        with self.assertRaises(OpenRouterUpstreamError):
            extract_openrouter_text({"error": {"code": 502, "message": "provider down"}})

    def test_generate_retries_upstream_errors(self):
        backend = _backend()
        responses = [{"error": {"code": 502, "message": "down"}}, RESPONSE]
        with (
            mock.patch("persian_eval.backends.post_json", side_effect=responses) as post,
            mock.patch("persian_eval.backends.time.sleep"),
        ):
            text, meta = backend.generate_with_meta(RECORD)
        self.assertEqual(text, "تهران")
        self.assertEqual(post.call_count, 2)
        request = post.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/chat/completions"))
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(json.loads(request.data)["model"], "anthropic/claude-opus-5.5")
        self.assertIn("latency_s", meta)


class FakeOpenRouter(BaseHTTPRequestHandler):
    """Minimal stand-in for openrouter.ai: /models and /chat/completions."""

    requests: ClassVar[list] = []
    fail_first_with_429 = False

    def do_GET(self):
        catalogue = {
            "data": [
                {
                    "id": "anthropic/claude-opus-5.5",
                    "pricing": {"prompt": "0.000004", "completion": "0.00002"},
                }
            ]
        }
        self._reply(200, catalogue)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeOpenRouter.requests.append((self.headers.get("Authorization"), body))
        if FakeOpenRouter.fail_first_with_429:
            FakeOpenRouter.fail_first_with_429 = False
            self._reply(429, {"error": {"code": 429, "message": "slow down"}}, retry_after="0")
            return
        self._reply(
            200,
            {
                "model": body["model"],
                "provider": "FakeProvider",
                "choices": [{"finish_reason": "stop", "message": {"content": "الف"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 5, "cost": 0.001},
            },
        )

    def _reply(self, status, payload, retry_after=None):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        if retry_after is not None:
            self.send_header("Retry-After", retry_after)
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class OpenRouterEndToEndTests(unittest.TestCase):
    def setUp(self):
        FakeOpenRouter.requests = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenRouter)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        base_url = f"http://127.0.0.1:{self.server.server_port}/api/v1"
        self.env = mock.patch.dict(
            os.environ,
            {
                "OPENROUTER_API_KEY": "test-key",
                "OPENROUTER_BASE_URL": base_url,
                "no_proxy": "127.0.0.1,localhost",
                "NO_PROXY": "127.0.0.1,localhost",
            },
        )
        self.env.start()
        self.sleep = mock.patch("persian_eval.backends.time.sleep")
        self.sleep.start()

    def tearDown(self):
        self.sleep.stop()
        self.env.stop()
        self.server.shutdown()
        self.server.server_close()

    def test_cli_run_through_openrouter(self):
        FakeOpenRouter.fail_first_with_429 = True
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "opus.json"
            code = cli_main(
                [
                    "run",
                    "--model",
                    "anthropic/claude-opus-5.5",
                    "--backend",
                    "openrouter",
                    "--data",
                    str(ROOT / "data" / "persian_eval_v1.dev.jsonl"),
                    "--output",
                    str(output),
                    "--reasoning-effort",
                    "low",
                    "--data-collection",
                    "deny",
                    "--concurrency",
                    "3",
                ]
            )
            self.assertEqual(code, 0)
            result = load_result(output)
        # 10 items plus one retried 429.
        self.assertEqual(len(FakeOpenRouter.requests), 11)
        auth, body = FakeOpenRouter.requests[-1]
        self.assertEqual(auth, "Bearer test-key")
        self.assertEqual(body["reasoning"], {"effort": "low", "exclude": True})
        self.assertEqual(body["provider"], {"data_collection": "deny"})
        self.assertEqual(result["backend"], "openrouter")
        self.assertEqual(result["model_type"], "api")
        self.assertEqual(result["run_config"]["data_collection"], "deny")
        self.assertEqual(result["usage"]["calls"], 10)
        self.assertAlmostEqual(result["usage"]["cost_usd"], 0.01)
        self.assertEqual(result["usage"]["providers"], {"FakeProvider": 10})

    def test_matrix_script_preflight_skips_unknown_slugs(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import run_openrouter_matrix  # noqa: PLC0415 - script module, not a package

        config = {
            "defaults": {"splits": ["dev"], "max_new_tokens": 64, "concurrency": 2},
            "models": [
                {"label": "opus", "slug": "anthropic/claude-opus-5.5"},
                {"label": "ghost", "slug": "openai/does-not-exist"},
                {"label": "off", "slug": "anthropic/claude-opus-5.5", "enabled": False},
            ],
        }
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "models.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            try:
                code = run_openrouter_matrix.main(
                    ["--config", str(config_path), "--results-dir", tmp]
                )
            finally:
                os.chdir(cwd)
            self.assertEqual(code, 0)
            self.assertTrue((Path(tmp) / "opus.dev.json").exists())
            self.assertFalse((Path(tmp) / "ghost.dev.json").exists())
            self.assertFalse((Path(tmp) / "off.dev.json").exists())
            result = load_result(Path(tmp) / "opus.dev.json")
        self.assertEqual(result["run_config"]["data"], ["data/persian_eval_v1.dev.jsonl"])


class CostEstimateTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import run_openrouter_matrix  # noqa: PLC0415 - script module, not a package

        self.matrix = run_openrouter_matrix

    def test_estimate_cost_counts_prompt_answer_and_thinking_tokens(self):
        profile = {"items": 10, "prompt_chars": 2900.0, "answer_chars": 290.0}
        model = {"slug": "openai/gpt-6-sol", "reasoning_effort": "low"}
        cost = self.matrix.estimate_cost(model, profile, (2.0, 10.0))
        # 2900/2.9 + 15*10 = 1150 input tokens; 290/2.9 + 600*10 = 6100 output tokens.
        self.assertAlmostEqual(cost, (1150 * 2.0 + 6100 * 10.0) / 1_000_000)

    def test_claude_rows_use_the_conservative_tokenizer_ratio(self):
        self.assertEqual(self.matrix.chars_per_token({"slug": "anthropic/claude-opus-5.5"}), 1.0)
        self.assertEqual(self.matrix.chars_per_token({"slug": "x-ai/grok-4.7"}), 2.0)

    def test_prices_fall_back_to_listed_values(self):
        model = {"slug": "openai/gpt-6-sol"}
        listed = {"openai/gpt-6-sol": [2, 10]}
        self.assertEqual(self.matrix.model_prices(model, None, listed), (2.0, 10.0))
        live = {"openai/gpt-6-sol": {"pricing": {"prompt": "0.000003", "completion": "0.00001"}}}
        self.assertEqual(self.matrix.model_prices(model, live, listed), (3.0, 10.0))
        self.assertIsNone(self.matrix.model_prices({"slug": "x/unknown"}, None, listed))

    def test_estimate_flag_runs_offline(self):
        cwd = os.getcwd()
        try:
            code = self.matrix.main(
                ["--estimate", "--skip-preflight", "--only", "opus-5.5", "--splits", "challenge"]
            )
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
