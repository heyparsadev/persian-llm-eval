import dataclasses
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from unittest import mock

from persian_eval.backends import (
    AnthropicBackend,
    APIError,
    GenerationConfig,
    read_anthropic_stream,
)
from persian_eval.cli import main as cli_main
from persian_eval.dataset import DatasetRecord
from persian_eval.results import load_result
from persian_eval.runner import batch_custom_ids, pending_batch, summarize_usage

ROOT = Path(__file__).resolve().parents[1]
DEV = str(ROOT / "data" / "persian_eval_v1.dev.jsonl")

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


def _backend(model="claude-opus-5-5", **overrides):
    with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        return AnthropicBackend(model, config=GenerationConfig(max_new_tokens=512, **overrides))


def _message(model, text="الف", stop_reason="end_turn", **extra):
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": [
            {"type": "thinking", "thinking": "", "signature": "sig"},
            {"type": "text", "text": text},
        ],
        "stop_reason": stop_reason,
        "usage": {"input_tokens": 1000, "output_tokens": 500},
        **extra,
    }


class Claude5PayloadTests(unittest.TestCase):
    def test_effort_uses_adaptive_thinking_without_temperature(self):
        payload = _backend(reasoning_effort="low").build_payload(RECORD)
        self.assertEqual(payload["thinking"], {"type": "adaptive"})
        self.assertEqual(payload["output_config"], {"effort": "low"})
        self.assertEqual(payload["max_tokens"], 512 + 4096)
        self.assertNotIn("temperature", payload)

    def test_max_effort_gets_at_least_64k_tokens(self):
        payload = _backend(reasoning_effort="max").build_payload(RECORD)
        self.assertEqual(payload["output_config"], {"effort": "max"})
        self.assertGreaterEqual(payload["max_tokens"], 64000)

    def test_no_effort_leaves_the_default_but_sizes_for_it(self):
        payload = _backend().build_payload(RECORD)
        self.assertNotIn("thinking", payload)
        self.assertNotIn("output_config", payload)
        self.assertNotIn("temperature", payload)
        self.assertEqual(payload["max_tokens"], 512 + 8192)  # Opus 5.5 defaults to medium.

    def test_sonnet_5_5_turns_thinking_off_with_between_tools(self):
        payload = _backend("claude-sonnet-5-5", reasoning_effort="none").build_payload(RECORD)
        self.assertEqual(payload["thinking"], {"type": "between_tools"})
        self.assertNotIn("output_config", payload)
        self.assertNotIn("temperature", payload)
        self.assertEqual(payload["max_tokens"], 512)

    def test_sonnet_5_5_medium(self):
        payload = _backend("claude-sonnet-5-5", reasoning_effort="medium").build_payload(RECORD)
        self.assertEqual(payload["thinking"], {"type": "adaptive"})
        self.assertEqual(payload["output_config"], {"effort": "medium"})

    def test_models_that_always_think_reject_none(self):
        for model in ("claude-opus-5-5", "claude-fable-5-1"):
            with self.assertRaisesRegex(ValueError, "cannot turn thinking off"):
                _backend(model, reasoning_effort="none")

    def test_unsupported_effort_and_budget_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "takes --reasoning-effort"):
            _backend("claude-sonnet-5-5", reasoning_effort="minimal")
        with self.assertRaisesRegex(ValueError, "no thinking token budget"):
            _backend(thinking_budget_tokens=2048)

    def test_older_models_keep_their_payloads(self):
        legacy = _backend("claude-sonnet-4-6").build_payload(RECORD)
        self.assertEqual(legacy["temperature"], 0.0)
        self.assertNotIn("thinking", legacy)
        opus_47 = _backend("claude-opus-4-7", reasoning_effort="low").build_payload(RECORD)
        self.assertEqual(opus_47["output_config"], {"effort": "low"})
        self.assertNotIn("temperature", opus_47)


class AnthropicResponseTests(unittest.TestCase):
    def test_text_usage_and_list_price_cost(self):
        prediction, meta = _backend().parse_message(_message("claude-opus-5-5"))
        self.assertEqual(prediction, "الف")
        self.assertEqual(meta["prompt_tokens"], 1000)
        self.assertEqual(meta["completion_tokens"], 500)
        self.assertAlmostEqual(meta["cost_usd"], (1000 * 4 + 500 * 20) / 1_000_000)
        _, batch_meta = _backend().parse_message(_message("claude-opus-5-5"), batch=True)
        self.assertAlmostEqual(batch_meta["cost_usd"], meta["cost_usd"] / 2)

    def test_refusal_scores_as_an_empty_answer(self):
        data = _message(
            "claude-opus-5-5",
            text="partial",
            stop_reason="refusal",
            stop_details={"category": "bio"},
        )
        prediction, meta = _backend().parse_message(data)
        self.assertEqual(prediction, "")
        self.assertEqual(meta["finish_reason"], "refusal")
        self.assertEqual(meta["refusal_category"], "bio")
        usage = summarize_usage([meta], [prediction])
        self.assertEqual(usage["refusals"], 1)

    def test_max_tokens_counts_as_truncated_and_unknown_models_have_no_cost(self):
        backend = _backend("claude-sonnet-4-6")
        _, meta = backend.parse_message(_message("claude-sonnet-4-6", stop_reason="max_tokens"))
        self.assertNotIn("cost_usd", meta)
        self.assertEqual(summarize_usage([meta], ["x"])["truncated"], 1)

    def test_stream_is_assembled_into_a_message(self):
        events = [
            {
                "type": "message_start",
                "message": {
                    "model": "claude-opus-5-5",
                    "content": [],
                    "usage": {"input_tokens": 1000, "output_tokens": 1},
                },
            },
            {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking"}},
            {"type": "ping"},
            {"type": "content_block_stop", "index": 0},
            {"type": "content_block_start", "index": 1, "content_block": {"type": "text"}},
            {
                "type": "content_block_delta",
                "index": 1,
                "delta": {"type": "text_delta", "text": "ال"},
            },
            {
                "type": "content_block_delta",
                "index": 1,
                "delta": {"type": "text_delta", "text": "ف"},
            },
            {
                "type": "message_delta",
                "delta": {"stop_reason": "end_turn"},
                "usage": {"output_tokens": 500},
            },
            {"type": "message_stop"},
        ]
        message = read_anthropic_stream(io.BytesIO(_sse(events)))
        prediction, meta = _backend().parse_message(message)
        self.assertEqual(prediction, "الف")
        self.assertEqual(meta["finish_reason"], "end_turn")
        self.assertEqual(meta["completion_tokens"], 500)
        self.assertEqual(meta["prompt_tokens"], 1000)

    def test_overloaded_stream_error_is_retryable(self):
        events = [{"type": "error", "error": {"type": "overloaded_error", "message": "busy"}}]
        with self.assertRaises(APIError) as caught:
            read_anthropic_stream(io.BytesIO(_sse(events)))
        self.assertEqual(caught.exception.status, 529)

    def test_batch_submission_is_never_retried_after_a_network_error(self):
        backend = _backend()
        with (
            mock.patch("persian_eval.backends.time.sleep"),
            mock.patch(
                "persian_eval.backends.urllib.request.urlopen",
                side_effect=urllib.error.URLError("connection reset"),
            ) as urlopen,
        ):
            with self.assertRaises(APIError):
                backend.submit_batch([])
            self.assertEqual(urlopen.call_count, 1)
            with self.assertRaises(APIError):
                backend.get_batch("msgbatch_1")
            self.assertEqual(urlopen.call_count, 5)

    def test_custom_ids_fall_back_to_positions(self):
        records = [RECORD, dataclasses.replace(RECORD, id="bad id/1")]
        self.assertEqual(batch_custom_ids(records), {"item-00000": "q", "item-00001": "bad id/1"})
        self.assertEqual(batch_custom_ids([RECORD]), {"q": "q"})


def _sse(events):
    lines = []
    for event in events:
        lines.append(f"event: {event['type']}")
        lines.append("data: " + json.dumps(event, ensure_ascii=False))
        lines.append("")
    return ("\n".join(lines) + "\n").encode("utf-8")


class FakeAnthropic(BaseHTTPRequestHandler):
    """Minimal stand-in for the Messages and Message Batches endpoints."""

    messages: ClassVar[list] = []
    batches: ClassVar[dict] = {}
    log: ClassVar[list] = []
    errored: ClassVar[set] = set()
    polls_before_end = 1
    overloaded_once = False

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path.endswith("/v1/messages/batches"):
            batch_id = f"msgbatch_{len(FakeAnthropic.batches) + 1}"
            FakeAnthropic.batches[batch_id] = {"requests": body["requests"], "polls": 0}
            FakeAnthropic.log.append(("create", batch_id))
            self._reply(200, self._batch(batch_id))
            return
        FakeAnthropic.messages.append((self.headers.get("x-api-key"), body))
        if FakeAnthropic.overloaded_once:
            FakeAnthropic.overloaded_once = False
            self._reply(529, {"type": "error", "error": {"type": "overloaded_error"}})
            return
        message = _message(body["model"])
        if not body.get("stream"):
            self._reply(200, message)
            return
        events = [
            {"type": "message_start", "message": {**message, "content": [], "stop_reason": None}},
            {"type": "content_block_start", "index": 0, "content_block": {"type": "text"}},
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "الف"},
            },
            {"type": "content_block_stop", "index": 0},
            {
                "type": "message_delta",
                "delta": {"stop_reason": "end_turn"},
                "usage": {"output_tokens": 500},
            },
            {"type": "message_stop"},
        ]
        data = _sse(events)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parts = self.path.rstrip("/").split("/")
        if parts[-1] == "results":
            batch = FakeAnthropic.batches[parts[-2]]
            rows = []
            for request in batch["requests"]:
                custom_id = request["custom_id"]
                if custom_id in FakeAnthropic.errored:
                    error = {"type": "error", "error": {"type": "api_error", "message": "boom"}}
                    result = {"type": "errored", "error": error}
                else:
                    result = {"type": "succeeded", "message": _message(request["params"]["model"])}
                rows.append(json.dumps({"custom_id": custom_id, "result": result}))
            data = ("\n".join(reversed(rows)) + "\n").encode("utf-8")  # any order
            self.send_response(200)
            self.send_header("Content-Type", "application/binary")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        FakeAnthropic.batches[parts[-1]]["polls"] += 1
        FakeAnthropic.log.append(("poll", parts[-1]))
        self._reply(200, self._batch(parts[-1]))

    def _batch(self, batch_id):
        batch = FakeAnthropic.batches[batch_id]
        ended = batch["polls"] >= FakeAnthropic.polls_before_end
        total = len(batch["requests"])
        return {
            "id": batch_id,
            "type": "message_batch",
            "processing_status": "ended" if ended else "in_progress",
            "request_counts": {
                "processing": 0 if ended else total,
                "succeeded": total if ended else 0,
                "errored": 0,
                "canceled": 0,
                "expired": 0,
            },
        }

    def _reply(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class AnthropicEndToEndTests(unittest.TestCase):
    def setUp(self):
        FakeAnthropic.messages = []
        FakeAnthropic.batches = {}
        FakeAnthropic.log = []
        FakeAnthropic.errored = set()
        FakeAnthropic.polls_before_end = 1
        FakeAnthropic.overloaded_once = False
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAnthropic)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.env = mock.patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "test-key",
                "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{self.server.server_port}",
                "no_proxy": "127.0.0.1,localhost",
                "NO_PROXY": "127.0.0.1,localhost",
            },
        )
        self.env.start()
        self.patches = [
            mock.patch("persian_eval.backends.time.sleep"),
            mock.patch("persian_eval.runner.time.sleep"),
        ]
        for patch in self.patches:
            patch.start()
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "opus.json"

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        self.env.stop()
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def _run(self, *extra, effort="low"):
        args = ["run", "--model", "claude-opus-5-5", "--backend", "anthropic", "--data", DEV]
        args += ["--output", str(self.output), "--max-new-tokens", "1024"]
        return cli_main([*args, "--reasoning-effort", effort, *extra])

    def test_synchronous_run_records_usage_and_retries_overload(self):
        FakeAnthropic.overloaded_once = True
        self.assertEqual(self._run("--concurrency", "3"), 0)
        result = load_result(self.output)
        self.assertEqual(len(FakeAnthropic.messages), 11)  # 10 items plus one retried 529.
        key, body = FakeAnthropic.messages[-1]
        self.assertEqual(key, "test-key")
        self.assertEqual(body["output_config"], {"effort": "low"})
        self.assertNotIn("temperature", body)
        self.assertNotIn("stream", body)
        self.assertEqual(result["usage"]["calls"], 10)
        self.assertAlmostEqual(result["usage"]["cost_usd"], 10 * 0.014)
        self.assertEqual(result["usage"]["served_models"], {"claude-opus-5-5": 10})

    def test_max_effort_requests_are_streamed(self):
        self.assertEqual(self._run(effort="max"), 0)
        result = load_result(self.output)
        self.assertTrue(all(body["stream"] for _, body in FakeAnthropic.messages))
        self.assertTrue(all(sample["prediction"] == "الف" for sample in result["samples"]))
        self.assertAlmostEqual(result["usage"]["cost_usd"], 10 * 0.014)

    def test_batch_run_costs_half_and_cleans_up(self):
        self.assertEqual(self._run("--batch"), 0)
        result = load_result(self.output)
        self.assertEqual(FakeAnthropic.messages, [])
        self.assertEqual(len(FakeAnthropic.batches), 1)
        requests = FakeAnthropic.batches["msgbatch_1"]["requests"]
        self.assertEqual(len(requests), 10)
        self.assertEqual(requests[0]["params"]["output_config"], {"effort": "low"})
        self.assertNotIn("stream", requests[0]["params"])
        self.assertEqual(result["run_config"]["batch"], True)
        self.assertAlmostEqual(result["usage"]["cost_usd"], 10 * 0.007)
        self.assertEqual(len(result["samples"]), 10)
        self.assertFalse(Path(f"{self.output}.partial.jsonl").exists())

    def test_no_wait_submits_once_and_resume_collects(self):
        checkpoint = Path(f"{self.output}.partial.jsonl")
        self.assertEqual(self._run("--batch", "--no-wait"), 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(pending_batch(checkpoint)["id"], "msgbatch_1")
        # Starting over would pay for a second batch, so it is refused.
        self.assertEqual(self._run("--batch"), 1)
        self.assertEqual(self._run("--batch", "--resume"), 0)
        self.assertEqual(len(FakeAnthropic.batches), 1)
        self.assertEqual(len(load_result(self.output)["samples"]), 10)

    def test_failed_batch_items_are_resent_on_resume(self):
        FakeAnthropic.errored = {"peval-dev-knowledge-001", "peval-dev-shortqa-001"}
        self.assertEqual(self._run("--batch"), 1)
        self.assertFalse(self.output.exists())
        FakeAnthropic.errored = set()
        self.assertEqual(self._run("--batch", "--resume"), 0)
        self.assertEqual(len(FakeAnthropic.batches), 2)
        resent = {
            request["custom_id"] for request in FakeAnthropic.batches["msgbatch_2"]["requests"]
        }
        self.assertEqual(resent, {"peval-dev-knowledge-001", "peval-dev-shortqa-001"})
        result = load_result(self.output)
        self.assertEqual(result["usage"]["item_errors"], 0)
        self.assertAlmostEqual(result["usage"]["cost_usd"], 10 * 0.007)

    def test_failed_batch_items_within_budget_score_zero(self):
        FakeAnthropic.errored = {"peval-dev-knowledge-001"}
        self.assertEqual(self._run("--batch", "--max-item-errors", "1"), 0)
        result = load_result(self.output)
        self.assertEqual(result["usage"]["item_errors"], 1)
        failed = next(s for s in result["samples"] if s["id"] == "peval-dev-knowledge-001")
        self.assertEqual(failed["score"], 0.0)
        self.assertIn("api_error", failed["meta"]["error"])

    def test_batch_needs_the_anthropic_backend(self):
        code = cli_main(
            [
                "run",
                "--model",
                "m",
                "--backend",
                "mock",
                "--data",
                DEV,
                "--output",
                "x.json",
                "--batch",
            ]
        )
        self.assertEqual(code, 1)

    def test_matrix_submits_every_batch_before_collecting(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import run_matrix  # noqa: PLC0415 - script module, not a package

        config = {
            "defaults": {"backend": "anthropic", "batch": True, "splits": ["dev"]},
            "models": [
                {"label": "opus-low", "slug": "claude-opus-5-5", "reasoning_effort": "low"},
                {"label": "sonnet-off", "slug": "claude-sonnet-5-5", "reasoning_effort": "none"},
            ],
        }
        config_path = Path(self.tmp.name) / "models.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        cwd = os.getcwd()
        try:
            code = run_matrix.main(
                ["--config", str(config_path), "--results-dir", self.tmp.name, "--max-items", "4"]
            )
        finally:
            os.chdir(cwd)
        self.assertEqual(code, 0)
        self.assertEqual(
            FakeAnthropic.log[:2], [("create", "msgbatch_1"), ("create", "msgbatch_2")]
        )
        sonnet = FakeAnthropic.batches["msgbatch_2"]["requests"]
        self.assertEqual(len(sonnet), 4)
        self.assertEqual(sonnet[0]["params"]["thinking"], {"type": "between_tools"})
        for label in ("opus-low", "sonnet-off"):
            result = load_result(Path(self.tmp.name) / f"{label}.dev.json")
            self.assertEqual(result["run_config"]["max_items"], 4)
            self.assertEqual(len(result["samples"]), 4)
            self.assertEqual(len({sample["track"] for sample in result["samples"]}), 4)


class AnthropicMatrixConfigTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import run_matrix  # noqa: PLC0415 - script module, not a package

        self.matrix = run_matrix

    def test_every_row_is_a_valid_backend_setting_with_a_price(self):
        path = ROOT / "configs" / "anthropic_models.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        prices = config["prices_usd_per_million"]
        _, enabled = self.matrix.load_config(path)
        self.assertEqual(len(enabled), 7)  # Phase 1: no max rows, no Fable.
        self.assertFalse(any(model["reasoning_effort"] == "max" for model in enabled))
        for row in config["models"]:  # Disabled rows too, so phase 2 starts clean.
            model = {**config["defaults"], **row}
            self.assertEqual(self.matrix.backend_of(model), "anthropic")
            self.assertIn(model["slug"], prices)
            effort = model["reasoning_effort"]
            _backend(model["slug"], reasoning_effort=effort)  # Raises on a rejected setting.

    def test_batch_rows_are_estimated_at_half_price(self):
        profile = {"items": 10, "prompt_chars": 1000.0, "answer_chars": 100.0}
        model = {"slug": "claude-opus-5-5", "reasoning_effort": "max"}
        full = self.matrix.estimate_cost(model, profile, (4.0, 20.0))
        half = self.matrix.estimate_cost({**model, "batch": True}, profile, (4.0, 20.0))
        self.assertAlmostEqual(half, full / 2)
        self.assertEqual(self.matrix.chars_per_token(model), 1.0)

    def test_pilot_profile_scales_to_max_items(self):
        full = self.matrix.split_profile("challenge")
        pilot = self.matrix.split_profile("challenge", max_items=20)
        self.assertEqual(pilot["items"], 20)
        self.assertAlmostEqual(pilot["prompt_chars"], full["prompt_chars"] * 20 / full["items"])


if __name__ == "__main__":
    unittest.main()
