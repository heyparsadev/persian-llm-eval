import unittest
from pathlib import Path

from persian_eval.dataset import duplicate_prompts, load_records


ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_seed_datasets_are_valid(self):
        records = load_records(
            [
                ROOT / "data" / "persian_eval_v1.dev.jsonl",
                ROOT / "data" / "persian_eval_v1.public_eval.jsonl",
            ]
        )
        self.assertEqual(len(records), 30)
        self.assertEqual(duplicate_prompts(records), [])

    def test_task_filter(self):
        records = load_records([ROOT / "data" / "persian_eval_v1.public_eval.jsonl"], tasks={"culture"})
        self.assertEqual(len(records), 4)
        self.assertTrue(all(record.track == "culture" for record in records))


if __name__ == "__main__":
    unittest.main()
