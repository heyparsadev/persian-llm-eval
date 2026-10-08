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


def _instruction(answer):
    return DatasetRecord.from_dict(
        {
            "id": "p",
            "track": "practical_creative",
            "prompt": "یک متن بنویس.",
            "choices": None,
            "answer": answer,
            "metadata": {"scoring": "instruction"},
            "source": "test",
            "split": "dev",
        }
    )


def _json_record(answer):
    return DatasetRecord.from_dict(
        {
            "id": "j",
            "track": "practical_extraction",
            "prompt": "اطلاعات را استخراج کن.",
            "choices": None,
            "answer": answer,
            "metadata": {"scoring": "json"},
            "source": "test",
            "split": "dev",
        }
    )


class ExtendedInstructionTests(unittest.TestCase):
    def test_required_any_accepts_any_option_per_group(self):
        record = _instruction({"required_any": [["خانه", "منزل"], ["فردا"]]})
        self.assertEqual(score_record(record, "فردا به منزل شما می‌آیم.")[0], 1.0)
        self.assertEqual(score_record(record, "امروز به منزل شما می‌آیم.")[0], 0.0)

    def test_forbidden_chars_lipogram(self):
        record = _instruction({"forbidden_chars": ["ر"], "min_words": 3})
        self.assertEqual(score_record(record, "گل‌ها شکفته و هوا دلپذیر است")[0], 0.0)
        self.assertEqual(score_record(record, "گل‌ها شکفته و هوا دلنشین است")[0], 1.0)

    def test_exact_constraints_keep_zwnj_significant(self):
        record = _instruction(
            {"required_exact": ["می‌خواهم"], "forbidden_exact": ["می خواهم", "میخواهم"]}
        )
        self.assertEqual(score_record(record, "من می‌خواهم بروم.")[0], 1.0)
        self.assertEqual(score_record(record, "من می خواهم بروم.")[0], 0.0)
        self.assertEqual(score_record(record, "من ميخواهم بروم.")[0], 0.0)

    def test_required_exact_alternatives(self):
        record = _instruction(
            {"required_exact": [["کتاب‌ها", "کتابها"]], "forbidden_exact": ["کتاب ها"]}
        )
        self.assertEqual(score_record(record, "کتابها را آوردم")[0], 1.0)
        self.assertEqual(score_record(record, "کتاب‌ها را آوردم")[0], 1.0)
        self.assertEqual(score_record(record, "کتاب ها را آوردم")[0], 0.0)

    def test_loose_start_and_end_ignore_punctuation(self):
        record = _instruction({"starts_with": "با سلام و احترام", "ends_with": "با سپاس"})
        letter = "«با سلام و احترام»،\nمتن نامه.\nبا سپاس."
        self.assertEqual(score_record(record, letter)[0], 1.0)
        self.assertEqual(score_record(record, "سلام\nمتن نامه.\nبا سپاس.")[0], 0.0)

    def test_acrostic_line_initials_skip_numbering(self):
        record = _instruction({"line_initials": ["م", "ه", "ر"]})
        poem = "۱. ماه در آسمان است\n۲. هوا سرد است\n- روز کوتاه شده است"
        score, details = score_record(record, poem)
        self.assertEqual(score, 1.0, details)
        self.assertEqual(score_record(record, "ماه\nروز\nهوا")[0], 0.0)

    def test_acrostic_treats_alef_madda_as_alef(self):
        record = _instruction({"line_initials": ["ا", "ب"]})
        self.assertEqual(score_record(record, "آسمان آبی است\nباران می‌بارد")[0], 1.0)

    def test_rhyme_and_distinct_endings(self):
        record = _instruction(
            {"line_count": 2, "lines_end_with": "ار", "distinct_line_endings": True}
        )
        self.assertEqual(score_record(record, "دلم تنگ است برای بهار\nنشسته‌ام به انتظار")[0], 1.0)
        self.assertEqual(score_record(record, "دلم تنگ بهار\nمنتظر بهار")[0], 0.0)
        self.assertEqual(score_record(record, "دلم تنگ بهار")[0], 0.0)

    def test_word_initial_alliteration(self):
        record = _instruction({"word_initial": "س", "min_words": 4, "max_words": 4})
        self.assertEqual(score_record(record, "سارا سه سیب سرخ")[0], 1.0)
        self.assertEqual(score_record(record, "سارا سه سیب خرید")[0], 0.0)

    def test_required_any_ignores_punctuation(self):
        record = _instruction({"required_any": [["اولین روز هفته شنبه"]]})
        self.assertEqual(score_record(record, "در ایران، اولین روز هفته، شنبه است.")[0], 1.0)

    def test_word_palindrome(self):
        record = _instruction({"word_palindrome": True, "min_words": 5})
        self.assertEqual(score_record(record, "من و تو یکی و یکی تو و من")[0], 1.0)
        self.assertEqual(score_record(record, "من و تو یکی هستیم")[0], 0.0)

    def test_letter_palindrome_with_min_letters(self):
        record = _instruction({"letter_palindrome": True, "min_letters": 8})
        self.assertEqual(score_record(record, "شکر بترازوی وزارت برکش")[0], 1.0)
        self.assertEqual(score_record(record, "کبک")[0], 0.0)
        self.assertEqual(score_record(record, "شکر بترازو")[0], 0.0)

    def test_word_length_step_rhopalic(self):
        record = _instruction({"word_length_step": 1, "min_words": 5})
        self.assertEqual(score_record(record, "و من باز آمدم امروز")[0], 1.0)
        self.assertEqual(score_record(record, "و من امروز باز آمدم")[0], 0.0)

    def test_words_per_line_keeps_zwnj_compounds_whole(self):
        record = _instruction({"words_per_line": [3, 5]})
        poem = "باران آرام می‌بارد\nقطره‌ها روی شیشه‌ی پنجره می‌رقصند"
        self.assertEqual(score_record(record, poem)[0], 1.0)
        self.assertEqual(score_record(record, "باران آرام می‌بارد")[0], 0.0)

    def test_word_final(self):
        record = _instruction({"word_final": "ان", "min_words": 4, "max_words": 4})
        self.assertEqual(score_record(record, "دوستان مهربان خندان تهران")[0], 1.0)
        self.assertEqual(score_record(record, "دوستان مهربان خندان شیراز")[0], 0.0)

    def test_legacy_constraints_unchanged_when_new_keys_absent(self):
        record = _instruction({"required_keywords": ["بهار"], "max_words": 3})
        score, details = score_record(record, "بهار آمد")
        self.assertEqual(score, 1.0)
        self.assertEqual(set(details["checks"]), {"required_keywords", "max_words"})


class JsonScoringTests(unittest.TestCase):
    def test_json_field_accuracy_with_fences_and_digits(self):
        record = _json_record(
            {"city": "تهران", "area_m2": 85, "price_toman": 8500000000, "parking": True}
        )
        prediction = (
            "```json\n"
            '{"city": "تهران", "area_m2": "۸۵", "price_toman": "8,500,000,000", "parking": true}'
            "\n```"
        )
        score, details = score_record(record, prediction)
        self.assertEqual(score, 1.0, details)
        self.assertTrue(details["parsed"])

    def test_json_partial_credit_and_null_fields(self):
        record = _json_record({"city": "شیراز", "floor": None, "elevator": None, "rooms": 2})
        prediction = 'نتیجه: {"city": "شیراز", "floor": 3, "rooms": 2}'
        score, details = score_record(record, prediction)
        # city and rooms right, elevator correctly omitted, floor hallucinated.
        self.assertAlmostEqual(score, 0.75)
        self.assertFalse(details["fields"]["floor"])
        self.assertTrue(details["fields"]["elevator"])

    def test_json_alternatives_and_lenient_strings(self):
        record = _json_record({"neighbourhood": ["سعادت آباد", "سعادت‌آباد"], "type": "برداشت"})
        prediction = '{"neighbourhood": "محله سعادت‌آباد", "type": "برداشت"}'
        self.assertEqual(score_record(record, prediction)[0], 1.0)

    def test_json_unparseable_scores_zero(self):
        record = _json_record({"city": "تهران"})
        score, details = score_record(record, "شهر: تهران")
        self.assertEqual(score, 0.0)
        self.assertFalse(details["parsed"])

    def test_json_bool_is_not_number(self):
        record = _json_record({"rooms": 1})
        self.assertEqual(score_record(record, '{"rooms": true}')[0], 0.0)

    def test_json_rows_require_object_answer(self):
        with self.assertRaises(ValueError):
            _json_record({})


if __name__ == "__main__":
    unittest.main()
