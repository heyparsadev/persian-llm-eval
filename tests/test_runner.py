import json
import random
import tempfile
import threading
import time
import unittest
from pathlib import Path

from persian_eval.backends import APIError, BaseBackend
from persian_eval.cli import main
from persian_eval.dataset import DatasetRecord
from persian_eval.results import load_result
from persian_eval.runner import rescore_result, run_records

ROOT = Path(__file__).resolve().parents[1]


def _records(count):
    return [
        DatasetRecord.from_dict(
            {
                "id": f"r{index:02d}",
                "track": "short_qa" if index % 2 else "math",
                "prompt": f"سوال {index}",
                "choices": None,
                "answer": [str(index)],
                "metadata": {"scoring": "exact"},
                "source": "test",
                "split": "dev",
            }
        )
        for index in range(count)
    ]


class EchoBackend(BaseBackend):
    """Answers the item number, sleeps a little, and reports fake usage."""

    name = "echo"

    def __init__(self, fail_on=None, error=None):
        self.calls = []
        self.fail_on = fail_on if isinstance(fail_on, (set, list)) else {fail_on}
        self.error = error or RuntimeError("simulated outage")
        self.lock = threading.Lock()

    def generate_with_meta(self, record):
        with self.lock:
            self.calls.append(record.id)
        if record.id in self.fail_on:
            raise self.error
        time.sleep(random.uniform(0, 0.01))
        number = str(int(record.id[1:]))
        return number, {"cost_usd": 0.001, "prompt_tokens": 10, "provider": "Fake"}


def _run(records, backend, **kwargs):
    return run_records(
        records,
        backend=backend,
        model_id="echo",
        model_type="api",
        revision=None,
        run_config={},
        **kwargs,
    )


class RunnerTests(unittest.TestCase):
    def test_concurrent_run_keeps_dataset_order_and_sums_usage(self):
        records = _records(12)
        result = _run(records, EchoBackend(), concurrency=4)
        self.assertEqual([sample["id"] for sample in result["samples"]], [r.id for r in records])
        self.assertEqual(result["overall_score"], 1.0)
        self.assertEqual(result["usage"]["calls"], 12)
        self.assertAlmostEqual(result["usage"]["cost_usd"], 0.012)
        self.assertEqual(result["usage"]["prompt_tokens"], 120)
        self.assertEqual(result["usage"]["providers"], {"Fake": 12})
        self.assertEqual(result["samples"][0]["meta"]["provider"], "Fake")

    def test_backends_without_meta_produce_no_usage_block(self):
        class Plain(BaseBackend):
            name = "plain"

            def generate(self, record):
                return "0"

        result = _run(_records(2), Plain())
        self.assertNotIn("usage", result)
        self.assertNotIn("meta", result["samples"][0])

    def test_resume_skips_checkpointed_predictions(self):
        records = _records(6)
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "out.json.partial.jsonl"
            with self.assertRaises(RuntimeError):
                _run(records, EchoBackend(fail_on="r03"), checkpoint_path=checkpoint)
            lines = [json.loads(line) for line in checkpoint.read_text().splitlines()]
            self.assertEqual(lines[0]["checkpoint"]["model_id"], "echo")
            self.assertEqual([line["id"] for line in lines[1:]], ["r00", "r01", "r02"])

            backend = EchoBackend()
            result = _run(records, backend, checkpoint_path=checkpoint, resume=True)
            self.assertEqual(backend.calls, ["r03", "r04", "r05"])
            self.assertEqual(result["overall_score"], 1.0)
            self.assertEqual(len(result["samples"]), 6)

    def test_resume_refuses_a_checkpoint_from_another_configuration(self):
        records = _records(4)
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "out.json.partial.jsonl"
            with self.assertRaises(RuntimeError):
                _run(records, EchoBackend(fail_on="r02"), checkpoint_path=checkpoint)
            with self.assertRaises(ValueError):
                run_records(
                    records,
                    backend=EchoBackend(),
                    model_id="another-model",
                    model_type="api",
                    revision=None,
                    run_config={},
                    checkpoint_path=checkpoint,
                    resume=True,
                )

    def test_fresh_run_ignores_stale_checkpoint(self):
        records = _records(3)
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "out.json.partial.jsonl"
            checkpoint.write_text(json.dumps({"id": "r00", "prediction": "wrong"}) + "\n")
            backend = EchoBackend()
            result = _run(records, backend, checkpoint_path=checkpoint)
            self.assertEqual(backend.calls, ["r00", "r01", "r02"])
            self.assertEqual(result["overall_score"], 1.0)

    def test_concurrent_failure_propagates(self):
        with self.assertRaises(RuntimeError):
            _run(_records(8), EchoBackend(fail_on="r05"), concurrency=3)

    def test_item_error_budget_scores_failed_items_zero(self):
        records = _records(6)
        flagged = APIError("OpenRouter API error 403: flagged", status=403)
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "out.json.partial.jsonl"
            result = _run(
                records,
                EchoBackend(fail_on="r02", error=flagged),
                checkpoint_path=checkpoint,
                max_item_errors=1,
                concurrency=2,
            )
            sample = result["samples"][2]
            self.assertEqual(sample["prediction"], "")
            self.assertEqual(sample["score"], 0.0)
            self.assertIn("403", sample["meta"]["error"])
            self.assertEqual(result["usage"]["item_errors"], 1)

            # A resumed run retries the failed item and keeps the rest.
            backend = EchoBackend()
            resumed = _run(records, backend, checkpoint_path=checkpoint, resume=True)
            self.assertEqual(backend.calls, ["r02"])
            self.assertEqual(resumed["overall_score"], 1.0)

    def test_item_error_budget_is_bounded(self):
        error = APIError("OpenRouter API error 400: bad", status=400)
        with self.assertRaises(APIError):
            _run(_records(6), EchoBackend(fail_on={"r01", "r03"}, error=error), max_item_errors=1)
        with self.assertRaises(APIError):
            _run(_records(3), EchoBackend(fail_on="r00", error=error))

    def test_credit_and_auth_errors_always_abort(self):
        for status in (401, 402):
            error = APIError(f"OpenRouter API error {status}", status=status)
            with self.assertRaises(APIError):
                _run(_records(3), EchoBackend(fail_on="r01", error=error), max_item_errors=5)

    def test_rescore_preserves_sample_meta(self):
        result = _run(_records(2), EchoBackend())
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data.jsonl"
            data.write_text(
                "\n".join(
                    json.dumps(
                        {
                            "id": record.id,
                            "track": record.track,
                            "prompt": record.prompt,
                            "choices": None,
                            "answer": record.answer,
                            "metadata": record.metadata,
                            "source": "test",
                            "split": "dev",
                        },
                        ensure_ascii=False,
                    )
                    for record in _records(2)
                ),
                encoding="utf-8",
            )
            rescored = rescore_result(result, data_paths=[data])
        self.assertEqual(rescored["samples"][0]["meta"]["provider"], "Fake")
        self.assertEqual(rescored["usage"], result["usage"])


class CliRunTests(unittest.TestCase):
    def test_mock_run_with_concurrency_writes_result_and_cleans_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "smoke.json"
            code = main(
                [
                    "run",
                    "--model",
                    "smoke",
                    "--backend",
                    "mock",
                    "--data",
                    str(ROOT / "data" / "persian_eval_v1.dev.jsonl"),
                    "--output",
                    str(output),
                    "--concurrency",
                    "3",
                ]
            )
            self.assertEqual(code, 0)
            result = load_result(output)
            self.assertEqual(len(result["samples"]), 10)
            self.assertFalse(Path(f"{output}.partial.jsonl").exists())

    def test_hf_backend_rejects_concurrency(self):
        code = main(
            [
                "run",
                "--model",
                "x",
                "--backend",
                "hf",
                "--data",
                str(ROOT / "data" / "persian_eval_v1.dev.jsonl"),
                "--output",
                "/nonexistent/out.json",
                "--concurrency",
                "2",
            ]
        )
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
