import unittest

from persian_eval.dataset import DatasetRecord
from persian_eval.normalize import normalize_persian, strip_punctuation
from persian_eval.scoring import extract_choice_index, prediction_candidates, score_record, token_f1


class ScoringTests(unittest.TestCase):
    def test_normalize_persian_variants(self):
        self.assertEqual(normalize_persian("كتاب ۱۲"), "کتاب 12")
        self.assertEqual(strip_punctuation("سلام، دنیا!"), "سلام دنیا")

    def test_extract_choice_label(self):
        index = extract_choice_index("گزینه ب درست است.", ["تهران", "اصفهان"], ["الف", "ب"])
        self.assertEqual(index, 1)

    def test_choice_text_is_not_confused_with_label(self):
        index = extract_choice_index(
            "پایتون", ["پایتون", "البرز", "نوروز", "سه تار"], ["الف", "ب", "پ", "ت"]
        )
        self.assertEqual(index, 0)

    def test_prediction_candidates_extract_final_answer(self):
        candidates = prediction_candidates("<think>تحلیل طولانی</think>\nپاسخ نهایی: گزینه ب")
        self.assertEqual(candidates[0], "گزینه ب")

    def test_exact_scoring_uses_final_answer(self):
        record = DatasetRecord.from_dict(
            {
                "id": "e",
                "track": "math",
                "prompt": "عدد؟",
                "choices": None,
                "answer": ["۲۰", "20"],
                "metadata": {"scoring": "exact"},
                "source": "test",
                "split": "dev",
            }
        )
        score, details = score_record(record, "<think>اول حساب می کنم</think>\nپاسخ نهایی: 20")
        self.assertEqual(score, 1.0)
        self.assertEqual(details["normalized_prediction"], "20")

    def test_mcq_scoring(self):
        record = DatasetRecord.from_dict(
            {
                "id": "x",
                "track": "knowledge",
                "prompt": "پایتخت ایران؟",
                "choices": ["تهران", "شیراز"],
                "answer": "تهران",
                "metadata": {"scoring": "mcq", "answer_index": 0},
                "source": "test",
                "split": "dev",
            }
        )
        score, details = score_record(record, "الف")
        self.assertEqual(score, 1.0)
        self.assertEqual(details["predicted_index"], 0)

    def test_f1_scoring(self):
        self.assertAlmostEqual(token_f1(["لوله", "کشی", "جدید"], ["لوله", "کشی"]), 0.8)

    def test_instruction_scoring(self):
        record = DatasetRecord.from_dict(
            {
                "id": "i",
                "track": "instruction",
                "prompt": "جمله ای درباره نوروز.",
                "choices": None,
                "answer": {"required_keywords": ["بهار", "خانواده"], "min_words": 4},
                "metadata": {"scoring": "instruction"},
                "source": "test",
                "split": "dev",
            }
        )
        score, details = score_record(record, "نوروز در بهار کنار خانواده زیباست")
        self.assertEqual(score, 1.0)
        self.assertTrue(details["checks"]["required_keywords"])


if __name__ == "__main__":
    unittest.main()
