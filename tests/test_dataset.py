import unittest
from pathlib import Path

from persian_eval.dataset import duplicate_prompts, load_records
from persian_eval.scoring import score_record

ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_seed_datasets_are_valid(self):
        records = load_records(
            [
                ROOT / "data" / "persian_eval_v1.dev.jsonl",
                ROOT / "data" / "persian_eval_v1.public_eval.jsonl",
                ROOT / "data" / "persian_eval_v1.hard.jsonl",
                ROOT / "data" / "persian_eval_v1.practical.jsonl",
                ROOT / "data" / "persian_eval_v1.challenge.jsonl",
            ]
        )
        # v1 baseline (50) plus v1.1 additions (260) for the public_eval and
        # hard splits.
        self.assertGreaterEqual(len(records), 50)
        self.assertEqual(duplicate_prompts(records), [])

    def test_practical_split_shape_and_references(self):
        self._check_generated_split("practical", expected_tracks=6)

    def test_challenge_split_shape_and_references(self):
        self._check_generated_split("challenge", expected_tracks=5)

    def _check_generated_split(self, split, *, expected_tracks):
        records = load_records([ROOT / "data" / f"persian_eval_v1.{split}.jsonl"])
        tracks = {}
        for record in records:
            tracks[record.track] = tracks.get(record.track, 0) + 1
            self.assertEqual(record.split, split)
            self.assertEqual(record.metadata["review"]["status"], "pending_review")
            reference = record.metadata["reference_response"]
            score, details = score_record(record, reference)
            self.assertEqual(score, 1.0, f"{record.id}: {details}")
        self.assertEqual(len(tracks), expected_tracks)
        self.assertTrue(all(count >= 20 for count in tracks.values()), tracks)

    def test_task_filter(self):
        records = load_records(
            [ROOT / "data" / "persian_eval_v1.public_eval.jsonl"], tasks={"culture"}
        )
        self.assertGreaterEqual(len(records), 4)
        self.assertTrue(all(record.track == "culture" for record in records))


if __name__ == "__main__":
    unittest.main()
