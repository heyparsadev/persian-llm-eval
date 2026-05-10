import json
import tempfile
import unittest
from pathlib import Path

from persian_eval.leaderboard import build_leaderboard, compute_bootstrap_ci
from persian_eval.results import write_result


class LeaderboardTests(unittest.TestCase):
    def test_build_splits_api_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result(
                root / "open.json",
                {
                    "model_id": "open/model",
                    "model_type": "open-weight",
                    "revision": None,
                    "backend": "hf",
                    "task_scores": {"knowledge": {"score": 0.5, "n": 2}},
                    "overall_score": 0.5,
                    "run_config": {},
                    "timestamp": "2026-05-01T00:00:00+00:00",
                },
            )
            write_result(
                root / "api.json",
                {
                    "model_id": "api-model",
                    "model_type": "api",
                    "revision": None,
                    "backend": "openai-compatible",
                    "task_scores": {"knowledge": {"score": 0.9, "n": 2}},
                    "overall_score": 0.9,
                    "run_config": {},
                    "timestamp": "2026-05-01T00:00:00+00:00",
                },
            )
            leaderboard = build_leaderboard([root / "open.json", root / "api.json"])
            self.assertEqual(len(leaderboard["main"]), 1)
            self.assertEqual(len(leaderboard["reference"]), 1)
            self.assertEqual(leaderboard["reference"][0]["model_id"], "api-model")
            for row in leaderboard["main"] + leaderboard["reference"]:
                self.assertIn("overall_score_ci_low", row)
                self.assertIn("overall_score_ci_high", row)
                self.assertLessEqual(row["overall_score_ci_low"], row["overall_score"])
                self.assertGreaterEqual(row["overall_score_ci_high"], row["overall_score"])

    def test_bootstrap_ci_uses_samples_when_present(self):
        result = {
            "model_id": "x",
            "model_type": "open-weight",
            "revision": None,
            "backend": "mock",
            "task_scores": {
                "knowledge": {"score": 0.5, "n": 4},
                "culture": {"score": 0.75, "n": 4},
            },
            "overall_score": 0.625,
            "run_config": {},
            "timestamp": "2026-05-01T00:00:00+00:00",
            "samples": [
                {"track": "knowledge", "score": 1.0},
                {"track": "knowledge", "score": 0.0},
                {"track": "knowledge", "score": 1.0},
                {"track": "knowledge", "score": 0.0},
                {"track": "culture", "score": 1.0},
                {"track": "culture", "score": 1.0},
                {"track": "culture", "score": 1.0},
                {"track": "culture", "score": 0.0},
            ],
        }
        ci = compute_bootstrap_ci(result, iterations=400, confidence=0.95, seed=42)
        self.assertIsNotNone(ci)
        assert ci is not None  # for mypy
        self.assertEqual(ci["method"], "bootstrap_sample")
        self.assertGreaterEqual(ci["high"], ci["low"])
        self.assertGreaterEqual(ci["high"], 0.625)
        self.assertLessEqual(ci["low"], 0.625)

    def test_bootstrap_ci_falls_back_to_normal_approx(self):
        result = {
            "model_id": "x",
            "model_type": "open-weight",
            "revision": None,
            "backend": "mock",
            "task_scores": {
                "knowledge": {"score": 0.5, "n": 30},
                "culture": {"score": 0.7, "n": 30},
            },
            "overall_score": 0.6,
            "run_config": {},
            "timestamp": "2026-05-01T00:00:00+00:00",
        }
        ci = compute_bootstrap_ci(result, iterations=200, confidence=0.95, seed=0)
        self.assertIsNotNone(ci)
        assert ci is not None  # for mypy
        self.assertEqual(ci["method"], "normal_approx")
        self.assertLess(ci["low"], 0.6)
        self.assertGreater(ci["high"], 0.6)

    def test_bootstrap_ci_serialises_through_leaderboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_result(
                root / "r.json",
                {
                    "model_id": "m",
                    "model_type": "open-weight",
                    "revision": None,
                    "backend": "hf",
                    "task_scores": {"knowledge": {"score": 0.5, "n": 20}},
                    "overall_score": 0.5,
                    "run_config": {},
                    "timestamp": "2026-05-01T00:00:00+00:00",
                },
            )
            board = build_leaderboard([root / "r.json"], bootstrap_iterations=100)
            payload = json.dumps(board)
            self.assertIn("overall_score_ci_low", payload)


if __name__ == "__main__":
    unittest.main()
