import tempfile
import unittest
from pathlib import Path

from persian_eval.leaderboard import build_leaderboard
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


if __name__ == "__main__":
    unittest.main()
