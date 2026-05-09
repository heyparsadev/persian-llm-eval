import unittest

from persian_eval.backends import extract_response_text


class BackendsTests(unittest.TestCase):
    def test_extract_response_text_from_output_text(self):
        self.assertEqual(extract_response_text({"output_text": " پاسخ "}), "پاسخ")

    def test_extract_response_text_from_output_content(self):
        data = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "الف"},
                        {"type": "output_text", "text": "ب"},
                    ]
                }
            ]
        }
        self.assertEqual(extract_response_text(data), "الف\nب")


if __name__ == "__main__":
    unittest.main()
